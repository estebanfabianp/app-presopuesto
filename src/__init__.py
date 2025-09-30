'''
# Paquete principal src

# Fix relative imports - from src level, database and controllers are in same directory
try:
    from .database import DatabaseConnector
except ImportError:
    DatabaseConnector = None

# Import only what exists in controllers module
try:
    from .controllers import validar_persona_para_operacion
except ImportError:
    validar_persona_para_operacion = None

# Commented out imports that don't exist yet
# from .controllers import UserController, registrar_usuario, autenticar_usuario

__all__ = [
    "DatabaseConnector", 
    "validar_persona_para_operacion"
]

# Remove non-existent imports from __all__:
# "UserModel" - doesn't exist
# "UserController", "registrar_usuario", "autenticar_usuario" - not available in controllers
'''