# Referencia API

Esta referencia cubre todos los endpoints REST disponibles en la capa web Flask.

## Base URL

```text
http://127.0.0.1:5000
```

Prefijo API:

```text
/api
```

## Autenticación

La API usa JWT Bearer tokens. Todos los endpoints requieren el encabezado:

```text
Authorization: Bearer <token>
```

Excepciones: `POST /api/auth/login` y `GET /health`.

## Endpoints

### Salud del servicio

#### `GET /health`

```json
{"status":"ok","app":"presopuesto-flask"}
```

---

### Auth (`/api/auth`)

#### `POST /api/auth/login`

Body:

```json
{"email": "usuario@correo.com", "password": "clave"}
```

Respuesta exitosa:

```json
{
  "token": "jwt-token",
  "user": {"id": 1, "email": "...", "nombre": "...", "username": "..."}
}
```

#### `GET /api/auth/me`

Devuelve el usuario autenticado a partir del token.

#### `POST /api/auth/logout`

Cierre de sesión del lado cliente.

---

### Dashboard (`/api/dashboard`)

#### `GET /api/dashboard/overview`

Dashboard extendido con:

- KPIs comparativos del mes: `ingresos_mes`, `gastos_mes`, `saldo_mes` (flujo), `saldo_total_cuentas` (suma real de saldos en `v_cuenta_saldos`),
- tasa de ahorro del mes (`tasa_ahorro_pct`),
- alertas financieras (presupuesto excedido, flujo negativo),
- flujo semanal,
- top categorías y beneficiarios,
- próximos compromisos (programadas).

Nota: `saldo_total_cuentas` refleja el patrimonio real en cuentas bancarias; `saldo_mes` es solo el flujo (ingresos - gastos) del mes en curso.

#### `GET /api/dashboard/summary`

Resumen: ingresos, gastos, saldo, presupuestos activos, transacciones recientes y datos para gráfico dona.

#### `GET /api/dashboard/gastos-por-categoria`

Estructura para gráficos de categorías.

#### `GET /api/dashboard/tendencia`

Serie de ingresos vs gastos por mes para gráfica de tendencia.

---

### Presupuesto (`/api/presupuesto`)

#### `GET /api/presupuesto`

Lista presupuestos del usuario autenticado.

#### `GET /api/presupuesto/<id>`

Obtiene un presupuesto específico.

#### `POST /api/presupuesto`

```json
{
  "nombre": "Presupuesto abril",
  "descripcion": "Control mensual",
  "monto": 1500000,
  "categoria": "Alimentación",
  "fecha_inicio": "2026-04-01",
  "fecha_fin": "2026-04-30"
}
```

#### `PUT /api/presupuesto/<id>`

Actualiza presupuesto existente.

#### `DELETE /api/presupuesto/<id>`

Elimina presupuesto y su relación en `presupuesto_categoria`.

#### `GET /api/presupuesto/hoja?year=2026&periodo=anual`

Obtiene una hoja de presupuesto anual o mensual con líneas de detalle, totales y valor real calculado por categoría.

#### `POST /api/presupuesto/hoja`

Guarda una hoja de presupuesto con múltiples líneas.

```json
{
  "year": 2026,
  "periodo": "mensual",
  "month": 1,
  "nombre": "Enero 2026",
  "descripcion": "Presupuesto mensual derivado",
  "lineas": [
    {
      "categoria": "Alimentación",
      "frecuencia": "Mensualmente",
      "importe": 1,
      "estimado": 1,
      "notas": "Base anual dividida en 12"
    }
  ]
}
```

#### `POST /api/presupuesto/hoja/derivar`

Deriva una hoja mensual desde el presupuesto anual del mismo año, dividiendo cada línea entre `12`.

---

### Transacciones (`/api/transacciones`)

#### `GET /api/transacciones`

Lista movimientos del usuario. Query param: `limit`.

