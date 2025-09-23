from ..database import DatabaseConnector
from typing import Optional, Dict, List, Any


class UserModel:
    """
    Modelo para gestionar usuarios en la base de datos.
    
    Esta clase maneja todas las operaciones CRUD (Create, Read, Update, Delete)
    relacionadas con usuarios, incluyendo la creación automática de la tabla
    si no existe.
    
    Attributes:
        db (DatabaseConnector): Instancia del conector de base de datos
    """
    
    def __init__(self, host: str = "localhost", database: str = "mydb", 
                 user: str = "root", password: str = "") -> None:
        """
        Inicializa el modelo de usuario y establece conexión a la base de datos.
        
        Args:
            host (str): Dirección del servidor MySQL. Default: 'localhost'
            database (str): Nombre de la base de datos. Default: 'mydb'
            user (str): Usuario de MySQL. Default: 'root'
            password (str): Contraseña de MySQL. Default: ''
        """
        # Crear instancia del conector con los parámetros proporcionados
        self.db = DatabaseConnector(host=host, database=database, user=user, password=password)
        # Asegurar que la tabla existe al inicializar
        self.create_table()

    def create_table(self) -> None:
        """
        Crea la tabla 'users' si no existe.
        
        La tabla contiene los siguientes campos:
        - id: Clave primaria auto-incremental
        - name: Nombre del usuario (requerido)
        - email: Email único del usuario (requerido y único)
        
        Note:
            Este método es llamado automáticamente en __init__
        """
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
        )
        """
        self.db.execute_non_query(query)

    def add_user(self, name: str, email: str) -> Optional[Dict[str, Any]]:
        """
        Añade un nuevo usuario a la base de datos.
        
        Args:
            name (str): Nombre completo del usuario
            email (str): Dirección de email única del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con los datos del usuario creado
                                     si es exitoso, None si hay error (ej: email duplicado)
            
        Example:
            >>> user_model = UserModel()
            >>> new_user = user_model.add_user("Juan Pérez", "juan@email.com")
            >>> if new_user:
            ...     print(f"Usuario creado: {new_user}")
            ... else:
            ...     print("Error: Email ya existe")
        """
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        user_id = self.db.execute_non_query(query, (name, email))

        # Si la inserción fue exitosa, retornar los datos del usuario
        if user_id:
            return {"id": user_id, "name": name, "email": email}
        return None  # Error en la inserción (probablemente email duplicado)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios de la base de datos.
        
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios, cada uno representa un usuario.
                                 Retorna lista vacía si no hay usuarios o hay error.
            
        Example:
            >>> user_model = UserModel()
            >>> users = user_model.get_all_users()
            >>> for user in users:
            ...     print(f"ID: {user['id']}, Nombre: {user['name']}, Email: {user['email']}")
        """
        query = "SELECT * FROM users"
        return self.db.execute_query(query)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario específico por su ID.
        
        Args:
            user_id (int): ID único del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con los datos del usuario
                                     si existe, None si no se encuentra
        """
        query = "SELECT * FROM users WHERE id = %s"
        results = self.db.execute_query(query, (user_id,))
        return results[0] if results else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario específico por su email.
        
        Args:
            email (str): Email único del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con los datos del usuario
                                     si existe, None si no se encuentra
        """
        query = "SELECT * FROM users WHERE email = %s"
        results = self.db.execute_query(query, (email,))
        return results[0] if results else None

    def update_user(self, user_id: int, name: str = None, email: str = None) -> bool:
        """
        Actualiza los datos de un usuario existente.
        
        Args:
            user_id (int): ID del usuario a actualizar
            name (str, optional): Nuevo nombre del usuario
            email (str, optional): Nuevo email del usuario
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        if not name and not email:
            return False  # No hay nada que actualizar
            
        # Construir query dinámicamente según los campos a actualizar
        fields = []
        params = []
        
        if name:
            fields.append("name = %s")
            params.append(name)
        if email:
            fields.append("email = %s")
            params.append(email)
            
        params.append(user_id)  # Para la condición WHERE
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        result = self.db.execute_non_query(query, tuple(params))
        
        return result is not None

    def delete_user(self, user_id: int) -> bool:
        """
        Elimina un usuario de la base de datos.
        
        Args:
            user_id (int): ID del usuario a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        query = "DELETE FROM users WHERE id = %s"
        result = self.db.execute_non_query(query, (user_id,))
        return result is not None

    def close_connection(self) -> None:
        """
        Cierra la conexión a la base de datos de forma segura.
        
        Note:
            Es recomendable llamar este método cuando se termine de usar
            el modelo para liberar recursos de la base de datos.
        """
        self.db.close()
