# App Presupuesto 💰

Aplicación de gestión de presupuestos desarrollada con Flet y arquitectura MVC con interfaz moderna y funcionalidades avanzadas de análisis financiero.

## 📋 Descripción

Sistema completo de gestión financiera personal con interfaz gráfica moderna construida con Python y Flet. Incluye dashboard de resumen financiero con gráficos interactivos, sistema de navegación lateral, tablas de datos profesionales y arquitectura MVC escalable preparada para integración con base de datos MySQL.

## 🚀 Características Principales

- ✅ **Interfaz Moderna**: UI profesional desarrollada con Flet, diseño responsive
- 🏗️ **Arquitectura MVC**: Separación clara de responsabilidades y código documentado
- 🗄️ **Base de Datos MySQL**: Estructura preparada para persistencia de datos
- 📊 **Dashboard Financiero**: Vista de resumen con métricas y análisis visual
- 🎨 **Diseño Professional**: Interfaz con sidebar navegable y layout de dos columnas
- 📱 **Responsive Design**: Ventana optimizada 1400x900px con redimensionamiento
- 💳 **Gestión Completa**: Cuentas bancarias, tarjetas de crédito, préstamos e inversiones
- 📈 **Análisis Visual**: Gráficos de ingresos vs gastos y tendencias financieras
- 🔐 **Sistema de Login**: Autenticación con validación robusta (preparado)
- 📋 **Tablas Interactivas**: Visualización de datos con filtros y acciones
- 🎯 **Navegación Intuitiva**: Menú lateral organizado por categorías
- 🎨 **Tema Moderno**: Paleta de colores profesional con tipografía Inter

## 📁 Estructura del Proyecto Actualizada

```
app-presupuesto/
├── src/                    # Código fuente principal
│   ├── views/              # Interfaces de usuario (UI Layer)
│   │   ├── __init__.py
│   │   ├── resumen.py      # 🆕 Vista principal de resumen financiero
│   │   ├── user_view.py    # Vista de login (base implementada)
│   │   ├── dashboard_view.py # Dashboard adicional (próximamente)
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
- **MySQL 8.0+** o **MariaDB 10.6+** (opcional para desarrollo inicial)
- **Git** para control de versiones
- **4GB RAM** mínimo, 8GB recomendado

### 1. Clonar y configurar proyecto:
```bash
git clone https://github.com/usuario/app-presupuesto.git
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
pip install flet
pip install plotly  # Opcional para gráficos avanzados

# Dependencias completas (cuando esté disponible)
# pip install -r requirements.txt
```

### 3. Configuración inicial:
```bash
# La aplicación funciona sin base de datos inicialmente
# Los datos son simulados para demostración

# Para configurar BD MySQL (opcional):
# copy .env.example .env
# Editar variables de entorno según necesidad
```

## 🎮 Uso y Ejecución

### Ejecutar aplicación principal:
```bash
# Vista de resumen financiero (principal)
python src/views/resumen.py

# Vista de login (base)
python src/views/user_view.py
```

### 🆕 Características de la Vista de Resumen:

#### 🏠 Dashboard Principal:
- **Sidebar Navegable**: Menú lateral organizado por secciones con badges
- **Breadcrumbs**: Navegación de ruta actual
- **Tarjetas de Resumen**: Métricas principales con indicadores de cambio
- **Layout Responsive**: Dos columnas adaptativas

#### 📊 Funcionalidades Implementadas:
- ✅ **Resumen de Cuentas**: Bancarias, tarjetas de crédito, préstamos
- ✅ **Análisis Visual**: Gráfico de ingresos vs gastos (últimos 30 días)
- ✅ **Tablas Interactivas**: Con headers personalizados y acciones
- ✅ **Indicadores de Progreso**: Barras de progreso para deudas
- ✅ **Próximas Transacciones**: Vista de transacciones pendientes
- ✅ **Categorías Top**: Análisis de gastos por categoría
- ✅ **Deuda Programada**: Gestión de pagos automáticos

#### 🎨 Características de Diseño:
- **Paleta de Colores**: Material Design con azul primario (#2196F3)
- **Tipografía**: Google Fonts Inter para mejor legibilidad
- **Iconografía**: Material Design Icons consistentes
- **Shadows y Borders**: Efectos sutiles para profundidad visual
- **Estados Hover**: Retroalimentación visual en interacciones

## 👨‍💻 Desarrollo y Arquitectura

### Stack Tecnológico Actual:
- **Frontend**: Flet (Python GUI Framework) con componentes profesionales
- **Visualización**: Gráficos con fallback visual (Plotly opcional)
- **Arquitectura**: MVC con documentación completa
- **Datos**: Simulación realista para desarrollo y demo
- **Testing**: Estructura preparada para pytest

### 🆕 Componentes Principales:

#### LeftSidebarMenu:
```python
class LeftSidebarMenu:
    """Gestiona el menú lateral con navegación y perfil de usuario"""
    - create_menu_item()     # Items individuales con badges
    - create_user_profile()  # Perfil con avatar y opciones
    - create_sidebar()       # Menú completo organizado por secciones
```

#### ResumenView:
```python
class ResumenView:
    """Vista principal del dashboard financiero"""
    - create_header_bar()           # Breadcrumbs y acciones
    - create_summary_cards()        # Tarjetas de métricas
    - create_data_table()           # Tablas profesionales
    - create_income_vs_expense_chart() # Análisis visual
    - create_main_content()         # Layout principal
