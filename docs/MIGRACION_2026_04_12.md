# Migración del Modelo de Datos - 2026-04-12

## Resumen

Se han agregado 3 nuevas tablas al modelo de datos para mejorar:
1. **Desglose de items** en movimientos
2. **Relación clara** entre diferidos y sus movimientos de cuota
3. **Auditoría** de movimientos rechazados

## Tablas Nuevas

### 1. `movimiento_tarjeta_item`
**Propósito:** Guardar items individuales de un movimiento desglosado

```sql
- id_item (PK)
- id_movimiento_tarjeta (FK → movimiento_tarjeta)
- numero_item (1, 2, 3...)
- descripcion (ej: "Comida", "Clases de baile")
- id_categoria (FK → categoria, opcional)
- monto (cantidad del item específico)
- fecha_creacion
```

**Ventajas:**
- Permite consultas granulares: "¿cuánto gasté en comida este mes?" (sin parsear notas)
- Reportes por ítem sin necesidad de texto parsing
- Mejor auditoría del desglose

**Ejemplo:**
```json
{
  "movimiento_id": 42,
  "lista": [
    {
      "numero": 1,
      "descripcion": "Comida",
      "id_categoria": 5,
      "monto": 20000
    },
    {
      "numero": 2,
      "descripcion": "Clases",
      "id_categoria": 8,
      "monto": 20000
    }
  ],
  "total": 40000
}
```

### 2. `detalle_diferido_movimiento`
**Propósito:** Relacionar diferidos con sus cuotas mensuales

```sql
- id_detalle (PK)
- id_diferido (FK → tarjeta_diferido)
- id_movimiento_tarjeta (FK → movimiento_tarjeta, nullable)
- numero_cuota (1, 2, 3... 12)
- tipo_cuota (CAPITAL, INTERES, TOTAL)
- estado (PENDIENTE, PAGADA, VENCIDA)
- fecha_creacion
```

**Ventajas:**
- Rastrear exactamente cuáles movimientos pertenecen a qué diferido
- Reportes de "cuotas del mes": filtrar por `estado='PENDIENTE'`
- Detectar cuotas vencidas vs pagadas vs pendientes

**Flujo:**
1. Diferido se crea → se registra `numero_cuota=1` en estado `PENDIENTE`
2. Se paga cuota 1 → se actualiza a `PAGADA` y se crea `numero_cuota=2`
3. Se puede liquidar anticipadamente marcando todas como `PAGADA`

### 3. `movimiento_rechazo`
**Propósito:** Auditoría completa de transacciones rechazadas

```sql
- id_rechazo (PK)
- id_persona (FK)
- id_tarjeta (FK, opcional)
- id_movimiento_tarjeta (FK, opcional - si se creó parcialmente)
- motivo (LIMIT_EXCEDIDO, TARJETA_BLOQUEADA, FRAUDE_DETECTADO, etc.)
- descripcion
- intento_valor (cuánto intentó gastar)
- intento_fecha
- intentos_consecutivos (detecta patrones de reintento)
- fecha_rechazo
- fecha_resolucion (cuándo se resolvió, si aplica)
- resolucion_nota (ej: "Límite aumentado a $2M")
```

**Ventajas:**
- **Debugging:** Ver exactamente por qué se rechazó
- **Seguridad:** Detectar patrones de fraude
- **Fidelización:** Saber qué clientes tienen problemas recurrentes

## Endpoints Nuevos

### 1. GET `/api/tarjetas/movimientos/{id}/items`
Obtiene los items desglosados de un movimiento

**Respuesta:**
```json
{
  "movimiento_id": 42,
  "items": [
    {
      "id": 1,
      "numero": 1,
      "descripcion": "Comida",
      "id_categoria": 5,
      "categoria": "Alimentación",
      "monto": 20000
    },
    {
      "numero": 2,
      "descripcion": "Clases",
      "id_categoria": 8,
      "categoria": "Educación",
      "monto": 20000
    }
  ],
  "total_items": 2
}
```

### 2. GET `/api/tarjetas/diferidos/{id}/movimientos`
Obtiene las cuotas asociadas a un diferido

**Respuesta:**
```json
{
  "diferido_id": 5,
  "cuotas": [
    {
      "numero_cuota": 1,
      "tipo": "TOTAL",
      "estado": "PAGADA",
      "movimiento_id": 42,
      "valor": 400000,
      "fecha": "2026-04-12"
    },
    {
      "numero_cuota": 2,
      "tipo": "TOTAL",
      "estado": "PENDIENTE",
      "movimiento_id": null,
      "valor": null,
      "fecha": null
    }
  ],
  "total_cuotas": 12
}
```

### 3. GET `/api/tarjetas/rechazos`
Obtiene el historial de rechazos

**Parámetros:**
- `limit`: cuántos últimos rechazos (default 50)

**Respuesta:**
```json
{
  "rechazos": [
    {
      "id": 1,
      "id_tarjeta": 3,
      "motivo": "LIMITE_EXCEDIDO",
      "descripcion": "Límite de crédito disponible insuficiente",
      "valor_intento": 500000,
      "fecha_rechazo": "2026-04-12T10:30:00",
      "intentos_consecutivos": 2,
      "resuelto": true,
      "nota_resolucion": "Límite aumentado a $2M"
    }
  ],
  "total": 1
}
```

