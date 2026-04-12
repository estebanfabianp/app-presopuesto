# Modelo de Datos

El modelo real del proyecto se basa en MySQL/MariaDB y hoy soporta tanto la aplicación Flet como la nueva capa web Flask.

## Entidades principales

### Persona

Tabla central de autenticación y perfil de usuario.

Campos relevantes:

- `id_persona`
- `nombre`
- `usuario`
- `correo_electronico`
- `clave`
- `estado`
- `fecha_creacion`
- `fecha_actualizacion`

Notas:

- `clave` puede venir de datos legacy y el sistema la migra a SHA-256 al primer login exitoso.
- `estado = 1` representa usuario activo.

### Cuenta

Representa cuentas financieras asociadas a una persona.

Campos usados por la capa web:

- `id_cuenta`
- `id_persona`
- datos de producto o cuenta según el esquema existente

Relación:

- `persona 1 -> N cuenta`

### Movimiento

Tabla principal de transacciones y movimientos financieros.

Campos relevantes:

- `id_movimiento`
- `codigo`
- `monto`
- `id_tipo`
- `id_estado`
- `id_categoria`
- `id_beneficiario`
- `id_cuenta`
- `numero_transaccion`
- `nota`
- `fecha_creacion`

Relaciones:

- `movimiento N -> 1 cuenta`
- `movimiento N -> 1 categoria`
- `movimiento N -> 1 tipo_movimiento`

### Tipo de movimiento

Catálogo usado para distinguir ingresos, gastos y otros tipos.

Campos relevantes:

- `id_tipo`
- `nombre`

### Categoría

Catálogo de categorías financieras usado por movimientos, presupuestos y ETL.

Campos relevantes:

- `id_categoria`
- `nombre`

### Presupuesto

Estructura de presupuesto por usuario.

Campos relevantes:

- `id_presupuesto`
- `id_persona`
- `nombre`
- `descripcion`
- `monto_total`
- `fecha_inicio`
- `fecha_fin`
- `fecha_creacion`

### Presupuesto categoría

Tabla pivote entre presupuesto y categoría.

Campos relevantes:

- `id_presupuesto`
- `id_categoria`

Relación:

- `presupuesto N <-> N categoria`

### Tarjeta y movimiento_tarjeta

Soportan el módulo de tarjeta de crédito y el ETL masivo.

Campos usados:

- `tarjeta.id_tarjeta`
- `movimiento_tarjeta.id_tarjeta`
- `movimiento_tarjeta.id_persona`
- `movimiento_tarjeta.fecha`
- `movimiento_tarjeta.valor`
- `movimiento_tarjeta.estado`
- `movimiento_tarjeta.nota`
- `movimiento_tarjeta.numero_transaccion`
- `movimiento_tarjeta.id_categoria`
- `movimiento_tarjeta.id_beneficiario`
- `movimiento_tarjeta.saldo`
- `movimiento_tarjeta.cuotas`

## Relaciones operativas

```text
persona
  ├── cuenta
  │     └── movimiento
  │            ├── categoria
  │            ├── tipo_movimiento
  │            └── beneficiario
  ├── presupuesto
  │     └── presupuesto_categoria
  │            └── categoria
  └── tarjeta
        └── movimiento_tarjeta
```

## Observaciones actuales

- El modelo web se apoya en el mismo esquema que la aplicación Flet.
- No toda la nomenclatura del esquema es uniforme; hay deuda histórica en algunos nombres.
- Antes de cambiar claves o relaciones, revisa `base_de_datos/db/01_core/create` y `docs/DATABASE_SETUP.md`.
