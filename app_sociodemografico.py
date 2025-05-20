from flask import Blueprint, render_template, request, jsonify
import conexion

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
            ingresos=ingresos
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
# ========= AQUÍ VA LA NUEVA RUTA PARA EL CONSOLIDADO SOCIODEOGRÁFICO ============
# =================================================================================
@sociodemografico_bp.route('/consolidado')
def consolidado_sociodemografico_tabla():
    conn = None
    cursor = None
    registros_para_tabla = [] # Inicializa como lista vacía

    try:
        conn = conexion.obtener_conexion()
        if conn is None:
            # Manejar fallo de conexión, podrías mostrar un mensaje en la plantilla
            print("Error al conectar con la BD para el consolidado")
            # Podrías pasar un mensaje de error a la plantilla si lo deseas
            return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla, error_db="No se pudo conectar a la base de datos.")

        cursor = conn.cursor(dictionary=True) # Obtener resultados como diccionarios

        # Consulta SQL para obtener todos los datos necesarios para el consolidado
        # Se hacen JOINs para obtener los nombres en lugar de solo los códigos
        # Se formatean las fechas directamente en la consulta
        sql_consolidado = """
            SELECT
                i.usuario, i.tipo_documento, i.documento_identidad,
                i.primer_nombre, i.segundo_nombre, i.primer_apellido, i.segundo_apellido,
                DATE_FORMAT(i.fecha_nacimiento, '%Y-%m-%d') AS fecha_nacimiento_formateada,
                i.sexo, i.nivel_escolaridad, i.estado_civil,
                i.composicion_familiar, i.hijos, i.cabeza_hogar,
                ciudad.nombre AS nombre_ciudad,          -- Nombre de la ciudad
                departamento.nombre AS nombre_departamento, -- Nombre del departamento
                i.direccion, i.tipo_vivienda, i.estrato,
                DATE_FORMAT(i.fecha_ingreso_empresa, '%Y-%m-%d') AS fecha_ingreso_formateada,
                i.tipo_contrato,
                cargo.nombre AS nombre_cargo,            -- Nombre del cargo
                area.nombre AS nombre_area,              -- Nombre del área
                proceso.nombre AS nombre_proceso,        -- Nombre del proceso
                i.turno_trabajo, i.ingresos, i.eps, i.afp
            FROM infosociodemografica i
            LEFT JOIN ciudad ON i.ciudad = ciudad.codigo
            LEFT JOIN departamento ON ciudad.departamento = departamento.codigo
            LEFT JOIN cargo ON i.cargo = cargo.codigo
            LEFT JOIN area ON cargo.area = area.codigo
            LEFT JOIN proceso ON area.proceso = proceso.codigo
            ORDER BY i.primer_apellido, i.primer_nombre; -- Opcional: ordenar los resultados
        """
        cursor.execute(sql_consolidado)
        registros_para_tabla = cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener datos para el consolidado sociodemográfico: {e}")
        # Podrías pasar un mensaje de error a la plantilla si lo deseas
        return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla, error_db=f"Error al obtener datos: {e}")
    finally:
        conexion.cerrar_conexion(conn, cursor)

    # Renderizar la plantilla HTML del consolidado, pasando los datos.
    # El nombre 'consolidado_sociodemografico.html' debe coincidir con tu archivo en la carpeta 'templates'.
    return render_template('consolidado_sociodemografico.html', registros_para_tabla=registros_para_tabla)
# =================================================================================
# ======================= FIN DE LA NUEVA RUTA ====================================
# =================================================================================