
import mysql.connector
from flask import Blueprint, render_template, request, jsonify, url_for
import os
import datetime # Para manejar fechas
import conexion
import math #para la paginación

ausentismo_bp = Blueprint('ausentismo', __name__)



# --- Funciones Auxiliares de Base de Datos ---
def fetch_all_from_table(table_name, order_by=None, columns='codigo, nombre'):
    """Obtiene registros de una tabla. Simplificado para evitar 'Unread result'."""
    conn = None # <-- Renombrado y inicializado
    cursor = None # <-- Inicializado
   
    if not order_by:
        order_by = columns.split(',')[0].strip()

    query_base = f"SELECT {columns} FROM {table_name}"
    query_con_orden = f"{query_base} ORDER BY {order_by}"

    try:
        conn = conexion.obtener_conexion()
        if not conexion: return []
        cursor = conn.cursor(dictionary=True)

        try:
            # Intento 1: Ejecutar con ORDER BY
            print(f"--- Ejecutando fetch_all (con orden por '{order_by}'): {query_con_orden} ---")
            cursor.execute(query_con_orden)
        except mysql.connector.Error as db_err:
            # Intento 2: Si falla específicamente por columna desconocida en ORDER BY (Error 1054)
            if db_err.errno == 1054 and order_by in db_err.msg:
                print(f"WARN: Falló orden por '{order_by}' en tabla '{table_name}'. Reintentando sin orden.")
                print(f"--- Ejecutando fetch_all (sin orden): {query_base} ---")
                cursor.execute(query_base) # Ejecutar consulta base SIN ORDER BY
            else:
                # Si es otro error, lo relanzamos para que se capture abajo
                raise db_err

        # Si alguna de las ejecuciones tuvo éxito, obtenemos los resultados
        resultados = cursor.fetchall()
        print(f"--- Datos obtenidos de '{table_name}': {len(resultados)} ---")
        return resultados

    except mysql.connector.Error as db_err:
        # Captura errores relanzados o errores en la conexión/cursor
        print(f"!!! Error de BD al obtener datos de '{table_name}': {db_err} !!!")
        return []
    except Exception as e:
         # Captura cualquier otro error inesperado
         print(f"!!! Error inesperado en fetch_all para '{table_name}': {e} !!!")
         return []
    finally:
       conexion.cerrar_conexion(conn, cursor)


# --- Rutas de la Aplicación Flask ---

@ausentismo_bp.route('/')
def formulario_ausentismo():
    """Carga datos iniciales para TODOS los selects del formulario."""
    print("--- Solicitud recibida en / ---")
    try:
        # Empleado
        cargos = fetch_all_from_table('cargo', columns='codigo, nombre', order_by='nombre')
        areas = fetch_all_from_table('area', columns='codigo, nombre', order_by='nombre')
        procesos = fetch_all_from_table('proceso', columns='codigo, nombre', order_by='nombre')
        tipos_contrato = fetch_all_from_table('tipo_contrato', columns='codigo, nombre', order_by='nombre')
        turnos_trabajo = fetch_all_from_table('turno_trabajo', columns='codigo, nombre', order_by='nombre')

        # Ausentismo (para los dropdowns)
        clases_incapacidades = fetch_all_from_table(
            'clase_incapacidad',  # Nombre de tabla según esquema
            columns='codigo, nombre', # Columnas según esquema (PK es codigo)
            order_by='nombre'
        )
        tipos_incapacidades = fetch_all_from_table(
            'tipo_incapacidad',
            columns='codigo, nombre', # Columnas según esquema (PK es codigo)
            order_by='nombre'
        )
        cie10_codigos = fetch_all_from_table(
            'cie_10',
            # Columna 'nombre' en lugar de 'descripcion' según esquema
            columns='codigo, nombre, grupo, segmento',
            order_by='codigo'
        )
        tipos_documentos = [
            "Registro civil de nacimiento", "Tarjeta de identidad", "Cédula de ciudadanía",
            "Tarjeta de extranjería", "Cédula de extranjería", "Pasaporte",
            "Permiso especial de permanencia"
        ]

        # Verificar si alguna carga falló (retornó lista vacía) - Opcional
        if not cargos or not areas or not procesos or not tipos_contrato or not turnos_trabajo or not clases_incapacidades or not tipos_incapacidades or not cie10_codigos:
             print("WARN: Faltaron datos al cargar uno o más selects iniciales.")
             # Podrías manejar este caso, quizás mostrando un error parcial o reintentando.

        return render_template(
            'index_ausentismo.html',
            cargos=cargos,
            areas=areas,
            procesos=procesos,
            tipos_documentos=tipos_documentos,
            tipos_contrato=tipos_contrato,
            turnos_trabajo=turnos_trabajo,
            # Pasar datos para selects de ausentismo
            clases_incapacidades=clases_incapacidades,
            tipos_incapacidades=tipos_incapacidades,
            cie10_codigos=cie10_codigos
        )
    except Exception as e:
        print(f"!!! Error General en /: {e} !!!")
        # Captura errores generales en la ruta, incluyendo los de fetch_all_from_table si no se manejaron antes
        return f"Error interno al cargar datos iniciales: {e}", 500


