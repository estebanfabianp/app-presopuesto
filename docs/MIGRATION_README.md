# Estado de Migración Flet -> HTML

Este documento resume el estado real de la migración de la interfaz hacia HTML/Jinja sin repetir planes históricos ya ejecutados.

## Objetivo

Migrar gradualmente la UI desde Flet a una capa web Flask + Jinja, conservando la lógica Python y la base MySQL/MariaDB.

## Ya implementado

- `app.py` como entrada web.
- `src/config.py` para configuración Flask.
- `src/routes/auth.py` con login real vía `PersonaModel`.
- `src/routes/presupuesto.py` con CRUD real.
- `src/routes/transacciones.py` con operaciones reales.
- `src/routes/reportes.py` con agregaciones reales.
- templates base en `src/templates/`.
- assets en `src/static/`.
- autenticación JWT corregida.
- migración de contraseñas legacy integrada.

## Pendiente

- reemplazar datos demo del dashboard web,
- completar módulos HTML secundarios,
- terminar saneamiento de instalación `full` en MariaDB,
- ampliar pruebas automatizadas de la capa web.

## Criterio actual de uso

- usa Flet si necesitas cobertura funcional histórica completa,
- usa Flask si necesitas validar la nueva experiencia web y los endpoints ya migrados.

## Documentos asociados

- `docs/API_REFERENCE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATABASE_SETUP.md`
