# Documentación de la Base de Datos

Este documento describe la estructura, scripts y buenas prácticas para la base de datos del proyecto **app-presopuesto** integrado con interfaz Flet y arquitectura MVC.

---

## 📦 Estructura del Proyecto y Base de Datos

```text
app-presupuesto/
├── src/                    # Código fuente principal
│   ├── views/              # Interfaces Flet (UI Layer)
│   │   ├── __init__.py
│   │   ├── user_view.py    # Vista de login con Flet
│   │   ├── dashboard_view.py # Dashboard principal (v0.6.0)
│   │   └── budget_view.py  # Gestión de presupuestos (v0.6.0)
│   ├── controllers/        # Lógica de negocio (Business Layer)
│   │   ├── __init__.py
│   │   ├── persona_controller.py    # Control de autenticación
│   │   ├── budget_controller.py     # Control de presupuestos (v0.6.0)
│   │   └── transaction_controller.py # Control de transacciones (v0.6.0)
│   ├── models/             # Modelos de datos (Data Layer)
│   │   ├── __init__.py
│   │   ├── persona.py      # Modelo de usuario
│   │   ├── presupuesto.py  # Modelo de presupuesto
│   │   ├── cuenta.py       # Modelo de cuenta bancaria
│   │   ├── transaccion.py  # Modelo de transacciones
│   │   └── categoria.py    # Modelo de categorías
│   ├── database/           # Capa de acceso a datos
│   │   ├── __init__.py
│   │   ├── connection.py   # Pool de conexiones MySQL
│   │   ├── queries.py      # Consultas SQL optimizadas
│   │   └── migrations.py   # Scripts de migración
│   └── utils/              # Utilidades y helpers
│       ├── __init__.py
│       ├── security.py     # Hash bcrypt, validaciones
│       ├── validators.py   # Validadores de entrada Flet
│       └── helpers.py      # Funciones auxiliares
├── database/               # Scripts de base de datos
│   └── scripts/
│       ├── create/         # Scripts de creación
│       │   ├── create_tables.sql
│       │   ├── create_triggers.sql
│       │   ├── create_views.sql
│       │   ├── create_functions.sql
│       │   ├── create_indexes.sql
│       │   └── create_data.sql
│       ├── migrations/     # Migraciones por versión
│       │   ├── v0.5.0_initial.sql
│       │   ├── v0.6.0_dashboard.sql
│       │   └── v0.7.0_ai_features.sql
│       └── backups/        # Respaldos automatizados
│   └── init_db.bat        # Script de inicialización Windows
├── config/                 # Configuración por ambiente
│   ├── development.env    # Variables desarrollo
│   ├── production.env     # Variables producción
│   └── testing.env        # Variables testing
└── tests/                  # Suite de pruebas
    ├── unit/              # Pruebas unitarias BD
    ├── integration/       # Pruebas integración Flet-BD
    └── fixtures/          # Datos de prueba
```

---

## 🗄️ Arquitectura de Base de Datos

### Diseño Orientado a la Aplicación Flet

La base de datos está optimizada para la interfaz gráfica Flet y sigue los principios de la arquitectura MVC:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flet Views    │ -> │  Controllers    │ -> │    Models       │
│  (user_view.py) │    │ (persona_c.py)  │    │ (persona.py)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ Database Layer  │
                        │ (connection.py) │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   MySQL 8.0+    │
                        │ (Optimizado)    │
                        └─────────────────┘
```

---

## 🚀 Configuración e Inicialización

### Requisitos del Sistema:
- **MySQL 8.0+** o **MariaDB 10.6+**
- **Python 3.8+** con mysql-connector-python
- **4GB RAM** mínimo para desarrollo
- **10GB espacio** para datos y logs

### Inicialización Rápida:

#### Opción 1: Script Automático (Recomendado)
```batch
# Windows
database\scripts\init_db.bat

# Linux/Mac
bash database/scripts/init_db.sh
```

#### Opción 2: Ejecución Manual Paso a Paso
```bash
# 1. Crear base de datos
mysql -u root -p -e "CREATE DATABASE presupuesto_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Crear usuario dedicado
mysql -u root -p -e "
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON presupuesto_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;"

