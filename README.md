# App Presupuesto

Aplicación web para gestión financiera personal y análisis de flujo de efectivo, construida con Flask, Jinja2 y MySQL/MariaDB.

## Visión general

App Presupuesto centraliza la operación financiera personal en una sola herramienta:

- registro de cuentas bancarias y movimientos,
- seguimiento de tarjetas de crédito y diferidos,
- gestión de presupuesto por categoría y dinero libre del mes,
- préstamos con cuotas, intereses, seguros y otros cargos,
- metas de ahorro con aportes y retiros manuales,
- análisis de consumo y tendencias,
- automatización de clasificación de movimientos,
- análisis de patrimonio, saldos y metas.

El proyecto está orientado a la versión web como interfaz principal, aunque conserva una capa desktop Flet heredada que no es el eje actual del desarrollo.

## Estado actual del proyecto

- La aplicación web Flask es la interfaz principal y se ejecuta desde `app.py`.
- La UI Flet de `main.py` sigue disponible como compatibilidad, pero el desarrollo activo se concentra en la web.
- La lógica continúa separada por capas: rutas, servicios de negocio, acceso a datos y plantillas.
- El rendimiento operativo depende de una base de datos MySQL/MariaDB real con inicialización y mantenimiento seguro.
- Existen módulos de ETL, validación, análisis y optimización de clasificación incorporados al flujo productivo.

## Stack tecnológico

- Python 3.10+
- Flask
- Jinja2
- MySQL 8 / MariaDB
- SQLAlchemy-like style via custom DB connector patterns
- JavaScript y Chart.js para dashboards y análisis
- Flask JWT para autenticación

## Requisitos previos

- Python 3.10 o superior.
- MySQL 8.0+ o MariaDB 10.6+.
- XAMPP o instalación equivalente de MySQL.
- Entorno virtual activo.
- Dependencias del proyecto instaladas desde `requirements.txt`.

## Inicio rápido

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Inicializar la base de datos

Para una instalación nueva, revisa primero [la guía de base de datos](docs/DATABASE_SETUP.md).
Si ya tienes datos, haz una copia de seguridad antes de cualquier migración: no
ejecutes scripts de creación o seed sin revisar su alcance. Las tablas de
préstamos y metas tienen migraciones aditivas documentadas en esa guía.

```powershell
$env:Path = "C:\xampp\mysql\bin;" + $env:Path
.\base_de_datos\db\init_db.bat
```

### Ejecutar la aplicación web

```powershell
python app.py
```

Luego abrir:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/login

## Flujo funcional principal

1. Login con JWT.
2. Dashboard con KPIs financieros principales.
3. Gestión de cuentas y movimientos bancarios.
4. Registro y categorización de tarjetas de crédito.
5. Presupuesto mensual, dinero libre y análisis por categorías.
6. Registro de préstamos y seguimiento de metas de ahorro independientes.
7. Revisión de saldos e inversiones y uso de la optimización de clasificación.

## Estructura relevante del repositorio

```text
app-presopuesto/
├── app.py                           # Entrada principal de la app web Flask
├── main.py                          # Entrada legacy Flet
├── config.yaml                     # Configuración global de entorno
├── requirements.txt                # Dependencias Python
├── src/
│   ├── business/
│   │   └── services/               # Servicios de negocio y ETL
│   ├── controllers/                # Lógica legacy soportada por escritorio
│   ├── database/                   # Conector y utilidades de acceso a BD
│   ├── models/                     # Modelos y dominio de la app
│   ├── routes/                     # Blueprints Flask
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── transacciones.py
│   │   ├── presupuesto.py
│   │   ├── reportes.py
│   │   ├── tarjetas.py
│   │   ├── inversiones.py
│   │   ├── metas.py
│   │   ├── prestamos.py
│   │   ├── productos.py
│   │   ├── cuentas_bancarias.py
│   │   ├── categorias.py
│   │   ├── beneficiarios.py
│   │   ├── constantes.py
│   │   ├── programadas.py
│   │   ├── analisis.py
│   │   └── optimizacion_categorias.py
│   ├── static/                    # Assets CSS/JS web
│   ├── templates/                 # Vistas Jinja2
│   ├── utils/                     # Utilidades varias
│   ├── views/                     # Vistas heredadas Flet
│   └── __init__.py
├── base_de_datos/
│   └── db/                        # Scripts de inicialización y mantenimiento
├── data/                          # Datos de apoyo y persistencia local
├── docs/                          # Documentación del proyecto
├── logs/                          # Logs de ejecución
├── scripts/
│   ├── migrations/                # Migraciones SQL/Python del esquema
│   ├── seed/                      # Semillas y datos de prueba
│   ├── verify/                   # Verificaciones manuales
│   └── ...
├── tests/                         # Pruebas automáticas y manuales
├── README.md                      # Documento principal
├── app-presopuesto.code-workspace # Workspace VS Code
└── main.py                        # Punto de entrada heredado
```