### 4. GET `/api/tarjetas/rechazos/estadisticas`
Análisis de patrones de rechazo

**Respuesta:**
```json
{
  "periodo": "90 días",
  "por_motivo": [
    {
      "motivo": "LIMITE_EXCEDIDO",
      "cantidad": 5,
      "valor_total": 2500000
    },
    {
      "motivo": "TARJETA_BLOQUEADA",
      "cantidad": 1,
      "valor_total": 100000
    }
  ],
  "por_tarjeta": [
    {
      "id_tarjeta": 3,
      "cantidad": 6,
      "ultimo_rechazo": "2026-04-12T10:30:00"
    }
  ],
  "sin_resolver": {
    "cantidad": 0,
    "valor_total": 0
  }
}
```

## Cambios en Backend

### `create_movimiento()` en `src/routes/tarjetas.py`
Ahora cuando se recibe un movimiento con items desglosados:
1. Crea el movimiento normalmente (con nota concatenada)
2. Inserta cada item en `movimiento_tarjeta_item`

```python
if items:  # Si viene con desglose
    for idx, item in enumerate(items, start=1):
        db.execute_non_query(
            "INSERT INTO movimiento_tarjeta_item ...",
            (mov_id, idx, item['descripcion'], item['id_categoria'], item['monto'])
        )
```

### `create_diferido()` en `src/routes/tarjetas.py`
Ahora cuando se crea un diferido:
1. Crea el diferido normalmente
2. Crea el movimiento de la 1ra cuota
3. Guarda items si aplica
4. Registra la relación en `detalle_diferido_movimiento`

```python
# Registrar relación cuota 1
db.execute_non_query(
    "INSERT INTO detalle_diferido_movimiento ...",
    (id_diferido, mov_id, 1, 'TOTAL', 'PENDIENTE')
)
```

## Vistas SQL Nuevas

### `v_items_por_movimiento`
Resumen de items agrupados por movimiento (sin necesidad de aplicación)

```sql
SELECT
    id_movimiento_tarjeta,
    COUNT(id_item) as cantidad_items,
    GROUP_CONCAT(descripcion) as items_list,
    SUM(monto) as total_items
FROM v_items_por_movimiento
WHERE id_persona = 1
GROUP BY id_movimiento_tarjeta;
```

### `v_diferidos_con_movimientos`
Diferidos con seguimiento automático de cuotas

```sql
SELECT
    id_diferido,
    descripcion,
    estado,
    cuotas_pagadas_sistema,
    cuotas_pendientes,
    cuotas_vencidas
FROM v_diferidos_con_movimientos
WHERE id_persona = 1;
```

## Aplicar la Migración

### Opción 1: Script Python (Recomendado)

```bash
cd /path/to/app-presopuesto
./venv/Scripts/python scripts/migrations/apply_migration_2026_04_12.py
```

**Salida esperada:**
```
[INFO] =========================================================================
[INFO] INICIANDO MIGRACIÓN: Items Desglosados, Diferidos y Rechazos
[INFO] =========================================================================
[INFO] Se encontraron 15 statements SQL para ejecutar
[INFO] [1/15] ✓ Ejecutado: CREATE TABLE IF NOT EXISTS movimiento_tarjeta_item...
...
[INFO] VERIFICACIÓN DE TABLAS:
[INFO]   ✓ Tabla movimiento_tarjeta_item: EXISTE
[INFO]   ✓ Tabla detalle_diferido_movimiento: EXISTE
[INFO]   ✓ Tabla movimiento_rechazo: EXISTE
```

### Opción 2: Verificar sin aplicar
```bash
./venv/Scripts/python scripts/migrations/apply_migration_2026_04_12.py --check-only
```

### Opción 3: SQL Directo (si prefieres)
```bash
mysql -u user -p app_presupuesto < base_de_datos/db/02_maintenance/schema/2026-04-12_items_diferidos_rechazos.sql
```

## Compatibilidad

- ✅ No elimina datos existentes
- ✅ No cambia tablas existentes
- ✅ Las migraciones son idempotentes (pueden re-ejecutarse sin problemas)
- ✅ Backward compatible: código antiguo sigue funcionando

## Próximas Mejoras

Con este modelo podrás:
1. **Reportes por ítem**: "¿Cuánto gasté en comida vs educación?"
2. **Análisis de diferidos**: "¿Cuáles diferidos tienen cuotas vencidas?"
3. **Dashboard de riesgos**: "¿Qué usuarios tienen más rechazos?"
4. **ML**: Entrenar modelos para predecir rechazos basados en patrones
5. **Alertas proactivas**: "¿Tarjeta bloqueada? Notificar al usuario"

## Documentación

- [BASE_DATOS.md](../../docs/BASE_DATOS.md) - Estructura general
- [DATA_MODEL.md](../../docs/DATA_MODEL.md) - Diagrama ER
- Script de migración: [2026-04-12_items_diferidos_rechazos.sql](../../base_de_datos/db/02_maintenance/schema/2026-04-12_items_diferidos_rechazos.sql)
