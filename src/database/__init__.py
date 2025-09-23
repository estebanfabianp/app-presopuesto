"""
Módulo de conectividad a base de datos.

Este módulo proporciona clases para manejar conexiones MySQL de forma
robusta con reconexión automática, logging y manejo de errores.

Classes:
    DatabaseConnector: Conector principal para MySQL con reconexión automática
    
Example:
    >>> from src.database import DatabaseConnector
    >>> db = DatabaseConnector(host="localhost", database="mi_db")
    >>> users = db.execute_query("SELECT * FROM users")
"""

from .db_connector import DatabaseConnector

__all__ = ["DatabaseConnector"]

# Información del módulo
__version__ = "0.1.0"
__author__ = "Esteban Fabián Patiño Montealegre"