from flask_mysqldb import MySQL
from flask import Flask

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'  # Cambia si MySQL está en otro host
app.config['MYSQL_USER'] = 'root'  # Usuario de MySQL
app.config['MYSQL_PASSWORD'] = ''  # Reemplaza con tu contraseña
app.config['MYSQL_DB'] = 'infosociodemografica_ausentismo'  # Nombre de la base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

try:
    cur = mysql.connection.cursor()
    print("Conexión exitosa a MySQL")
except Exception as e:
    print("Error en la conexión:", e)