# Arquitectura del Sistema: App Presupuesto con Flet

El sistema utiliza una arquitectura MVC moderna con interfaz gráfica Flet, base de datos MySQL/MariaDB y está preparado para integración de IA y analítica avanzada.

---

## 🏗️ Arquitectura General

### Patrón MVC Implementado

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLET APPLICATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   VIEWS     │ -> │ CONTROLLERS  │ -> │     MODELS      │    │
│  │ (Flet UI)   │    │ (Business)   │    │ (Data Layer)    │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│         │                    │                     │           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ VALIDATORS  │    │   SECURITY   │    │    DATABASE     │    │
│  │ (Input Val) │    │ (Auth/Hash)  │    │ (MySQL Pool)    │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. Capa de Presentación (Views)
**Ubicación:** `/src/views/`

- **Framework:** Flet (Python GUI Framework)
- **Características:**
  - Interfaz gráfica nativa multiplataforma
  - Ventana fija de 400x500px optimizada para UX
  - Componentes reactivos con feedback inmediato
  - Validación en tiempo real

**Estructura actual:**
```
src/views/
├── __init__.py
├── user_view.py          # Vista de login principal ✅
├── dashboard_view.py     # Dashboard principal (v0.6.0)
├── budget_view.py        # Gestión de presupuestos (v0.6.0)
├── transaction_view.py   # Gestión de transacciones (v0.6.0)
└── settings_view.py      # Configuración de usuario (v0.7.0)
```

### 2. Capa de Lógica de Negocio (Controllers)
**Ubicación:** `/src/controllers/`

- **Responsabilidades:**
  - Procesamiento de entrada de usuario
  - Validación de reglas de negocio
  - Coordinación entre vistas y modelos
  - Manejo de errores y excepciones

**Estructura actual:**
```
src/controllers/
├── __init__.py
├── persona_controller.py       # Autenticación ✅
├── budget_controller.py        # Control de presupuestos (v0.6.0)
├── transaction_controller.py   # Control de transacciones (v0.6.0)
├── category_controller.py      # Control de categorías (v0.6.0)
└── investment_controller.py    # Control de inversiones (v0.9.0)
```

### 3. Capa de Datos (Models)
**Ubicación:** `/src/models/`

- **Responsabilidades:**
  - Definición de entidades de datos
  - Mapeo objeto-relacional simplificado
  - Validación de tipos de datos
  - Serialización/deserialización

**Estructura planificada:**
```
src/models/
├── __init__.py
├── persona.py          # Modelo de usuario ✅
├── presupuesto.py      # Modelo de presupuesto
├── transaccion.py      # Modelo de transacciones
├── cuenta.py           # Modelo de cuentas bancarias
├── categoria.py        # Modelo de categorías
└── inversion.py        # Modelo de inversiones
```

### 4. Capa de Acceso a Datos (Database)
**Ubicación:** `/src/database/`

- **Tecnología:** MySQL 8.0+ con mysql-connector-python
- **Características:**
  - Pool de conexiones optimizado
  - Consultas preparadas para seguridad
  - Transacciones ACID
  - Logging de operaciones

**Estructura:**
```
src/database/
├── __init__.py
├── connection.py       # Pool de conexiones ✅
├── queries.py          # Consultas SQL optimizadas
├── migrations.py       # Sistema de migraciones
└── backup.py           # Respaldos automáticos
```

---

## 🔧 Capa de Utilidades

### Security Layer
**Ubicación:** `/src/utils/security.py`

```python
# Funcionalidades implementadas:
- Hash bcrypt para contraseñas ✅
- Validación de entrada contra SQL injection ✅
- Sanitización automática de datos ✅
- Logging de eventos de seguridad ✅
- Gestión de sesiones seguras ✅
```

### Validation Layer
**Ubicación:** `/src/utils/validators.py`

```python
# Validadores disponibles:
- Validación de email y formatos
- Verificación de longitud de campos
- Sanitización de caracteres especiales
- Validación de tipos de datos
- Rangos numéricos y fechas
```

### Helpers Layer
**Ubicación:** `/src/utils/helpers.py`

```python
# Funciones auxiliares:
- Formateo de monedas y números
- Conversión de fechas
- Utilidades de exportación
- Funciones de cálculo financiero
- Helpers de interfaz gráfica
```

---

## 🗄️ Arquitectura de Base de Datos

### Diseño Relacional Optimizado

