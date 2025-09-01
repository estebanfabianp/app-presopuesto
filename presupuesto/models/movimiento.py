"""
Modelo SQLAlchemy para la tabla 'movimiento'.
Representa los movimientos financieros realizados por personas.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movimiento(Base):
    """
    Clase Movimiento que representa un movimiento financiero.

    Atributos:
        id_movimiento (int): Identificador único del movimiento.
        codigo (str): Código del movimiento.
        monto (Decimal): Monto del movimiento.
        tipo (str): Tipo de movimiento ('CARGO' o 'ABONO').
        cuotas (int): Número de cuotas.
        estado (str): Estado del movimiento.
        id_producto (int): ID del producto asociado.
        id_persona (int): ID de la persona asociada.
        id_categoria (int): ID de la categoría asociada.
        id_beneficiario (int): ID del beneficiario asociado.
    """
    __tablename__ = 'movimiento'

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(45), nullable=True)
    monto = Column(DECIMAL(15,2), nullable=False)
    tipo = Column(Enum('CARGO', 'ABONO'), nullable=False)
    cuotas = Column(Integer, nullable=True)
    estado = Column(Enum('PENDIENTE', 'PAGADO', 'CANCELADO'), nullable=True, default='PENDIENTE')
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=False)
    id_categoria = Column(Integer, ForeignKey('categoria.id_categoria'), nullable=False)
    id_beneficiario = Column(Integer, ForeignKey('beneficiario.id_beneficiario'), nullable=False)
