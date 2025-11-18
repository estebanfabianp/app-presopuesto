# 🚀 Guía de Instalación - App Presupuesto

Guía completa de instalación y configuración para el sistema de gestión financiera personal con arquitectura MVC optimizada y funcionalidades de IA avanzadas.

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#-requisitos-del-sistema)
2. [Instalación Rápida](#-instalación-rápida)
3. [Configuración Detallada](#-configuración-detallada)
4. [Configuración de Base de Datos](#-configuración-de-base-de-datos)
5. [Configuración de Desarrollo](#-configuración-de-desarrollo)
6. [Verificación de Instalación](#-verificación-de-instalación)
7. [Solución de Problemas](#-solución-de-problemas)
8. [Configuraciones Avanzadas](#-configuraciones-avanzadas)

---

## 🖥️ Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Python**: 3.9+ (Recomendado: 3.11+ para mejor rendimiento)
- **Memoria RAM**: 4GB mínimo (8GB recomendado)
- **Espacio en Disco**: 2GB libres
- **Resolución de Pantalla**: 1024x768 mínimo

### Requisitos Recomendados para Desarrollo
- **Python**: 3.11+
- **Memoria RAM**: 16GB
- **Espacio en Disco**: 10GB libres
- **SSD**: Para mejor performance de base de datos
- **Resolución**: 1920x1080 o superior

### Software Requerido
- **Git**: Para control de versiones
- **MySQL**: 8.0+ o MariaDB 10.6+ con UTF-8
- **Editor de Código**: VS Code, PyCharm o similar (opcional)

---

## ⚡ Instalación Rápida

### 1. Clonar el Repositorio
```bash
# Clonar el repositorio principal
git clone https://github.com/FinanceAI-Labs/app-presupuesto.git
cd app-presupuesto

# Verificar la estructura del proyecto
ls -la
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Verificar activación
which python  # Debe mostrar la ruta del entorno virtual
```

### 3. Instalar Dependencias Básicas
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias core
pip install -r requirements/base.txt

# Verificar instalación de Flet
python -c "import flet; print(f'Flet version: {flet.__version__}')"
```

### 4. Configuración Inicial Rápida
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración básica (usar tu editor favorito)
nano .env  # o code .env para VS Code
```

### 5. Ejecutar la Aplicación
```bash
# Ejecutar en modo de desarrollo
python src/views/main.py

# Si hay problemas de dependencias, usar el login directo:
python src/views/login.py
```

---

## 🔧 Configuración Detallada

### Variables de Entorno (.env)

Crear y configurar el archivo `.env` con las siguientes variables:

```bash
# Configuración de Aplicación
APP_NAME="App Presupuesto"
APP_VERSION="0.7.1+"
APP_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here_minimum_32_characters

# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_presupuesto
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_CHARSET=utf8mb4
DB_POOL_SIZE=5
DB_POOL_RECYCLE=3600

# Configuración de Seguridad
BCRYPT_ROUNDS=12
SESSION_TIMEOUT=28800  # 8 horas en segundos
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_TIME=1800  # 30 minutos

# Configuración de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Funcionalidades IA (Opcional)
AI_ENABLED=True
ML_MODEL_PATH=models/
OCR_ENABLED=False
PREDICTION_ENABLED=True

# Configuración UI
UI_THEME=light
UI_WINDOW_WIDTH=1400
UI_WINDOW_HEIGHT=900
UI_RESIZABLE=True
```

### Generar SECRET_KEY Segura
```python
# Ejecutar este script para generar una clave segura
import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))

print(f"SECRET_KEY={generate_secret_key()}")
```

---

## 🗄️ Configuración de Base de Datos

### Instalación MySQL (Windows)
```bash
# Descargar MySQL Community Server 8.0+
# https://dev.mysql.com/downloads/mysql/

# Durante la instalación:
# - Usar Strong Password Encryption
# - Crear usuario root con contraseña segura
# - Configurar como Windows Service
```

### Instalación MySQL (Ubuntu/Debian)
```bash
# Actualizar repositorios
sudo apt update

# Instalar MySQL Server
sudo apt install mysql-server

# Configuración segura inicial
sudo mysql_secure_installation

# Crear usuario y base de datos
sudo mysql -u root -p
```

### Instalación MySQL (macOS)
```bash
# Usando Homebrew
brew install mysql

# Iniciar servicio
brew services start mysql

# Configuración inicial
mysql_secure_installation
```

### Crear Base de Datos y Usuario
```sql
-- Conectar como root
mysql -u root -p

-- Crear base de datos
CREATE DATABASE app_presupuesto 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Crear usuario específico para la aplicación
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password_here';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON app_presupuesto.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;

-- Verificar conexión
USE app_presupuesto;
SHOW TABLES;
```

### Ejecutar Migraciones Iniciales
```bash
# Ejecutar script de setup automático
python scripts/setup.py

# O configuración manual paso a paso:
mysql -u app_user -p app_presupuesto < database/schemas/001_initial_tables.sql
mysql -u app_user -p app_presupuesto < database/schemas/002_financial_tables.sql

# Verificar estructura
mysql -u app_user -p app_presupuesto -e "SHOW TABLES;"
```

### Poblar con Datos de Ejemplo
```bash
# Ejecutar seeders para datos de prueba
python scripts/seed_database.py

# Verificar datos de ejemplo
mysql -u app_user -p app_presupuesto -e "SELECT COUNT(*) FROM personas;"
```

---

## 👨‍💻 Configuración de Desarrollo

### Instalar Dependencias de Desarrollo
```bash
# Herramientas de desarrollo
pip install -r requirements/dev.txt

# Herramientas de testing
pip install -r requirements/test.txt

# Herramientas de IA (opcional, para desarrollo completo)
pip install -r requirements/ai.txt
```

### Configurar Pre-commit Hooks
```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files
```

### Configurar VS Code (Recomendado)
Crear `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true
    }
}
```

Crear `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "App Presupuesto - Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/views/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "App Presupuesto - Login Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/views/login.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src",
                "DEBUG": "True"
            }
        }
    ]
}
```

---

## ✅ Verificación de Instalación

### Test de Componentes Básicos
```bash
# 1. Verificar Python y dependencias
python --version
pip list | grep flet
pip list | grep mysql-connector-python

# 2. Test de conexión a base de datos
python -c "
import sys
sys.path.append('src')
from database.connection import test_connection
if test_connection():
    print('✅ Conexión a BD exitosa')
else:
    print('❌ Error de conexión a BD')
"

# 3. Test de importaciones críticas
python -c "
try:
    import flet as ft
    print('✅ Flet importado correctamente')
    import sys
    sys.path.append('src')
    from controllers.persona_controller import verificar_sesion_activa
    print('✅ Controladores importados correctamente')
    print('🎉 Instalación verificada exitosamente!')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
"
```

### Test de Aplicación Completa
```bash
# Ejecutar suite de tests básica
pytest tests/unit/ -v

# Test específico del sistema de autenticación
python -c "
import sys
sys.path.append('src')
from controllers.persona_controller import iniciar_sesion
# Test con credenciales de ejemplo (si existen)
print('Sistema de autenticación listo para usar')
"

# Ejecutar aplicación en modo debug
python src/views/login.py --debug
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error de Importación de Flet
```bash
# Error: ModuleNotFoundError: No module named 'flet'
# Solución:
pip uninstall flet
pip install flet==0.21.0

# Verificar instalación
python -c "import flet; print('Flet OK')"
```

#### 2. Error de Conexión MySQL
```bash
# Error: Can't connect to MySQL server
# Verificar servicio MySQL:

# Windows:
net start mysql

# Linux:
sudo systemctl start mysql
sudo systemctl status mysql

# macOS:
brew services restart mysql
```

#### 3. Error de Permisos de Base de Datos
```sql
-- Error: Access denied for user
-- Solución: Verificar permisos

SHOW GRANTS FOR 'app_user'@'localhost';

-- Si es necesario, otorgar permisos nuevamente:
GRANT ALL PRIVILEGES ON app_presupuesto.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Error de Variables de Entorno
```bash
# Error: KeyError en variables de entorno
# Verificar archivo .env existe y está bien configurado:

ls -la .env
cat .env | grep -v PASSWORD  # Ver configuración (ocultar passwords)

# Recargar variables:
source .env  # Linux/macOS
# En Windows, reiniciar terminal
```

#### 5. Error de Puertos en Uso
```bash
# Error: Address already in use
# Verificar puertos:

# Windows:
netstat -ano | findstr :3306

# Linux/macOS:
lsof -i :3306

# Cambiar puerto en .env si es necesario
```

### Debug Avanzado

#### Habilitar Logging Detallado
```python
# En el archivo .env
LOG_LEVEL=DEBUG

# O temporalmente en código:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test de Componentes Individuales
```bash
# Test del controlador de personas
python -c "
import sys
sys.path.append('src')
from controllers.persona_controller import obtener_sesion_activa
print('Controlador OK')
"

# Test de la vista de login
python src/views/login.py --test-mode

# Test de conexión detallado
python scripts/test_connection.py --verbose
```

---

## 🚀 Configuraciones Avanzadas

### Configuración para Producción

#### Variables de Entorno Producción
```bash
# .env.production
APP_ENV=production
DEBUG=False
SECRET_KEY=production_secret_key_very_secure

# Base de datos optimizada
DB_POOL_SIZE=20
DB_POOL_RECYCLE=1800

# Seguridad reforzada
BCRYPT_ROUNDS=14
SESSION_TIMEOUT=14400  # 4 horas

# Logging optimizado
LOG_LEVEL=WARNING
LOG_FILE=/var/log/app-presupuesto/app.log
```

#### Optimización MySQL Producción
```sql
-- my.cnf optimizations
[mysqld]
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
```

### Configuración Docker (Opcional)

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/prod.txt

COPY src/ src/
COPY config/ config/
COPY .env .env

EXPOSE 8000
CMD ["python", "src/views/main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
    depends_on:
      - mysql
    volumes:
      - ./logs:/app/logs

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: app_presupuesto
      MYSQL_USER: app_user
      MYSQL_PASSWORD: secure_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/schemas:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

### Configuración de Monitoreo

#### Logging Avanzado
```python
# config/logging.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

### Backup y Recuperación

#### Script de Backup Automático
```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/app-presupuesto"
DB_NAME="app_presupuesto"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
mysqldump -u app_user -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de configuración
cp .env $BACKUP_DIR/env_backup_$DATE

# Comprimir y limpiar archivos antiguos
gzip $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completado: $DATE"
```

---

## 📞 Soporte y Recursos Adicionales

### Documentación Relacionada
- [Arquitectura del Sistema](ARCHITECTURE.md)
- [Guía de Contribución](CONTRIBUTING.md)
- [Referencia de API](API_REFERENCE.md)
- [Guía de Despliegue](DEPLOYMENT.md)

### Canales de Soporte
- **GitHub Issues**: Para bugs y preguntas técnicas
- **Discord**: [Comunidad de Desarrolladores](https://discord.gg/financeai-devs)
- **Email**: estebanfabianp@gmail.com para consultas avanzadas

### Recursos de Aprendizaje
- [Documentación oficial de Flet](https://flet.dev)
- [Guía de MySQL 8.0](https://dev.mysql.com/doc/)
- [Best Practices de Python](https://docs.python.org/3/tutorial/)

---

**📅 Última Actualización**: Enero 2025  
**🎯 Versión Compatible**: v0.7.1+ - Authentication & Session Optimization  
**✅ Estado**: Guía Completa y Verificada  
**📧 Soporte**: estebanfabianp@gmail.com

**¡Tu instalación está lista para construir el futuro de las finanzas personales! 🚀💰**