#### `POST /api/transacciones`

```json
{
  "descripcion": "Compra supermercado",
  "categoria": "Compras",
  "tipo": "gasto",
  "monto": 120000,
  "fecha": "2026-04-12"
}
```

#### `PUT /api/transacciones/<id>`

Actualiza una transacción.

#### `DELETE /api/transacciones/<id>`

Elimina una transacción.

#### `GET /api/transacciones/import/catalogos`

Obtiene catálogos requeridos para importación ETL (personas, cuentas con `saldo_actual` calculado, tipos, categorías, estados, tarjetas).

#### `POST /api/transacciones/import/upload`

Recibe archivo Excel y procesa ETL según la fuente (`tarjeta_credito` o `cuenta_bancaria`). El cliente debe seleccionar una tarjeta o cuenta válida antes de enviar; el servidor devuelve mensaje descriptivo si no hay productos registrados.

Form data:

| Campo       | Requerido | Descripción                                        |
|-------------|-----------|----------------------------------------------------|
| `source`    | Sí        | `tarjeta_credito` o `cuenta_bancaria`              |
| `file`      | Sí        | Archivo `.xlsx` o `.xls`                           |
| `id_tarjeta`| Condicional| ID de tarjeta (cuando `source=tarjeta_credito`)   |
| `id_cuenta` | Condicional| ID de cuenta (cuando `source=cuenta_bancaria`)    |

**Nota operativa**: lanzar Flask con `use_reloader=False` para evitar que el watchdog interrumpa la carga del Excel.

#### `GET /api/transacciones/import/template?source=<origen>`

Descarga plantilla de ejemplo para el origen seleccionado.

#### `GET /api/transacciones/debug/status`

Endpoint de diagnóstico sin JWT. Devuelve estado del servidor y guía para verificar token desde consola del navegador.

#### `GET /api/transacciones/debug/whoami`

Devuelve `id_persona`, tarjetas y cuentas del usuario autenticado. Útil para confirmar qué IDs están disponibles al depurar importaciones.

---

### Reportes (`/api/reportes`)

#### `GET /api/reportes/data`

Devuelve `months`, `balance_trend` y `categories` con agregaciones SQL sobre `movimiento`.

---

### Tarjetas (`/api/tarjetas`)

#### `GET /api/tarjetas`

Lista tarjetas de crédito del usuario con saldo y estado.

#### `GET /api/tarjetas/<id>/movimientos`

Movimientos de la tarjeta con filtros de búsqueda, tipo y rango de fechas.

#### `GET /api/tarjetas/<id>/diferidos`

Compras diferidas activas de la tarjeta.

#### `GET /api/tarjetas/<id>/diferidos/<id_diferido>/detalle`

Detalle completo de una compra diferida: tabla de amortización, historial de pagos, historial de cambios.

#### `POST /api/tarjetas/<id>/diferidos`

Registra una nueva compra diferida.

#### `PUT /api/tarjetas/<id>/diferidos/<id_diferido>`

Modifica cuotas o tasa de una compra diferida.

#### `POST /api/tarjetas/<id>/diferidos/<id_diferido>/pagar`

Registra el pago de la siguiente cuota.

#### `DELETE /api/tarjetas/<id>/diferidos/<id_diferido>`

Liquida/elimina una compra diferida.

---

### Inversiones (`/api/inversiones`)

#### `GET /api/inversiones/summary`

Resumen de inversiones activas: total invertido, rendimiento estimado, próximos vencimientos.

---

### Metas de Ahorro (`/api/metas`)

#### `GET /api/metas/summary`

Resumen: total metas, monto acumulado, metas vigentes por vencer.

#### `GET /api/metas`

Lista metas del usuario.

#### `POST /api/metas`

Crea una nueva meta.

#### `PUT /api/metas/<id>`

Actualiza meta existente.

#### `DELETE /api/metas/<id>`

Elimina meta.

---

