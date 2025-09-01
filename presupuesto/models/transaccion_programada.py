"""
Modelo SQLAlchemy para la tabla 'transaccion_programada'.
Representa las transacciones programadas que se ejecutan periódicamente.
"""

from sqlalchemy import Column, Integer, Date, DECIMAL, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransaccionProgramada(Base):
    """
    Clase TransaccionProgramada que representa una transacción programada.

    Atributos:
        id_transaccion (int): Identificador único de la transacción.
        fecha (date): Fecha de la transacción programada.
        tipo (str): Tipo de transacción ('CARGO' o 'ABONO').
        monto (Decimal): Monto de la transacción.
        frecuencia (str): Frecuencia de la transacción ('DIARIA', 'SEMANAL', 'MENSUAL', 'ANUAL').
        repeticion (int): Número de repeticiones.
        id_categoria (int): ID de la categoría asociada.
        id_beneficiario (int): ID del beneficiario asociado.
    """
    __tablename__ = 'transaccion_programada'

    id_transaccion = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    tipo = Column(Enum('CARGO', 'ABONO'), nullable=False)
    monto = Column(DECIMAL(15,2), nullable=False)
    frecuencia = Column(Enum('DIARIA', 'SEMANAL', 'MENSUAL', 'ANUAL'), nullable=False)
    repeticion = Column(Integer, nullable=True)
    id_categoria = Column(Integer, ForeignKey('categoria.id_categoria'), nullable=False)
    id_beneficiario = Column(Integer, ForeignKey('beneficiario.id_beneficiario'), nullable=False)
