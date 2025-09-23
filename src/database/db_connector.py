try:
    import mysql.connector
    from mysql.connector import Error
    from mysql.connector import IntegrityError  # New import for handling integrity errors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL connector not available. Install with: pip install mysql-connector-python")

class DatabaseConnector:
    def __init__(self, host="localhost", database="mydb", user="root", password=""):
        self.db_type = "mysql"
        self.conn = None
        
        if MYSQL_AVAILABLE:
            self._connect_mysql(host, database, user, password)
        else:
            print("MySQL is required for this application")
    
    def execute(self, query, params=None):
        if not self.conn or not self.conn.is_connected():
            print("Connection lost, attempting to reconnect...")
            self._reconnect()
            if not self.conn:
                return None
        
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor
        except Exception as e:
            print(f"Database error: {e}")
            cursor.close()
            return None
    
    def _reconnect(self):
        if hasattr(self, '_connection_params'):
            self._connect_mysql(**self._connection_params)
    
    def _connect_mysql(self, host, database, user, password):
        self._connection_params = {
            'host': host,
            'database': database, 
            'user': user,
            'password': password
        }
        try:
            self.conn = mysql.connector.connect(**self._connection_params)
            print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.conn = None
    
    def is_connected(self):
        return self.conn and self.conn.is_connected()
    
    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Database connection closed")
