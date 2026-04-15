# ETL Tarjeta de Crédito

Documentación operativa del servicio de carga masiva de movimientos de tarjeta desde Excel.

## Archivo principal

```text
src/business/services/etl_tarjeta_credito.py
```

## Objetivo

Tomar un archivo Excel, validarlo, transformar sus filas y registrar datos en:

- `movimiento`
- `movimiento_tarjeta`

## Flujo general

1. leer archivo Excel,
2. validar columnas mínimas,
3. normalizar tipos y fechas,
4. resolver categorías,
5. insertar en `movimiento`,
6. insertar en `movimiento_tarjeta`,
7. confirmar transacción o hacer rollback ante error.

## Columnas esperadas

Obligatorias:

- `Concepto`
- `Monto`

Opcionales:

- `Fecha`
- `Categoría`
- `Cuotas`
- `Referencia`

## Alias soportados

- fecha: `fecha`, `date`
- concepto: `concepto`, `description`, `descripcion`
- monto: `monto`, `amount`, `valor`
- categoría: `categoria`, `categoría`, `category`
- cuotas: `cuotas`, `installments`
- referencia: `referencia`, `reference`, `ref`

## Validaciones principales

- monto mayor que cero,
- concepto no vacío,
- cuotas entre 1 y 36,
- fecha interpretable,
- archivo Excel válido,
- existencia de persona y tarjeta objetivo.

## Notas operativas

- **Reloader**: al ejecutar `python app.py` el watchdog de Flask detecta módulos XML cargados por `openpyxl` y reinicia el servidor, cortando la conexión. Para evitarlo, lanzar con:

  ```python
  app.run(debug=True, use_reloader=False, port=5000)
  ```

- **Validación en cliente**: la interfaz web valida que exista una tarjeta seleccionada antes de enviar el formulario. Si no hay tarjetas registradas muestra un mensaje con guía.

- El endpoint `GET /api/transacciones/debug/whoami` permite verificar qué tarjetas tiene asociadas el usuario autenticado.

## Uso programático

```python
from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito
from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
etl = ETLTarjetaCredito(db)
processed, errors = etl.process_file(
	file_path='transacciones.xlsx',
	id_persona=1,
	id_tarjeta=5,
)
db.close()
```

## Prueba manual disponible

Archivo:

```text
tests/manual/test_etl_tarjeta.py
```

Ejecución:

```powershell
python tests/manual/test_etl_tarjeta.py
```

## Observaciones

- El servicio sigue siendo útil aunque la migración web avance.
- El flujo ETL está disponible tanto en la interfaz web (`/transacciones`, pestaña Importar) como en Flet.
- Si cambias el esquema de `movimiento` o `movimiento_tarjeta`, revisa este servicio primero.
