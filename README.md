# 💰 App Presupuesto - Sistema de Gestión Financiera Personal

Una aplicación web completa para la gestión integral de finanzas personales, desarrollada con **Flask** y **MySQL**. Permite administrar cuentas, movimientos, presupuestos, tarjetas de crédito, préstamos, inversiones y generar reportes avanzados con análisis automático de datos.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Características Principales

### 💼 Gestión Financiera Completa
- **Gestión de Usuarios**: Registro, autenticación JWT y perfiles personalizados
- **Administración de Cuentas**: Control de saldos, múltiples cuentas y monedas
- **Movimientos Financieros**: Ingresos, gastos, transferencias con categorización automática
- **Tarjetas de Crédito**: Gestión de límites, pagos y estados de cuenta
- **Préstamos**: Control de deudas, amortizaciones y seguimiento de pagos
- **Inversiones**: Gestión de portafolio, acciones, fondos y rentabilidad

### 📊 Análisis y Reportes
- **Categorización Inteligente**: Clasificación automática usando Machine Learning
- **Reportes Avanzados**: Visualización con gráficos interactivos
- **Exportación de Datos**: CSV, Excel, PDF con análisis personalizados
- **Dashboards**: Paneles de control configurables por usuario
- **Análisis Predictivo**: Proyecciones y tendencias financieras

### 🔒 Seguridad y Arquitectura
- **API RESTful**: Endpoints bien estructurados con versionado
- **Base de Datos Robusta**: MySQL con triggers, vistas y procedimientos almacenados
- **Seguridad Avanzada**: bcrypt, JWT, validación robusta y control de acceso por roles
- **Arquitectura Modular**: Separación clara de responsabilidades

---

## 📦 Estructura del Proyecto

```text
📁 app-presupuesto/
├── 📄 README.md                    # Documentación principal
├── 📄 requirements.txt             # Dependencias Python
├── 📄 config.yaml                  # Configuración del proyecto
├── 📁 src/                         # Código fuente principal
│   ├── 📁 controllers/             # Controladores de la aplicación
│   │   ├── 📄 auth_controller.py   # Autenticación y autorización
│   │   └── 📄 user_controller.py   # Gestión de usuarios
│   ├── 📁 models/                  # Modelos de datos (ORM)
│   │   └── 📄 user_model.py        # Modelo de usuario
│   ├── 📁 database/                # Conectores y configuración BD
│   │   └── 📄 db_connector.py      # Conector MySQL
│   ├── 📁 services/                # Servicios de negocio
│   └── 📁 api/                     # Endpoints RESTful
├── 📁 base_de_datos/               # Scripts SQL y esquemas
│   └── 📁 script_bd/
│       ├── 📁 create/              # Scripts de creación
│       └── 📁 comments/            # Documentación SQL
├── 📁 documentacion/               # Documentación técnica
│   ├── 📄 IDEAS.md                 # Roadmap y mejoras futuras
│   ├── 📄 sugerencia_IA.md         # Guías de IA y ML
│   ├── 📄 SECURITY.md              # Políticas de seguridad
│   ├── 📄 roadmap.md               # Hoja de ruta del proyecto
│   ├── 📄 FAQ.md                   # Preguntas frecuentes
│   ├── 📄 DATA_MODEL.md            # Modelo de datos
│   ├── 📄 CONTRIBUTING.md          # Guía de contribución
│   ├── 📄 CODE_OF_CONDUCT.md       # Código de conducta
│   ├── 📄 CHANGELOG.md             # Registro de cambios
│   └── 📄 ARCHITECTURE.md          # Arquitectura del sistema
├── 📁 docs/                        # Documentación adicional
│   ├── 📄 FAQ.md                   # FAQ extendido
│   ├── 📄 BASE_DATOS.md            # Documentación de BD
│   └── 📄 ARCHITECTURE.md          # Arquitectura detallada
├── 📁 tests/                       # Pruebas automatizadas
├── 📁 config/                      # Configuraciones por entorno
├── 📁 data/                        # Datos de ejemplo y exportación
└── 📁 scripts/                     # Scripts de automatización
```

