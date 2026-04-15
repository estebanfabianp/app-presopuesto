# App Presupuesto

Aplicación de gestión de finanzas personales con capa web Flask + Jinja y base de datos MySQL/MariaDB.

## Estado actual

- Capa web Flask como interfaz principal, con entrada en `app.py`.
- Interfaz de escritorio Flet heredada disponible en `main.py` (en proceso de deprecación).
- APIs REST completas para autenticación, dashboard, presupuesto, transacciones, reportes, tarjetas, inversiones, metas, categorías, beneficiarios, constantes, transacciones programadas y análisis de consumo.
- Base de datos real en MySQL/MariaDB con script de inicialización y modo de mantenimiento seguro.
- Módulos de ETL y utilidades de verificación activos en el proyecto.

## Modos de ejecución

### Escritorio Flet

```powershell
python main.py
```

### Web Flask

```powershell
python app.py
```

La aplicación web usa templates en `src/templates`, assets en `src/static` y blueprints en `src/routes`.

## Requisitos

- Python 3.10 o superior.
- MySQL 8.0+ o MariaDB 10.6+.
- Entorno virtual activo.
- Dependencias instaladas desde `requirements.txt`.

## Inicio rápido

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Inicializa o verifica la base de datos:

```powershell
$env:Path = "C:\xampp\mysql\bin;" + $env:Path
.\base_de_datos\db\init_db.bat
```

Notas:

- Si la base está vacía, `init_db.bat` intenta una instalación completa.
- Si la base ya tiene tablas, entra en modo `maintenance` y ejecuta solo tareas seguras.
- La migración de contraseñas legacy a SHA-256 está integrada al flujo del batch.

## Estructura relevante

```text
app-presopuesto/
├── app.py                     # Entrada web Flask (principal)
├── main.py                    # Entrada escritorio Flet (heredado)
├── src/
│   ├── business/services/     # ETL y servicios de negocio
│   ├── controllers/           # Lógica usada por la UI de escritorio
│   ├── database/              # Conector y configuración de BD
│   ├── models/                # Modelos de dominio
│   ├── routes/                # Blueprints Flask
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── transacciones.py
│   │   ├── presupuesto.py
│   │   ├── reportes.py
│   │   ├── tarjetas.py
│   │   ├── inversiones.py
│   │   ├── metas.py
│   │   ├── productos.py
│   │   ├── cuentas_bancarias.py
│   │   ├── categorias.py
│   │   ├── beneficiarios.py
│   │   ├── constantes.py
│   │   ├── programadas.py              # Transacciones programadas (recurrentes)
│   │   ├── analisis.py                 # Análisis de consumo
│   │   └── optimizacion_categorias.py  # Optimización de categorías y beneficiarios
│   ├── static/                # CSS y JS de la versión web
│   ├── templates/             # Templates Jinja
│   │   ├── dashboard/
│   │   ├── transacciones/
│   │   ├── presupuesto/
│   │   ├── reportes/
│   │   ├── tarjetas/
│   │   ├── inversiones/
│   │   ├── metas/
│   │   ├── productos/
│   │   ├── cuentas_bancarias/
│   │   ├── categorias/
│   │   ├── beneficiarios/
│   │   ├── constantes/
│   │   ├── programadas/       # Interfaz transacciones programadas
│   │   ├── analisis/                    # Interfaz análisis de consumo
│   │   ├── optimizacion_categorias/     # Interfaz optimización de clasificación
│   │   └── components/
│   └── views/                 # Vistas Flet existentes (heredadas)
├── base_de_datos/db/          # Scripts SQL y batch de inicialización
├── docs/                      # Documentación vigente
├── scripts/verify/            # Verificaciones manuales
└── tests/                     # Tests y pruebas manuales
```

## Documentación recomendada

- `docs/INSTALLATION.md`: instalación y arranque.
- `docs/ARCHITECTURE.md`: arquitectura actual.
- `docs/DATABASE_SETUP.md`: inicialización y mantenimiento de BD.
- `docs/API_REFERENCE.md`: endpoints web disponibles.
- `docs/USER_GUIDE.md`: guía de uso de módulos web.
- `docs/ETL_TARJETA_CREDITO.md`: ETL de tarjetas de crédito.
- `docs/ETL_CUENTA_BANCARIA.md`: ETL de extractos de cuenta bancaria.
- `docs/README.md`: índice maestro de documentación.

## Módulos web disponibles

| Ruta                 | Descripción                                    |
|----------------------|------------------------------------------------|
| `/dashboard`         | Resumen principal de finanzas                 |
| `/transacciones`     | Historial y CRUD de movimientos               |
| `/presupuesto`       | Gestión de presupuestos por categoría         |
| `/reportes`          | Reportes mensuales y por categoría            |
| `/tarjetas`          | Tarjetas de crédito y compras diferidas       |
| `/inversiones`       | Seguimiento de inversiones                    |
| `/metas`             | Metas de ahorro                               |
| `/productos`         | Resumen de productos financieros              |
| `/cuentas-bancarias` | Gestión de cuentas bancarias                  |
| `/categorias`        | Catálogo de categorías                        |
| `/beneficiarios`     | Catálogo de beneficiarios                     |
| `/constantes`        | Constantes del sistema                        |
| `/programadas`       | Transacciones programadas y recurrentes       |
| `/analisis`                | Análisis de consumo con gráficos interactivos                  |
| `/optimizacion-categorias` | Optimización automática de categorías y beneficiarios          |

## Limitaciones conocidas

- La UI Flet (`main.py`) convive con la web pero ya no es el foco principal de desarrollo.
- Para importaciones ETL desde Excel se recomienda lanzar Flask con `use_reloader=False` para evitar que el watchdog reinicie el servidor al cargar módulos XML.
- La instalación `full` desde cero sobre algunos entornos MariaDB aún requiere saneamiento adicional de scripts históricos.

## Organización del repositorio

- Los documentos de estado y resúmenes técnicos viven en `docs/status/`.
- Las pruebas manuales y de exploración deben guardarse en `tests/manual/`.
- Evita dejar scripts de prueba en la raíz del proyecto.

## Verificación rápida

Aplicación web:

```powershell
python app.py
```

Luego abre:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/health`

Aplicación de escritorio:

```powershell
python main.py
```
