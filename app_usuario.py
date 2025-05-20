from flask import Blueprint, render_template, request, jsonify
import hashlib
import conexion 


usuario_bp = Blueprint('usuario', __name__)


# Ruta para procesar el formulario y guardar los datos

@usuario_bp.route('/guardar_usuario', methods=['POST'])

def guardar_usuario():
    # Inicializamos las variables para que existan en el contexto del finally
    conn = None
    cur = None
    
    try:
        print(request.form)  # Para ver qué datos llegan al servidor
        
        #Obtener datos del formulario 
        
        tipo_documento = request.form['tipo_documento']
        doc_id = request.form['doc_id']
        primer_nombre = request.form['primer_nombre']
        segundo_nombre = request.form['segundo_nombre']
        primer_apellido = request.form['primer_apellido']
        segundo_apellido = request.form['segundo_apellido']
        email = request.form['email']
        password = request.form['password']
        fecha_creacion = request.form['fecha_creacion']
        fecha_actualizacion = request.form['fecha_actualizacion']
        
               
         # Conectar a MySQL
        conn = conexion.obtener_conexion()
        if conn is None:
             # Manejar el caso donde la conexión falla
             return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor()
        
        
               
        #cifrar la contraseña
        cifrado = hashlib.sha256()
        cifrado.update(password.encode('utf8'))
        password_cifrada = cifrado.hexdigest()
              
         # Insertar datos en la base de datos, tabla usuario
        sql = """
            INSERT INTO usuario 
            (tipo_documento, doc_id, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, password, fecha_creacion, fecha_actualizacion) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """       
        valores = (tipo_documento, doc_id,  primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, password_cifrada, fecha_creacion, fecha_actualizacion)
        
        cur.execute(sql, valores)

        # Guardar cambios
        conn.commit()

        return jsonify({
            "mensaje": "Datos guardados correctamente",
            # "codigo_ausentismo": codigo_ausentismo,
            "documento": doc_id            
        }), 200

    except Exception as e:
        # Manejo de errores
        # Es buena idea hacer rollback si algo falla durante la transacción
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
         # Cierre de conexión usando la función del módulo (opcional pero recomendado)
        # <-- CAMBIO: Se llama a la función de cierre del módulo 'conexion'
        conexion.cerrar_conexion(conn, cur)
        
  #_________________________________________________________________________________
  #Ruta para mostrar el formulario
  
  
# trae cargos y departamentos

@usuario_bp.route('/')
def formulario_registro():
    print("Entró al formulario")
    conn = None
    cursor = None
    try:
        # <-- CAMBIO: Se llama a la función desde el módulo 'conexion'
        conn = conexion.obtener_conexion()
        if conn is None:
             return f"Error al cargar datos: No se pudo conectar a la base de datos"
        
        cursor = conn.cursor(dictionary=True)

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
     
          
        return render_template(
            'index_usuario.html',
            
            tipos_documentos=tipos_documentos
           
        )
    except Exception as e:
        print("Error:", e)
        return f"Error al cargar datos: {e}"
    finally:
        conexion.cerrar_conexion(conn, cursor)