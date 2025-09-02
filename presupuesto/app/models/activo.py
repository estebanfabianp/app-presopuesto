"""
Modelo SQLAlchemy para la tabla 'activo'.
Representa los activos financieros de una persona.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Activo(Base):
    """
    Clase Activo que representa un activo financiero.

    Atributos:
        id_activo (int): Identificador único del activo.
        nombre_activo (str): Nombre del activo.
        valor (Decimal): Valor del activo.
        depreciacion (Decimal): Depreciación del activo.
        id_persona (int): ID de la persona propietaria del activo.
        fecha_creacion (datetime): Fecha de creación del activo.
    """
    __tablename__ = 'activo'

    id_activo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_activo = Column(String(100), nullable=False)
    valor = Column(DECIMAL(15,2), nullable=False)
    depreciacion = Column(DECIMAL(15,2), nullable=True)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
