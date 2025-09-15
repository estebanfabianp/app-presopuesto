"""
Modelo SQLAlchemy para la tabla 'tarjeta_credito'.
Representa las tarjetas de crédito asociadas a productos y personas.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TarjetaCredito(Base):
    """
    Clase TarjetaCredito que representa una tarjeta de crédito.

    Atributos:
        id_tarjeta (int): Identificador único de la tarjeta.
        id_producto (int): ID del producto asociado.
        numero_tarjeta (str): Número de la tarjeta.
        limite_credito (Decimal): Límite de crédito de la tarjeta.
        saldo_actual (Decimal): Saldo actual de la tarjeta.
        fecha_corte (date): Fecha de corte de la tarjeta.
        fecha_pago (date): Fecha de pago de la tarjeta.
        fecha_creacion (datetime): Fecha de creación de la tarjeta.
        estado (str): Estado de la tarjeta ('ACTIVA', 'INACTIVA', 'CANCELADA').
    """
    __tablename__ = 'tarjeta_credito'

    id_tarjeta = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), nullable=False)
    numero_tarjeta = Column(String(20), nullable=False)
    limite_credito = Column(DECIMAL(15,2), nullable=False)
    saldo_actual = Column(DECIMAL(15,2), nullable=False)
    fecha_corte = Column(Date, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    estado = Column(Enum('ACTIVA', 'INACTIVA', 'CANCELADA'), nullable=False, default='ACTIVA')