## Módulos funcionales principales

### Dashboard y resumen financiero

- KPIs de patrimonio, flujo del mes y cuentas.
- Visualización consolidada del estado económico personal.
- Integración con saldos reales por persona y por producto.
- Presencia de movimientos por mes para cuentas y tarjetas; no confirma que los extractos estén completos.

### Cuentas y movimientos

- Gestión de cuentas bancarias.
- Registro y detalle de movimientos.
- Categorización de entradas y egresos.

### Tarjetas y diferidos

- Administración de tarjetas de crédito.
- Seguimiento de movimientos, cuotas y saldo.
- Carga de información desde ETL y cálculo de pagos diferidos.

### Presupuesto y categorías

- Hoja anual y mensual con categorías y subcategorías desplegables.
- Gastos reales con compras positivas de tarjeta y exclusión de pagos bancarios de tarjeta identificados; los abonos se excluyen y algunos requieren revisión.
- Dinero libre a partir de ingresos y gastos presupuestados, diferidos, cuotas de préstamos y ajustes manuales.

### Préstamos

- Registro de capital, tasa, cuotas, seguros y otros cargos.
- Pagos parciales y abonos extraordinarios; registro bancario opcional. El plan es una estimación, no incluye mora ni variaciones de tasa.

### Metas de ahorro

- Metas independientes de los presupuestos, con objetivo, fecha opcional, progreso e historial.
- Aportes y retiros manuales: no transfieren dinero ni modifican cuentas bancarias.

### Análisis y reportes

- Períodos móviles hasta hoy para las cifras principales de consumo.
- Comparativa del mes actual parcial con el anterior completo y presupuesto por categoría del mes.
- Indicador orientativo de salud financiera sujeto a datos y clasificación suficientes; algunas secciones antiguas todavía usan solo cuentas bancarias.

### Optimización de clasificación

- Identificación de conceptos repetidos sin categoría.
- Reglas automáticas basadas en historial.
- Resolución de conflictos y confirmación manual de reglas.
- Aplicación masiva a movimientos pendientes.

### ETL y carga de datos

- ETL de cuenta bancaria.
- ETL de tarjeta de crédito.
- Procesado de registros históricos y migración de archivos.

## Documentación disponible

- `docs/README.md`: índice maestro de documentación.
- `docs/ARCHITECTURE.md`: arquitectura actual del sistema.
- `docs/DATABASE_SETUP.md`: preparación y mantenimiento de la base de datos.
- `docs/API_REFERENCE.md`: referencia de endpoints.
- `docs/USER_GUIDE.md`: guía operativa para usuarios.
- `docs/INSTALLATION.md`: instalación y configuración del entorno.
- `docs/DEVELOPMENT.md`: flujo de trabajo para desarrollo.
- `docs/TROUBLESHOOTING.md`: resolución de problemas comunes.
- `docs/status/`: reportes y resúmenes de evolución del proyecto.

## Buenas prácticas del proyecto

- Mantener la base de datos como fuente única de verdad.
- Preferir cambios en servicios empresariales antes de tocar la capa visual.
- Validar los cambios con la propia base de datos y con la UI de escenarios reales.
- No dejar scripts de prueba en la raíz del repositorio.
- Usar `use_reloader=False` si se trabaja con ETL y carga de archivos para evitar reinicios innecesarios del servidor.

## Limitaciones conocidas

- La parte desktop Flet está desfasada respecto a la web y no es prioridad de desarrollo.
- Algunos scripts históricos requieren saneamiento para instalaciones nuevas o limpias.
- El proyecto combina módulos modernos con código heredado en distintos puntos del repositorio.
- Las metas no ofrecen eliminación de metas ni movimientos; sus movimientos no se vinculan automáticamente con cuentas.
- Abonos de tarjeta potencialmente correspondientes a devoluciones requieren revisión; no se descuentan automáticamente.

## Verificación rápida

```powershell
python app.py
```

Validaciones recomendadas:

- Abrir http://127.0.0.1:5000/login
- Revisar que el dashboard se cargue correctamente
- Confirmar que las rutas de módulos principales responden sin errores
- Validar que la base de datos esté disponible en MySQL/MariaDB

## Contribución

Para trabajar sobre el proyecto:

1. Crear un entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Revisar la BD y scripts de migración.
4. Ejecutar la app en modo local.
5. Probar los cambios con la ruta afectada y la lógica relevante.

Si se modifica la estructura de datos, revisar antes los scripts bajo `scripts/migrations/` y la documentación de `docs/DATABASE_SETUP.md`.
