from flask import Blueprint, render_template, request, jsonify, url_for
import os
import conexion
import math #para la paginación

sociodemografico_bp = Blueprint('sociodemografico', __name__)

@sociodemografico_bp.route('/intro') # O la URL que prefieras, ej: '/bienvenida_sociodemografico'
def intro():
    # Simplemente renderiza la plantilla HTML que creaste
    return render_template('intro.html')

# @sociodemografico_bp.route('/intro_sociodemografico') # O la URL que prefieras, ej: '/bienvenida_sociodemografico'
# def intro_sociodemografico():
#     # Simplemente renderiza la plantilla HTML que creaste
#     return render_template('intro_sociodemografico.html')


# Ruta para procesar el formulario y guardar los datos

@sociodemografico_bp.route('/guardar_info', methods=['POST'])

def guardar_info():
    # Inicializamos las variables para que existan en el contexto del finally
    conn = None 
    cur = None
    
    try:
        print(request.form)  # Para ver qué datos llegan al servidor
        
        #Obtener datos del formulario 
        usuario = request.form['usuario']
        tipo_documento = request.form['tipo_documento']
        documento_identidad = request.form['documento_identidad']
        primer_nombre = request.form['primer_nombre']
        segundo_nombre = request.form['segundo_nombre']
        primer_apellido = request.form['primer_apellido']
        segundo_apellido = request.form['segundo_apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        sexo = request.form['sexo']
        nivel_escolaridad = request.form['nivel_escolaridad']
        estado_civil = request.form['estado_civil']
        composicion_familiar = request.form['composicion_familiar']
        hijos = request.form['hijos'] 
        cabeza_hogar = request.form['cabeza_hogar']
        #departamento = request.form['departamento']        
        ciudad = request.form['ciudad']                    
        direccion = request.form['direccion']
        tipo_vivienda = request.form['tipo_vivienda']
        estrato = request.form['estrato']
        fecha_ingreso_empresa = request.form['fecha_ingreso_empresa']        
        tipo_contrato = request.form['tipo_contrato']
        cargo = request.form['cargo']
        # area = request.form['area']        
        # proceso = request.form['proceso']
        turno_trabajo = request.form['turno_trabajo']
        ingresos = request.form['ingresos']
        eps = request.form['eps']
        afp = request.form['afp']
        
       

        
       # Conectar a MySQL usando la función del módulo importado
        # <--  Se llama a la función desde el módulo 'conexion' y se asigna a 'conn'
        conn = conexion.obtener_conexion()
        if conn is None:
             # <--  Manejar fallo de conexión
             return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        cur = conn.cursor()
              
         # Insertar datos en la base de datos, tabla principal infosociodemotrafica
        sql = """
            INSERT INTO infosociodemografica 
            (usuario, tipo_documento, documento_identidad, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, sexo, nivel_escolaridad, estado_civil, composicion_familiar, hijos, cabeza_hogar, ciudad, direccion, tipo_vivienda, estrato, fecha_ingreso_empresa, tipo_contrato, cargo, turno_trabajo,ingresos, eps, afp) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """       
        valores = (usuario, tipo_documento, documento_identidad,  primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, sexo, nivel_escolaridad, estado_civil, composicion_familiar, hijos, cabeza_hogar, ciudad, direccion, tipo_vivienda, estrato,  fecha_ingreso_empresa, tipo_contrato, cargo, turno_trabajo, ingresos, eps, afp)
        
        cur.execute(sql, valores)

        # Guardar cambios
        conn.commit()

        return jsonify({
            "mensaje": "Datos guardados correctamente",
            "documento": documento_identidad            
        }), 200

    except Exception as e:
        # Manejo de errores
        if conn:
            conn.rollback()
        print(f"Error en guardar_info: {e}") # <-- CAMBIO: Mejor loguear el error en el servidor
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500

    finally:
       # Cierre de conexión usando la función del módulo
        # <--  Se llama a la función de cierre del módulo 'conexion'
        conexion.cerrar_conexion(conn, cur)

  #_________________________________________________________________________________
  #Ruta para mostrar el formulario
  
  
# trae cargos y departamentos

@sociodemografico_bp.route('/')
def formulario_sociodemografico():
    print("Entró al formulario")
    conn = None  # <--  Inicializar
    cursor = None # <-- Inicializar
    try:
        conn = conexion.obtener_conexion()
        if conn is None:
             # <-- CAMBIO: Manejar fallo de conexión
             return "Error al cargar datos: No se pudo conectar a la base de datos", 500
        cursor = conn.cursor(dictionary=True)

        # Cargar cargos
        cursor.execute("SELECT codigo, nombre FROM cargo")
        cargos = cursor.fetchall()

       #Cargar departamentos
        cursor.execute("SELECT codigo, nombre FROM departamento")
        departamentos = cursor.fetchall()
        
         #Cargar contratos
        cursor.execute("SELECT codigo, nombre FROM tipo_contrato")
        contratos = cursor.fetchall()
        
         #Cargar turnos
        cursor.execute("SELECT codigo, nombre FROM turno_trabajo")
        turnos = cursor.fetchall()
        
          #Cargar epss
        cursor.execute("SELECT codigo, nombre FROM eps")
        epss = cursor.fetchall()
        
         #Cargar afps
        cursor.execute("SELECT codigo, nombre FROM afp")
        afps = cursor.fetchall()
            
        
        
 # Lista de tipo documento
        tipos_documentos = [
            "Registro civil de nacimiento",
            "Tarjeta de identidad",
            "Cédula de ciudadanía",
            "Tarjeta de extranjería",
            "Cédula de extranjería",
            "Pasaporte",
            "Permiso especial de permanencia"
        ]

        # Lista de niveles de escolaridad
        niveles_escolaridad = [
            "Ninguno",
            "Primaria incompleta",
            "Primaria completa",
            "Secundaria incompleta",
            "Secundaria completa",
            "Técnica",
            "Tecnología",
            "Profesional",
            "Especialización",
            "Maestría",
            "Doctorado"
        ]
        
         # Lista de estado civil
        estado_civil = [
            "Soltero(a)",
            "Casado(a)",
            "Viudo(a)",
            "Separado(a)",
            "Divorciado(a)",
            "Compañero(a) permanente"           
        ]
        
         # Lista de hijos
        hijos = [
            "No tengo",
            "Entre 1 y 2",
            "Entre 3 y 5",
            "Mas de 6"                     
        ]
        
        # Lista de tipos vivienda
        tipos_viviendas = [
            "Propia",
            "Arrendada",
            "Familiar"                       
        ]
        
          # Lista de estratos
        estratos = [
            "1",
            "2",
            "3",
            "4", 
            "5",
            "6"                         
        ]
        
        ingresos = [
            "1 SMLMV",
            "Entre 2 y 3 SMLMV",
            "Entre 4 y 5 SMLMV",
            "Entre 6 y 7 SMLMV", 
            "Mas de 8 SMLMV"                       
        ]  
        
        return render_template(
            'index_sociodemografico.html',
            
            tipos_documentos=tipos_documentos,
            cargos=cargos,
            departamentos=departamentos,
            niveles_escolaridad=niveles_escolaridad,
            estado_civil=estado_civil,
            hijos=hijos,
            tipos_viviendas=tipos_viviendas,
            estratos=estratos,
            ingresos=ingresos,
            contratos=contratos,
            turnos=turnos,
            epss=epss,
            afps=afps
            
        )
    except Exception as e:
        print(f"Error en formulario_sociodemografico: {e}") # <--  Log error
        return f"Error al cargar datos: {e}", 500 # <--  Devolver código 500
    finally:
        # <-- Usar función de cierre del módulo
        conexion.cerrar_conexion(conn, cursor)

# Ruta para obtener ciudades según el departamento
@sociodemografico_bp.route('/obtener_ciudades')
def obtener_ciudades():
    departamento_id = request.args.get('departamento')
    conn = None # <--  Inicializar
    cursor = None # <--  Inicializar    
    try:
         # <-- CAMBIO: Usar módulo conexion y asignar a 'conn'
        conn = conexion.obtener_conexion()
        if conn is None:
             # <-- CAMBIO: Manejar fallo de conexión
             return jsonify({"error": "No se pudo conectar a la base de datos"}), 500 
    
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT codigo, nombre FROM ciudad WHERE departamento = %s", (departamento_id,))
        ciudades = cursor.fetchall()
        return jsonify(ciudades)
    except Exception as e:
        print(f"Error en obtener_ciudades: {e}") # <-- CAMBIO: Log error
        return jsonify({"error": str(e)}), 500
    finally:
        conexion.cerrar_conexion(conn, cursor) 
 

 # Carga la vista con los cargos      

@sociodemografico_bp.route('/obtener_area_proceso')
def obtener_area_proceso():
    cargo_codigo = request.args.get('cargo_codigo')
    conn = None # <--  Inicializar
    cursor = None # <--  Inicializar
    try:
        conn = conexion.obtener_conexion()
        if conn is None:
             # <-- CAMBIO: Manejar fallo de conexión
             return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
         
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                area.nombre AS area,
                proceso.nombre AS proceso
            FROM cargo
            JOIN area ON cargo.area = area.codigo
            JOIN proceso ON area.proceso = proceso.codigo
            WHERE cargo.codigo = %s
        """
        cursor.execute(query, (cargo_codigo,))
        resultado = cursor.fetchone()
        
        
        return jsonify(resultado if resultado else {})
    except Exception as e:
        print(f"Error en obtener_area_proceso: {e}") # <-- CAMBIO: Log error
        return jsonify({"error": str(e)}), 500
    finally:
        conexion.cerrar_conexion(conn, cursor)


# =================================================================================
# ========= AQUÍ VA LA RUTA PARA EL CONSOLIDADO SOCIODEOGRÁFICO ============
# =================================================================================
@sociodemografico_bp.route('/consolidado')
def consolidado_sociodemografico_tabla():
    conn = None
    cursor = None
    registros_para_tabla = [] # Inicializa como lista vacía    
    page = 1
    total_pages = 1

    try:
        conn = conexion.obtener_conexion()
        if conn is None:
            # Manejar fallo de conexión, podrías mostrar un mensaje en la plantilla
            print("Error al conectar con la BD para el consolidado")
            # Podrías pasar un mensaje de error a la plantilla si lo deseas
            return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla, page=page, total_pages=total_pages, error_db="No se pudo conectar a la base de datos.")

        cursor = conn.cursor(dictionary=True) # Obtener resultados como diccionarios
        
        page = request.args.get('page', 1, type=int)
        per_page = 20 
        offset = (page - 1) * per_page
        
         # ===========================================================================
        # === INICIO DEL CAMBIO: CORREGIR NOMBRE DE TABLA EN COUNT(*) ===
        # Contar desde la tabla 'ausentismo' (singular, según tu esquema)
        cursor.execute("SELECT COUNT(*) AS total FROM infosociodemografica") 
        # === FIN DEL CAMBIO ===
        # ===========================================================================
        total_records_result = cursor.fetchone()
        total_records = total_records_result['total'] if total_records_result else 0
        total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1
        

        # --- COMIENZO DEL CAMBIO: MODIFICAR ESTA CONSULTA SQL ---
        # Se añaden 4 LEFT JOIN más y se cambian los campos en el SELECT
        # para obtener los NOMBRES en lugar de los códigos.
        sql_consolidado = """
            SELECT
                i.usuario, i.tipo_documento, i.documento_identidad,
                i.primer_nombre, i.segundo_nombre, i.primer_apellido, i.segundo_apellido,
                DATE_FORMAT(i.fecha_nacimiento, '%Y-%m-%d') AS fecha_nacimiento_formateada,
                
                -- LÍNEA AÑADIDA PARA CALCULAR LA EDAD --
                TIMESTAMPDIFF(YEAR, i.fecha_nacimiento, CURDATE()) AS edad,
                
                i.sexo, i.nivel_escolaridad, i.estado_civil,
                i.composicion_familiar, i.hijos, i.cabeza_hogar,
                ciudad.nombre AS nombre_ciudad,           -- Nombre de la ciudad
                departamento.nombre AS nombre_departamento, -- Nombre del departamento
                i.direccion, i.tipo_vivienda, i.estrato,
                DATE_FORMAT(i.fecha_ingreso_empresa, '%Y-%m-%d') AS fecha_ingreso_formateada,
                
                -- CAMBIO 1: Obtener nombre del tipo de contrato
                tc.nombre AS tipo_contrato,
                
                cargo.nombre AS nombre_cargo,             -- Nombre del cargo
                area.nombre AS nombre_area,               -- Nombre del área
                proceso.nombre AS nombre_proceso,         -- Nombre del proceso
                
                -- CAMBIO 2: Obtener nombre del turno de trabajo
                tt.nombre AS turno_trabajo,
                
                i.ingresos, 
                
                -- CAMBIO 3: Obtener nombre de la EPS
                e.nombre AS eps, 
                
                -- CAMBIO 4: Obtener nombre de la AFP
                a.nombre AS afp
                
            FROM infosociodemografica i
            LEFT JOIN ciudad ON i.ciudad = ciudad.codigo
            LEFT JOIN departamento ON ciudad.departamento = departamento.codigo
            LEFT JOIN cargo ON i.cargo = cargo.codigo
            LEFT JOIN area ON cargo.area = area.codigo
            LEFT JOIN proceso ON area.proceso = proceso.codigo
            
            -- CAMBIO 5: Añadir las nuevas uniones (JOINs) a las tablas correspondientes
            LEFT JOIN tipo_contrato tc ON i.tipo_contrato = tc.codigo
            LEFT JOIN turno_trabajo tt ON i.turno_trabajo = tt.codigo
            LEFT JOIN eps e ON i.eps = e.codigo
            LEFT JOIN afp a ON i.afp = a.codigo
            
            ORDER BY i.primer_apellido, i.primer_nombre; -- Opcional: ordenar los resultados
            
            LIMIT %s OFFSET %s;
        """
        # --- FIN DEL CAMBIO ---

        cursor.execute(sql_consolidado, (per_page, offset))
        registros_para_tabla = cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener datos para el consolidado sociodemográfico: {e}")
      
        return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla, error_db=f"Error al obtener datos: {e}")
    finally:
        conexion.cerrar_conexion(conn, cursor)

    # Renderizar la plantilla HTML del consolidado, pasando los datos.
    # El nombre 'consolidado_sociodemografic.html' debe coincidir con tu archivo en la carpeta 'templates'.
    return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla, page=page,
                           total_pages=total_pages)
# =================================================================================
# ======================= FIN DE LA NUEVA RUTA ====================================
# =================================================================================




# =====================================================================
# === RUTA PARA MOSTRAR LA PÁGINA DEL DASHBOARD DE GRÁFICOS ===
# =====================================================================
@sociodemografico_bp.route('/dashboard')
def dashboard():
    # Esta ruta simplemente renderiza el HTML. 
    # El JavaScript se encargará de pedir los datos y dibujar los gráficos.
    return render_template('dashboard_sociodemografico.html')


# =====================================================================
# === RUTA "API" PARA PROVEER TODOS LOS DATOS A LOS GRÁFICOS ===
# =====================================================================
@sociodemografico_bp.route('/dashboard/data')
def dashboard_data():
    conn = None
    cursor = None
    try:
        conn = conexion.obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        # Diccionario para almacenar los resultados de todas las consultas
        data = {}

        # 1. Gráfico por Edad (Rango)
        query_edad = """
            SELECT CASE
                WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
                WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 26 AND 35 THEN '26-35'
                WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 36 AND 45 THEN '36-45'
                WHEN TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) BETWEEN 46 AND 55 THEN '46-55'
                ELSE '55+' END AS rango_edad, COUNT(*) as total
            FROM infosociodemografica WHERE fecha_nacimiento IS NOT NULL GROUP BY rango_edad ORDER BY rango_edad;
        """
        cursor.execute(query_edad)
        data['edad'] = cursor.fetchall()

        # 2. Gráfico por Género
        cursor.execute("SELECT sexo, COUNT(*) as total FROM infosociodemografica WHERE sexo IS NOT NULL AND sexo != '' GROUP BY sexo;")
        data['genero'] = cursor.fetchall()

        # 3. Gráfico por Nivel de Escolaridad
        cursor.execute("SELECT nivel_escolaridad, COUNT(*) as total FROM infosociodemografica WHERE nivel_escolaridad IS NOT NULL AND nivel_escolaridad != '' GROUP BY nivel_escolaridad ORDER BY total DESC;")
        data['escolaridad'] = cursor.fetchall()

        # 4. Gráfico por Estado Civil
        cursor.execute("SELECT estado_civil, COUNT(*) as total FROM infosociodemografica WHERE estado_civil IS NOT NULL AND estado_civil != '' GROUP BY estado_civil ORDER BY total DESC;")
        data['estado_civil'] = cursor.fetchall()

        # 5. Gráfico por Número de Hijos
        cursor.execute("SELECT hijos, COUNT(*) as total FROM infosociodemografica WHERE hijos IS NOT NULL AND hijos != '' GROUP BY hijos ORDER BY hijos;")
        data['hijos'] = cursor.fetchall()

        # 6. Gráfico por Lugar de Residencia (Top 10 Ciudades)
        query_residencia = """
            SELECT c.nombre as ciudad, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i JOIN ciudad c ON i.ciudad = c.codigo
            GROUP BY c.nombre ORDER BY total DESC LIMIT 10;
        """
        cursor.execute(query_residencia)
        data['residencia'] = cursor.fetchall()

        # 7. Gráfico por Tipo de Vivienda
        cursor.execute("SELECT tipo_vivienda, COUNT(*) as total FROM infosociodemografica WHERE tipo_vivienda IS NOT NULL AND tipo_vivienda != '' GROUP BY tipo_vivienda ORDER BY total DESC;")
        data['vivienda'] = cursor.fetchall()

        # 8. Gráfico por Estrato
        cursor.execute("SELECT estrato, COUNT(*) as total FROM infosociodemografica WHERE estrato IS NOT NULL AND estrato != '' GROUP BY estrato ORDER BY estrato;")
        data['estrato'] = cursor.fetchall()

        # 9. Gráfico por Cabeza de Hogar
        cursor.execute("SELECT cabeza_hogar, COUNT(*) as total FROM infosociodemografica WHERE cabeza_hogar IS NOT NULL AND cabeza_hogar != '' GROUP BY cabeza_hogar;")
        data['cabeza_hogar'] = cursor.fetchall()

        # 10. Gráfico por Tipo de Vinculación (Contrato)
        query_vinculacion = """
            SELECT tc.nombre as tipo_contrato, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i JOIN tipo_contrato tc ON i.tipo_contrato = tc.codigo
            GROUP BY tc.nombre ORDER BY total DESC;
        """
        cursor.execute(query_vinculacion)
        data['vinculacion'] = cursor.fetchall()

        # 11. Gráfico por Proceso
        query_proceso = """
            SELECT p.nombre as proceso, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i
            JOIN cargo c ON i.cargo = c.codigo
            JOIN area a ON c.area = a.codigo
            JOIN proceso p ON a.proceso = p.codigo
            GROUP BY p.nombre ORDER BY total DESC;
        """
        cursor.execute(query_proceso)
        data['proceso'] = cursor.fetchall()

        # 12. Gráfico por Área
        query_area = """
            SELECT a.nombre as area, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i
            JOIN cargo c ON i.cargo = c.codigo
            JOIN area a ON c.area = a.codigo
            GROUP BY a.nombre ORDER BY total DESC;
        """
        cursor.execute(query_area)
        data['area'] = cursor.fetchall()

        # 13. Gráfico por EPS (Top 10)
        query_eps = """
            SELECT e.nombre as eps, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i JOIN eps e ON i.eps = e.codigo
            GROUP BY e.nombre ORDER BY total DESC LIMIT 10;
        """
        cursor.execute(query_eps)
        data['eps'] = cursor.fetchall()

        # 14. Gráfico por AFP (Top 10)
        query_afp = """
            SELECT af.nombre as afp, COUNT(i.documento_identidad) as total
            FROM infosociodemografica i JOIN afp af ON i.afp = af.codigo
            GROUP BY af.nombre ORDER BY total DESC LIMIT 10;
        """
        cursor.execute(query_afp)
        data['afp'] = cursor.fetchall()

        # Retornamos todo el diccionario de datos como un único JSON
        return jsonify(data)

    except Exception as e:
        print(f"Error al obtener datos para el dashboard: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.cerrar_conexion(conn, cursor)