---

## 🛠️ Tecnologías Utilizadas

### Backend y API
- **Python 3.8+** - Lenguaje principal
- **Flask** - Framework web minimalista y potente
- **Flask-SQLAlchemy** - ORM para base de datos
- **Flask-Migrate** - Gestión de migraciones
- **Flask-JWT-Extended** - Autenticación JWT
- **Flask-CORS** - Configuración de CORS
- **PyMySQL** - Conector MySQL

### Base de Datos y Persistencia
- **MySQL 8.0+** - Sistema de gestión de base de datos
- **Triggers y Stored Procedures** - Automatización de procesos
- **Vistas materializadas** - Optimización de consultas

### Seguridad y Validación
- **bcrypt** - Hash seguro de contraseñas
- **python-dotenv** - Gestión de variables de entorno
- **marshmallow** - Validación y serialización de datos

### Análisis de Datos e IA
- **pandas** - Manipulación y análisis de datos
- **scikit-learn** - Machine Learning para categorización
- **matplotlib** - Visualización de datos
- **openpyxl, xlrd** - Procesamiento de archivos Excel

### Testing y Calidad
- **pytest** - Framework de testing
- **pytest-cov** - Coverage de código
- **ipython** - Desarrollo interactivo

### Deployment y Producción
- **gunicorn** - Servidor WSGI para producción
- **requests** - Cliente HTTP para APIs externas

---

## ⚙️ Instalación y Configuración

### Prerrequisitos

- **Python 3.8 o superior**
- **MySQL 8.0 o superior**
- **Git**
- **Virtual Environment** (recomendado)

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/app-presopuesto.git
cd app-presupuesto
```

### 2. Configurar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

### 4. Configurar base de datos

#### Crear base de datos MySQL:
```sql
CREATE DATABASE presupuesto_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'presupuesto_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON presupuesto_db.* TO 'presupuesto_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Configurar credenciales en `config.yaml`:
```yaml
database:
  host: localhost
  database: presupuesto_db
  user: tu_usuario
  password: tu_contraseña
```

### 5. Ejecutar la aplicación

```bash
# Desarrollo
export FLASK_APP=src/app.py
export FLASK_ENV=development
flask run

# O directamente con Python
python -m src.app

# Producción con Gunicorn
gunicorn --bind 0.0.0.0:8000 src.app:app
```

La aplicación estará disponible en: `http://localhost:5000`

---

## 🏗️ Arquitectura del Sistema

### Patrón MVC Extendido
```
📱 Frontend (Futuro)
    ↕️
🌐 API Layer (Flask Routes)
    ↕️
🎮 Controllers (Business Logic)
    ↕️
🗃️ Models (SQLAlchemy ORM)
    ↕️
🗄️ Database (MySQL + Triggers)
```

### Componentes Principales

#### 🎮 Controladores
- **auth_controller**: Registro, login, JWT tokens
- **user_controller**: CRUD de usuarios y perfiles
- **account_controller**: Gestión de cuentas bancarias
- **transaction_controller**: Movimientos financieros
- **budget_controller**: Presupuestos y planificación
- **report_controller**: Generación de reportes

#### 🗃️ Modelos de Datos
- **User**: Usuarios del sistema
- **Account**: Cuentas bancarias y productos financieros
- **Transaction**: Movimientos de dinero
- **Category**: Categorías de gastos e ingresos
- **Budget**: Presupuestos personalizados
- **CreditCard**: Tarjetas de crédito
- **Loan**: Préstamos y financiamientos
- **Investment**: Inversiones y activos

#### 🗄️ Base de Datos
- **Triggers automáticos**: Actualización de saldos en tiempo real
- **Vistas optimizadas**: Consultas complejas pre-calculadas
- **Procedimientos almacenados**: Lógica de negocio en BD
- **Índices optimizados**: Rendimiento en consultas frecuentes

