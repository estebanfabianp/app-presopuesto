# Modelo de Datos

Este documento describe las principales tablas y relaciones del sistema, alineadas con la estructura real de la base de datos.

---

## Diagrama Entidad-Relación (ER)

![Diagrama ER](../base_de_datos/modelo_ENR.png)

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
- `rol` (usuario, admin)
- `preferencias` (JSON, configuración personalizada)

### cuenta
- `id_cuenta` (PK)
- `id_persona` (FK)
- `nombre`
- `tipo`
- `saldo_inicial`
- `moneda`
- `fecha_creacion`
- `fecha_actualizacion`
- `activo`

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
- `fecha_actualizacion`
- `id_cuenta` (FK)
- `usuario_creador` (FK a persona)
- `origen` (manual, importado, automático)

### presupuesto
- `id_presupuesto` (PK)
- `nombre`
- `descripcion`
- `monto_total`
- `fecha_inicio`
- `fecha_fin`
- `id_persona` (FK)
- `fecha_creacion`
- `fecha_actualizacion`
- `activo`

### presupuesto_categoria
- `id_presupuesto` (PK, FK)
- `id_categoria` (PK, FK)

### categoria
- `id_categoria` (PK)
- `nombre`
- `descripcion`
- `tipo` (ingreso, gasto, transferencia)
- `color`

### prestamo
- `id_prestamo` (PK)
- `fecha`
- `id_estado` (FK a estado_prestamo)
- `moneda`
- `saldo_inicial`
- `limite_credito`
- `fecha_creacion`
- `fecha_actualizacion`
- `id_persona` (FK)
- `descripcion`

### prestamo_movimiento
- `persona_id_persona` (PK, FK)
- `prestamo_id_prestamo` (PK, FK)
- `valor`
- `interes`
- `numero_transaccion`
- `seguro`
- `saldo`
- `fecha`
- `nota`

### tarjeta_credito
- `id_tarjeta` (PK)
- `id_producto`
- `numero_tarjeta`
- `limite_credito`
- `saldo_actual`
- `fecha_corte`
- `fecha_pago`
- `fecha_creacion`
- `fecha_actualizacion`
- `id_estado` (FK a estado_tarjeta)
- `id_persona` (FK)

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
- `fecha_actualizacion`
- `tipo`
- `descripcion`

### beneficiario
- `id_beneficiario` (PK)
- `nombre`
- `tipo`
- `contacto`

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
- `descripcion`

### tipo_movimiento
- `id_tipo` (PK)
- `nombre`
- `descripcion`

### estado_movimiento
- `id_estado` (PK)
- `nombre`
- `descripcion`

### estado_prestamo
- `id_estado` (PK)
- `nombre`
- `descripcion`

### estado_tarjeta
- `id_estado` (PK)
- `nombre`
- `descripcion`

### moneda
- `codigo` (PK)
- `nombre`
- `simbolo`

### notificacion
- `id_notificacion` (PK)
- `id_persona` (FK)
- `mensaje`
- `tipo`
- `leida`
- `fecha_creacion`

### configuracion_usuario
- `id_configuracion` (PK)
- `id_persona` (FK)
- `preferencias` (JSON)
- `fecha_actualizacion`

### log_actividad
- `id_log` (PK)
- `id_persona` (FK)
- `accion`
- `detalle`
- `fecha`

### inversion
- `id_inversion` (PK)
- `tipo_inversion`
- `valor_inicial`
- `valor_actual`
- `fecha_inicio`
- `fecha_fin`
- `id_persona` (FK)
- `descripcion`
- `rentabilidad`
- `fecha_creacion`
- `fecha_actualizacion`

--- 

## Relaciones

- Una **persona** puede tener varias **cuentas**, **presupuestos**, **préstamos**, **tarjetas de crédito**, **activos**, **inversiones** y **movimientos**.
- Una **cuenta** puede tener muchos **movimientos**.
- Un **movimiento** pertenece a una **cuenta**, una **categoría**, un **beneficiario**, un **tipo** y un **estado**.
- Un **presupuesto** puede estar asociado a varias **categorías** (tabla intermedia).
- Un **préstamo** puede tener varios **movimientos** asociados (tabla intermedia).
- Una **tarjeta de crédito** puede tener varios **movimientos** asociados.
- Catálogos de **moneda** y **estado** normalizan los valores en las tablas principales.

--- 

## Vistas y Automatización

- **Triggers**: Actualizan automáticamente los saldos de cuentas, tarjetas y préstamos tras operaciones en sus movimientos. También registran logs de actividad y auditoría.
- **Procedimientos**: Permiten recalcular manualmente los saldos y generar reportes personalizados.
- **Funciones**: Reclasificación de categorías de movimientos por rango de fecha, cálculo de intereses y alertas automáticas.
- **Vistas**: Existen vistas para resúmenes y detalles de saldos, movimientos, presupuestos y reportes avanzados (ver archivos `create_views.sql`).

---

Para detalles adicionales, consulta los scripts SQL en `/base de datos/script_bd/create/` y la documentación técnica del proyecto.
#archivoMD