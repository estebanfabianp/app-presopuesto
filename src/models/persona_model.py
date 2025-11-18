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
        print(f"DEBUG [MODEL] - Inicializando PersonaModel")
        print(f"DEBUG [MODEL] - Parámetros de conexión: host={host}, database={database}, user={user}")
        self.db = DatabaseConnector(host=host, database=database, user=user, clave=clave)
        print(f"DEBUG [MODEL] - DatabaseConnector creado exitosamente")

    def get_all_personas(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las personas con información de estado.
        
        Returns:
            List[Dict[str, Any]]: Lista de personas con datos del estado
        """
        print("DEBUG [MODEL] - Obteniendo todas las personas...")
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
        print(f"DEBUG [MODEL] - Query ejecutar: {query}")
        result = self.db.execute_query(query)
        print(f"DEBUG [MODEL] - Personas obtenidas: {len(result) if result else 0}")
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
            password_hash = hashlib.sha256(clave.encode()).hexdigest()
        
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

    def verificar_password(self, email: str, clave: str) -> bool:
        """
        Verifica si la contraseña proporcionada es correcta para el usuario dado.
        
        Args:
            email (str): correo_electronico del usuario
            clave (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        print(f"DEBUG [MODEL] - Verificando clave para correo_electronico: '{email}'")
        print(f"DEBUG [MODEL] - clave recibido: {'[PRESENTE]' if clave else '[VACÍO]'}")
        
        # Hash de la contraseña para comparación segura
        password_hash = hashlib.sha256(clave.encode()).hexdigest()
        print(f"DEBUG [MODEL] - clave hasheado: {password_hash[:10]}...")
        
        query = """
        SELECT COUNT(*) as count
        FROM persona p
        WHERE p.correo_electronico = %s AND p.clave = %s AND p.estado = 1
        """
        print(f"DEBUG [MODEL] - Query verificación: {query}")
        print(f"DEBUG [MODEL] - Parámetros: correo_electronico='{email}', password_hash='{password_hash[:10]}...'")
        
        try:
            results = self.db.execute_query(query, (email, clave))
            print(f"DEBUG [MODEL] - Resultados query: {results}")
            
            if results and results[0]['count'] > 0:
                print("DEBUG [MODEL] - ✅ Contraseña válida")
                return True
            else:
                print("DEBUG [MODEL] - ❌ Contraseña inválida o usuario no encontrado")
                return False
                
        except Exception as e:
            print(f"DEBUG [MODEL] - 🚨 Error en verificar_password: {type(e).__name__}: {str(e)}")
            return False

    def get_usuario_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos completos de un usuario por su username/correo_electronico.
        
        Args:
            username (str): Username o correo_electronico del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Datos completos del usuario si existe
        """
        print(f"DEBUG [MODEL] - Obteniendo usuario por username: '{username}'")
        
        # Buscar tanto por correo_electronico como por nombre (username podría ser cualquiera)
        query = """
        SELECT 
            p.id_persona,
            p.id_persona as persona_id,
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
        
        print(f"DEBUG [MODEL] - Query get_usuario_by_username: {query}")
        print(f"DEBUG [MODEL] - Parámetros: username='{username}'")
        
        try:
            results = self.db.execute_query(query, (username, username))
            print(f"DEBUG [MODEL] - Resultados obtenidos: {len(results) if results else 0}")
            
            if results:
                user_data = results[0]
                print(f"DEBUG [MODEL] - Usuario encontrado:")
                print(f"DEBUG [MODEL] - - ID: {user_data.get('id_persona')}")
                print(f"DEBUG [MODEL] - - Persona ID: {user_data.get('persona_id')}")
                print(f"DEBUG [MODEL] - - Nombres: {user_data.get('nombres')}")
                print(f"DEBUG [MODEL] - - correo_electronico: {user_data.get('correo_electronico')}")
                print(f"DEBUG [MODEL] - - Estado ID: {user_data.get('estado')}")
                print(f"DEBUG [MODEL] - - Estado nombre: {user_data.get('estado_nombre')}")
                return user_data
            else:
                print(f"DEBUG [MODEL] - No se encontró usuario con username: '{username}'")
                return None
                
        except Exception as e:
            print(f"DEBUG [MODEL] - 🚨 Error en get_usuario_by_username: {type(e).__name__}: {str(e)}")
            return None

    def get_current_timestamp(self):
        """
        Obtiene el timestamp actual de la base de datos.
        
        Returns:
            datetime: Timestamp actual
        """
        print("DEBUG [MODEL] - Obteniendo timestamp actual de la base de datos")
        
        query = "SELECT NOW() as timestamp"
        
        try:
            results = self.db.execute_query(query)
            if results:
                timestamp = results[0]['timestamp']
                print(f"DEBUG [MODEL] - Timestamp obtenido: {timestamp}")
                return timestamp
            else:
                print("DEBUG [MODEL] - No se pudo obtener timestamp, usando datetime.now()")
                from datetime import datetime
                return datetime.now()
                
        except Exception as e:
            print(f"DEBUG [MODEL] - Error obteniendo timestamp: {e}")
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
        print(f"DEBUG [MODEL] - Verificando si persona está activa: ID={persona_id}")
        
        persona = self.get_persona_by_id(persona_id)
        
        if persona is None:
            print(f"DEBUG [MODEL] - Persona con ID {persona_id} no encontrada")
            return False
        
        estado_activo = persona['estado'] == 1
        print(f"DEBUG [MODEL] - Persona ID {persona_id}:")
        print(f"DEBUG [MODEL] - - Estado actual: {persona['estado']} ({persona.get('estado_nombre', 'N/A')})")
        print(f"DEBUG [MODEL] - - ¿Está activa?: {estado_activo}")
        
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
        print("DEBUG [MODEL] - Cerrando conexión a la base de datos")
        try:
            self.db.close()
            print("DEBUG [MODEL] - Conexión cerrada exitosamente")
        except Exception as e:
            print(f"DEBUG [MODEL] - Error al cerrar conexión: {e}")

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
        # Hash de la contraseña para comparación segura
        #password_hash = hashlib.sha256(password.encode()).hexdigest()
        password_hash = password
        
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
        WHERE p.correo_electronico = %s AND p.clave = %s AND p.estado = 1
        """
        
        results = self.db.execute_query(query, (email, password_hash))
        
        if results:
            # Remover la contraseña del resultado por seguridad
            user_data = results[0].copy()
            return user_data
        
        return None

    def verificar_password(self, username: str, password: str) -> bool:
        """
        Verifica credenciales de usuario (username puede ser correo_electronico o nombre).
        
        Args:
            username (str): Username o correo_electronico del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            bool: True si las credenciales son válidas
        """
        print(f"DEBUG [MODEL] - Verificando credenciales para: '{username}'")
        print(f"DEBUG [MODEL] - password proporcionado: {'[PRESENTE]' if password else '[VACÍO]'}")
        
        if not username or not password:
            print("DEBUG [MODEL] - Username o password vacío")
            return False
        
        # Buscar usuario por correo_electronico o nombre
        query = """
        SELECT id_persona , clave, estado
        FROM persona 
        WHERE (correo_electronico = %s OR nombre = %s)
        LIMIT 1
        """
        
        print(f"DEBUG [MODEL] - Ejecutando query de verificación... " +  query)
        
        try:
            results = self.db.execute_query(query, (username, username))
            print(f"DEBUG [MODEL] - Usuarios encontrados: {len(results) if results else 0}")
            
            if not results:
                print("DEBUG [MODEL] - Usuario no encontrado en la base de datos")
                return False
            
            user_data = results[0]
            stored_password = user_data.get('clave')
            user_id = user_data.get('id')
            estado_id = user_data.get('estado')
            
            print(f"DEBUG [MODEL] - Usuario encontrado - ID: {user_id}, Estado: {estado_id}")
            print(f"DEBUG [MODEL] - password almacenado presente: {stored_password is not None}")
            
            # Verificar estado activo
            if estado_id != 1:
                print(f"DEBUG [MODEL] - Usuario no está en estado activo (estado: {estado_id})")
                return False
            
            # Comparar contraseñas
            # Primero intentar comparación directa (para desarrollo)
            if stored_password == password:
                print("DEBUG [MODEL] - ✅ password correcto (comparación directa)")
                return True
            
            # Si no funciona, intentar con hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if stored_password == password_hash:
                print("DEBUG [MODEL] - ✅ password correcto (comparación hasheada)")
                return True
            
            print("DEBUG [MODEL] - ❌ password incorrecto")
            return False
            
        except Exception as e:
            print(f"DEBUG [MODEL] - 🚨 Error verificando password: {type(e).__name__}: {str(e)}")
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
        WHERE p.id_persona = %s AND p.clave = %s AND p.estado = 1
        """
        
        results = self.db.execute_query(query, (persona_id, password))
        
        if results and results[0]['count'] > 0:
            return True
        
        return False
