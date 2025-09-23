import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector

class UserModel:
    def __init__(self, host="localhost", database="mydb", user="root", password=""):
        self.db = DatabaseConnector(host=host, database=database, user=user, password=password)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
        """
        self.db.execute(query)

    def add_user(self, name, email):
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        
        try:
            cursor = self.db.execute(query, (name, email))
            if cursor:
                user_id = cursor.lastrowid
                cursor.close()
                return {"id": user_id, "name": name, "email": email}
            return None
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    def get_all_users(self):
        query = "SELECT * FROM users"
        cursor = self.db.execute(query)
        if cursor:
            users = cursor.fetchall()
            cursor.close()
            return users
        return []
    
    def close_connection(self):
        self.db.close()