@ausentismo_bp.route('/obtener_datos_empleado')
def obtener_datos_empleado():
    """Busca datos del empleado (sin cambios respecto a la versión que funcionaba)."""
    # ... (Código exactamente igual a la versión anterior) ...
    documento_identidad = request.args.get('documento_identidad')
    print(f"--- Solicitud /obtener_datos_empleado para documento: {documento_identidad} ---")
    if not documento_identidad: return jsonify({"error": "Número de documento no proporcionado"}), 400
    
    conn = None # <--  Inicializar
    cursor = None # <-- Inicializar
    
    try:
        conn = conexion.obtener_conexion()
        
        if not conexion: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT
                i.primer_nombre, i.segundo_nombre, i.primer_apellido, i.segundo_apellido,
                i.fecha_nacimiento, i.sexo, i.fecha_ingreso_empresa,
                i.eps, i.afp, i.ciudad,
                i.tipo_contrato AS tipo_contrato_codigo,
                i.turno_trabajo AS turno_trabajo_codigo,
                i.cargo AS cargo_codigo,
                a.codigo AS area_codigo,
                p.codigo AS proceso_codigo
            FROM infosociodemografica i
            LEFT JOIN cargo cg ON i.cargo = cg.codigo
            LEFT JOIN area a ON cg.area = a.codigo
            LEFT JOIN proceso p ON a.proceso = p.codigo
            WHERE i.documento_identidad = %s
            ORDER BY i.documento_identidad DESC
            LIMIT 1
        """
        cursor.execute(query, (documento_identidad,))
        resultado = cursor.fetchone()
        print(f"--- Resultado BD Empleado: {resultado} ---")
        if resultado:
            for key in ['fecha_nacimiento', 'fecha_ingreso_empresa']:
                 if resultado.get(key):
                    if isinstance(resultado[key], (datetime.date, datetime.datetime)):
                         resultado[key] = resultado[key].strftime('%Y-%m-%d')
                    else:
                         resultado[key] = str(resultado[key]).split(' ')[0]
        return jsonify(resultado if resultado else {})
    except mysql.connector.Error as db_err:
        print(f"!!! Error BD /obtener_datos_empleado: {db_err} !!!")
        return jsonify({"error": f"Error BD ({db_err.errno}): {db_err.msg}"}), 500
    except Exception as e:
        print(f"!!! Error General /obtener_datos_empleado: {e} !!!")
        return jsonify({"error": f"Error interno: {e}"}), 500
    finally:
        conexion.cerrar_conexion(conn, cursor)
        print("--- Conexión /obtener_datos_empleado cerrada ---")


# --- RUTA /obtener_datos_ausentismo ELIMINADA ---
# (Se mantiene eliminada según el flujo de "solo guardar nuevo")


@ausentismo_bp.route('/guardar_ausentismo', methods=['POST'])
def guardar_ausentismo():
    """Guarda un NUEVO registro de ausentismo vinculado al empleado.
       (Sin cambios respecto a la versión anterior)."""
    # ... (Código exactamente igual a la versión anterior) ...
    print("--- Solicitud /guardar_ausentismo (POST) ---")
    
    conn = None # <-- CAMBIO: Inicializar y renombrar
    cur = None # <-- CAMBIO: Inicializar
    
    try:
        print("--- Datos recibidos del formulario:", request.form)
        # Obtener datos
        documento_identidad = request.form.get('documento_identidad')
        fecha_inicial = request.form.get('fecha_inicial')
        fecha_final = request.form.get('fecha_final')
        clase_incapacidad_codigo = request.form.get('clase_incapacidad')
        tipo_incapacidad_codigo = request.form.get('tipo_incapacidad')
        cie_10_codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        grupo = request.form.get('grupo')
        segmento = request.form.get('segmento')
        
           

        # Validación
        campos_obligatorios_ausentismo = {
            'documento_identidad': documento_identidad, 'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final, 'clase_incapacidad': clase_incapacidad_codigo,
            'tipo_incapacidad': tipo_incapacidad_codigo, 'cie_10': cie_10_codigo
        }
        
        
        faltantes_aus = [name for name, val in campos_obligatorios_ausentismo.items() if not val]
        if faltantes_aus:
             error_msg = f"Faltan datos obligatorios para registrar el ausentismo: {', '.join(faltantes_aus)}"
             print(f"!!! Error de Validación: {error_msg} !!!")
             return jsonify({"error": error_msg}), 400

        # Operaciones BD
        conn = conexion.obtener_conexion()
        if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        cur = conn.cursor()
        conn.start_transaction()        
        print("--- Transacción iniciada ---")
        try:
            cur.execute("SELECT codigo FROM cie_10 WHERE codigo=%s", (cie_10_codigo,))
            codigoEnfermedad=cur.fetchone()
            if not codigoEnfermedad:
                nombre = request.form.get('nombre')                
                grupo = request.form.get('grupo')
                segmento = request.form.get('segmento')
                cur.execute("INSERT INTO cie_10(codigo, nombre, grupo, segmento) VALUES(%s, %s, %s, %s)",(cie_10_codigo, nombre, grupo, segmento))
                
            # 1. Insertar en 'ausentismo' VINCULANDO
            sql_ausentismo = """INSERT INTO ausentismo
                                (fecha_inicio, fecha_final)
                                VALUES (%s, %s)"""
            cur.execute(sql_ausentismo, (fecha_inicial, fecha_final))
            codigo_ausentismo = cur.lastrowid
            if not codigo_ausentismo: raise Exception("No se pudo obtener el ID del ausentismo insertado.")
            print(f"--- Nuevo codigo_ausentismo generado: {codigo_ausentismo} para empleado {documento_identidad} ---")

            # 2. NO se inserta/modifica infosociodemografica

            # 3. Insertar en tablas intermedias
            sql_clase = "INSERT INTO ausentismo_clase (codigo_clase, codigo_ausentismo) VALUES (%s, %s)"
            cur.execute(sql_clase, (clase_incapacidad_codigo, codigo_ausentismo))
            sql_tipo = "INSERT INTO ausentismo_tipo_incapacidad (codigo_tipo_incapacidad, codigo_ausentismo) VALUES (%s, %s)"
            cur.execute(sql_tipo, (tipo_incapacidad_codigo, codigo_ausentismo))
            sql_cie = "INSERT INTO ausentismo_cie_10 (cie_10, codigo_ausentismo) VALUES (%s, %s)"
            cur.execute(sql_cie, (cie_10_codigo, codigo_ausentismo))

            # 4. Commit
            conn.commit()
            print(f"--- COMMIT realizado. Ausentismo: {codigo_ausentismo} guardado para empleado: {documento_identidad}. ---")
            
        
    # --- INICIO DEL ÚNICO CAMBIO ESTRUCTURAL EN EL JSON DE ÉXITO ---
            return jsonify({"mensaje": f"Datos de ausentismo para el documento {documento_identidad} guardados correctamente. Código Ausentismo: {codigo_ausentismo}", # Mensaje mejorado
                "codigo_ausentismo": codigo_ausentismo, 
                "documento": documento_identidad,
                "redirect_url": url_for('ausentismo.formulario_ausentismo') # <<<--- CAMBIO NECESARIO: Añadir esta URL
            }), 201
            # --- FIN DEL ÚNICO CAMBIO ESTRUCTURAL EN EL JSON DE ÉXITO --

        except mysql.connector.Error as db_err_tran:
            print(f"!!! Error de BD DENTRO de la transacción: {db_err_tran} !!!")
            if conn: conn.rollback(); print("--- ROLLBACK realizado ---")
            error_msg = f"Error de base de datos al guardar ({db_err_tran.errno}): {db_err_tran.msg}"
            return jsonify({"error": error_msg }), 500
        except Exception as e_tran:
            print(f"!!! Error General DENTRO de la transacción: {e_tran} !!!")
            if conn: conn.rollback(); print("--- ROLLBACK realizado ---")
            return jsonify({"error": f"Error interno al procesar el guardado: {e_tran}"}), 500
    except Exception as e_outer:
        print(f"!!! Error General ANTES de la transacción en /guardar_ausentismo: {e_outer} !!!")
        return jsonify({"error": "Error interno del servidor al procesar la solicitud"}), 500
    finally:
        conexion.cerrar_conexion(conn, cur)
        print("--- Conexión /guardar_ausentismo cerrada ---")

# ==============================================================================
# === RUTA PARA EL CONSOLIDADO DE AUSENTISMO (SOLO CAMBIOS EN ESTA SECCIÓN) ===
# ==============================================================================
@ausentismo_bp.route('/consolidado')
def consolidado_ausentismo():
    conn = None
    cursor = None
    registros_ausentismo = [] # Inicializar para asegurar que siempre se pase a la plantilla
    page = 1
    total_pages = 1
    try:
        conn = conexion.obtener_conexion()
        if not conn:
            print("Error: No se pudo conectar a la base de datos para el consolidado.")
            # Pasamos valores por defecto para que la plantilla no falle
            return render_template('consolidado_ausentismo.html', registros_para_tabla=registros_ausentismo, page=page, total_pages=total_pages, error_db="No se pudo conectar a la base de datos.")
        
        cursor = conn.cursor(dictionary=True)

        page = request.args.get('page', 1, type=int)
        per_page = 20 
        offset = (page - 1) * per_page

        # ===========================================================================
        # === INICIO DEL CAMBIO: CORREGIR NOMBRE DE TABLA EN COUNT(*) ===
        # Contar desde la tabla 'ausentismo' (singular, según tu esquema)
        cursor.execute("SELECT COUNT(*) AS total FROM ausentismo") 
        # === FIN DEL CAMBIO ===
        # ===========================================================================
        total_records_result = cursor.fetchone()
        total_records = total_records_result['total'] if total_records_result else 0
        total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1
        
        # ===========================================================================
        # === INICIO DEL CAMBIO: CONSULTA SQL TOTALMENTE REVISADA Y AJUSTADA AL ESQUEMA ===
        # Consulta SQL para obtener los datos de ausentismo con nombres de tablas relacionadas
        sql_consolidado_aus = """
           SELECT
                                
                infosociodemografica.tipo_documento AS tipo_documento_empleado,
                infosociodemografica.documento_identidad AS documento_identidad_empleado,
                infosociodemografica.primer_nombre AS primer_nombre_empleado,
                infosociodemografica.segundo_nombre AS segundo_nombre_empleado,
                infosociodemografica.primer_apellido AS primer_apellido_empleado,
                infosociodemografica.segundo_apellido AS segundo_apellido_empleado,
                DATE_FORMAT(infosociodemografica.fecha_nacimiento, '%%Y-%%m-%%d') AS fecha_nacimiento_empleado_f,
                TIMESTAMPDIFF(YEAR, infosociodemografica.fecha_nacimiento, CURDATE()) AS edad_empleado, 
                infosociodemografica.sexo AS sexo_empleado,
                DATE_FORMAT(infosociodemografica.fecha_ingreso_empresa, '%%Y-%%m-%%d') AS fecha_ingreso_empresa_f,
                tipoContrato.nombre AS nombre_tipo_contrato,
                proceso.nombre AS nombre_proceso,
                area.nombre AS nombre_area,
                cargo.nombre AS nombre_cargo, 
                turnoTrabajo.nombre AS nombre_turno_trabajo,
                DATE_FORMAT(aus.fecha_inicio, '%%Y-%%m-%%d') AS fecha_inicial_ausentismo_f,
                DATE_FORMAT(aus.fecha_final, '%%Y-%%m-%%d') AS fecha_final_ausentismo_f,
                
                claseinc.nombre AS nombre_clase_incapacidad,               
                cie_10.codigo AS codigo_diagnostico_cie10,
                cie_10.nombre AS nombre_diagnostico,
                cie_10.grupo AS grupo_diagnostico,
                cie_10.segmento AS segmento_diagnostico,          
               
                tp.nombre AS nombre_tipo_incapacidad,
                eps.nombre AS nombre_eps
                
            FROM 
                infosociodemografica as infosociodemografica
                INNER JOIN 
                tipo_contrato as tipoContrato ON infosociodemografica.tipo_contrato = tipoContrato.codigo
                INNER JOIN 
                turno_trabajo as turnoTrabajo ON infosociodemografica.turno_trabajo = turnoTrabajo.codigo
                INNER JOIN 
                eps as eps ON infosociodemografica.eps = eps.codigo
                INNER JOIN
                cargo as cargo ON infosociodemografica.cargo = cargo.codigo
                INNER JOIN
                area as area ON cargo.area = area.codigo
                INNER JOIN
                proceso as proceso ON area.proceso = proceso.codigo
                
                INNER JOIN
                ausentismo_infosociodemografica as auinfo ON infosociodemografica.documento_identidad = auinfo.infosociodemografica_docIumento_identidad
                INNER JOIN
                ausentismo as aus ON auinfo.codigo_ausentismo = aus.codigo
                INNER JOIN
                ausentismo_tipo_incapacidad as austp ON aus.codigo = austp.codigo_ausentismo
                INNER JOIN 
                tipo_incapacidad as tp ON austp.codigo_tipo_incapacidad = tp.codigo
                INNER JOIN 
                ausentismo_cie_10 as auscie10 ON aus.codigo = auscie10.codigo_ausentismo
                INNER JOIN
                cie_10 as cie_10 ON auscie10.cie_10 = cie_10.codigo
                INNER JOIN
                ausentismo_clase as ausclase ON aus.codigo = ausclase.codigo_ausentismo
                INNER JOIN
                clase_incapacidad as claseinc ON ausclase.codigo_clase = claseinc.codigo
                
                
            LIMIT %s OFFSET %s;
        """
        # === FIN DEL CAMBIO EN LA CONSULTA SQL ===
        # ===========================================================================
        cursor.execute(sql_consolidado_aus, (per_page, offset))
        registros_ausentismo = cursor.fetchall()
        
        # ==============================================================
        # === AÑADIR ESTA LÍNEA PARA VER LOS DATOS EN LA CONSOLA ===
        # ==============================================================
        print("***************** DATOS DE LA CONSULTA *****************")
        print(registros_ausentismo)
        print("********************************************************")

    except Exception as e:
        print(f"Error al obtener datos para el consolidado de ausentismo: {e}")
        # No sobrescribir page y total_pages aquí si ya se calcularon o se quiere mantener el error
    finally:
        conexion.cerrar_conexion(conn, cursor)

    return render_template('consolidado_ausentismo.html',
                           registros_para_tabla=registros_ausentismo,
                           page=page,
                           total_pages=total_pages)