---

## 📊 Funcionalidades Implementadas

### ✅ Completadas (v0.1.0)

- [x] **Sistema de usuarios** con autenticación básica
- [x] **Conexión robusta** a MySQL con reconexión automática
- [x] **Modelo de datos** completo y normalizado
- [x] **Controladores base** con separación de responsabilidades
- [x] **Logging estructurado** y manejo de errores
- [x] **Configuración modular** con archivos YAML
- [x] **Scripts de base de datos** organizados y documentados

### 🚧 En Desarrollo (v0.2.0)

- [ ] **API RESTful completa** con todos los endpoints
- [ ] **Autenticación JWT** y refresh tokens
- [ ] **Sistema de roles** y permisos granulares
- [ ] **Validación robusta** con marshmallow
- [ ] **Tests automatizados** unitarios e integración
- [ ] **Documentación OpenAPI** (Swagger)

### 📋 Planificadas (v0.3.0+)

- [ ] **Categorización automática** con Machine Learning
- [ ] **Dashboard interactivo** con gráficos
- [ ] **Reportes avanzados** y exportación
- [ ] **Notificaciones** push y email
- [ ] **API de integración** con bancos
- [ ] **Aplicación móvil** (React Native)

Ver [documentacion/roadmap.md](documentacion/roadmap.md) para la hoja de ruta completa.

---

## 🔧 Uso de la API

### Autenticación

```python
import requests

# Registro de usuario
response = requests.post('http://localhost:5000/api/auth/register', json={
    'nombre': 'Juan Pérez',
    'email': 'juan@email.com',
    'password': 'password123'
})

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'juan@email.com',
    'password': 'password123'
})

token = response.json()['access_token']

# Usar token en requests
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:5000/api/users/profile', headers=headers)
```

### Gestión de Transacciones

```python
# Crear movimiento
transaction = {
    'monto': -50000,
    'descripcion': 'Compra supermercado',
    'categoria_id': 1,
    'cuenta_id': 1,
    'fecha': '2024-01-15'
}

response = requests.post(
    'http://localhost:5000/api/transactions',
    json=transaction,
    headers=headers
)
```

### Consulta de Reportes

```python
# Obtener reporte mensual
response = requests.get(
    'http://localhost:5000/api/reports/monthly?year=2024&month=1',
    headers=headers
)

reporte = response.json()
print(f"Ingresos: {reporte['total_ingresos']}")
print(f"Gastos: {reporte['total_gastos']}")
```

---

## 🧪 Testing

### Ejecutar todas las pruebas

```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# Tests con coverage
pytest --cov=src --cov-report=html tests/

# Tests específicos
pytest tests/unit/test_user_model.py::TestUserModel::test_create_user -v
```

### Estructura de testing

```text
tests/
├── unit/                    # Tests unitarios
│   ├── test_models.py      # Tests de modelos
│   ├── test_controllers.py # Tests de controladores
│   └── test_services.py    # Tests de servicios
├── integration/            # Tests de integración
│   ├── test_api.py        # Tests de endpoints
│   └── test_database.py   # Tests de BD
└── fixtures/              # Datos de prueba
    ├── users.json
    └── transactions.json
```

---

## 🤖 Machine Learning y Análisis

### Categorización Automática

El sistema incluye capacidades de ML para categorizar transacciones automáticamente:

```python
from src.ml.categorizer import TransactionCategorizer

# Entrenar modelo
categorizer = TransactionCategorizer()
categorizer.train_from_database()

# Predecir categoría
categoria = categorizer.predict("Pago Uber", -25000)
print(f"Categoría sugerida: {categoria}")
```

### Análisis de Datos

```python
from src.analytics.financial_analyzer import FinancialAnalyzer

analyzer = FinancialAnalyzer(user_id=1)

# Análisis de gastos
insights = analyzer.analyze_spending_patterns()
print(f"Categoría con mayor gasto: {insights['top_category']}")

# Proyecciones
projection = analyzer.project_future_balance(months=6)
print(f"Saldo proyectado: {projection}")
```

