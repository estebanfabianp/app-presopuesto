# App Presupuesto 💰

Aplicación de gestión de presupuestos desarrollada con Flet y arquitectura MVC con integración de base de datos MySQL.

## 📋 Descripción

Sistema completo de gestión de presupuestos personales con interfaz gráfica moderna construida con Python y Flet. Incluye sistema de autenticación robusto, validación de entrada avanzada, manejo de errores comprehensive y arquitectura MVC escalable con base de datos MySQL optimizada.

## 🚀 Características Principales

- ✅ **Interfaz Moderna**: UI desarrollada con Flet, multiplataforma
- 🏗️ **Arquitectura MVC**: Separación clara de responsabilidades
- 🗄️ **Base de Datos MySQL**: Persistencia de datos confiable
- 🔐 **Autenticación Segura**: Sistema de login con validación robusta
- 🛡️ **Validación Avanzada**: Entrada de datos con sanitización
- 🎨 **Diseño Responsive**: Interfaz adaptativa y centrada
- 📱 **Ventana Optimizada**: Tamaño fijo 400x500px, no redimensionable
- ⚠️ **Feedback Visual**: Retroalimentación inmediata para usuario
- 🔄 **Sistema Resiliente**: Importaciones con fallback automático
- 📊 **Gestión Integral**: Presupuestos, gastos e inversiones
- 🔧 **Automatización**: Scripts de BD y configuración automática
- 🚦 **Manejo de Errores**: Try-catch comprehensivo en toda la app

## 📁 Estructura del Proyecto

```
app-presupuesto/
├── src/                    # Código fuente principal
│   ├── views/              # Interfaces de usuario (UI Layer)
│   │   ├── __init__.py
│   │   ├── user_view.py    # Vista de login principal
│   │   ├── dashboard_view.py # Dashboard principal (próximamente)
│   │   └── budget_view.py  # Gestión de presupuestos (próximamente)
│   ├── controllers/        # Lógica de negocio (Business Layer)
│   │   ├── __init__.py
│   │   ├── persona_controller.py    # Control de autenticación
│   │   ├── budget_controller.py     # Control de presupuestos
│   │   └── investment_controller.py # Control de inversiones
│   ├── models/             # Modelos de datos (Data Layer)
│   │   ├── __init__.py
│   │   ├── persona.py      # Modelo de usuario
│   │   ├── presupuesto.py  # Modelo de presupuesto
│   │   ├── categoria.py    # Modelo de categorías
│   │   └── inversion.py    # Modelo de inversiones
│   ├── database/           # Capa de acceso a datos
│   │   ├── __init__.py
│   │   ├── connection.py   # Configuración y pool de conexiones
│   │   ├── queries.py      # Consultas SQL optimizadas
│   │   └── migrations.py   # Scripts de migración
│   └── utils/              # Utilidades y helpers
│       ├── __init__.py
│       ├── security.py     # Funciones de seguridad
│       ├── validators.py   # Validadores de entrada
│       └── helpers.py      # Funciones auxiliares
├── database/               # Scripts y esquemas de BD
│   ├── scripts/
│   │   ├── create/         # Scripts de creación
│   │   │   ├── create_tables.sql
│   │   │   ├── create_triggers.sql
│   │   │   ├── create_views.sql
│   │   │   ├── create_functions.sql
│   │   │   ├── create_investments.sql
│   │   │   └── create_data.sql
│   │   ├── migrations/     # Migraciones de BD
│   │   └── backups/        # Respaldos automatizados
│   └── init_db.bat        # Script de inicialización
├── docs/                   # Documentación completa
│   ├── BASE_DATOS.md      # Documentación de BD
│   ├── API.md             # Documentación de API
│   ├── SECURITY.md        # Consideraciones de seguridad
│   ├── DEPLOYMENT.md      # Guía de despliegue
│   └── TESTING.md         # Guía de testing
├── tests/                  # Suite de pruebas
│   ├── unit/              # Pruebas unitarias
│   ├── integration/       # Pruebas de integración
│   └── fixtures/          # Datos de prueba
├── config/                 # Archivos de configuración
│   ├── development.env    # Config desarrollo
│   ├── production.env     # Config producción
│   └── testing.env        # Config testing
├── logs/                   # Archivos de log
├── requirements.txt        # Dependencias Python
├── requirements-dev.txt    # Dependencias de desarrollo
├── .env.example           # Template variables de entorno
├── .gitignore             # Exclusiones Git
├── setup.py               # Script de instalación
└── README.md              # Este archivo
```

