"""
Módulo de modelos para la aplicación de presupuesto.

Este módulo contiene todas las clases modelo que manejan la interacción
con la base de datos y la lógica de datos de la aplicación.

Classes:
    UserModel: Manejo de usuarios y autenticación
    PersonaModel: Gestión de personas con estados
    
Example:
    >>> from models.user_model import UserModel
    >>> from models.persona_model import PersonaModel
    >>> user_model = UserModel()
    >>> persona_model = PersonaModel()
"""

from .user_model import UserModel
from .persona_model import PersonaModel

__all__ = ["UserModel", "PersonaModel"]

# Información del módulo
__version__ = "0.2.0"
__author__ = "Esteban Fabián Patiño Montealegre"

# Modelos del proyecto