"""
Modelo SQLAlchemy para la tabla 'persona'.
Representa las personas que utilizan el sistema.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Persona(Base):
    """
    Clase Persona que representa un usuario del sistema.

    Atributos:
        id_persona (int): Identificador único de la persona.
        nombre (str): Nombre de la persona.
        correo_electronico (str): Correo electrónico de la persona.
        usuario (str): Nombre de usuario.
        contrasena (str): Contraseña encriptada.
        fecha_creacion (datetime): Fecha de creación del registro.
        fecha_actualizacion (datetime): Fecha de última actualización.
        activo (bool): Estado de la persona (activo/inactivo).
    """
    __tablename__ = 'persona'

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    usuario = Column(String(45), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
