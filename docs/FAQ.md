# FAQ

## ¿El proyecto ya es completamente web?

No. El repositorio está en fase híbrida. Sigue existiendo la interfaz Flet y ya hay una base web Flask + Jinja para módulos prioritarios.

## ¿Cuál es la entrada principal?

Depende del modo:

- `main.py` para escritorio Flet.
- `app.py` para la capa web Flask.

## ¿Qué base de datos usa?

MySQL o MariaDB, con inicialización oficial desde `base_de_datos/db/init_db.bat`.

## ¿La API web ya cubre todo el sistema?

La cobertura web ya incluye autenticación, dashboard, presupuestos, transacciones, reportes, tarjetas, inversiones, metas, productos, categorías, beneficiarios, constantes, programadas y análisis.

El repositorio sigue en modo híbrido porque aún existen flujos heredados en Flet, pero la web es la interfaz principal.

## ¿Qué pasa con las contraseñas antiguas?

El sistema soporta migración automática de contraseñas legacy a SHA-256 al primer login exitoso y también mediante script SQL de mantenimiento.

## ¿Puedo reejecutar la inicialización de la base sin destruir datos?

Sí, si la base ya existe el batch entra en modo `maintenance` y evita scripts no idempotentes.

## ¿Por qué hay carpetas `legacy` o vistas viejas?

Porque la migración es incremental. Parte del código antiguo se conserva mientras la versión web termina de absorber funcionalidades.

## ¿El ETL de tarjeta sigue vigente?

Sí. El servicio `etl_tarjeta_credito.py` sigue activo y documentado, y ahora también existe ETL para cuenta bancaria (`etl_cuenta_bancaria.py`) con integración web.

## ¿Qué archivos no deben quedarse versionados?

No deben quedar como parte del árbol limpio del proyecto:

- `__pycache__/`
- logs y salidas debug,
- artefactos temporales,
- entornos virtuales,
- configuraciones puramente locales del editor.