# 3. Ejecutar scripts en orden
mysql -u app_user -p presupuesto_db < database/scripts/create/create_tables.sql
mysql -u app_user -p presupuesto_db < database/scripts/create/create_indexes.sql
mysql -u app_user -p presupuesto_db < database/scripts/create/create_triggers.sql
mysql -u app_user -p presupuesto_db < database/scripts/create/create_views.sql
mysql -u app_user -p presupuesto_db < database/scripts/create/create_functions.sql
mysql -u app_user -p presupuesto_db < database/scripts/create/create_data.sql
```

---

## ⚙️ Configuración de Conexión Optimizada

### Variables de Entorno para Producción:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=presupuesto_db
DB_USER=app_user
DB_PASSWORD=UltraSecurePassword123!@#

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Security Settings
SECRET_KEY=your-ultra-secure-secret-key-minimum-64-characters-long
JWT_SECRET_KEY=different-secret-for-jwt-tokens-also-64-chars-minimum

# Application Settings
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
```

### Configuración Optimizada en Python:
```python
# src/database/connection.py
import os
import mysql.connector.pooling
from mysql.connector import Error
import logging

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self._create_pool()
    
    def _create_pool(self):
        """Crear pool de conexiones optimizado para Flet UI"""
        try:
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'database': os.getenv('DB_NAME', 'presupuesto_db'),
                'user': os.getenv('DB_USER', 'app_user'),
                'password': os.getenv('DB_PASSWORD', ''),
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'pool_name': 'flet_app_pool',
                'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
                'pool_reset_session': True,
                'autocommit': True
            }
            
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**config)
            logging.info("✅ Pool de conexiones creado exitosamente")
            
        except Error as e:
            logging.error(f"❌ Error creando pool de conexiones: {e}")
            raise
    
    def get_connection(self):
        """Obtener conexión del pool con manejo de errores"""
        try:
            return self.pool.get_connection()
        except Error as e:
            logging.error(f"❌ Error obteniendo conexión: {e}")
            raise

# Instancia global del manager
db_manager = DatabaseManager()

def get_db_connection():
    """Helper function para obtener conexiones"""
    return db_manager.get_connection()
```

---

## 📊 Esquema de Base de Datos Actual (v0.5.0)

### Tablas Principales Implementadas:

#### 1. Tabla `usuarios` (personas)
```sql
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL,
    
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_ultimo_login (ultimo_login)
);
```

#### 2. Tabla `sesiones` (manejo de sesiones Flet)
```sql
CREATE TABLE sesiones (
    id_sesion VARCHAR(255) PRIMARY KEY,
    id_usuario INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    activa BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_expiracion (fecha_expiracion)
);
```

#### 3. Tabla `logs_seguridad` (auditoría)
```sql
CREATE TABLE logs_seguridad (
    id_log BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    accion VARCHAR(100) NOT NULL,
    detalle TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    resultado ENUM('EXITOSO', 'FALLIDO', 'BLOQUEADO') NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_usuario (id_usuario),
    INDEX idx_fecha (fecha),
    INDEX idx_accion (accion)
);
```

---

## 🔮 Esquema Futuro (v0.6.0 - Dashboard)

### Tablas a Implementar:

#### 1. Cuentas Bancarias
```sql
CREATE TABLE cuentas (
    id_cuenta INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('corriente', 'ahorros', 'efectivo', 'inversion') NOT NULL,
    saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    moneda VARCHAR(3) DEFAULT 'COP',
    numero_cuenta VARCHAR(50),
    banco VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_activa (activa)
);
```

#### 2. Categorías
```sql
CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo ENUM('ingreso', 'gasto', 'transferencia') NOT NULL,
    color VARCHAR(7) DEFAULT '#2196F3',  -- Color hex para UI
    icono VARCHAR(50) DEFAULT 'category', -- Icono Flet
    padre_id INT NULL,  -- Para subcategorías
    activa BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (padre_id) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    INDEX idx_tipo (tipo),
    INDEX idx_padre (padre_id)
);
```

