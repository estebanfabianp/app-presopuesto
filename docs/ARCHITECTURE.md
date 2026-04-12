# Arquitectura del Sistema

El repositorio se encuentra en una etapa híbrida. Conviven una interfaz Flet ya existente y una nueva capa web Flask + Jinja, ambas apoyadas por la misma lógica Python y la misma base de datos MySQL/MariaDB.

## Vista general

```text
Flet Desktop UI          Flask + Jinja UI
     |                         |
     |                         |
     +-----------+-------------+
                 |
          Controllers / Models
                 |
          DatabaseConnector
                 |
            MySQL / MariaDB
```

## Capas principales

### Presentación

- `main.py` y `src/views/`: interfaz de escritorio en Flet.
- `app.py`, `src/templates/`, `src/static/`: capa web en Flask.
- `src/routes/`: blueprints y endpoints para la versión web.

### Lógica de negocio

- `src/controllers/`: lógica heredada usada sobre todo por Flet.
- `src/business/services/`: servicios específicos, incluido el ETL de tarjeta de crédito.
- `src/models/`: acceso a entidades y autenticación de usuario.

### Persistencia

- `src/database/db_connector.py`: acceso común a MySQL/MariaDB.
- `base_de_datos/db/`: scripts SQL, seeds y mantenimiento.

## Componentes relevantes

### Autenticación

- `src/models/persona_model.py`: validación de credenciales y actualización automática de contraseñas legacy.
- `src/routes/auth.py`: login JWT, logout y endpoint `/api/auth/me`.

### Presupuestos y transacciones web

- `src/routes/presupuesto.py`: CRUD real sobre `presupuesto` y `presupuesto_categoria`.
- `src/routes/transacciones.py`: CRUD y listado real sobre `movimiento`.
- `src/routes/reportes.py`: agregaciones por mes y categoría.

### ETL

- `src/business/services/etl_tarjeta_credito.py`: carga masiva desde Excel a `movimiento` y `movimiento_tarjeta`.

## Decisiones actuales

- La migración web no reemplaza aún toda la interfaz Flet.
- Se priorizó exponer módulos críticos vía Flask sin romper el flujo existente.
- La base de datos se mantiene como fuente única de verdad.
- La inicialización de BD prioriza seguridad operativa en reejecuciones sobre bases existentes.

## Limitaciones abiertas

- El dashboard web aún no está totalmente conectado a datos reales.
- Parte del código heredado sigue en `src/views/` y `src/controllers/`.
- Algunos scripts SQL históricos todavía requieren saneamiento para una instalación `full` completamente idempotente.
