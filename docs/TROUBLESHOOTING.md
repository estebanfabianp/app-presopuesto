# Troubleshooting

## La aplicación web no arranca

Verifica:

```powershell
python app.py
```

Problemas comunes:

- dependencia faltante en `requirements.txt`,
- puerto ocupado,
- `.env` inconsistente,
- error de conexión a MySQL/MariaDB.

## `GET /health` falla

Pasos:

1. confirma que `app.py` levantó sin excepciones,
2. valida host y puerto,
3. revisa errores de importación en `src/routes`.

## El login devuelve 401

Revisa:

- existencia del usuario en `persona`,
- `estado = 1`,
- contraseña correcta,
- conectividad a base de datos.

Recuerda que el modelo puede migrar contraseñas legacy al primer login exitoso.

## `init_db.bat` falla

Verifica:

- cliente `mysql` en PATH,
- servidor MySQL/MariaDB levantado,
- credenciales válidas,
- permisos para crear o usar `app_presupuesto`.

Si la base ya existía, el batch debe entrar en modo `maintenance`.

## La instalación `full` falla en MariaDB

Estado conocido del proyecto:

- algunos scripts históricos todavía no son totalmente idempotentes o portables,
- el modo `maintenance` ya es seguro y reejecutable,
- para una base nueva puede requerirse revisión puntual de scripts bajo `01_core/create`.

## Flet falla por imports o vistas

Pasos:

1. activa el entorno virtual,
2. instala dependencias,
3. revisa imports rotos en `src/views` y `src/controllers`,
4. prueba también el modo web para aislar si el problema es solo de la UI heredada.

## El ETL no procesa el Excel

Revisa:

- ruta del archivo,
- columnas mínimas esperadas,
- tarjeta y persona existentes,
- datos numéricos válidos.

Consulta `docs/ETL_TARJETA_CREDITO.md` para el formato soportado.
