"""
Configuración por ambiente para la aplicación Flask
"""

import os
from datetime import timedelta


class Config:
    """Configuración base compartida entre ambientes"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'presopuesto_db')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Mail (opcional)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')


class DevelopmentConfig(Config):
    """Configuración para ambiente de desarrollo"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuración para environment de testing"""
    DEBUG = True
    TESTING = True
    DB_NAME = 'presopuesto_db_test'


class ProductionConfig(Config):
    """Configuración para ambiente de producción"""
    DEBUG = False
    TESTING = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
