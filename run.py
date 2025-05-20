# AUSENTISMO/run.py
from flask import Flask, redirect, url_for, render_template # Añadido render_template
import os
import datetime # Para el año en el layout



# ---- Importar tus Blueprints ----
# Asegúrate que los nombres de los archivos y los nombres de las variables Blueprint coincidan
# con lo que definiste en cada archivo .py
# COMENTARIO ARRIBA DEL CAMBIO: Importar cada Blueprint que creaste
from login import auth_bp
from app_usuario import usuario_bp
from app_sociodemografico import sociodemografico_bp
from app_ausentismo import ausentismo_bp

# ---- Crear la instancia principal de la aplicación Flask ----
app = Flask(__name__)
# COMENTARIO ARRIBA DEL CAMBIO: Configurar una SECRET_KEY es importante para sesiones, mensajes flash, etc.
app.config['SECRET_KEY'] = os.urandom(24) # Genera una clave secreta aleatoria

# ---- Registrar los Blueprints en la aplicación principal ----
# COMENTARIO ARRIBA DEL CAMBIO: Registrar el Blueprint de autenticación (login)
app.register_blueprint(auth_bp, url_prefix='/auth') # Todas las rutas de login estarán bajo /auth (ej. /auth/, /auth/guardar_login)

# COMENTARIO ARRIBA DEL CAMBIO: Registrar el Blueprint de usuarios
app.register_blueprint(usuario_bp, url_prefix='/usuario') # Rutas como /usuario/, /usuario/guardar_usuario

# COMENTARIO ARRIBA DEL CAMBIO: Registrar el Blueprint sociodemográfico
app.register_blueprint(sociodemografico_bp, url_prefix='/sociodemografico') # Rutas como /sociodemografico/, /sociodemografico/guardar_info

# COMENTARIO ARRIBA DEL CAMBIO: Registrar el Blueprint de ausentismo
app.register_blueprint(ausentismo_bp, url_prefix='/ausentismo') # Rutas como /ausentismo/, /ausentismo/guardar_ausentismo

# ---- Context Processor para el año actual (para el layout.html) ----
# COMENTARIO ARRIBA DEL CAMBIO: Función para inyectar el año actual en todas las plantillas
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

# ---- Ruta raíz principal de la aplicación unificada (Opcional, pero recomendado) ----
# COMENTARIO ARRIBA DEL CAMBIO: Ruta principal de la aplicación
@app.route('/')
def home():
    # Redirigir a la página de login por defecto, por ejemplo.
    # Usa el nombre del blueprint y el nombre de la función (endpoint).
    return redirect(url_for('auth.index')) # Redirige a la función 'index' del blueprint 'auth'

# ---- Bloque para ejecutar la aplicación ----
if __name__ == '__main__':
    # Asegúrate de que debug=True SOLO para desarrollo
    print("--- Iniciando servidor Flask UNIFICADO (http://127.0.0.1:5000/) ---")
    app.run(debug=True, port=5000)