### Productos (`/api/productos`)

#### `GET /api/productos/summary`

Resumen de todos los productos financieros del usuario.

---

### Cuentas Bancarias (`/api/cuentas-bancarias`)

#### `GET /api/cuentas-bancarias`

Lista cuentas del usuario.

#### `POST /api/cuentas-bancarias`

Crea nueva cuenta.

#### `PUT /api/cuentas-bancarias/<id>`

Actualiza cuenta.

#### `DELETE /api/cuentas-bancarias/<id>`

Elimina cuenta.

#### `GET /api/cuentas-bancarias/catalogos`

Devuelve cuentas con `saldo_actual` calculado (saldo_inicial + ingresos - gastos), categorías, estados y productos. Usado por la vista de cuentas bancarias para mostrar el panel de saldos reales.

---

### Categorías (`/api/categorias`)

#### `GET /api/categorias`

Lista todas las categorías.

#### `POST /api/categorias`

Crea categoría.

#### `PUT /api/categorias/<id>`

Actualiza categoría.

#### `DELETE /api/categorias/<id>`

Elimina categoría.

---

### Beneficiarios (`/api/beneficiarios`)

#### `GET /api/beneficiarios`

Lista beneficiarios.

#### `POST /api/beneficiarios`

Crea beneficiario.

#### `PUT /api/beneficiarios/<id>`

Actualiza beneficiario.

#### `DELETE /api/beneficiarios/<id>`

Elimina beneficiario.

---

### Constantes (`/api/constantes`)

#### `GET /api/constantes`

Lista constantes del sistema.

#### `POST /api/constantes`

Crea constante.

#### `PUT /api/constantes/<id>`

Actualiza constante.

#### `DELETE /api/constantes/<id>`

Elimina constante.

---

### Transacciones Programadas (`/api/programadas`)

#### `GET /api/programadas`

Lista todas las transacciones programadas con datos de tipo, categoría y beneficiario.

#### `GET /api/programadas/<id>`

Obtiene una transacción programada específica con sus claves foráneas.

#### `POST /api/programadas`

Registra una nueva transacción programada.

Campos:

```json
{
  "id_tipo": 1,
  "fecha": "2026-05-01",
  "monto": 250000,
  "numero_transaccion": "REF-001",
  "id_categoria": 3,
  "id_beneficiario": 2,
  "repeticion": 0
}
```

`repeticion`: número de ejecuciones; `0` = indefinido.

#### `PUT /api/programadas/<id>`

Actualiza todos los campos de una transacción programada.

#### `DELETE /api/programadas/<id>`

Elimina la transacción programada.

#### `GET /api/programadas/catalogos`

Devuelve listas auxiliares para poblar selectores:

```json
{
  "tipos":         [{"id": 1, "nombre": "Gasto"}],
  "categorias":    [{"id": 1, "nombre": "Servicios"}],
  "beneficiarios": [{"id": 1, "nombre": "Empresa de servicios"}]
}
```

---

### Análisis de Consumo (`/api/analisis`)

#### `GET /api/analisis/resumen?meses=<n>`

KPIs del periodo: ingresos, gastos, ahorro neto, tasa de ahorro, gasto del mes actual y ejecución vs presupuesto vigente.

#### `GET /api/analisis/por-categoria?meses=<n>`

Gasto agrupado por categoría en el periodo, ordenado de mayor a menor (top 15).

#### `GET /api/analisis/tendencia?meses=<n>`

Serie mensual de ingresos, gastos y ahorro neto. Ideal para gráficos de líneas.

#### `GET /api/analisis/top-gastos?meses=<n>&limite=<l>`

Las `limite` transacciones de mayor monto en el periodo (por defecto top 10).

#### `GET /api/analisis/comparativa-meses`

Gasto por categoría comparando mes actual vs mes anterior con porcentaje de variación.

#### `GET /api/analisis/tarjetas`

