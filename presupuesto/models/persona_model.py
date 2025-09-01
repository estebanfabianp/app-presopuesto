from config import get_connection

class PersonaModel:
    @staticmethod
    def obtener_todos():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM persona")
        personas = cursor.fetchall()
        cursor.close()
        conn.close()
        return personas

    @staticmethod
    def crear(nombre):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO persona (nombre) VALUES (%s)", (nombre,))
        conn.commit()
        cursor.close()
        conn.close()
