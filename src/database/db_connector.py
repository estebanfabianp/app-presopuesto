import logging
from typing import List, Dict, Any, Optional
import mysql.connector
from mysql.connector import Error, IntegrityError



class DatabaseConnector:
    """
    Clase para manejar conexiones MySQL con reconexión automática y logging.
    
    Esta clase proporciona una interfaz robusta para ejecutar consultas SQL
    con manejo automático de errores, reconexión y logging detallado.
    
    Attributes:
        _connection_params (dict): Parámetros de conexión a la base de datos
        conn: Objeto de conexión MySQL
    """
    
    def __init__(self, host: str = "localhost", database: str = "app_presupuesto",
                 user: str = "root", clave: str = "") -> None:
        """
        Inicializa la conexión a la base de datos MySQL.
        
        Args:
            host (str): Dirección del servidor MySQL. Default: 'localhost'
            database (str): Nombre de la base de datos. Default: 'app_presupuesto'
            user (str): Usuario de MySQL. Default: 'root'
            clave (str): Contraseña de MySQL. Default: ''
        """
        self._connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': clave  # Cambiado de 'clave' a 'password'
        }
        self.conn = None
        self._connect_mysql()

    def _connect_mysql(self) -> None:
        """
        Establece la conexión inicial a MySQL.
        
        Intenta conectar usando los parámetros proporcionados y registra
        el resultado en los logs. En caso de error, establece conn como None.
        """
        try:
            self.conn = mysql.connector.connect(**self._connection_params)
            if self.conn.is_connected():
                logging.info("Conexión exitosa a la base de datos MySQL")
        except Error as e:
            logging.error("Error conectando a MySQL: %s", e)
            self.conn = None

    def _reconnect(self) -> None:
        """
        Intenta reconectar a la base de datos si la conexión se perdió.
        
        Este método se llama automáticamente antes de cada operación
        para asegurar que la conexión esté activa.
        """
        if not self.is_connected():
            self._connect_mysql()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta consultas SELECT y retorna los resultados.
        
        Args:
            query (str): Consulta SQL SELECT a ejecutar
            params (tuple, optional): Parámetros para la consulta preparada
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los resultados.
                                 Retorna lista vacía si hay error o no hay resultados.
            
        Example:
            >>> db = DatabaseConnector()
            >>> results = db.execute_query("SELECT * FROM users WHERE id = %s", (1,))
            >>> print(results)
            [{'id': 1, 'name': 'Juan', 'email': 'juan@email.com'}]
        """
        self._reconnect()  # Asegurar conexión activa
        if not self.conn:
            return []

        try:
            # Usar cursor con dictionary=True para retornar resultados como diccionarios
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            logging.error("Error en consulta SELECT: %s", e)
            return []

    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """
        Ejecuta consultas INSERT, UPDATE, DELETE.
        
        Args:
            query (str): Consulta SQL de modificación a ejecutar
            params (tuple, optional): Parámetros para la consulta preparada
            
        Returns:
            Optional[int]: Para INSERT retorna el lastrowid (ID del nuevo registro).
                          Para UPDATE/DELETE retorna el rowcount si es exitoso.
                          Retorna None en caso de error.
            
        Example:
            >>> db = DatabaseConnector()
            >>> user_id = db.execute_non_query(
            ...     "INSERT INTO users (name, email) VALUES (%s, %s)", 
            ...     ("Juan", "juan@email.com")
            ... )
            >>> print(f"Usuario creado con ID: {user_id}")
        """
        self._reconnect()  # Asegurar conexión activa
        if not self.conn:
            return None

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                self.conn.commit()  # Confirmar la transacción
                return cursor.lastrowid  # Retorna ID para INSERT, 0 para UPDATE/DELETE
        except IntegrityError as e:
            # Error específico para violaciones de integridad (ej: duplicados)
            logging.warning("Error de integridad (ej: dato duplicado): %s", e)
            return None
        except Error as e:
            logging.error("Error en consulta no-SELECT: %s", e)
            return None

    def is_connected(self) -> bool:
        """
        Verifica si la conexión a la base de datos está activa.
        
        Returns:
            bool: True si la conexión está activa, False en caso contrario
        """
        return self.conn and self.conn.is_connected()

    def close(self) -> None:
        """
        Cierra la conexión a la base de datos de forma segura.
        
        Verifica que la conexión esté activa antes de cerrarla y
        registra la acción en los logs.
        """
        if self.conn and self.conn.is_connected():
            self.conn.close()
            logging.info("Conexión MySQL cerrada")