#### 3. Transacciones
```sql
CREATE TABLE transacciones (
    id_transaccion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_cuenta INT NOT NULL,
    id_categoria INT NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    beneficiario VARCHAR(150),
    numero_referencia VARCHAR(100),
    notas TEXT,
    origen ENUM('manual', 'importado', 'automatico') DEFAULT 'manual',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_cuenta) REFERENCES cuentas(id_cuenta) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    INDEX idx_cuenta (id_cuenta),
    INDEX idx_fecha (fecha),
    INDEX idx_categoria (id_categoria),
    INDEX idx_monto (monto)
);
```

---

## 🔧 Optimizaciones para Interfaz Flet

### 1. Consultas Optimizadas para UI:
```sql
-- Vista para dashboard principal
CREATE VIEW vista_dashboard_usuario AS
SELECT 
    u.id_usuario,
    u.nombre,
    COUNT(DISTINCT c.id_cuenta) as total_cuentas,
    COALESCE(SUM(c.saldo_actual), 0) as patrimonio_total,
    COALESCE(
        (SELECT SUM(t.monto) 
         FROM transacciones t 
         JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
         WHERE c2.id_usuario = u.id_usuario 
         AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
         AND t.monto < 0), 0
    ) as gastos_ultimo_mes
FROM usuarios u
LEFT JOIN cuentas c ON u.id_usuario = c.id_usuario AND c.activa = TRUE
WHERE u.activo = TRUE
GROUP BY u.id_usuario, u.nombre;
```

### 2. Procedimientos para Operaciones Comunes:
```sql
-- Procedimiento para autenticación (usado por persona_controller.py)
DELIMITER //
CREATE PROCEDURE sp_autenticar_usuario(
    IN p_username VARCHAR(50),
    OUT p_user_id INT,
    OUT p_password_hash VARCHAR(255),
    OUT p_intentos_fallidos INT,
    OUT p_bloqueado_hasta TIMESTAMP
)
BEGIN
    SELECT 
        id_usuario,
        password_hash,
        intentos_fallidos,
        bloqueado_hasta
    INTO p_user_id, p_password_hash, p_intentos_fallidos, p_bloqueado_hasta
    FROM usuarios 
    WHERE (username = p_username OR email = p_username) 
    AND activo = TRUE;
END //
DELIMITER ;
```

### 3. Triggers para Mantener Integridad:
```sql
-- Trigger para actualizar saldo_actual al insertar transacción
DELIMITER //
CREATE TRIGGER tr_actualizar_saldo_insert
AFTER INSERT ON transacciones
FOR EACH ROW
BEGIN
    UPDATE cuentas 
    SET saldo_actual = saldo_actual + NEW.monto
    WHERE id_cuenta = NEW.id_cuenta;
END //
DELIMITER ;
```

---

## 📈 Estrategia de Migraciones

### Sistema de Versionado:
```
database/scripts/migrations/
├── v0.5.0_initial.sql         # Estado actual
├── v0.6.0_dashboard.sql       # Próxima versión
├── v0.7.0_ai_features.sql     # IA y categorización
├── v0.8.0_reports.sql         # Reportes avanzados
└── v0.9.0_investments.sql     # Inversiones
```

### Script de Migración Automática:
```python
# src/database/migrations.py
class MigrationManager:
    def __init__(self):
        self.current_version = self.get_current_version()
        
    def get_current_version(self):
        """Obtener versión actual de la BD"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else "0.0.0"
        except Error:
            return "0.0.0"
    
    def apply_migrations(self, target_version):
        """Aplicar migraciones hasta la versión objetivo"""
        migrations = self.get_pending_migrations(target_version)
        for migration in migrations:
            self.apply_migration(migration)
```

---

## 🔒 Seguridad de Base de Datos

### 1. Configuración de Usuario Seguro:
```sql
-- Crear usuario con permisos mínimos
CREATE USER 'app_flet_user'@'localhost' IDENTIFIED BY 'ComplexPassword123!@#';

-- Otorgar solo permisos necesarios
GRANT SELECT, INSERT, UPDATE, DELETE ON presupuesto_db.usuarios TO 'app_flet_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON presupuesto_db.sesiones TO 'app_flet_user'@'localhost';
GRANT INSERT ON presupuesto_db.logs_seguridad TO 'app_flet_user'@'localhost';

-- Para producción, habilitar SSL
ALTER USER 'app_flet_user'@'localhost' REQUIRE SSL;
FLUSH PRIVILEGES;
```

