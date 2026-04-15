# Arquitectura del Sistema

El sistema está consolidado como aplicación web Flask + Jinja con base de datos MySQL/MariaDB. La interfaz de escritorio Flet sigue disponible pero ya no es el foco de desarrollo activo.

## Vista general

```text
Flask + Jinja Web UI          Flet Desktop UI (heredado)
        |                              |
        |                              |
        +--------------+---------------+
                       |
               Blueprints Flask / Controllers
                       |
               DatabaseConnector
                       |
                 MySQL / MariaDB
```

## Capas principales

### Presentación

- `app.py`, `src/templates/`, `src/static/`: capa web principal en Flask.
- `src/routes/`: blueprints Flask con todos los endpoints y páginas.
- `main.py` y `src/views/`: interfaz de escritorio Flet (heredada, en proceso de deprecación).

### Lógica de negocio

- `src/controllers/`: lógica heredada, usada principalmente por Flet.
- `src/business/services/`: servicios específicos, incluido el ETL de tarjeta de crédito.
- `src/models/`: acceso a entidades y autenticación de usuario.

### Persistencia

- `src/database/db_connector.py`: acceso común a MySQL/MariaDB.
- `base_de_datos/db/`: scripts SQL, seeds y mantenimiento.

## Blueprints Flask registrados

| Blueprint              | Prefijo                 | Descripción                                  |
|------------------------|-------------------------|----------------------------------------------|
| `auth`                 | `/api/auth`             | Login JWT, logout, perfil                   |
| `dashboard`            | `/api/dashboard`        | Resumen financiero, gráficos                |
| `transacciones`        | `/api/transacciones`    | CRUD de movimientos                         |
| `presupuesto`          | `/api/presupuesto`      | CRUD de presupuestos y categorías           |
| `reportes`             | `/api/reportes`         | Agregaciones mensuales y por categoría      |
| `tarjetas`             | `/api/tarjetas`         | Tarjetas de crédito y compras diferidas     |
| `inversiones`          | `/api/inversiones`      | Seguimiento de inversiones                  |
| `metas`                | `/api/metas`            | Metas de ahorro                             |
| `productos`            | `/api/productos`        | Productos financieros consolidados          |
| `cuentas_bancarias`    | `/api/cuentas-bancarias`| Cuentas bancarias                           |
| `categorias`           | `/api/categorias`       | Catálogo de categorías                      |
| `beneficiarios`        | `/api/beneficiarios`    | Catálogo de beneficiarios                   |
| `constantes`           | `/api/constantes`       | Constantes del sistema                      |
| `programadas`          | `/api/programadas`      | Transacciones programadas (recurrentes)     |
| `analisis`             | `/api/analisis`         | Análisis de consumo e indicadores           |

## Componentes clave

### Autenticación

- `src/models/persona_model.py`: validación de credenciales y migración automática de contraseñas legacy.
- `src/routes/auth.py`: login JWT, logout y endpoint `/api/auth/me`.

### Tarjetas y compras diferidas

- `src/routes/tarjetas.py`: gestión completa de tarjetas de crédito, movimientos y compras diferidas por cuotas (amortización, historial, simulador, pago anticipado).

### Transacciones Programadas

- `src/routes/programadas.py`: CRUD de `transaccion_programada`, catálogos auxiliares (tipos, categorías, beneficiarios).
- `src/templates/programadas/index.html`: interfaz con KPIs, tabla con alertas de vencimiento y modal de edición.

### Análisis de Consumo

- `src/routes/analisis.py`: endpoints de resumen KPI, gasto por categoría, tendencia mensual, top gastos, comparativa mes a mes y uso de tarjetas.
- Helper `_get_meses(default, max_meses=120)` centraliza la conversión y validación del parámetro `meses` (rango 1–120).
- `src/templates/analisis/index.html`: dashboard analítico con Chart.js (donuts, líneas) y selector de periodo dinámico (1, 3, 6, 12, 24, 36 meses y opción `desde_2024`).

### Optimización de Clasificación

- `src/routes/optimizacion_categorias.py`: motor de reglas automáticas para categorías y beneficiarios, gestión de conflictos y asignación individual/masiva.
- `src/business/services/` (servicio subyacente): `get_categorias`, `get_beneficiarios`, `asignar_categoria_movimiento(origen, id_movimiento, id_categoria, user_id)`, equivalentes para beneficiario y reglas.
- Soporta dos orígenes de movimientos: `tarjeta` y `cuenta`.

### Saldos y Auditoría de Cuentas

- Vista `v_cuenta_saldos`: saldo real por cuenta calculado sobre `movimiento` (saldo_inicial + ingresos - gastos).
- Vista `v_resumen_saldos_persona`: totales consolidados por persona.
- Vista `v_producto_unificado`: unión de cuentas, tarjetas y préstamos.
- Tabla `auditoria_saldo_cuenta`: log de cambios de saldo con tipo de cambio y diferencia.
- Procedimiento `calc_saldo_cuenta`: cálculo estándar de saldo.
- El dashboard principal muestra `saldo_total_cuentas` (desde `v_cuenta_saldos`) como KPI de patrimonio real, separado del flujo del mes (`saldo_mes`).

- `src/business/services/etl_tarjeta_credito.py`: carga masiva desde Excel a `movimiento` y `movimiento_tarjeta`.
- `src/business/services/etl_cuenta_bancaria.py`: carga masiva de extractos bancarios a `movimiento`.

**Nota operativa**: al lanzar Flask en modo desarrollo el watchdog puede reiniciar el servidor mientras `openpyxl` carga módulos XML, interrumpiendo la importación. Usar `use_reloader=False` para evitarlo.

## Decisiones de diseño

- La capa web es ahora la interfaz principal; Flet queda como legado.
- Todos los endpoints de API requieren JWT excepto `/api/auth/login` y `/health`.
- La base de datos es la única fuente de verdad; no hay estado en memoria entre peticiones.
- La inicialización de BD prioriza seguridad operativa en reejecuciones sobre bases existentes.

## Limitaciones abiertas

- Scripts SQL históricos todavía requieren saneamiento para una instalación `full` completamente idempotente en algunos entornos MariaDB.
- Parte del código heredado sigue en `src/views/` y `src/controllers/` para uso de Flet.
