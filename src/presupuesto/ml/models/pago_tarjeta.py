"""
Modelo SQLAlchemy para la tabla 'pago_tarjeta'.
Representa los pagos realizados a tarjetas de crédito.
"""

from sqlalchemy import Column, Integer, Date, DECIMAL, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PagoTarjeta(Base):
    """
    Clase PagoTarjeta que representa un pago realizado a una tarjeta de crédito.

    Atributos:
        id_pago (int): Identificador único del pago.
        id_tarjeta (int): ID de la tarjeta asociada.
        fecha_pago (date): Fecha en que se realizó el pago.
        monto_pago (Decimal): Monto pagado.
        referencia (str): Referencia del pago.
        id_persona (int): ID de la persona que realizó el pago.
    """
    __tablename__ = 'pago_tarjeta'

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_tarjeta = Column(Integer, ForeignKey('tarjeta_credito.id_tarjeta'), nullable=False)
    fecha_pago = Column(Date, nullable=False)
    monto_pago = Column(DECIMAL(15,2), nullable=False)
    referencia = Column(String(100), nullable=True)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=True)
