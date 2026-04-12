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
    
    def __init__(self, host: str = "localhost", database: str = "app_presupuesto", 
                 user: str = "root", clave: str = "") -> None:
        """
        Inicializa el modelo de persona y establece conexión a la base de datos.
        
        Args:
            host (str): Dirección del servidor MySQL
            database (str): Nombre de la base de datos
            user (str): Usuario de MySQL
            clave (str): Contraseña de MySQL
        """
        self.db = DatabaseConnector(host=host, database=database, user=user, clave=clave)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def _looks_like_sha256_hash(value: Optional[str]) -> bool:
        if not value or len(value) != 64:
            return False
        return all(ch in '0123456789abcdef' for ch in value.lower())

    def _password_matches(self, stored_password: Optional[str], candidate_password: str) -> bool:
        if not stored_password or not candidate_password:
            return False
        candidate_hash = self._hash_password(candidate_password)
        return stored_password == candidate_password or stored_password == candidate_hash

    def _upgrade_password_hash(self, persona_id: int, plain_password: str) -> None:
        hashed_password = self._hash_password(plain_password)
        self.db.execute_non_query(
            "UPDATE persona SET clave = %s WHERE id_persona = %s",
            (hashed_password, persona_id),
        )

    def _get_user_for_auth(self, identifier: str) -> Optional[Dict[str, Any]]:
        query = """
        SELECT
            p.id_persona,
            p.nombre,
            p.correo_electronico,
            p.usuario,
            p.clave,
            p.estado,
            CASE
                WHEN p.estado = 1 THEN 'activo'
                WHEN p.estado = 0 THEN 'inactivo'
                ELSE 'desconocido'
            END as estado_nombre,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        WHERE (p.correo_electronico = %s OR p.nombre = %s OR p.usuario = %s)
        LIMIT 1
        """
        results = self.db.execute_query(query, (identifier, identifier, identifier))
        return results[0] if results else None

    def get_all_personas(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las personas con información de estado.
        
        Returns:
            List[Dict[str, Any]]: Lista de personas con datos del estado
        """
        query = """
        SELECT 
            p.id_persona,
            p.nombre,
            p.correo_electronico,
           
            p.estado,
            CASE 
                WHEN p.estado = 1 THEN 'activo'
                WHEN p.estado = 0 THEN 'inactivo'
                ELSE 'desconocido'
            END as estado_nombre,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        ORDER BY p.nombre
        """
        result = self.db.execute_query(query)
        return result

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
            p.id_persona,
            p.nombre,
            p.correo_electronico,
           
            p.estado,
            CASE 
                WHEN p.estado = 1 THEN 'activo'
                WHEN p.estado = 0 THEN 'inactivo'
                ELSE 'desconocido'
            END as estado_nombre,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        WHERE p.id_persona = %s
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
            p.id_persona,
            p.nombre,
            p.correo_electronico,
           
            p.estado,
            CASE 
                WHEN p.estado = 1 THEN 'activo'
                WHEN p.estado = 0 THEN 'inactivo'
                ELSE 'desconocido'
            END as estado_nombre
        FROM persona p
        WHERE p.estado = %s
        ORDER BY p.nombre
        """
        return self.db.execute_query(query, (estado_id,))

    def add_persona(self, nombre: str, email: str, telefono: str = None, 
                   clave: str = None, estado_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Añade una nueva persona a la base de datos.
        
        Args:
            nombre (str): Nombre completo de la persona
            email (str): correo_electronico único de la persona
            telefono (str, optional): Teléfono de la persona
            clave (str, optional): Contraseña del usuario
            estado_id (int): ID del estado (default: 1 = ACTIVO)
            
        Returns:
            Optional[Dict[str, Any]]: Datos de la persona creada si es exitoso
        """
        # Hash de la contraseña si se proporciona
        password_hash = None
        if clave:
            password_hash = self._hash_password(clave)
        
        query = """
        INSERT INTO persona (nombre, correo_electronico, telefono, clave, estado) 
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
        SET estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP 
        WHERE id_persona = %s
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
        return self.update_persona_estado(persona_id, 0)  # 0 = INACTIVO

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

    def get_usuario_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos completos de un usuario por su username/correo_electronico.
        
        Args:
            username (str): Username o correo_electronico del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Datos completos del usuario si existe
        """
        
        # Buscar tanto por correo_electronico como por nombre (username podría ser cualquiera)
        query = """
        SELECT 
            p.id_persona,
            p.id_persona as persona_id,
            p.nombre,
            p.usuario,
            p.nombre as nombres,
            '' as apellidos,
            p.correo_electronico,
           
            p.estado,
            CASE 
                WHEN p.estado = 1 THEN 'activo'
                WHEN p.estado = 0 THEN 'inactivo'
                ELSE 'desconocido'
            END as estado_nombre,
            'usuario' as rol,
            p.fecha_creacion,
            p.fecha_actualizacion
        FROM persona p
        WHERE (p.correo_electronico = %s OR p.nombre = %s)
        LIMIT 1
        """
        
        
        try:
            results = self.db.execute_query(query, (username, username))
            
            if results:
                user_data = results[0]
                return user_data
            else:
                return None
                
        except Exception as e:
            return None

    def get_current_timestamp(self):
        """
        Obtiene el timestamp actual de la base de datos.
        
        Returns:
            datetime: Timestamp actual
        """
        
        query = "SELECT NOW() as timestamp"
        
        try:
            results = self.db.execute_query(query)
            if results:
                timestamp = results[0]['timestamp']
                return timestamp
            else:
                from datetime import datetime
                return datetime.now()
                
        except Exception as e:
            from datetime import datetime
            return datetime.now()

    def persona_activa(self, persona_id: int) -> bool:
        """
        Verifica si una persona está en estado ACTIVO.
        
        Args:
            persona_id (int): ID de la persona a verificar
            
        Returns:
            bool: True si la persona está activa, False en caso contrario
        """
        
        persona = self.get_persona_by_id(persona_id)
        
        if persona is None:
            return False
        
        estado_activo = persona['estado'] == 1
        
        return estado_activo

    def get_estados_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los estados disponibles para personas.
        
        Returns:
            List[Dict[str, Any]]: Lista de estados disponibles
        """
        # Devolver estados hardcodeados ya que no existe tabla estado_persona
        return [
            {'id': 1, 'nombre': 'activo', 'descripcion': 'Usuario activo', 'activo': True},
            {'id': 0, 'nombre': 'inactivo', 'descripcion': 'Usuario inactivo', 'activo': True}
        ]

    def close_connection(self) -> None:
        """
        Cierra la conexión a la base de datos de forma segura.
        """
        if self.db:
            self.db.close()

    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica a un usuario mediante correo_electronico y contraseña.
        
        Args:
            email (str): correo_electronico del usuario
            password (str): Contraseña del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Datos del usuario si las credenciales son válidas,
                                    None si son inválidas o el usuario no está activo
        """
        user_data = self._get_user_for_auth(email)
        if not user_data or user_data.get('estado') != 1:
            return None

        stored_password = user_data.get('clave')
        if not self._password_matches(stored_password, password):
            return None

        if stored_password == password and not self._looks_like_sha256_hash(stored_password):
            self._upgrade_password_hash(user_data['id_persona'], password)
            user_data['clave'] = self._hash_password(password)

        user_data.pop('clave', None)
        return user_data

    def verificar_password(self, username: str, password: str) -> bool:
        """
        Verifica credenciales de usuario (username puede ser correo_electronico o nombre).
        
        Args:
            username (str): Username o correo_electronico del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            bool: True si las credenciales son válidas
        """
        
        if not username or not password:
            return False
        
        user_data = self._get_user_for_auth(username)
        if not user_data or user_data.get('estado') != 1:
            return False

        stored_password = user_data.get('clave')
        if not self._password_matches(stored_password, password):
            return False

        if stored_password == password and not self._looks_like_sha256_hash(stored_password):
            self._upgrade_password_hash(user_data['id_persona'], password)

        return True

    def verificar_password_por_id(self, persona_id: int, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada es correcta para el usuario con ID dado.
        
        Args:
            persona_id (int): ID del usuario
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        query = """
        SELECT id_persona, clave, estado
        FROM persona p
        WHERE p.id_persona = %s
        LIMIT 1
        """
        results = self.db.execute_query(query, (persona_id,))
        if not results:
            return False

        user_data = results[0]
        if user_data.get('estado') != 1:
            return False

        stored_password = user_data.get('clave')
        if not self._password_matches(stored_password, password):
            return False

        if stored_password == password and not self._looks_like_sha256_hash(stored_password):
            self._upgrade_password_hash(persona_id, password)

        return True
