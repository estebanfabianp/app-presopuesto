# ETL Cuenta Bancaria

Documentacion operativa del servicio de carga masiva de extractos bancarios desde Excel.

## Archivo principal

```text
src/business/services/etl_cuenta_bancaria.py
```

## Objetivo

Tomar un archivo Excel bancario, validar su estructura y registrar movimientos en `movimiento`.

## Formato esperado

Columnas base del extracto:

- `FECHA`
- `DESCRIPCION SUCURSAL`
- `DCTO.`
- `VALOR`
- `SALDO`

## Flujo general

1. leer archivo Excel,
2. normalizar nombres de columnas,
3. validar fecha y valor por fila,
4. inferir tipo (ingreso/gasto) segun signo o reglas del movimiento,
5. construir `movimiento` con categoria y beneficiario cuando aplique,
6. insertar movimientos en transaccion atomica,
7. confirmar o revertir ante error.

## Integracion en la web

Disponible en `/transacciones` -> pestana `Importar`.

Endpoints involucrados:

- `GET /api/transacciones/import/catalogos`
- `POST /api/transacciones/import/upload`
- `GET /api/transacciones/import/template?source=cuenta_bancaria`

## Notas operativas

- Validar que la cuenta destino corresponda al usuario autenticado.
- Revisar filas con errores y corregir antes de reintentar la carga.
- Si se modifica la estructura de `movimiento`, actualizar este ETL en paralelo.