## 🛠️ Instalación y Configuración

### Requisitos del Sistema:
- **Python 3.8+** (Recomendado: 3.10+)
- **MySQL 8.0+** o **MariaDB 10.6+**
- **Git** para control de versiones
- **4GB RAM** mínimo, 8GB recomendado

### 1. Clonar y configurar proyecto:
```bash
git clone https://github.com/usuario/app-presopuesto.git
cd app-presopuesto

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependencias:
```bash
# Dependencias principales
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 3. Configurar base de datos:
```bash
# Copiar template de configuración
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar variables en .env:
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=presupuesto_db
# DB_USER=app_user
# DB_PASSWORD=secure_password
# SECRET_KEY=your-secret-key-here

# Ejecutar scripts de inicialización
database\init_db.bat  # Windows
# bash database/init_db.sh  # Linux/Mac
```

## 🎮 Uso y Ejecución

### Ejecutar aplicación:
```bash
# Desde el directorio raíz del proyecto
python src/views/user_view.py

# O usando el módulo
python -m src.views.user_view
```

### Características de la Interfaz:

#### 🔐 Sistema de Login:
- **Validación en Tiempo Real**: Campos obligatorios con feedback inmediato
- **Sanitización**: Eliminación automática de espacios y caracteres especiales
- **Seguridad**: Hash de contraseñas y validación de sesión
- **Accesibilidad**: Iconos descriptivos y mensajes claros

#### ✅ Validaciones Implementadas:
- ✅ **Campos Obligatorios**: Usuario y contraseña no pueden estar vacíos
- ✅ **Sanitización**: Trim automático y validación de caracteres
- ✅ **Longitud**: Mínimo 3 caracteres para usuario, 6 para contraseña
- ✅ **Caracteres Especiales**: Prevención de inyección SQL
- ✅ **Intentos Fallidos**: Límite de intentos de login
- ✅ **Sesión**: Timeout automático por inactividad

## 👨‍💻 Desarrollo y Arquitectura

### Stack Tecnológico:
- **Frontend**: Flet (Python GUI Framework)
- **Backend**: Python 3.8+ con arquitectura MVC
- **Base de Datos**: MySQL 8.0+ / MariaDB 10.6+
- **ORM**: mysql-connector-python con queries optimizadas
- **Testing**: pytest + coverage
- **Logging**: Python logging module
- **Security**: bcrypt para hashing, validación de entrada

### Patrones de Diseño Implementados:
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Views     │ -> │ Controllers  │ -> │   Models    │
│ (Flet UI)   │    │ (Business)   │    │ (Data)      │
└─────────────┘    └──────────────┘    └─────────────┘
       │                    │                   │
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Validators │    │   Security   │    │  Database   │
│ (Input Val) │    │ (Auth/Hash)  │    │  (MySQL)    │
└─────────────┘    └──────────────┘    └─────────────┘
```

### 🔧 Mejoras Técnicas Implementadas:
- **Connection Pooling**: Pool de conexiones a BD para mejor rendimiento
- **Lazy Loading**: Carga bajo demanda de módulos pesados
- **Error Handling**: Manejo granular de excepciones por tipo
- **Logging**: Sistema de logs rotativo con niveles configurables
- **Caching**: Cache en memoria para consultas frecuentes
- **Validation**: Validadores reutilizables con decoradores

## 🔒 Consideraciones de Seguridad

### Implementadas:
- ✅ **Hash de Contraseñas**: bcrypt con salt automático
- ✅ **Validación de Entrada**: Sanitización contra inyección SQL
- ✅ **Variables de Entorno**: Credenciales fuera del código
- ✅ **Timeout de Sesión**: Cierre automático por inactividad
- ✅ **Logs de Seguridad**: Registro de intentos de acceso

### Próximas:
- 🔜 **2FA**: Autenticación de dos factores
- 🔜 **JWT Tokens**: Tokens de sesión seguros
- 🔜 **Rate Limiting**: Límite de peticiones por IP
- 🔜 **Encryption**: Cifrado de datos sensibles en BD

## 📚 Documentación Completa

- 📖 [Documentación de Base de Datos](docs/BASE_DATOS.md)
- 🔌 [API y Endpoints](docs/API.md)
- 🛡️ [Guía de Seguridad](docs/SECURITY.md)
- 🚀 [Guía de Despliegue](docs/DEPLOYMENT.md)
- 🧪 [Guía de Testing](docs/TESTING.md)
- 📋 [Roadmap del Proyecto](docs/ROADMAP.md)

## 🐛 Solución de Problemas Avanzada

### Errores de Importación:
```bash
# Verificar estructura del proyecto
python -c "import sys; print('\n'.join(sys.path))"

# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Verificar versión de Python
python --version  # Debe ser 3.8+
```

### Errores de Base de Datos:
```bash
# Verificar estado de MySQL
mysql -u root -p -e "SHOW DATABASES;"

# Probar conexión desde Python
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(host='localhost', user='root', password='')
    print('✅ Conexión exitosa')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Recrear base de datos
database\scripts\reset_db.bat
```

### Errores de Autenticación:
```bash
# Verificar configuración
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'DB_HOST: {os.getenv(\"DB_HOST\")})
print(f'DB_NAME: {os.getenv(\"DB_NAME\")})
"

# Probar función de autenticación
python -c "
from src.controllers.persona_controller import autenticar_usuario
result = autenticar_usuario('test', 'test123')
print(f'Resultado: {result}')
"
```

## 🧪 Testing y Calidad

### Ejecutar Suite de Pruebas:
```bash
# Pruebas unitarias
python -m pytest tests/unit/ -v

# Pruebas de integración
python -m pytest tests/integration/ -v

# Cobertura de código
python -m pytest tests/ --cov=src/ --cov-report=html

# Linting y formateo
flake8 src/
black src/
isort src/
```

### Métricas de Calidad:
- **Cobertura de Código**: >90%
- **Complejidad Ciclomática**: <10 por función
- **Líneas por Función**: <50 líneas
- **Documentación**: Docstrings en todas las funciones públicas

## 📄 Versión y Changelog

**0.5.0** - Mejoras de seguridad, arquitectura y documentación completa

### Changelog Detallado:
- **0.5.0**: 
  - ✅ Implementación de seguridad avanzada
  - ✅ Sistema de logging completo
  - ✅ Documentación técnica exhaustiva
  - ✅ Suite de testing ampliada
  - ✅ Optimizaciones de rendimiento
- **0.4.0**: Integración MySQL, documentación básica
- **0.3.0**: Manejo de errores y validación
- **0.2.0**: Interfaz mejorada con Flet
- **0.1.0**: Versión inicial con login básico

## 🚀 Próximas Versiones

### v0.6.0 - Dashboard y Gestión (Q1 2024):
- [ ] Dashboard principal con métricas
- [ ] CRUD completo de presupuestos
- [ ] Gestión de categorías de gastos
- [ ] Gráficos y reportes básicos

### v0.7.0 - Análisis y Reportes (Q2 2024):
- [ ] Reportes avanzados con gráficos
- [ ] Exportación a PDF/Excel
- [ ] Análisis predictivo básico
- [ ] Notificaciones y alertas

### v1.0.0 - Versión Estable (Q3 2024):
- [ ] API REST completa
- [ ] Aplicación móvil companion
- [ ] Sincronización en la nube
- [ ] Múltiples monedas y idiomas

---

<div align="center">
  <p>Desarrollado con ❤️ por Esteban Fabián Patiño Montealegre</p>
  <p>🌟 Si te gusta este proyecto, no olvides darle una estrella</p>
</div>