```

### Patrones de Diseño Implementados:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Views         │    │   Controllers    │    │    Models       │
│ LeftSidebarMenu │ -> │ (Preparados)     │ -> │ (Preparados)    │
│ ResumenView     │    │ Business Logic   │    │ Data Models     │
│ UserView        │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Components    │    │    Utils         │    │   Database      │
│ DataTable       │    │ Security         │    │ (MySQL Ready)   │
│ SummaryCards    │    │ Validators       │    │ Connection Pool │
│ Chart (Visual)  │    │ Helpers          │    │ Migrations      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Estado Actual del Proyecto

### ✅ Completado (v0.6.0):
- **Vista de Resumen**: Dashboard completo con navegación
- **Componentes UI**: Tablas, tarjetas, gráficos y menús
- **Arquitectura**: Estructura MVC documentada
- **Diseño**: Interfaz profesional y responsive
- **Datos Demo**: Simulación realista para desarrollo

### 🔄 En Desarrollo:
- **Integración BD**: Conexión con datos reales
- **Autenticación**: Sistema de login funcional
- **CRUD Operations**: Gestión completa de datos

### 📋 Próximas Funcionalidades:

#### v0.7.0 - Integración de Datos (Q1 2024):
- [ ] Conexión MySQL funcional
- [ ] CRUD completo de transacciones
- [ ] Sistema de autenticación integrado
- [ ] Persistencia de datos real

#### v0.8.0 - Funcionalidades Avanzadas (Q2 2024):
- [ ] Gráficos interactivos con Plotly
- [ ] Filtros y búsqueda en tablas
- [ ] Exportación de reportes
- [ ] Notificaciones y alertas

#### v1.0.0 - Versión Estable (Q3 2024):
- [ ] Sistema completo de presupuestos
- [ ] Análisis predictivo
- [ ] API REST
- [ ] Aplicación móvil

## 🧩 Funcionalidades Destacadas

### 📊 Dashboard de Resumen:
- **Métricas Principales**: Cuentas bancarias, préstamos, tarjetas, fondos
- **Indicadores Visuales**: Porcentajes de cambio con colores semánticos
- **Gráfico de Flujo**: Análisis de ingresos vs gastos con tendencias
- **Tablas Organizadas**: Datos estructurados por tipo de cuenta

### 🎯 Gestión de Transacciones:
- **Próximas Transacciones**: Vista de pagos pendientes
- **Categorías Top**: Análisis de gastos más frecuentes
- **Deuda Programada**: Control de pagos automáticos
- **Progreso Visual**: Barras de progreso para objetivos

### 🔍 Análisis y Reportes:
- **Tendencias**: Identificación de patrones de gasto
- **Balance Diario**: Cálculo automático de flujo de efectivo
- **Estadísticas**: Promedios y totales calculados
- **Alertas Visuales**: Códigos de color para estados financieros

## 📚 Documentación Técnica

### Guías de Desarrollo:
- 📖 **Código Documentado**: Docstrings completos con type hints
- 🏗️ **Arquitectura**: Separación clara de responsabilidades
- 🎨 **Design System**: Paleta de colores y componentes reutilizables
- 🔧 **Extensibilidad**: Estructura preparada para nuevas funcionalidades

### Estándares de Código:
- **Type Hints**: Tipado completo para mejor IDE support
- **Docstrings**: Documentación detallada de clases y métodos
- **Naming Conventions**: Nomenclatura clara y consistente
- **Error Handling**: Manejo de excepciones apropiado

## 🐛 Solución de Problemas

### Errores Comunes:

#### Error de Importación de Flet:
```bash
pip install flet>=0.18.0
python -c "import flet; print('✅ Flet instalado correctamente')"
```

#### Error de Plotly (Opcional):
```bash
# Si quieres gráficos avanzados
pip install plotly>=5.0.0

# La aplicación funciona sin Plotly con visualización alternativa
```

#### Problema de Ventana:
```bash
# Verificar resolución de pantalla compatible (mínimo 1024x768)
# La aplicación ajusta automáticamente el tamaño

# Si hay problemas de rendering:
python src/views/resumen.py --no-web
```

## 💡 Cómo Contribuir

### Para Desarrolladores:
1. **Fork** el repositorio
2. **Crear branch**: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollar** siguiendo los estándares de código
4. **Documentar** con docstrings y comentarios
5. **Probar** la funcionalidad
6. **Pull Request** con descripción detallada

### Áreas de Contribución:
- 🎨 **UI/UX**: Mejoras de diseño y usabilidad
- 🔧 **Backend**: Integración de base de datos
- 📊 **Analytics**: Nuevos tipos de análisis
- 🔐 **Security**: Mejoras de seguridad
- 📱 **Mobile**: Versión responsive/móvil
- 🌐 **i18n**: Internacionalización

## 📄 Changelog

### v0.6.0 (Actual) - Dashboard Profesional:
- ✅ Vista de resumen financiero completa
- ✅ Navegación lateral con categorías organizadas
- ✅ Tablas interactivas con datos simulados
- ✅ Gráficos visuales con fallback
- ✅ Diseño responsive y profesional
- ✅ Documentación técnica completa

### Versiones Anteriores:
- **v0.5.0**: Mejoras de seguridad y arquitectura
- **v0.4.0**: Integración MySQL preparada
- **v0.3.0**: Manejo de errores y validación
- **v0.2.0**: Interfaz mejorada con Flet
- **v0.1.0**: Versión inicial con login básico

---

<div align="center">
  <p>🚀 <strong>Desarrollado con ❤️ usando Python + Flet</strong></p>
  <p>📧 Contacto: estebanfabianp@gmail.com</p>
  <p>🌟 Si te gusta este proyecto, no olvides darle una estrella</p>
  
  <br>
  
  **Estado del Proyecto**: 🟢 En Desarrollo Activo  
  **Próxima Release**: v0.7.0 - Integración de Datos (Q1 2024)
</div>