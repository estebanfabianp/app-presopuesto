import sys
import os
import hashlib
import logging
from datetime import date

# Configurar path para importación absoluta
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from database import DatabaseConnector
from typing import Optional, Dict, List, Any


logger = logging.getLogger(__name__)


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

    def _build_default_constants(self) -> List[Dict[str, Any]]:
        fiscal_year = str(date.today().year)
        return [
            {
                'categoria': 'IMPUESTOS',
                'nombre': 'IVA',
                'valor': '0.19',
                'tipo_dato': 'DECIMAL',
                'descripcion': 'Tasa de IVA por defecto para calculos fiscales',
                'es_editable': 1,
            },
            {
                'categoria': 'FISCAL',
                'nombre': 'ANIO_FISCAL',
                'valor': fiscal_year,
                'tipo_dato': 'INTEGER',
                'descripcion': 'Anio fiscal de trabajo para reportes y presupuesto',
                'es_editable': 1,
            },
            {
                'categoria': 'TASAS',
                'nombre': 'TASA_REFERENCIA',
                'valor': '0.00',
                'tipo_dato': 'DECIMAL',
                'descripcion': 'Tasa de referencia editable del usuario',
                'es_editable': 1,
            },
        ]

    def _get_system_template_constants(self) -> List[Dict[str, Any]]:
        """Obtiene plantilla base desde un usuario del sistema (id minimo)."""
        defaults = self._build_default_constants()
        keys = {(d['categoria'], d['nombre']) for d in defaults}

        owner_row = self.db.execute_query("SELECT MIN(id_persona) AS id_persona FROM persona")
        system_owner = owner_row[0]['id_persona'] if owner_row else None
        if not system_owner:
            return defaults

        rows = self.db.execute_query(
            """
            SELECT categoria, nombre, valor, tipo_dato, descripcion, es_editable
            FROM constantes
            WHERE id_persona = %s AND estado = 1
            """,
            (system_owner,),
        )

        by_key = {}
        for r in rows or []:
            key = (r.get('categoria'), r.get('nombre'))
            if key in keys:
                by_key[key] = {
                    'categoria': r.get('categoria'),
                    'nombre': r.get('nombre'),
                    'valor': str(r.get('valor') or ''),
                    'tipo_dato': r.get('tipo_dato') or 'STRING',
                    'descripcion': r.get('descripcion') or '',
                    'es_editable': 1 if r.get('es_editable') else 0,
                }

        resolved = []
        for item in defaults:
            resolved.append(by_key.get((item['categoria'], item['nombre']), item))
        return resolved

    def ensure_default_constants_for_user(self, persona_id: int) -> None:
        """Crea constantes base para el usuario si aun no existen."""
        if not persona_id:
            return

        templates = self._get_system_template_constants()
        for c in templates:
            self.db.execute_non_query(
                """
                INSERT IGNORE INTO constantes
                (id_persona, categoria, nombre, valor, tipo_dato, descripcion, es_editable, estado, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 'system')
                """,
                (
                    persona_id,
                    c['categoria'],
                    c['nombre'],
                    c['valor'],
                    c['tipo_dato'],
                    c['descripcion'],
                    c['es_editable'],
                ),
            )

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

    @staticmethod
    def _is_active_user_status(status_value: Any) -> bool:
        """Compatibilidad: en datos legacy estado NULL equivale a usuario activo."""
        if status_value is None:
            return True
        if isinstance(status_value, str):
            normalized = status_value.strip().lower()
            return normalized in ('1', 'true', 'activo')
        return status_value == 1 or status_value is True

    def _upgrade_password_hash(self, persona_id: int, plain_password: str) -> None:
        hashed_password = self._hash_password(plain_password)
        self.db.execute_non_query(
            "UPDATE persona SET clave = %s WHERE id_persona = %s",
            (hashed_password, persona_id),
        )

    def change_password(self, persona_id: int, current_password: str, new_password: str) -> tuple:
        """
        Cambia la contraseña de un usuario validando la contraseña actual.

        Returns:
            (True, 'ok') si el cambio fue exitoso.
            (False, 'wrong_password') si la contraseña actual no coincide.
            (False, 'not_found') si el usuario no existe.
        """
        results = self.db.execute_query(
            "SELECT clave FROM persona WHERE id_persona = %s", (persona_id,)
        )
        if not results:
            return False, 'not_found'

        stored = results[0].get('clave')
        if not self._password_matches(stored, current_password):
            return False, 'wrong_password'

        new_hash = self._hash_password(new_password)
        self.db.execute_non_query(
            "UPDATE persona SET clave = %s WHERE id_persona = %s",
            (new_hash, persona_id),
        )
        return True, 'ok'

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

    def _build_unique_username(self, nombre: str, email: str) -> str:
        base = (email.split('@')[0] if email and '@' in email else nombre).strip().lower()
        base = ''.join(ch if ch.isalnum() else '_' for ch in base).strip('_')
        if not base:
            base = 'usuario'

        candidate = base[:45]
        i = 1
        while True:
            exists = self.db.execute_query(
                "SELECT id_persona FROM persona WHERE usuario = %s LIMIT 1",
                (candidate,),
            )
            if not exists:
                return candidate
            suffix = f"_{i}"
            candidate = (base[: max(1, 45 - len(suffix))] + suffix)[:45]
            i += 1

    @staticmethod
    def _derive_lastname(nombre: str) -> str:
        parts = [p for p in (nombre or '').strip().split() if p]
        if len(parts) >= 2:
            return parts[-1][:20]
        return 'N/A'

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
        # Contraseña por defecto para altas sin clave explícita.
        plain_password = (clave or '').strip() or '123456'
        password_hash = self._hash_password(plain_password)
        
        apellido = self._derive_lastname(nombre)
        usuario = self._build_unique_username(nombre, email)

        query = """
        INSERT INTO persona (nombre, apellido, correo_electronico, usuario, clave, estado, fecha_creacion)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        persona_id = self.db.execute_non_query(query, (nombre, apellido, email, usuario, password_hash, estado_id))
        
        if persona_id:
            try:
                self.ensure_default_constants_for_user(persona_id)
            except Exception as exc:
                logger.warning("No se pudieron sembrar constantes base para usuario %s: %s", persona_id, exc)
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
        if not user_data or not self._is_active_user_status(user_data.get('estado')):
            return None

        stored_password = user_data.get('clave')
        if not self._password_matches(stored_password, password):
            return None

        if stored_password == password and not self._looks_like_sha256_hash(stored_password):
            self._upgrade_password_hash(user_data['id_persona'], password)
            user_data['clave'] = self._hash_password(password)

        try:
            self.ensure_default_constants_for_user(user_data['id_persona'])
        except Exception as exc:
            logger.warning("No se pudieron asegurar constantes base en login de %s: %s", user_data['id_persona'], exc)

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
        if not user_data or not self._is_active_user_status(user_data.get('estado')):
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
        if not self._is_active_user_status(user_data.get('estado')):
            return False

        stored_password = user_data.get('clave')
        if not self._password_matches(stored_password, password):
            return False

        if stored_password == password and not self._looks_like_sha256_hash(stored_password):
            self._upgrade_password_hash(persona_id, password)

        return True

    def reset_password_by_email(self, email: str, new_password: str) -> tuple:
        """
        Restablece la contraseña de un usuario por correo electrónico.

        Returns:
            (True, 'ok') si el cambio fue exitoso.
            (False, 'not_found') si no existe el usuario.
        """
        if not email or not new_password:
            return False, 'not_found'

        results = self.db.execute_query(
            "SELECT id_persona FROM persona WHERE correo_electronico = %s LIMIT 1",
            (email,),
        )
        if not results:
            return False, 'not_found'

        persona_id = results[0]['id_persona']
        new_hash = self._hash_password(new_password)
        self.db.execute_non_query(
            "UPDATE persona SET clave = %s WHERE id_persona = %s",
            (new_hash, persona_id),
        )
        return True, 'ok'