### 2. Configuración de Logs de Auditoría:
```sql
-- Habilitar logs generales (solo en desarrollo)
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/log/mysql/general.log';

-- Logs de consultas lentas
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

---

## 🧪 Testing de Base de Datos

### 1. Datos de Prueba:
```sql
-- Insertar usuario de prueba
INSERT INTO usuarios (nombre, email, username, password_hash) VALUES 
('Usuario Test', 'test@test.com', 'testuser', '$2b$12$hash_bcrypt_aqui');

-- Categorías básicas
INSERT INTO categorias (nombre, tipo, color, icono) VALUES 
('Alimentación', 'gasto', '#FF5722', 'restaurant'),
('Transporte', 'gasto', '#2196F3', 'directions_car'),
('Salario', 'ingreso', '#4CAF50', 'work');
```

### 2. Tests de Integración:
```python
# tests/integration/test_database.py
import pytest
from src.database.connection import get_db_connection

def test_database_connection():
    """Test conexión a base de datos"""
    conn = get_db_connection()
    assert conn is not None
    conn.close()

def test_user_authentication():
    """Test autenticación de usuario"""
    from src.controllers.persona_controller import autenticar_usuario
    user, msg = autenticar_usuario('testuser', 'testpass')
    assert user is not None
```

---

## 📊 Monitoreo y Mantenimiento

### 1. Consultas de Monitoreo:
```sql
-- Verificar performance de consultas
SELECT 
    SCHEMA_NAME as database_name,
    SUM(COUNT_READ) as total_reads,
    SUM(COUNT_WRITE) as total_writes,
    SUM(SUM_TIMER_READ)/1000000000 as read_time_seconds
FROM performance_schema.table_io_waits_summary_by_table
WHERE SCHEMA_NAME = 'presupuesto_db'
GROUP BY SCHEMA_NAME;

-- Verificar conexiones activas
SHOW PROCESSLIST;

-- Verificar tamaño de tablas
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables 
WHERE table_schema = 'presupuesto_db'
ORDER BY size_mb DESC;
```

### 2. Respaldos Automatizados:
```bash
#!/bin/bash
# database/scripts/backup_db.sh
BACKUP_DIR="/backup/presupuesto_db"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -u app_user -p presupuesto_db \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    > $BACKUP_DIR/backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/backup_$DATE.sql

# Limpiar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

---

## 📚 Referencias y Documentación

### Enlaces Importantes:
- 📖 [README Principal](../README.md)
- 🏗️ [Arquitectura del Sistema](ARCHITECTURE.md)
- 🔒 [Política de Seguridad](../documentacion/SECURITY.md)
- 🚀 [Roadmap del Proyecto](../documentacion/roadmap.md)
- 👥 [Guía de Contribución](../documentacion/CONTRIBUTING.md)

### Herramientas Recomendadas:
- **MySQL Workbench**: Para diseño y administración visual
- **DBeaver**: Cliente universal de base de datos
- **Adminer**: Interfaz web ligera para administración
- **Percona Toolkit**: Herramientas de optimización y monitoring

---

## 👨‍💻 Información del Proyecto

**Autor**: Esteban Fabián Patiño Montealegre  
**Email**: estebanfabianp@gmail.com  
**Versión Actual**: 0.5.0 - Login System & Security  
**Próxima Versión**: 0.6.0 - Dashboard & Basic CRUD  
**Última Actualización**: Enero 2025

---

**🔧 Estado de Implementación**:
- ✅ **Autenticación y Seguridad**: 100% completado
- ✅ **Pool de Conexiones**: 100% optimizado  
- ✅ **Logs de Auditoría**: 100% implementado
- 🚧 **Dashboard Tables**: En desarrollo (v0.6.0)
- 📋 **Migration System**: Planificado (v0.6.0)
- 🔮 **AI Features DB**: Diseñado (v0.7.0)

**¡La base de datos está lista para soportar el crecimiento de la aplicación Flet! 🚀**