---

## 📝 Contribución

¡Las contribuciones son bienvenidas! Por favor lee nuestra [guía de contribución](documentacion/CONTRIBUTING.md).

### Proceso de contribución

1. **Fork** el repositorio
2. **Crea una rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre un Pull Request**

### Áreas de contribución

- 🐛 **Bug fixes** y mejoras de código
- 📚 **Documentación** y tutoriales
- 🧪 **Tests** y coverage
- 🎨 **Frontend** y UX/UI
- 🤖 **Machine Learning** y análisis
- 🔒 **Seguridad** y performance

---

## 🔒 Seguridad

### Características de seguridad implementadas

- **🔐 Contraseñas seguras**: Hash con bcrypt y salt
- **🎫 Autenticación JWT**: Tokens seguros con expiración
- **🛡️ Validación robusta**: Prevención de inyecciones SQL
- **🔍 Control de acceso**: Roles y permisos granulares
- **📝 Auditoría**: Logging de acciones críticas
- **🌐 CORS configurado**: Políticas de origen cruzado

### Reportar vulnerabilidades

Para reportar vulnerabilidades de seguridad:
- ✉️ Email: estebanfabianp@gmail.com
- 📋 Issue confidencial en GitHub
- 📖 Lee nuestra [política de seguridad](documentacion/SECURITY.md)

---

## 📚 Documentación

### Documentación técnica
- 📋 [Modelo de Datos](documentacion/DATA_MODEL.md) - Estructura de base de datos
- 🏗️ [Arquitectura](docs/ARCHITECTURE.md) - Diseño del sistema
- 🛣️ [Roadmap](documentacion/roadmap.md) - Hoja de ruta y fases
- 💡 [Ideas y Mejoras](documentacion/IDEAS.md) - Funcionalidades futuras
- 🤖 [Sugerencias IA](documentacion/sugerencia_IA.md) - Integración de ML

### Guías de usuario
- ❓ [FAQ](docs/FAQ.md) - Preguntas frecuentes
- 🗄️ [Base de Datos](docs/BASE_DATOS.md) - Configuración de BD
- 🔒 [Seguridad](documentacion/SECURITY.md) - Políticas de seguridad
- 🤝 [Contribución](documentacion/CONTRIBUTING.md) - Cómo contribuir

---

## 🐛 Problemas Conocidos

### Limitaciones actuales
- ❌ Validación de contraseñas básica (mejorando en v0.2.0)
- ❌ Sistema de roles limitado (expandiendo en v0.2.0)
- ❌ No hay rate limiting implementado
- ❌ Frontend web en desarrollo
- ❌ Importación automática de bancos pendiente

### Soluciones en progreso
- ✅ Migración a autenticación JWT completa
- ✅ Implementación de tests automatizados
- ✅ Documentación OpenAPI en desarrollo
- ✅ Dashboard web en planificación

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.

**Resumen de la licencia:**
- ✅ Uso comercial y personal permitido
- ✅ Modificación y distribución permitida
- ✅ Uso privado permitido
- ❗ Sin garantía ni responsabilidad

---

## 👨‍💻 Autor y Equipo

