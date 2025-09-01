import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",      # Cambia por tu host
        user="root",           # Cambia por tu usuario
        password="tu_password",# Cambia por tu password
        database="mydb"        # Cambia por tu base de datos
    )