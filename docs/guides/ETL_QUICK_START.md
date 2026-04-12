# ETL Tarjeta - Inicio Rápido

## 1. Ubicación del servicio

```text
src/business/services/etl_tarjeta_credito.py
```

## 2. Formato mínimo del Excel

```text
Fecha | Concepto | Monto | Categoría | Cuotas | Referencia
```

Solo `Concepto` y `Monto` son obligatorios.

## 3. Ejecutar prueba manual

```powershell
python tests/manual/test_etl_tarjeta.py
```

## 4. Qué valida

- estructura del archivo,
- monto válido,
- concepto presente,
- cuotas válidas,
- categorías y referencias.

## 5. Qué inserta

- registro en `movimiento`,
- registro relacionado en `movimiento_tarjeta`.

## 6. Cuándo revisar la guía completa

Si cambias columnas, lógica de categorías o tablas destino, consulta `docs/ETL_TARJETA_CREDITO.md`.