Resumen de uso de cada tarjeta de crédito: límite, saldo, disponible, porcentaje de uso, gasto del mes y cantidad de diferidos activos.

Parámetro `meses` soportado (1–120) en todos los endpoints que lo aceptan. Valor especial `desde_2024` calculado dinámicamente en el cliente (meses desde enero 2024 hasta hoy).

---

### Optimización de Clasificación (`/api/optimizacion-categorias`)

#### `GET /api/optimizacion-categorias/resumen`

KPIs del módulo:

```json
{
  "reglas": 15,
  "conflictos": 2,
  "sin_categoria": 30,
  "reglas_beneficiario": 8,
  "conflictos_beneficiario": 1,
  "sin_beneficiario": 45
}
```

#### `GET /api/optimizacion-categorias/catalogos`

Devuelve `categorias` y `beneficiarios` disponibles para los selectores.

#### `GET /api/optimizacion-categorias/reglas`

Lista reglas automáticas de categoría con concepto, categoría sugerida, total de movimientos y fuente (`automatica` / `confirmada`).

#### `GET /api/optimizacion-categorias/conflictos`

Conceptos que tienen movimientos asignados a múltiples categorías (requieren resolución manual).

#### `GET /api/optimizacion-categorias/pendientes?limit=<n>`

Movimientos sin categoría asignada, ordenados por valor descendente. Incluye `origen` (`tarjeta` / `cuenta`).

#### `POST /api/optimizacion-categorias/aplicar`

Aplica todas las reglas automáticas de categoría a movimientos sin clasificar.

```json
{ "actualizados": 12 }
```

#### `POST /api/optimizacion-categorias/reglas/confirmar`

Confirma una regla de categoría:

```json
{ "concepto": "RAPPI", "id_categoria": 5 }
```

#### `POST /api/optimizacion-categorias/reglas/ignorar`

Excluye un concepto de la automatización de categorías.

#### `DELETE /api/optimizacion-categorias/reglas?concepto=<concepto>`

Elimina la regla confirmada de un concepto.

#### `POST /api/optimizacion-categorias/movimientos/asignar`

Asigna categoría a un movimiento individual:

```json
{ "origen": "tarjeta", "id_movimiento": 123, "id_categoria": 5 }
```

`origen`: `tarjeta` o `cuenta`.

---

#### Beneficiarios (sub-módulo de optimización)

#### `GET /api/optimizacion-categorias/reglas-beneficiario`

Lista reglas automáticas de beneficiario.

#### `GET /api/optimizacion-categorias/conflictos-beneficiario`

Conceptos con múltiples beneficiarios detectados.

#### `GET /api/optimizacion-categorias/pendientes-beneficiario?limit=<n>`

Movimientos sin beneficiario asignado.

#### `POST /api/optimizacion-categorias/aplicar-beneficiario`

Aplica reglas de beneficiario masivamente.

#### `POST /api/optimizacion-categorias/reglas-beneficiario/confirmar`

```json
{ "concepto": "RAPPI", "id_beneficiario": 3 }
```

#### `POST /api/optimizacion-categorias/reglas-beneficiario/ignorar`

```json
{ "concepto": "RAPPI" }
```

#### `DELETE /api/optimizacion-categorias/reglas-beneficiario?concepto=<concepto>`

Elimina regla de beneficiario.

#### `POST /api/optimizacion-categorias/movimientos/asignar-beneficiario`

```json
{ "origen": "cuenta", "id_movimiento": 456, "id_beneficiario": 3 }
```

---

## Códigos de respuesta comunes

| Código | Significado                             |
|--------|-----------------------------------------|
| `200`  | Operación exitosa                       |
| `201`  | Recurso creado                          |
| `400`  | Petición inválida o campos faltantes    |
| `401`  | Token ausente, inválido o expirado      |
| `404`  | Recurso no encontrado                   |
| `500`  | Error interno del servidor              |
