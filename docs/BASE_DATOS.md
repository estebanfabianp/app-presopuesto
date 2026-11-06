# Base de Datos

Resumen operativo de la estructura SQL y del flujo de mantenimiento del proyecto.

## Directorios principales

```text
base_de_datos/db/
├── 01_core/
│   ├── create/          # Scripts de creación
│   ├── drop/            # Scripts destructivos o de limpieza
│   └── seed/            # Datos iniciales
├── 02_maintenance/      # Scripts de mantenimiento seguro
├── data/                # Datos auxiliares
├── jobs/                # Automatizaciones SQL o batch
└── init_db.bat          # Punto oficial de inicialización
```

## Flujo recomendado

1. Levantar MySQL/MariaDB y respaldar los datos existentes.
2. Revisar el modo y los scripts aplicables en [la guía de base de datos](DATABASE_SETUP.md), y ejecutar `init_db.bat` cuando corresponda.
3. Verificar el resumen final del batch.
4. Si la base ya existía, confirmar que el modo fue `maintenance`.

## Modo `full`

Se usa cuando la base está vacía.

Ejecuta:

- tablas base,
- claves foráneas,
- índices,
- funciones,
- procedimientos,
- triggers,
- comentarios,
- vistas,
- tablas y procedimientos de documentación,
- seed histórico.

## Modo `maintenance`

Se usa cuando ya hay tablas creadas.

Ejecuta únicamente:

- verificaciones seguras,
- mantenimiento compatible,
- creación de las tablas de préstamos y metas si faltan,
- migración de contraseñas legacy,
- resumen de estado.

## Migración de contraseñas legacy

Script:

```text
base_de_datos/db/02_maintenance/2026-04-12_hash_legacy_persona_passwords.sql
```

Características:

- convierte claves en texto plano a SHA-256,
- evita rehasear claves ya migradas,
- puede correrse varias veces sin efectos secundarios.

## Estado actual de la base

El estado y la compatibilidad dependen de la instalación. Comprueba el resultado de cada migración y el esquema de la base concreta antes de utilizarlo.

## Riesgos pendientes

- algunos scripts históricos de creación no son completamente idempotentes,
- la compatibilidad `full` con MariaDB todavía necesita limpieza adicional,
- algunos artefactos antiguos del esquema aún requieren revisión antes de una estandarización mayor.
