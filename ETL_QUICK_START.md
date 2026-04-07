# 🚀 ETL Tarjeta de Crédito - Inicio Rápido

## ✅ Lo que hemos creado

Un sistema **ETL completo y robusto** para cargar transacciones de tarjeta de crédito desde Excel directo a la base de datos.

---

## 📁 Archivos Creados

```
src/business/
├── __init__.py (nuevo)
└── services/
    ├── __init__.py (nuevo)
    └── etl_tarjeta_credito.py (NUEVO - 430+ líneas)

docs/
└── ETL_TARJETA_CREDITO.md (NUEVA - Documentación completa)

test_etl_tarjeta.py (NUEVO - Script de prueba)

src/views/
└── nueva_trasacion.py (ACTUALIZADO - Integración ETL)
```

---

## 🎯 Cómo Usar en la App

### 1️⃣ Desde la UI
```
➜ Nueva Transacción
   ➜ Selecciona: "Carga a Tarjeta de Crédito"
   ➜ Selecciona tu tarjeta
   ➜ Click en "Carga masiva Excel"
   ➜ Selecciona tu archivo
   ➜ Sistema carga automáticamente
```

### 2️⃣ Archivo Excel esperado
Las columnas deben ser (case-insensitive):

```
Fecha    | Concepto     | Monto    | Categoría | Cuotas | Referencia
---------|--------------|----------|-----------|--------|------------
07/04/26 | Supermercado | 150000   | Compras   | 1      | Ref-001
08/04/26 | Gasolina     | 80000    | Transporte| 1      | Ref-002
09/04/26 | Restaurante  | 45000    | Alimentos | 3      | Ref-003
```

**Notas:**
- ✅ Solo **Concepto y Monto** son obligatorios
- ✅ Fecha es hoy si está vacía
- ✅ Categoría es "Compras" si está vacía
- ✅ Cuotas es 1 si está vacía
- ✅ Soporta múltiples nombres de columnas (fecha/date, monto/amount, etc.)

---

## 🧪 Test incluido

Para probar que funciona correctamente:

```bash
python test_etl_tarjeta.py
```

Output esperado:
```
✓ Archivo válido: True
✓ Procesadas: 3 transacción(es)
✓ Movimientos en BD: X
✓ Movimientos de tarjeta en BD: Y
```

---

## 🔧 Características del ETL

| Feature | Descripción |
|---------|-------------|
| **Validación** | Valida estructura, tipos, rangos |
| **Transformación** | Mapea categorías, genera códigos únicos |
| **Carga** | Inserta en movimiento + movimiento_tarjeta |
| **Errores por fila** | Reporta pero continúa procesando |
| **Transacciones** | Rollback automático si hay error |
| **Auditoría** | Registra errores y estadísticas |
| **Seguridad** | Prepared statements, validación de tipos |

---

## 📊 Ejemplo Completo

### Input: archivo Excel
```
Fecha       Concepto              Monto    Categoría  Cuotas  Referencia
2026-04-07  Supermercado Éxito    150000   Compras    1       Ref-001
2026-04-07  Restaurante La Canoa   45000   Alimentos  3       Ref-002
2026-04-08  Gasolina Petrobras     80000   Transporte 1       Ref-003
```

### Output: Base de datos
```sql
-- tabla: movimiento
INSERT INTO movimiento 
(codigo, monto, id_tipo, id_estado, id_producto, id_categoria, 
 numero_transaccion, nota, fecha_creacion, id_cuenta)
VALUES
('MOV-20260407120530-1', 150000, 2, 1, 1, 5, 'TRX-20260407120530-1', 'Supermercado Éxito - Ref-001', NOW(), 1),
('MOV-20260407120530-2', 45000, 2, 1, 1, 6, 'TRX-20260407120530-2', 'Restaurante La Canoa - Ref-002', NOW(), 1),
('MOV-20260408120530-3', 80000, 2, 1, 1, 7, 'TRX-20260408120530-3', 'Gasolina Petrobras - Ref-003', NOW(), 1);

-- tabla: movimiento_tarjeta
INSERT INTO movimiento_tarjeta 
(id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, 
 id_categoria, saldo, cuotas)
VALUES
(1, 1, '2026-04-07', 150000, 'compra', 'Supermercado Éxito', 'TRX-20260407120530-1', 5, 150000, 1),
(1, 1, '2026-04-07', 45000, 'compra', 'Restaurante La Canoa', 'TRX-20260407120530-2', 6, 45000, 3),
(1, 1, '2026-04-08', 80000, 'compra', 'Gasolina Petrobras', 'TRX-20260408120530-3', 7, 80000, 1);
```

---

## ⚠️ Validaciones Implementadas

```python
✅ Monto > 0
✅ Concepto no vacío
✅ Cuotas entre 1-36
✅ Fecha válida (multiple formatos)
✅ Categoría valid (crea si no existe)
✅ Archivo no vacío
✅ Excel con estructura correcta
✅ Usuario activo existe
✅ Tarjeta existe
```

---

## 🎓 Documentación

Para documentación completa y detallada:

👉 **[docs/ETL_TARJETA_CREDITO.md](./docs/ETL_TARJETA_CREDITO.md)**

Incluye:
- ✅ Estructura de datos
- ✅ Alias de columnas
- ✅ Ejemplos de uso
- ✅ Personalización
- ✅ Solución de problemas

---

## 💡 Flow Técnico

```
User selecciona Excel
          ↓
  ✅ _load_excel_with_etl()
          ↓
  🔍 validate_excel_file()
          ↓
  📂 ETL.process_file()
     • Leer y parsear Excel
     • Validar cada fila
     • Transformar datos
     • Insertar en BD (transacción)
          ↓
  ✅ Reportar resultados
          ↓
  📊 Base de datos actualizada
```

---

## 🚨 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Columnas faltantes" | Nombre de column incorrecto | Usa nombres: Fecha, Concepto, Monto, etc. |
| "Monto inválido" | Contiene letras | Usa: 150000 o 150.000 (solo números) |
| "Archivo vacío" | No hay datos | Agrega al menos 1 fila |
| "Usuario no encontrado" | Sin login | Haz login en la app primero |
| "Tarjeta no encontrada" | Ta tarjeta fue eliminada | Verifica que tarjeta exista |

---

## 📝 Próximos Pasos

Para probar:

1. **Descarga plantilla** desde la app (botón "Descargar Plantilla Excel")
2. **Completa con tus datos** siguiendo el formato
3. **Súbela usando** "Carga masiva Excel"
4. **Verifica en Resumen** que aparecen los movimientos

---

## 🔐 Seguridad

- ✅ Validación completa de tipos
- ✅ Prepared statements (sin SQL injection)
- ✅ Transacciones atómicas
- ✅ Rollback automático en errores
- ✅ Códigos únicos generados con timestamp

---

## 📞 Soporte

- Documentación: `docs/ETL_TARJETA_CREDITO.md`
- Pruebas: `python test_etl_tarjeta.py`
- Código fuente: `src/business/services/etl_tarjeta_credito.py`

---

**Created:** 2026-04-07  
**Status:** ✅ Tested and Working  
**Version:** 1.0