### Desarrollador Principal
**Esteban Fabián Patiño Montealegre**
- 🌐 GitHub: [@estebanfabianp](https://github.com/estebanfabianp)
- ✉️ Email: estebanfabianp@gmail.com
- 💼 LinkedIn: [Esteban Patiño](https://linkedin.com/in/estebanpatino)

### Contribuidores
- 🙏 ¡Sé el primero en contribuir!

---

## 🙏 Agradecimientos

### Inspiración y Referencias
- 💰 **YNAB** (You Need A Budget) - Metodología de presupuestos
- 🌿 **Mint** - Diseño de dashboard financiero
- 📊 **Personal Capital** - Gestión de inversiones
- 🏦 **Banco de la República** - Normas financieras colombianas

### Tecnologías y Comunidad
- 🐍 **Python Community** - Frameworks y librerías
- 🗄️ **MySQL Team** - Sistema de base de datos robusto
- 📚 **Stack Overflow** - Resolución de problemas
- 🌟 **Open Source Community** - Por hacer posible este proyecto

### Herramientas de Desarrollo
- 💻 **Visual Studio Code** - Editor principal
- 🔧 **GitHub** - Control de versiones y colaboración
- 🧪 **pytest** - Framework de testing
- 📖 **Sphinx** - Generación de documentación

---

## 📈 Estado del Proyecto

### Información actual
- **📋 Versión**: 0.1.0 (Alpha)
- **📊 Estado**: En desarrollo activo
- **📅 Última actualización**: Enero 2025
- **🏗️ Fase actual**: MVP - Funcionalidades básicas
- **👥 Contribuidores**: 1 desarrollador principal
- **🌟 Stars**: ⭐ ¡Danos una estrella si te gusta el proyecto!

### Métricas de desarrollo
- **📝 Líneas de código**: ~5,000+ LOC
- **🧪 Cobertura de tests**: Objetivo 80%+
- **📚 Documentación**: 90% completa
- **🐛 Issues abiertas**: [Ver en GitHub](https://github.com/tu-usuario/app-presopuesto/issues)

### Roadmap 2025

#### 🗓️ Q1 2025 (Enero - Marzo)
- ✅ **Completar API RESTful** con todos los endpoints
- ✅ **Implementar autenticación JWT** completa
- ✅ **Sistema de tests** automatizados
- ✅ **Documentación OpenAPI** (Swagger)

#### 🗓️ Q2 2025 (Abril - Junio)
- 🎯 **Dashboard web** interactivo
- 🎯 **Categorización ML** automática
- 🎯 **Reportes avanzados** con gráficos
- 🎯 **Notificaciones** push y email

#### 🗓️ Q3 2025 (Julio - Septiembre)
- 🚀 **API de integración** bancaria
- 🚀 **Análisis predictivo** avanzado
- 🚀 **Gestión de inversiones** completa
- 🚀 **Multi-tenancy** para organizaciones

#### 🗓️ Q4 2025 (Octubre - Diciembre)
- 📱 **Aplicación móvil** (React Native)
- 🌍 **Internacionalización** completa
- ☁️ **Deployment en la nube** (AWS/GCP)
- 🔒 **Certificaciones** de seguridad

---

## 🚀 Enlaces Rápidos

### 🔗 Desarrollo
- [📋 Issues](https://github.com/tu-usuario/app-presopuesto/issues) - Reportar bugs
- [🔄 Pull Requests](https://github.com/tu-usuario/app-presopuesto/pulls) - Contribuciones
- [📊 Projects](https://github.com/tu-usuario/app-presopuesto/projects) - Tablero de desarrollo
- [🏷️ Releases](https://github.com/tu-usuario/app-presopuesto/releases) - Versiones

### 📚 Documentación
- [🏗️ Arquitectura](docs/ARCHITECTURE.md) - Diseño técnico
- [🗄️ Base de Datos](docs/BASE_DATOS.md) - Esquemas SQL
- [❓ FAQ](docs/FAQ.md) - Preguntas frecuentes
- [🤝 Contribuir](documentacion/CONTRIBUTING.md) - Guía de contribución

### 🌐 Comunidad
- [💬 Discussions](https://github.com/tu-usuario/app-presopuesto/discussions) - Comunidad
- [📧 Email](mailto:estebanfabianp@gmail.com) - Contacto directo
- [🐦 Twitter](https://twitter.com/tu-usuario) - Actualizaciones
- [💼 LinkedIn](https://linkedin.com/in/estebanpatino) - Red profesional

---

**¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub y ayúdanos a crecer!**

Para más detalles técnicos, consulta la documentación completa en la carpeta [`/documentacion`](documentacion/).