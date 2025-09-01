"""
Modelo SQLAlchemy para la tabla 'producto'.
Representa los productos financieros disponibles en el sistema.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Producto(Base):
    """
    Clase Producto que representa un producto financiero.

    Atributos:
        id_producto (int): Identificador único del producto.
        nombre (str): Nombre del producto.
        monto_maximo (Decimal): Monto máximo permitido.
        monto_minimo (Decimal): Monto mínimo permitido.
        porcentaje_interes (Decimal): Porcentaje de interés.
        tipo_producto (str): Tipo de producto ('TARJETA', 'PRESTAMO', 'OTRO').
    """
    __tablename__ = 'producto'

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    monto_maximo = Column(DECIMAL(15,2), nullable=True)
    monto_minimo = Column(DECIMAL(15,2), nullable=True)
    porcentaje_interes = Column(DECIMAL(5,2), nullable=True)
    tipo_producto = Column(Enum('TARJETA', 'PRESTAMO', 'OTRO'), nullable=False, default='OTRO')
