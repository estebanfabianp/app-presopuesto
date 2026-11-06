# Índice de documentación

Este índice organiza la documentación vigente del proyecto por objetivo y por nivel de detalle.

## 1. Inicio y puesta en marcha

- `INSTALLATION.md` — instalación del proyecto, requisitos y pasos de arranque.
- `DEVELOPMENT.md` — flujo de trabajo para desarrollo local y buenas prácticas.
- `TROUBLESHOOTING.md` — solución de errores comunes durante setup o ejecución.

## 2. Arquitectura y modelado de datos

- `ARCHITECTURE.md` — visión general de la aplicación, capas y módulos.
- `DATA_MODEL.md` — entidades principales y relaciones del dominio financiero.
- `BASE_DATOS.md` — estructura y reglas de la base de datos.
- `DATABASE_SETUP.md` — preparación, migración y mantenimiento de la BD.

## 3. APIs y uso funcional

- `API_REFERENCE.md` — endpoints web y contratos de servicio.
- `USER_GUIDE.md` — guía de uso para el usuario final.
- `FAQ.md` — preguntas frecuentes y soluciones rápidas.

## 4. ETL, automatización e integración

- `ETL_TARJETA_CREDITO.md` — carga y transformación de movimientos de tarjeta.
- `ETL_CUENTA_BANCARIA.md` — ETL de extractos bancarios.
- `THRESHOLDS_GUIDE.md` — guía de thresholds y reglas automáticas.
- `CHANGES_THRESHOLDS_ACTIONS.md` — cambios operativos y acciones asociadas.
- `guides/CONSTANTS_QUICK_START.md` — guía rápida para usar constantes del sistema.
- `guides/CONSTANTS_VIEW_GUIDE.md` — visión de uso y mantenimiento de constantes.
- `guides/ETL_QUICK_START.md` — arranque rápido de procesos ETL.

## 5. Migraciones y evolución del esquema

- `MIGRATION_README.md` — guía general sobre migraciones.
- `MIGRACION_2026_04_12.md` — migración histórica del 12 de abril de 2026.
- `scripts/migrations/` — scripts de migración y normalización de datos.

## 6. Estado del proyecto y resúmenes

- `status/MEJORAS_3_RESUMEN_FINAL.md` — resumen final de mejoras aplicadas.
- `status/PRUEBAS_DIFERIDOS_RESUMEN.md` — estado y resultados de pruebas diferidas.

## 7. Cómo elegir la documentación correcta

### Si quieres arrancar la app

- `INSTALLATION.md`
- `DATABASE_SETUP.md`
- `TROUBLESHOOTING.md`

### Si quieres entender la estructura

- `ARCHITECTURE.md`
- `DATA_MODEL.md`
- `BASE_DATOS.md`

### Si quieres operar la app

- `USER_GUIDE.md`
- `FAQ.md`
- `API_REFERENCE.md`

### Si quieres depurar o cambiar lógica

- `DEVELOPMENT.md`
- `THRESHOLDS_GUIDE.md`
- `CHANGES_THRESHOLDS_ACTIONS.md`

### Si quieres trabajar con importaciones o ETL

- `ETL_TARJETA_CREDITO.md`
- `ETL_CUENTA_BANCARIA.md`
- `guides/ETL_QUICK_START.md`

## 8. Recomendación general

Para el desarrollo cotidiano, empezar por:

1. `README.md` del repositorio.
2. `docs/ARCHITECTURE.md`.
3. `docs/DATABASE_SETUP.md`.
4. `docs/DEVELOPMENT.md`.

Esto permite entender tanto la funcionalidad del negocio como la estructura técnica antes de hacer cambios en rutas, servicios o modelos.