```sql
-- Estructura principal implementada (v0.5.0)
usuarios (id_usuario, nombre, email, password_hash, fecha_creacion...)
    ↓
sesiones (id_sesion, id_usuario, token_hash, fecha_expiracion...)
    ↓
logs_seguridad (id_log, id_usuario, accion, resultado, fecha...)

-- Estructura planificada (v0.6.0+)
usuarios
    ├── cuentas (id_cuenta, id_usuario, nombre, tipo, saldo...)
    │    └── transacciones (id_transaccion, id_cuenta, monto...)
    ├── presupuestos (id_presupuesto, id_usuario, monto_total...)
    └── categorias (id_categoria, nombre, tipo, color...)
```

### Pool de Conexiones

```python
# Configuración optimizada para aplicación desktop
class DatabaseManager:
    - Pool size: 20 conexiones máximo
    - Timeout: 30 segundos
    - Reconnect automático
    - Logging de operaciones
    - Manejo de errores robusto
```

---

## 🚀 Flujo de Datos y Operaciones

### 1. Flujo de Autenticación (Implementado)

```
[Usuario ingresa credenciales] 
    ↓
[user_view.py valida formato]
    ↓
[persona_controller.py procesa]
    ↓
[Security layer hash/verifica]
    ↓
[Database layer consulta BD]
    ↓
[Respuesta con feedback visual]
```

### 2. Flujo de Transacciones (Planificado v0.6.0)

```
[Usuario registra transacción]
    ↓
[transaction_view.py captura datos]
    ↓
[Validadores verifican entrada]
    ↓
[transaction_controller.py procesa]
    ↓
[Models actualizan BD]
    ↓
[Dashboard actualiza automáticamente]
```

### 3. Flujo de Reportes (Planificado v0.8.0)

```
[Usuario solicita reporte]
    ↓
[Filtros y parámetros]
    ↓
[Controllers consultan datos]
    ↓
[Procesamiento y cálculos]
    ↓
[Generación de gráficos]
    ↓
[Exportación PDF/Excel]
```

---

## 🔒 Arquitectura de Seguridad

### Capas de Protección

```
┌─────────────────────────────────────────┐
│            UI VALIDATION                │  ← Validación en interfaz
├─────────────────────────────────────────┤
│         INPUT SANITIZATION              │  ← Limpieza de entrada
├─────────────────────────────────────────┤
│       BUSINESS LOGIC VALIDATION         │  ← Reglas de negocio
├─────────────────────────────────────────┤
│         DATABASE PROTECTION             │  ← Queries preparadas
├─────────────────────────────────────────┤
│           AUDIT LOGGING                 │  ← Registro de eventos
└─────────────────────────────────────────┘
```

### Medidas Implementadas

1. **Nivel de Aplicación:**
   - Hash bcrypt para contraseñas
   - Validación exhaustiva de entrada
   - Sanitización automática
   - Manejo seguro de errores

2. **Nivel de Base de Datos:**
   - Usuario con permisos limitados
   - Consultas preparadas únicamente
   - Logs de auditoría completos
   - Backup automático encriptado

3. **Nivel de Sistema:**
   - Variables de entorno para credenciales
   - Archivos de configuración protegidos
   - Logs de seguridad separados

---

## 📊 Escalabilidad y Rendimiento

### Optimizaciones Implementadas

1. **Pool de Conexiones:**
   ```python
   # Configuración optimizada
   pool_size = 20          # Conexiones simultáneas
   pool_overflow = 30      # Conexiones adicionales
   pool_timeout = 30       # Timeout en segundos
   pool_recycle = 3600     # Reciclaje cada hora
   ```

2. **Lazy Loading:**
   ```python
   # Carga bajo demanda de módulos pesados
   - Importación diferida de librerías ML
   - Carga condicional de vistas
   - Inicialización lazy de conexiones
   ```

3. **Caching Strategy:**
   ```python
   # Cache en memoria para datos frecuentes
   - Configuración de usuario
   - Categorías predefinidas
   - Tipos de cuenta
   - Validadores compilados
   ```

---

## 🔮 Extensibilidad y Módulos Futuros

### Arquitectura Preparada para:

1. **Módulo de IA (v0.7.0):**
   ```
   src/ai/
   ├── categorization.py    # Clasificación automática
   ├── predictions.py       # Análisis predictivo
   ├── recommendations.py   # Sugerencias financieras
   └── models/             # Modelos ML entrenados
   ```

