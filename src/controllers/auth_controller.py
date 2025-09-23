from ..models import UserModel
from typing import Tuple, Optional, Dict, Any
import re
import logging

def registrar_usuario(nombre: str, correo: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Registra un nuevo usuario en la base de datos.
    
    Esta función valida que el correo no esté ya registrado y crea un nuevo
    usuario si es posible. Actualmente la contraseña se almacena en texto plano,
    pero debería ser hasheada en una implementación de producción.
    
    Args:
        nombre (str): Nombre completo del usuario
        correo (str): Correo electrónico único del usuario
        password (str): Contraseña en texto plano (temporal - debe ser hasheada)
        
    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[str]]: 
            - Primer elemento: Diccionario con datos del usuario si el registro es exitoso, None si falla
            - Segundo elemento: None si es exitoso, mensaje de error si falla
            
    Example:
        >>> usuario, error = registrar_usuario("Juan Pérez", "juan@email.com", "password123")
        >>> if usuario:
        ...     print(f"Usuario registrado: {usuario['name']}")
        ... else:
        ...     print(f"Error: {error}")
        
    Note:
        TODO: Implementar hash de contraseñas usando bcrypt antes de almacenar
    """
    # Instanciar el modelo de usuario
    user_model = UserModel()
    
    try:
        # Verificar si el usuario ya existe por email
        existing_user = user_model.get_user_by_email(correo)
        if existing_user:
            return None, "El correo ya está registrado"
        
        # TODO: Hashear la contraseña antes de almacenar
        # password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Crear nuevo usuario (actualmente sin campo password en la tabla)
        nuevo_usuario = user_model.add_user(nombre, correo)
        
        if nuevo_usuario:
            return nuevo_usuario, None
        else:
            return None, "Error al crear el usuario"
            
    except Exception as e:
        return None, f"Error interno: {str(e)}"
    finally:
        # Cerrar conexión para liberar recursos
        user_model.close_connection()


def autenticar_usuario(correo: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario verificando correo y contraseña.
    
    Esta función busca un usuario por correo y verifica su contraseña.
    Actualmente es una implementación básica que necesita mejoras de seguridad.
    
    Args:
        correo (str): Correo electrónico del usuario
        password (str): Contraseña en texto plano para verificar
        
    Returns:
        Optional[Dict[str, Any]]: Diccionario con datos del usuario si la 
                                 autenticación es exitosa, None si falla
                                 
    Example:
        >>> usuario = autenticar_usuario("juan@email.com", "password123")
        >>> if usuario:
        ...     print(f"Bienvenido {usuario['name']}")
        ... else:
        ...     print("Credenciales inválidas")
        
    Note:
        TODO: 
        - Implementar verificación de contraseñas hasheadas
        - Añadir rate limiting para prevenir ataques de fuerza bruta
        - Implementar generación de tokens JWT
        - Registrar intentos de login en logs de seguridad
    """
    user_model = UserModel()
    
    try:
        # Buscar usuario por correo
        usuario = user_model.get_user_by_email(correo)
        
        if not usuario:
            return None  # Usuario no encontrado
        
        # TODO: Verificar contraseña hasheada
        # if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
        #     return usuario
        
        # Implementación temporal - verificación insegura
        # En producción, la tabla debe tener campo password y usar bcrypt
        if usuario and password:  # Verificación placeholder
            return usuario
            
        return None  # Contraseña incorrecta
        
    except Exception as e:
        # Log del error para debugging
        logging.error(f"Error en autenticación: {str(e)}")
        return None
    finally:
        # Cerrar conexión para liberar recursos
        user_model.close_connection()


def validar_credenciales(correo: str, password: str) -> Tuple[bool, str]:
    """
    Valida formato y requisitos básicos de credenciales.
    
    Args:
        correo (str): Email a validar
        password (str): Contraseña a validar
        
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    
    # Validar formato de email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, correo):
        return False, "Formato de email inválido"
    
    # Validar longitud de contraseña
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    return True, ""
