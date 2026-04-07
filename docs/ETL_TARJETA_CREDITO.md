# ETL Tarjeta de Crédito - Guía de Uso

## 📋 Resumen

Se ha implementado un **ETL (Extract, Transform, Load) robusto** para cargar masivamente transacciones de tarjeta de crédito desde archivos Excel. El sistema:

- ✅ Valida la estructura del Excel
- ✅ Transforma datos y mapea categorías automáticamente
- ✅ Inserta en `movimiento` y `movimiento_tarjeta` con transacciones
- ✅ Reporta errores por fila
- ✅ Genera códigos únicos (transacción, movimiento)

---

## 📁 Archivos Creados

### 1. **`src/business/services/etl_tarjeta_credito.py`**
Módulo ETL completo con las siguientes clases:

#### `ETLTarjetaCredito`
```python
from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito

etl = ETLTarjetaCredito()
processed_count, errors = etl.process_file(
    file_path='ruta/archivo.xlsx',
    id_persona=1,
    id_tarjeta=5
)
```

**Métodos principales:**
- `process_file(file_path, id_persona, id_tarjeta)` → Procesa archivo completo
- `validate_excel_file(file_path)` → Validación rápida

#### `ValidationResult` (Dataclass)
Resultado de validación de fila individual.

#### `TransformResult` (Dataclass)
Datos transformados listos para insertar en BD.

---

## 📊 Estructura del Archivo Excel

El archivo Excel debe tener las siguientes columnas (nombres case-insensitive):

| Columna | Requerida | Tipo | Descripción |
|---------|-----------|------|-------------|
| **Fecha** | Opcional | Date | Fecha de la transacción (default: hoy) |
| **Concepto** | ✅ Sí | String | Descripción de la compra (ej: "Supermercado") |
| **Monto** | ✅ Sí | Decimal | Cantidad gastada (ej: 150000) |
| **Categoría** | Opcional | String | Categoría (default: "Compras") |
| **Cuotas** | Opcional | Integer | Número de cuotas (1-36, default: 1) |
| **Referencia** | Opcional | String | Código/referencia de la transacción |

### ✅ Alias Aceptados
Las columnas aceptan múltiples nombres:

- **Fecha**: `fecha`, `date`, `date_transaction`
- **Concepto**: `concepto`, `description`, `descripcion`, `transaccion`
- **Monto**: `monto`, `amount`, `valor`, `quantity`
- **Cuotas**: `cuotas`, `quotas`, `installments`, `nro_cuotas`
- **Categoría**: `categoria`, `category`, `categoría`
- **Referencia**: `referencia`, `reference`, `ref`, `numero_referencia`

### 📄 Ejemplo de Archivo

```
Fecha       | Concepto      | Monto   | Categoría  | Cuotas | Referencia
2026-04-07  | Supermercado  | 150000  | Compras    | 1      | Ref-001
2026-04-08  | Gasolina      | 80000   | Transporte | 1      | Ref-002
2026-04-09  | Restaurante   | 45000   | Alimentos  | 3      | Ref-003
2026-04-10  | Farmacia      | 25000   | Salud      | 1      | Ref-004
```

---

## 🚀 Cómo Usar en la Aplicación

### Desde la UI (Nueva Transacción)

1. **Selecciona modalidad**: "Carga a Tarjeta de Crédito"
2. **Selecciona la tarjeta** de crédito
3. **Click en "Carga masiva Excel"**
4. **Selecciona archivo** con estructura correcta
5. **Sistema procesa** automáticamente:
   - Valida cada fila
   - Mapea categorías (crea si no existen)
   - Inserta en `movimiento` y `movimiento_tarjeta`
   - Reporta éxitos y errores

### Programáticamente

```python
from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito
from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
etl = ETLTarjetaCredito(db)

# Procesar archivo
processed, errors = etl.process_file(
    file_path='transacciones.xlsx',
    id_persona=1,
    id_tarjeta=5
)

print(f"Procesadas: {processed} transacciones")
if errors:
    for err in errors:
        print(f"Fila {err['row']}: {', '.join(err['errors'])}")

db.close()
```

---

## 🔍 Validaciones Realizadas

### A Nivel de Fila
✅ **Campos obligatorios:**
- Concepto (no vacío)
- Monto (> 0)

