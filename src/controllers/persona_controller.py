from models.persona_model import PersonaModel
from typing import Tuple, Optional, Dict, Any, List


def obtener_todas_personas() -> List[Dict[str, Any]]:
    """
    Obtiene todas las personas con información de estado.
    
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
    Obtiene una persona específica por su ID.
    
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
    Obtiene todas las personas en estado ACTIVO.
    
    Returns:
        List[Dict[str, Any]]: Lista de personas activas
    """
    persona_model = PersonaModel()
    try:
        return persona_model.get_personas_by_estado(1)  # 1 = ACTIVO
    finally:
        persona_model.close_connection()


def cambiar_estado_persona(persona_id: int, nuevo_estado_id: int) -> Tuple[bool, str]:
    """
    Cambia el estado de una persona.
    
    Args:
        persona_id (int): ID de la persona
        nuevo_estado_id (int): ID del nuevo estado
        
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    persona_model = PersonaModel()
    try:
        # Verificar que la persona existe
        if not persona_model.persona_existe(persona_id):
            return False, "La persona no existe"
        
        # Verificar que el estado es válido
        estados = persona_model.get_estados_disponibles()
        estado_valido = any(estado['id'] == nuevo_estado_id for estado in estados)
        
        if not estado_valido:
            return False, "El estado especificado no es válido"
        
        # Actualizar el estado
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


def validar_usuario_credenciales(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Valida las credenciales de un usuario (nombre de usuario y contraseña).
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña
        
    Returns:
        Tuple[bool, str, Optional[Dict[str, Any]]]: (éxito, mensaje, datos_usuario)
    """
    if not username or not password:
        return False, "Usuario y contraseña son requeridos 2", None
    
    persona_model = PersonaModel()
    try:
        
        # Verificar contraseña
        if not persona_model.verificar_password(username, password):
            return False, "Usuario o  Contraseña incorrecta", None
        else:
            return True, username, "OK"

    except Exception as e:
        return False, f"Error al validar credenciales: {str(e)}", None
    finally:
        persona_model.close_connection()


def autenticar_usuario(username: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Autentica un usuario y retorna sus datos si las credenciales son válidas.
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña
        
    Returns:
        Tuple[Optional[Dict[str, Any]], str]: (datos_usuario, mensaje)
    """
    exito, mensaje, usuario = validar_usuario_credenciales(username, password)
    
    if exito:
        return usuario, mensaje
    else:
        return None, mensaje