2. **Módulo de Reportes (v0.8.0):**
   ```
   src/reports/
   ├── generators.py       # Generadores de reportes
   ├── charts.py          # Gráficos con Matplotlib
   ├── exporters.py       # Exportación PDF/Excel
   └── templates/         # Plantillas de reportes
   ```

3. **Módulo de Integración (v1.0.0):**
   ```
   src/integrations/
   ├── banks/             # Conectores bancarios
   ├── markets/           # APIs financieras
   ├── export/            # Exportación a terceros
   └── sync/              # Sincronización nube
   ```

---

## 🧪 Testing y Calidad

### Estrategia de Testing

```
tests/
├── unit/                   # Pruebas unitarias
│   ├── test_controllers.py
│   ├── test_models.py
│   ├── test_validators.py
│   └── test_security.py
├── integration/            # Pruebas de integración
│   ├── test_database.py
│   ├── test_ui_flows.py
│   └── test_end_to_end.py
└── fixtures/              # Datos de prueba
    ├── sample_users.json
    ├── test_transactions.csv
    └── mock_responses.py
```

### Herramientas de Calidad

- **Testing:** pytest + coverage
- **Linting:** flake8 + black + isort
- **Security:** bandit para análisis de seguridad
- **Performance:** memory_profiler para optimización

---

## 📈 Métricas y Monitoreo

### Logging Estructurado

```python
# Niveles de logging implementados
- DEBUG: Información detallada de desarrollo
- INFO: Eventos normales de la aplicación
- WARNING: Situaciones que requieren atención
- ERROR: Errores manejados correctamente
- CRITICAL: Errores que pueden parar la app
```

### Métricas de Rendimiento

```python
# Métricas capturadas automáticamente
- Tiempo de respuesta de queries
- Uso de memoria de la aplicación
- Conexiones activas a BD
- Operaciones por minuto
- Errores por categoría
```

---

## 🔧 Configuración y Deployment

### Configuración por Ambientes

```
config/
├── development.env         # Desarrollo local
├── testing.env            # Pruebas automatizadas
├── production.env          # Producción (template)
└── docker.env             # Contenedores (futuro)
```

### Deployment Strategy

1. **Desktop Application:**
   - Empaquetado con PyInstaller
   - Instalador para Windows/Mac/Linux
   - Auto-updater integrado

2. **Base de Datos:**
   - Scripts de migración automática
   - Backup/restore integrado
   - Verificación de integridad

---

## 📚 Documentación y Standards

### Estándares de Código

```python
# Convenciones seguidas:
- PEP 8 para estilo de código Python
- Docstrings en formato Google
- Type hints obligatorios
- Nombres descriptivos en español
- Comentarios en código complejo
```

### Arquitectura de Documentación

```
docs/                       # Documentación técnica
documentacion/              # Documentación de usuario
README.md                   # Guía principal
CHANGELOG.md               # Historial de cambios
```

---

## 🌟 Ventajas de la Arquitectura Actual

### ✅ Fortalezas Implementadas

1. **Separación Clara:** MVC bien definido y respetado
2. **Seguridad Robusta:** Múltiples capas de protección
3. **Escalabilidad:** Arquitectura preparada para crecimiento
4. **Mantenibilidad:** Código limpio y bien documentado
5. **Performance:** Optimizaciones desde el diseño
6. **Testing:** Cobertura amplia y pruebas automatizadas

### 🔄 Áreas de Mejora Continua

1. **Cache Layer:** Implementar Redis para cache distribuido
2. **Message Queue:** Agregar Celery para tareas asíncronas
3. **Microservices:** Preparar para arquitectura distribuida
4. **API Gateway:** Implementar para integraciones futuras

---

## 👨‍💻 Información del Proyecto

**Arquitecto Principal:** Esteban Fabián Patiño Montealegre  
**Email:** estebanfabianp@gmail.com  
**Versión Arquitectura:** 2.0 (Flet-based)  
**Última Revisión:** Enero 2025  

---

**🏗️ Estado de Implementación:**
- ✅ **MVC Architecture**: 100% implementado
- ✅ **Security Layer**: 100% funcional
- ✅ **Database Layer**: 100% optimizado
- 🚧 **Business Logic**: 60% completado (login listo)
- 📋 **UI Components**: 20% completado (dashboard pendiente)
- 🔮 **AI Integration**: 0% (planificado v0.7.0)

**¡La arquitectura está sólida y lista para el siguiente nivel de desarrollo! 🚀**