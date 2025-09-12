# Modelo de Datos

Este documento describe las principales tablas y relaciones del sistema, alineadas con la estructura real de la base de datos.

---

## Diagrama Entidad-Relación (ER)

![Diagrama ER](base%20de%20datos/modelo%20ENR.png)

```
Persona ──< Cuenta ──< Movimiento >── Categoría
       │           │
       │           └──< Presupuesto >── Categoría
       │
       ├──< Préstamo
       ├──< Tarjeta de Crédito
       └──< Activo
```

---

## Tablas Principales

### persona
- `id_persona` (PK)
- `nombre`
- `correo_electronico`
- `usuario`
- `hash_contrasena`
- `fecha_creacion`
- `fecha_actualizacion`
- `activo`

### cuenta
- `id_cuenta` (PK)
- `id_persona` (FK)
- `nombre`
- `tipo`
- `saldo_inicial`
- `moneda`
- `fecha_creacion`

### movimiento
- `id_movimiento` (PK)
- `codigo`
- `monto`
- `id_tipo` (FK a tipo_movimiento)
- `id_estado` (FK a estado_movimiento)
- `id_producto`
- `id_categoria` (FK)
- `id_beneficiario` (FK)
- `numero_transaccion`
- `nota`
- `fecha_creacion`
- `id_cuenta` (FK)

### presupuesto
- `id_presupuesto` (PK)
- `nombre`
- `descripcion`
- `monto_total`
- `fecha_inicio`
- `fecha_fin`
- `id_persona` (FK)
- `fecha_creacion`

### presupuesto_categoria
- `id_presupuesto` (PK, FK)
- `id_categoria` (PK, FK)

### categoria
- `id_categoria` (PK)
- `nombre`

### prestamo
- `id_prestamo` (PK)
- `fecha`
- `id_estado` (FK a estado_prestamo)
- `moneda`
- `saldo_inicial`
- `limite_credito`
- `fecha_creacion`
- `id_persona` (FK)

### prestamo_movimiento
- `persona_id_persona` (PK, FK)
- `prestamo_id_prestamo` (PK, FK)
- `valor`
- `interes`
- `numero_transaccion`
- `seguro`
- `saldo`

### tarjeta_credito
- `id_tarjeta` (PK)
- `id_producto`
- `numero_tarjeta`
- `limite_credito`
- `saldo_actual`
- `fecha_corte`
- `fecha_pago`
- `fecha_creacion`
- `id_estado` (FK a estado_tarjeta)

### movimiento_tarjeta
- `id_movimiento_tarjeta` (PK)
- `id_tarjeta` (FK)
- `id_persona` (FK)
- `fecha`
- `valor`
- `estado`
- `nota`
- `numero_transaccion`
- `id_categoria` (FK)
- `id_beneficiario` (FK)
- `saldo`
- `cuotas`

### activo
- `id_activo` (PK)
- `nombre_activo`
- `valor`
- `depreciacion`
- `id_persona` (FK)
- `fecha_creacion`

### beneficiario
- `id_beneficiario` (PK)
- `nombre`

### deuda_financiada
- `id_deuda` (PK)
- `entidad`
- `monto_inicial`
- `saldo_actual`
- `numero_transaccion`
- `tasa_interes`
- `fecha_inicio`
- `fecha_fin`
- `id_persona` (FK)

### tipo_movimiento
- `id_tipo` (PK)
- `nombre`

### estado_movimiento
- `id_estado` (PK)
- `nombre`

### estado_prestamo
- `id_estado` (PK)
- `nombre`

### estado_tarjeta
- `id_estado` (PK)
- `nombre`

### moneda
- `codigo` (PK)
- `nombre`

---

## Relaciones

- Una **persona** puede tener varias **cuentas**, **presupuestos**, **préstamos**, **tarjetas de crédito**, **activos** y **movimientos**.
- Una **cuenta** puede tener muchos **movimientos**.
- Un **movimiento** pertenece a una **cuenta**, una **categoría**, un **beneficiario**, un **tipo** y un **estado**.
- Un **presupuesto** puede estar asociado a varias **categorías** (tabla intermedia).
- Un **préstamo** puede tener varios **movimientos** asociados (tabla intermedia).
- Una **tarjeta de crédito** puede tener varios **movimientos** asociados.
- Catálogos de **moneda** y **estado** normalizan los valores en las tablas principales.

---

## Vistas y Automatización

- **Triggers**: Actualizan automáticamente los saldos de cuentas, tarjetas y préstamos tras operaciones en sus movimientos.
- **Procedimientos**: Permiten recalcular manualmente los saldos.
- **Funciones**: Reclasificación de categorías de movimientos por rango de fecha.
- **Vistas**: Existen vistas para resúmenes y detalles de saldos y movimientos (ver archivos `create_views.sql`).

---

Para detalles adicionales, consulta los scripts SQL en `/base de datos/script_bd/create/`.
