from flask import Blueprint, render_template, request, redirect, url_for, jsonify,session
import hashlib
import conexion # Importamos tu módulo de conexión

auth_bp = Blueprint('auth', __name__)

# --- Ruta para servir la página de login (DESCOMENTADA) ---
@auth_bp.route('/')
def index():
    # Renderiza el archivo login.html que está en la carpeta 'templates'
    if session.get('user_logged_in'):
        return redirect(url_for('auth.intro'))
    
    return render_template('index_login.html')

# --- Ruta para procesar el formulario de login (Ya corregida para usar conexion.py) ---
@auth_bp.route('/guardar_login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Obtener email y password del formulario
        email = request.form['email']
        password = request.form['password']

        # Validación básica
        if not email or not password:
            # Puedes retornar un error o redirigir con un mensaje
            print("Error: Email o password faltantes en la solicitud.")
            return jsonify({"message": "Error: Email o password faltantes"}), 400 # Ejemplo JSON

        # Cifrar la contraseña
        cifrado = hashlib.sha256()
        cifrado.update(password.encode('utf8'))
        password_cifrada = cifrado.hexdigest()
        
          # *** LÍNEAS DE DEPURACIÓN AGREGADAS/RESALTADAS ***
        print(f"--- Intento de Login ---")
        print(f"Email ingresado: {email}")
        print(f"Password en texto plano (no guardado): {password}") # ¡Solo para depuración! No hagas esto en producción
        print(f"Hash SHA256 generado del password ingresado: {password_cifrada}")
        print(f"-----------------------")
        # *** FIN LÍNEAS DE DEPURACIÓN ***

        

        # Conexión y consulta a la base de datos
        conn = None
        cursor = None
        result = None
        try:
            # *** Usar la función obtener_conexion() de tu módulo ***
            conn = conexion.obtener_conexion()

            if conn is None:
                # Error si no se pudo obtener la conexión
                 print("No se pudo obtener la conexión a la base de datos.")
                 return jsonify({"message": "Error interno del servidor (conexión a BD fallida)"}), 500

            cursor = conn.cursor()

            sql = "SELECT * FROM usuario WHERE email = %s AND password = %s"
            usuario_data = (email, password_cifrada)

            cursor.execute(sql, usuario_data)

            # Llamar a fetchone()
            result = cursor.fetchone()
            
            
            
            # *** 1. CAMBIO PARA DEPURACIÓN: Imprimir el resultado de la consulta ***
            print(f"DEBUG: Resultado de la consulta a la BD (result): {result}")
            # *** FIN DEL CAMBIO 1 ***
            
            
            

            # Manejar el resultado
            if result:
                
                
                  # *** 2. CAMBIO PARA DEPURACIÓN: Mensaje ANTES de establecer la sesión ***
                print(f"DEBUG: LOGIN EXITOSO - El bloque 'if result:' se ha ejecutado.")
                # *** FIN DEL CAMBIO 2 ***
                
                
                # *** 2. CAMBIO AQUÍ: Guardar estado de login en la sesión ***
                session['user_logged_in'] = True
                 # Opcionalmente, guardar más datos del usuario si los necesitas en la sesión
                # session['user_email'] = email # El email ya lo tienes
                # session['user_id'] = result[0] # Si el primer campo de 'result' es el ID de usuario
                
                
                 # *** 3. CAMBIO PARA DEPURACIÓN: Mensaje DESPUÉS de establecer la sesión ***
                print(f"DEBUG: session['user_logged_in'] establecida a: {session.get('user_logged_in')}")
                print(f"DEBUG: Contenido completo de la sesión AHORA: {session}")
                # *** FIN DEL CAMBIO 3 ***
                
              
                return redirect(url_for('auth.intro'))

            else:
                
                
                   # *** 4. CAMBIO PARA DEPURACIÓN: Mensaje si el login falla (result es None) ***
                print(f"DEBUG: LOGIN FALLIDO - 'result' es None o vacío. No se establece la sesión.")
                # *** FIN DEL CAMBIO 4 ***
                
                
                # Usuario no encontrado - Login fallido
                print(f"Intento de login fallido para: {email}")
                #
                return jsonify({"message": "Login fallido", "error": "Credenciales inválidas"}), 401 # Ejemplo JSON


        except Exception as e:
            # Manejo de errores durante la ejecución de la consulta, etc.
            print(f"Error en el proceso de login: {e}")
            return jsonify({"message": "Ocurrió un error en el servidor durante el login", "error": str(e)}), 500

        finally:
            # *** Usar la función cerrar_conexion() de tu módulo ***
            conexion.cerrar_conexion(conn, cursor)
            
    return redirect(url_for('auth.index'))

# *** 4. BLOQUE AÑADIDO: Ruta para cerrar sesión ***
@auth_bp.route('/logout')
def logout():
    session.pop('user_logged_in', None) # Elimina la variable de sesión
    
     # *** 5. CAMBIO PARA DEPURACIÓN: Mensaje en logout ***
    print("DEBUG: Ejecutando logout. Sesión 'user_logged_in' eliminada.")
    print(f"DEBUG: Contenido de la sesión después de pop: {session}")
    # *** FIN DEL CAMBIO 5 ***
    
    # session.clear() # Alternativa: borra toda la sesión
    print("Sesión cerrada.")
    return redirect(url_for('auth.index')) # Redirige a la página de login
# *** FIN BLOQUE AÑADIDO ***

@auth_bp.route('/intro') # O la URL que prefieras, ej: '/bienvenida_sociodemografico'
def intro():
    
    # *** 6. CAMBIO PARA DEPURACIÓN: Mensaje en intro ***
    print(f"DEBUG: Entrando a la ruta /intro. Valor de session.get('user_logged_in'): {session.get('user_logged_in')}")
    print(f"DEBUG: Contenido completo de la sesión en /intro: {session}")
    # *** FIN DEL CAMBIO 6 ***
    
    
     # *** 5. CAMBIO AQUÍ: Proteger esta ruta verificando la sesión ***
    if not session.get('user_logged_in'):
        return redirect(url_for('auth.index')) # Si no está logueado, va al login
    # Si llega aquí, está logueado.
    return render_template('intro.html')