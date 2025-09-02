"""
Modelo SQLAlchemy para la tabla 'presupuesto'.
Representa los presupuestos asignados a personas.
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Presupuesto(Base):
    """
    Clase Presupuesto que representa un presupuesto en el sistema.

    Atributos:
        id_presupuesto (int): Identificador único del presupuesto.
        nombre (str): Nombre del presupuesto.
        descripcion (str): Descripción del presupuesto.
        monto_total (Decimal): Monto total asignado.
        fecha_inicio (date): Fecha de inicio del presupuesto.
        fecha_fin (date): Fecha de fin del presupuesto.
        id_persona (int): ID de la persona asociada al presupuesto.
    """
    __tablename__ = 'presupuesto'

    id_presupuesto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    monto_total = Column(DECIMAL(15,2), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=False)
