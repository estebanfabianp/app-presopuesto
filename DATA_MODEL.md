# Modelo de Datos

Este documento describe las principales tablas y relaciones del sistema.

---

## Diagrama Entidad-Relación (ER)

```
Usuario ──< Cuenta ──< Movimiento >── Categoría
        │           │
        │           └──< Presupuesto >── Categoría
        │
        ├──< Préstamo
        ├──< Tarjeta de Crédito
        └──< Activo
```

---

## Tablas Principales

### usuario
- `id_usuario` (PK)
- `nombre`
- `email`
- `hash_contrasena`
- `fecha_registro`

### cuenta
- `id_cuenta` (PK)
- `id_usuario` (FK)
- `nombre`
- `tipo`
- `saldo_inicial`
- `moneda`

### movimiento
- `id_movimiento` (PK)
- `id_cuenta` (FK)
- `monto`
- `tipo` (ingreso/gasto)
- `categoria`
- `descripcion`
- `fecha`

### presupuesto
- `id_presupuesto` (PK)
- `id_usuario` (FK)
- `categoria`
- `monto`
- `periodo`

### categoria
- `id_categoria` (PK)
- `nombre`
- `descripcion`

### prestamo
- `id_prestamo` (PK)
- `id_usuario` (FK)
- `monto`
- `moneda`
- `tasa_interes`
- `fecha_inicio`
- `fecha_fin`

### tarjeta_credito
- `id_tarjeta` (PK)
- `id_usuario` (FK)
- `nombre`
- `limite`
- `saldo`
- `fecha_corte`
- `fecha_pago`

### activo
- `id_activo` (PK)
- `id_usuario` (FK)
- `nombre`
- `valor`
- `tipo`

---

## Relaciones

- Un **usuario** puede tener varias **cuentas**, **presupuestos**, **préstamos**, **tarjetas de crédito** y **activos**.
- Una **cuenta** puede tener muchos **movimientos**.
- Un **movimiento** pertenece a una **cuenta** y a una **categoría**.
- Un **presupuesto** puede estar asociado a varias **categorías**.

---

Para detalles adicionales, consulta los scripts SQL en `/base de datos/`.
