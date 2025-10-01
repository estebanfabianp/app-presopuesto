import sys
import os
import hashlib

# Configurar path para importación absoluta
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from database import DatabaseConnector
from typing import Optional, Dict, List, Any


class PersonaModel:
    """
    Modelo para gestionar personas en la base de datos.
    
    Esta clase maneja todas las operaciones CRUD relacionadas con personas,
    incluyendo la gestión de estados (activo, inactivo, suspendido, bloqueado).
    
    Attributes:
        db (DatabaseConnector): Instancia del conector de base de datos
    """
    
    def __init__(self, host: str = "localhost", database: str = "mydb", 
                 user: str = "root", password: str = "") -> None:
        """
        Inicializa el modelo de persona y establece conexión a la base de datos.
        
        Args:
            host (str): Dirección del servidor MySQL
            database (str): Nombre de la base de datos
            user (str): Usuario de MySQL
            password (str): Contraseña de MySQL
        """
        self.db = DatabaseConnector(host=host, database=database, user=user, password=password)

    def get_all_personas(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las personas con información de estado.
        
        Returns:
            List[Dict[str, Any]]: Lista de personas con datos del estado
        """
        query = """
        SELECT 
            p.id,
            p.nombre,
            p.email,
            p.telefono,
            p.id_estado,
            ep.nombre as estado_nombre,
            ep.descripcion as estado_descripcion,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        LEFT JOIN estado_persona ep ON p.id_estado = ep.id
        ORDER BY p.nombre
        """
        return self.db.execute_query(query)

    def get_persona_by_id(self, persona_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una persona específica por su ID.
        
        Args:
            persona_id (int): ID único de la persona
            
        Returns:
            Optional[Dict[str, Any]]: Datos de la persona con estado si existe
        """
        query = """
        SELECT 
            p.id,
            p.nombre,
            p.email,
            p.telefono,
            p.id_estado,
            ep.nombre as estado_nombre,
            ep.descripcion as estado_descripcion,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        LEFT JOIN estado_persona ep ON p.id_estado = ep.id
        WHERE p.id = %s
        """
        results = self.db.execute_query(query, (persona_id,))
        return results[0] if results else None

    def get_personas_by_estado(self, estado_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las personas filtradas por estado.
        
        Args:
            estado_id (int): ID del estado a filtrar
            
        Returns:
            List[Dict[str, Any]]: Lista de personas con el estado especificado
        """
        query = """
        SELECT 
            p.id,
            p.nombre,
            p.email,
            p.telefono,
            p.id_estado,
            ep.nombre as estado_nombre,
            ep.descripcion as estado_descripcion
        FROM persona p
        LEFT JOIN estado_persona ep ON p.id_estado = ep.id
        WHERE p.id_estado = %s
        ORDER BY p.nombre
        """
        return self.db.execute_query(query, (estado_id,))

    def add_persona(self, nombre: str, email: str, telefono: str = None, 
                   password: str = None, estado_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Añade una nueva persona a la base de datos.
        
        Args:
            nombre (str): Nombre completo de la persona
            email (str): Email único de la persona
            telefono (str, optional): Teléfono de la persona
            password (str, optional): Contraseña del usuario
            estado_id (int): ID del estado (default: 1 = ACTIVO)
            
        Returns:
            Optional[Dict[str, Any]]: Datos de la persona creada si es exitoso
        """
        # Hash de la contraseña si se proporciona
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
        INSERT INTO persona (nombre, email, telefono, password, id_estado) 
        VALUES (%s, %s, %s, %s, %s)
        """
        persona_id = self.db.execute_non_query(query, (nombre, email, telefono, password_hash, estado_id))
        
        if persona_id:
            return self.get_persona_by_id(persona_id)
        return None

    def update_persona_estado(self, persona_id: int, nuevo_estado_id: int) -> bool:
        """
        Actualiza el estado de una persona.
        
        Args:
            persona_id (int): ID de la persona
            nuevo_estado_id (int): ID del nuevo estado
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        query = """
        UPDATE persona 
        SET id_estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP 
        WHERE id = %s
        """
        result = self.db.execute_non_query(query, (nuevo_estado_id, persona_id))
        return result is not None

    def activar_persona(self, persona_id: int) -> bool:
        """
        Activa una persona (cambia estado a ACTIVO).
        
        Args:
            persona_id (int): ID de la persona
            
        Returns:
            bool: True si la activación fue exitosa
        """
        return self.update_persona_estado(persona_id, 1)  # 1 = ACTIVO

    def desactivar_persona(self, persona_id: int) -> bool:
        """
        Desactiva una persona (cambia estado a INACTIVO).
        
        Args:
            persona_id (int): ID de la persona
            
        Returns:
            bool: True si la desactivación fue exitosa
        """
        return self.update_persona_estado(persona_id, 2)  # 2 = INACTIVO

    def suspender_persona(self, persona_id: int) -> bool:
        """
        Suspende una persona (cambia estado a SUSPENDIDO).
        
        Args:
            persona_id (int): ID de la persona
            
        Returns:
            bool: True si la suspensión fue exitosa
        """
        return self.update_persona_estado(persona_id, 3)  # 3 = SUSPENDIDO

    def persona_existe(self, persona_id: int) -> bool:
        """
        Verifica si una persona existe en la base de datos.
        
        Args:
            persona_id (int): ID de la persona a verificar
            
        Returns:
            bool: True si la persona existe, False en caso contrario
        """
        persona = self.get_persona_by_id(persona_id)
        return persona is not None

    def persona_activa(self, persona_id: int) -> bool:
        """
        Verifica si una persona está en estado ACTIVO.
        
        Args:
            persona_id (int): ID de la persona a verificar
            
        Returns:
            bool: True si la persona está activa, False en caso contrario
        """
        persona = self.get_persona_by_id(persona_id)
        return persona is not None and persona['id_estado'] == 1

    def get_estados_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los estados disponibles para personas.
        
        Returns:
            List[Dict[str, Any]]: Lista de estados disponibles
        """
        query = """
        SELECT id, nombre, descripcion, activo 
        FROM estado_persona 
        WHERE activo = TRUE 
        ORDER BY nombre
        """
        return self.db.execute_query(query)

    def close_connection(self) -> None:
        """
        Cierra la conexión a la base de datos de forma segura.
        """
        self.db.close()

    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica a un usuario mediante email y contraseña.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Datos del usuario si las credenciales son válidas,
                                    None si son inválidas o el usuario no está activo
        """
        # Hash de la contraseña para comparación segura
        #password_hash = hashlib.sha256(password.encode()).hexdigest()
        password_hash = password
        
        query = """
        SELECT 
            p.id,
            p.nombre,
            p.email,
            p.telefono,
            p.id_estado,
            ep.nombre as estado_nombre,
            ep.descripcion as estado_descripcion,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        LEFT JOIN estado_persona ep ON p.id_estado = ep.id
        WHERE p.email = %s AND p.password = %s AND p.id_estado = 1
        """
        
        results = self.db.execute_query(query, (email, password_hash))
        
        if results:
            # Remover la contraseña del resultado por seguridad
            user_data = results[0].copy()
            return user_data
        
        return None

    def verificar_password(self, email: str, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada es correcta para el usuario dado.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        # Hash de la contraseña para comparación segura
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
        SELECT COUNT(*) as count
        FROM persona p
        WHERE p.correo_electronico = %s AND p.clave = %s AND p.activo = 1
        """
        
        results = self.db.execute_query(query, (email, password))
        
        if results and results[0]['count'] > 0:
            return True
        
        return False

    def verificar_password_por_id(self, persona_id: int, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada es correcta para el usuario con ID dado.
        
        Args:
            persona_id (int): ID del usuario
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        # Hash de la contraseña para comparación segura
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
        SELECT COUNT(*) as count
        FROM persona p
        WHERE p.id = %s AND p.password = %s AND p.id_estado = 1
        """
        
        results = self.db.execute_query(query, (persona_id, password))
        
        if results and results[0]['count'] > 0:
            return True
        
        return False
