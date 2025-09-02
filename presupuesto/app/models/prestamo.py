"""
Modelo SQLAlchemy para la tabla 'prestamo'.
Representa los préstamos otorgados a personas.
"""

from sqlalchemy import Column, Integer, Date, Enum, String, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prestamo(Base):
    """
    Clase Prestamo que representa un préstamo en el sistema.

    Atributos:
        id_prestamo (int): Identificador único del préstamo.
        fecha (date): Fecha de otorgamiento del préstamo.
        estado (str): Estado del préstamo.
        moneda (str): Moneda del préstamo.
        saldo_inicial (Decimal): Saldo inicial del préstamo.
        limite_credito (Decimal): Límite de crédito del préstamo.
        id_persona (int): ID de la persona asociada al préstamo.
    """
    __tablename__ = 'prestamo'

    id_prestamo = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    estado = Column(Enum('ACTIVO', 'CANCELADO', 'MORA'), nullable=False)
    moneda = Column(String(10), nullable=False)
    saldo_inicial = Column(DECIMAL(15,2), nullable=False)
    limite_credito = Column(DECIMAL(15,2), nullable=False)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=False)
