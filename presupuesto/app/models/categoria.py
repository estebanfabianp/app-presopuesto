"""
Modelo SQLAlchemy para la tabla 'categoria'.
Representa las categorías de movimientos y transacciones.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Categoria(Base):
    """
    Clase Categoria que representa una categoría en el sistema.

    Atributos:
        id_categoria (int): Identificador único de la categoría.
        nombre (str): Nombre de la categoría.
    """
    __tablename__ = 'categoria'

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
