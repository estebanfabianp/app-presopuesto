# App Presupuesto

Aplicación de gestión financiera en transición desde una interfaz Flet hacia una capa web Flask + Jinja, manteniendo la lógica de negocio y la persistencia en Python y MySQL/MariaDB.

## Estado actual

- Interfaz de escritorio existente en Flet con entrada principal en `main.py`.
- Capa web inicial en Flask con entrada principal en `app.py`.
- APIs web disponibles para autenticación, presupuestos, transacciones y reportes.
- Base de datos real en MySQL/MariaDB con script de inicialización y modo de mantenimiento seguro.
- Módulos de ETL y utilidades de verificación todavía activos en el proyecto.

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
├── app.py                     # Entrada web Flask
├── main.py                    # Entrada escritorio Flet
├── src/
│   ├── business/services/     # ETL y servicios de negocio
│   ├── controllers/           # Lógica usada por la UI de escritorio
│   ├── database/              # Conector y configuración de BD
│   ├── models/                # Modelos de dominio
│   ├── routes/                # Blueprints Flask
│   ├── static/                # CSS y JS de la versión web
│   ├── templates/             # Templates Jinja
│   └── views/                 # Vistas Flet existentes
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
- `docs/MIGRATION_README.md`: estado de la migración Flet -> HTML.
- `docs/ETL_TARJETA_CREDITO.md`: ETL de tarjetas de crédito.

## Limitaciones conocidas

- El dashboard web todavía usa datos demo en parte del flujo.
- La instalación `full` desde cero sobre algunos entornos MariaDB aún requiere saneamiento adicional de scripts históricos.
- La UI Flet y la UI web conviven; no todo el sistema ha sido migrado a HTML.

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
