from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import hashlib
import conexion # Importamos tu módulo de conexión

auth_bp = Blueprint('auth', __name__)

# --- Ruta para servir la página de login (DESCOMENTADA) ---
@auth_bp.route('/')
def index():
    # Renderiza el archivo login.html que está en la carpeta 'templates'
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

            # Manejar el resultado
            if result:
                # Usuario encontrado - Login exitoso
                print(f"Login exitoso para el usuario: {email}")
                # Aquí podrías iniciar una sesión Flask, redirigir al dashboard, etc.
                # Ejemplo: return redirect(url_for('dashboard')) # Necesitas definir la ruta 'dashboard'
                return redirect(url_for('auth.intro'))

            else:
                # Usuario no encontrado - Login fallido
                print(f"Intento de login fallido para: {email}")
                # Ejemplo: return redirect(url_for('index', error="Credenciales inválidas")) # Redirigir a la página de login con mensaje de error
                # Ejemplo: return render_template('login.html', error="Credenciales inválidas")
                return jsonify({"message": "Login fallido", "error": "Credenciales inválidas"}), 401 # Ejemplo JSON


        except Exception as e:
            # Manejo de errores durante la ejecución de la consulta, etc.
            print(f"Error en el proceso de login: {e}")
            return jsonify({"message": "Ocurrió un error en el servidor durante el login", "error": str(e)}), 500

        finally:
            # *** Usar la función cerrar_conexion() de tu módulo ***
            conexion.cerrar_conexion(conn, cursor)

@auth_bp.route('/intro') # O la URL que prefieras, ej: '/bienvenida_sociodemografico'
def intro():
    # Simplemente renderiza la plantilla HTML que creaste
    return render_template('intro.html')