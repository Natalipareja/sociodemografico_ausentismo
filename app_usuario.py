from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import hashlib
import conexion 
from datetime import datetime

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
        
        
        # --- 2. OBTENER FECHA Y HORA ACTUAL ---
        ahora = datetime.now() # Esto será usado para fecha_creacion y fecha_actualizacion
               
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
        valores = (tipo_documento, doc_id,  primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, password_cifrada, ahora, ahora) #Ahora para ambas fechas
        
        cur.execute(sql, valores)
        # Guardar cambios
        conn.commit()
        
        
        # --- 2. MENSAJE FLASH DE ÉXITO ---
        flash(f"¡Usuario {primer_nombre} {primer_apellido} guardado correctamente!", "success")
        
        return redirect(url_for('usuario.formulario_registro'))

       

    except Exception as e:
        # Manejo de errores
        # Es buena idea hacer rollback si algo falla durante la transacción
        if conn:
            conn.rollback()
            
        error_message = f"Error del servidor: {str(e)}"
        print(f"ERROR DETALLADO en guardar_usuario: {type(e).__name__} - {str(e)}")
        
         # --- 4. MENSAJE FLASH DE ERROR Y REDIRECCIÓN (OPCIONAL PERO RECOMENDADO) ---
        flash(f"No se pudo guardar el usuario. {error_message}", "error")
        # Redirigir de vuelta al formulario en caso de error para que el usuario pueda intentarlo de nuevo.
        return redirect(url_for('usuario.formulario_registro'))
        # ANTERIORMENTE:
        # return jsonify({"error": error_message}), 500

    finally:
        conexion.cerrar_conexion(conn, cur)
    
    #_________________________________________________________________________________
  #Ruta para mostrar el formulario
  
  

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