✅ **Formato de datos:**
- Monto: número válido, puede tener coma decimal
- Fecha: formato reconocible por pandas (múltiples formatos)
- Cuotas: 1-36 enteros
- Categoría: string, default "Compras" si vacío

### A Nivel de Archivo
✅ Estructura (contiene columnas requeridas)
✅ No vacío
✅ Formato válido (Excel .xlsx)

### Durante la Transformación
✅ Mapeo automático de categorías (crea si no existen)
✅ Obtención de tipos de movimiento (gasto)
✅ Obtención de estados
✅ Generación de códigos únicos

---

## 📝 Datos Generados Automáticamente

### Para tabla `movimiento`
- **codigo**: `MOV-20260407120530-1` (timestamp + número)
- **numero_transaccion**: `TRX-20260407120530-1`
- **nota**: Combinación de Concepto + Referencia
- **id_tipo**: ID de tipo "gasto"
- **id_estado**: Estado por defecto
- **id_producto**: ID de la tarjeta de crédito
- **fecha_creacion**: Fecha/hora actual

### Para tabla `movimiento_tarjeta`
- **numero_transaccion**: Mismo que movimiento
- **estado**: "compra"
- **saldo**: Igual al valor (para cálculo de saldos)
- **cuotas**: Número de cuotas del Excel

---

## ⚠️ Manejo de Errores

### Errores por Fila
Se reportan pero continúa procesando:
- Monto inválido
- Concepto vacío
- Fecha mal formada
- Cuotas fuera de rango (1-36)

### Errores Fatales
Detiene el proceso:
- Archivo no encontrado
- Estructura inválida
- Error de conexión a BD
- Error en transacción de BD

---

## 🧪 Pruebas

Se incluye script de prueba:

```bash
python test_etl_tarjeta.py
```

**Valida:**
- ✅ Lectura correcta de Excel
- ✅ Validaciones funcionan
- ✅ Inserts en BD son correctos
- ✅ Conteos de registros

---

## 🔧 Configuración

### Límites Actuales
- **Cuotas máximo**: 36
- **Cuotas mínimo**: 1
- **Filas máximo**: Sin límite (procesa todas)
- **Tamaño de archivo**: Depende de memoria disponible

### Personalización
Para modificar límites, edita en `ETLTarjetaCredito`:

```python
# En método _validate_row()
if cuotas < 1 or cuotas > 36:  # Cambiar 36 aquí
    result.is_valid = False
    result.errors.append("Cuotas debe estar entre 1 y 36")
```

---

## 📊 Ejemplo de Salida

**Éxito:**
```
✓ Carga completada: 12 transacción(es) registrada(s).
```

**Con errores:**
```
⚠ Filas con errores:
Fila 3: Monto inválido: 'abc'
Fila 5: Seguros debe estar entre 1 y 36
Fila 7: Concepto es obligatorio
```

---

## 🔐 Seguridad

- ✅ Validación de tipos de datos
- ✅ Inyección SQL prevenida (prepared statements)
- ✅ Transacciones atómicas (rollback en error)
- ✅ Generación de códigos únicos con timestamp
- ✅ Auditoría de errores por fila

---

## 📌 Notas Importantes

1. **Las categorías se crean automáticamente** si no existen en la BD
2. **La fecha por defecto es hoy** si no se proporciona
3. **Si falla una fila, no afecta a otras** (se reporta pero continúa)
4. **El archivo no se modifica** (solo lectura)
5. **Los códigos de transacción son únicos** (timestamp + número)

---

## 🆘 Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| "Columnas faltantes" | Estructura incorrecta | Usa plantilla descargada desde la app |
| "Archivo vacío" | Excel sin datos | Agrega al menos 1 fila de datos |
| "Usuario no encontrado" | Sin usuario activo | Login primero en la aplicación |
| "Tarjeta no encontrada" | ID inválida | Selecciona tarjeta correcta |
| "Monto inválido" | Caracteres no numéricos | Usa formato: 150000 o 150.000 |

---

## 📞 Soporte

Para reportar errores o sugerencias, revisa los logs:
- Archivo: `app.log` (si está configurado)
- Consola: mensajes de error mostrados en UI

---

*Generado: 2026-04-07*
*Versión: 1.0*
