# Nombre del archivo: conexion.py
import mysql.connector
import os # Opcional: para leer credenciales desde variables de entorno

def obtener_conexion():
    """
    Establece y devuelve una conexión a la base de datos MySQL.
    """
    try:
       # Hardcoded (como en tu ejemplo original, menos recomendado para producción)
        host = "localhost"
        user = "root"
        password = ""
        database = "infosociodemografica_ausentismo"

        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        # Podrías lanzar una excepción personalizada o devolver None
        # dependiendo de cómo quieras manejar los errores de conexión.
        return None

# Puedes agregar aquí otras funciones relacionadas con la base de datos si es necesario,
# por ejemplo, una función para cerrar la conexión de forma segura.
def cerrar_conexion(conexion, cursor=None):
    """Cierra el cursor y la conexión a la base de datos."""
    if cursor:
        try:
            cursor.close()
        except Exception as e:
            print(f"Error al cerrar el cursor: {e}")
    if conexion and conexion.is_connected():
        try:
            conexion.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")