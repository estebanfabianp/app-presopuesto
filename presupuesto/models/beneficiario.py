"""
Modelo SQLAlchemy para la tabla 'beneficiario'.
Representa los beneficiarios asociados a movimientos y transacciones.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Beneficiario(Base):
    """
    Clase Beneficiario que representa un beneficiario en el sistema.

    Atributos:
        id_beneficiario (int): Identificador único del beneficiario.
        nombre (str): Nombre del beneficiario.
    """
    __tablename__ = 'beneficiario'

    id_beneficiario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
