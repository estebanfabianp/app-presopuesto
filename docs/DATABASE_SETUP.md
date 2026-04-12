# Configuración de Base de Datos

Este documento describe el flujo oficial para preparar, reejecutar y verificar la base de datos del proyecto.

## Motor soportado

- MySQL 8.0+
- MariaDB 10.6+

## Script oficial

Archivo principal:

```text
base_de_datos/db/init_db.bat
```

## Qué hace `init_db.bat`

1. Verifica que el cliente `mysql` esté disponible.
2. Prueba la conexión con el servidor.
3. Crea la base `app_presupuesto` si no existe.
4. Detecta si la base ya contiene tablas.
5. Ejecuta uno de dos modos:

- `full`: para una base vacía.
- `maintenance`: para una base ya inicializada.

6. Ejecuta la migración de contraseñas legacy a SHA-256.
7. Reporta estadísticas finales de tablas, vistas, funciones, procedimientos y triggers.

## Ejecución recomendada

```powershell
$env:Path = "C:\xampp\mysql\bin;" + $env:Path
.\base_de_datos\db\init_db.bat
```

## Modo `maintenance`

Si la base ya contiene tablas, el batch evita reejecutar scripts no idempotentes de estructura y seed. En ese modo:

- no recrea tablas,
- no recrea claves foráneas,
- no vuelve a insertar seed histórico,
- sí ejecuta tareas seguras de mantenimiento,
- sí corre la migración de contraseñas legacy.

Esto permite reruns seguros sobre bases existentes.

## Manejo de contraseña vacía

Si `DB_PASS` está vacío, el batch omite automáticamente el parámetro `-p` para evitar prompts interactivos innecesarios.

## Migración de contraseñas

Script integrado:

```text
base_de_datos/db/02_maintenance/2026-04-12_hash_legacy_persona_passwords.sql
```

Objetivo:

- detectar claves legacy en texto plano,
- convertirlas a SHA-256,
- permitir reejecución idempotente.

## Verificación manual

```sql
SELECT COUNT(*) AS tablas
FROM information_schema.tables
WHERE table_schema = 'app_presupuesto' AND table_type = 'BASE TABLE';

SELECT COUNT(*) AS vistas
FROM information_schema.views
WHERE table_schema = 'app_presupuesto';
```

## Limitación conocida

La instalación `full` histórica todavía tiene deuda en algunos scripts para entornos MariaDB. Si necesitas una instalación desde cero y encuentras errores, usa este orden de diagnóstico:

1. revisar el output del batch,
2. confirmar compatibilidad del servidor,
3. revisar scripts bajo `base_de_datos/db/01_core/create`,
4. repetir el batch sobre una base ya creada para validar modo `maintenance`.
