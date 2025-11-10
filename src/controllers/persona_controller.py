"""
Controlador de Persona - Gestión de Usuarios y Sesiones
======================================================

Este módulo proporciona la lógica de negocio para la gestión de personas/usuarios
y el manejo de sesiones de usuario en la aplicación de presupuesto.

Funcionalidades principales:
- Gestión de personas (CRUD básico y cambio de estados)
- Autenticación de usuarios
- Manejo de sesiones de usuario (login/logout)
- Validación de permisos y roles
- Verificación de estados de usuario

Autor: Esteban Fabian
Versión: 1.3.0 - Optimizada
Fecha: 2024
"""

from models.persona_model import PersonaModel
from typing import Tuple, Optional, Dict, Any, List

# Variable global para almacenar la sesión activa
_sesion_activa: Optional[Dict[str, Any]] = None


# ============================
# GESTIÓN DE PERSONAS
# ============================

def obtener_todas_personas() -> List[Dict[str, Any]]:
    """
    Obtiene todas las personas registradas en el sistema con información de estado.
    
    Returns:
        List[Dict[str, Any]]: Lista de personas con datos completos
    """
    persona_model = PersonaModel()
    try:
        return persona_model.get_all_personas()
    finally:
        persona_model.close_connection()


def obtener_persona_por_id(persona_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una persona específica por su ID único.
    
    Args:
        persona_id (int): ID de la persona
        
    Returns:
        Optional[Dict[str, Any]]: Datos de la persona si existe
    """
    persona_model = PersonaModel()
    try:
        return persona_model.get_persona_by_id(persona_id)
    finally:
        persona_model.close_connection()


def obtener_personas_activas() -> List[Dict[str, Any]]:
    """
    Obtiene todas las personas que están en estado ACTIVO.
    
    Returns:
        List[Dict[str, Any]]: Lista de personas activas
    """
    persona_model = PersonaModel()
    try:
        return persona_model.get_personas_by_estado(1)  # 1 = ACTIVO
    finally:
        persona_model.close_connection()


# ============================
# GESTIÓN DE ESTADOS
# ============================

def cambiar_estado_persona(persona_id: int, nuevo_estado_id: int) -> Tuple[bool, str]:
    """
    Cambia el estado de una persona a un nuevo estado válido.
    
    Args:
        persona_id (int): ID de la persona
        nuevo_estado_id (int): ID del nuevo estado (1=ACTIVO, 2=INACTIVO, 3=SUSPENDIDO)
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    persona_model = PersonaModel()
    try:
        if not persona_model.persona_existe(persona_id):
            return False, "La persona no existe"
        
        estados = persona_model.get_estados_disponibles()
        estado_valido = any(estado['id'] == nuevo_estado_id for estado in estados)
        
        if not estado_valido:
            return False, "El estado especificado no es válido"
        
        if persona_model.update_persona_estado(persona_id, nuevo_estado_id):
            return True, "Estado actualizado correctamente"
        else:
            return False, "Error al actualizar el estado"
            
    except Exception as e:
        return False, f"Error interno: {str(e)}"
    finally:
        persona_model.close_connection()


def activar_persona(persona_id: int) -> Tuple[bool, str]:
    """
    Activa una persona (estado ACTIVO).
    
    Args:
        persona_id (int): ID de la persona
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    return cambiar_estado_persona(persona_id, 1)  # 1 = ACTIVO


def desactivar_persona(persona_id: int) -> Tuple[bool, str]:
    """
    Desactiva una persona (estado INACTIVO).
    
    Args:
        persona_id (int): ID de la persona
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    return cambiar_estado_persona(persona_id, 2)  # 2 = INACTIVO


def validar_persona_para_operacion(persona_id: int) -> Tuple[bool, str]:
    """
    Valida si una persona puede realizar operaciones (debe estar activa).
    
    Args:
        persona_id (int): ID de la persona
        
    Returns:
        Tuple[bool, str]: (puede_operar, mensaje)
    """
    persona_model = PersonaModel()
    try:
        if not persona_model.persona_existe(persona_id):
            return False, "La persona no existe"
        
        if not persona_model.persona_activa(persona_id):
            return False, "La persona no está activa"
        
        return True, "Persona válida para operaciones"
        
    finally:
        persona_model.close_connection()


# ============================
# AUTENTICACIÓN Y SESIONES
# ============================

def iniciar_sesion(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Inicia sesión de usuario y almacena los datos en variables de sesión globales.
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña
        
    Returns:
        Tuple[bool, str, Optional[Dict[str, Any]]]: (éxito, mensaje, datos_sesión)
        
    Session Data Structure:
        {
            'usuario_id': int,           # ID único del usuario
            'persona_id': int,           # ID de la persona asociada
            'username': str,             # Nombre de usuario
            'nombre_completo': str,      # Nombres + Apellidos
            'email': str,                # Email del usuario
            'rol': str,                  # Rol/tipo de usuario
            'activo': bool,              # Estado de la sesión
            'fecha_login': datetime,     # Timestamp del login
            'permisos': List[str]        # Lista de permisos del usuario
        }
    """
    global _sesion_activa
    
    if not username or not password:
        return False, "Usuario y contraseña son requeridos", None
    
    persona_model = PersonaModel()
    try:
        # Verificar credenciales
        if not persona_model.verificar_password(username, password):
            return False, "Usuario o contraseña incorrecta", None
        
        # Obtener datos completos del usuario
        usuario_data = persona_model.get_usuario_by_username(username)
        if not usuario_data:
            return False, "Error al obtener datos del usuario", None
        
        # Verificar que el usuario esté activo
        if not persona_model.persona_activa(usuario_data.get('persona_id')):
            return False, "El usuario no está activo", None
        
        # Crear datos de sesión
        _sesion_activa = {
            'usuario_id': usuario_data.get('id'),
            'persona_id': usuario_data.get('persona_id'),
            'username': username,
            'nombre_completo': f"{usuario_data.get('nombres', '')} {usuario_data.get('apellidos', '')}".strip(),
            'email': usuario_data.get('email'),
            'rol': usuario_data.get('rol', 'usuario'),
            'activo': True,
            'fecha_login': persona_model.get_current_timestamp(),
            'permisos': usuario_data.get('permisos', [])
        }
        
        return True, "Sesión iniciada correctamente", _sesion_activa
        
    except Exception as e:
        return False, f"Error al iniciar sesión: {str(e)}", None
    finally:
        persona_model.close_connection()


def cerrar_sesion() -> Tuple[bool, str]:
    """
    Cierra la sesión activa del usuario.
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    global _sesion_activa
    
    if _sesion_activa is None:
        return False, "No hay sesión activa"
    
    _sesion_activa = None
    return True, "Sesión cerrada correctamente"


def verificar_sesion_activa() -> bool:
    """
    Verifica si hay una sesión válida y activa.
    
    Returns:
        bool: True si hay sesión activa, False si no
    """
    global _sesion_activa
    return _sesion_activa is not None and _sesion_activa.get('activo', False)


def obtener_sesion_activa() -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de la sesión activa si existe y es válida.
    
    Returns:
        Optional[Dict[str, Any]]: Datos de sesión o None
    """
    if verificar_sesion_activa():
        return _sesion_activa
    return None


# ============================
# UTILIDADES DE SESIÓN
# ============================

def obtener_dato_sesion(campo: str) -> Optional[Any]:
    """
    Obtiene un dato específico de la sesión activa.
    
    Args:
        campo (str): Nombre del campo a obtener
        
    Returns:
        Optional[Any]: Valor del campo o None si no existe sesión/campo
    """
    sesion = obtener_sesion_activa()
    return sesion.get(campo) if sesion else None


def obtener_id_usuario_logueado() -> Optional[int]:
    """Obtiene el ID del usuario logueado."""
    return obtener_dato_sesion('usuario_id')


def obtener_id_persona_logueada() -> Optional[int]:
    """Obtiene el ID de la persona del usuario logueado."""
    return obtener_dato_sesion('persona_id')


def obtener_nombre_usuario_logueado() -> Optional[str]:
    """Obtiene el nombre completo del usuario logueado."""
    return obtener_dato_sesion('nombre_completo')


def obtener_username_logueado() -> Optional[str]:
    """Obtiene el username del usuario logueado."""
    return obtener_dato_sesion('username')


def obtener_rol_usuario_logueado() -> Optional[str]:
    """Obtiene el rol del usuario logueado."""
    return obtener_dato_sesion('rol')


# ============================
# CONTROL DE PERMISOS
# ============================

def usuario_tiene_permiso(permiso: str) -> bool:
    """
    Verifica si el usuario logueado tiene un permiso específico.
    
    Args:
        permiso (str): Nombre del permiso a verificar
        
    Returns:
        bool: True si tiene el permiso, False si no
    """
    permisos = obtener_dato_sesion('permisos')
    return permiso in permisos if permisos else False


def validar_sesion_y_permisos(permisos_requeridos: List[str] = None) -> Tuple[bool, str]:
    """
    Valida sesión activa y opcionalmente verifica permisos específicos.
    
    Args:
        permisos_requeridos (List[str], optional): Lista de permisos requeridos
        
    Returns:
        Tuple[bool, str]: (válido, mensaje)
    """
    if not verificar_sesion_activa():
        return False, "No hay sesión activa. Inicie sesión para continuar."
    
    if permisos_requeridos:
        for permiso in permisos_requeridos:
            if not usuario_tiene_permiso(permiso):
                return False, f"No tiene permisos suficientes. Requiere: {permiso}"
    
    return True, "Sesión y permisos válidos"


def actualizar_datos_sesion(nuevos_datos: Dict[str, Any]) -> bool:
    """ 
    Actualiza datos específicos de la sesión activa de forma segura.
    
    Args:
        nuevos_datos (Dict[str, Any]): Campos a actualizar
        
    Returns:
        bool: True si se actualizó correctamente
    """
    global _sesion_activa
    
    if not verificar_sesion_activa():
        return False
    
    # Campos permitidos por seguridad
    campos_permitidos = {'nombre_completo', 'email', 'rol', 'permisos'}
    
    for campo, valor in nuevos_datos.items():
        if campo in campos_permitidos:
            _sesion_activa[campo] = valor
    
    return True
