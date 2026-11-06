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

### Préstamos (`/api/prestamos`)

Todas las rutas requieren autenticación y están limitadas al propietario.
Los préstamos se registran en COP. Aplicar primero la migración
`base_de_datos/db/02_maintenance/2026-11-06_prestamos.sql` a la base existente;
no ejecutar el script de inicialización para actualizar una base con datos.

- `GET /api/prestamos` lista préstamos y saldos de capital.
- `POST /api/prestamos` crea el préstamo y las cuotas: recibe `nombre`,
  `acreedor`, `capital`, `tasa_ea` (porcentaje efectivo anual con hasta cuatro
  decimales), `numero_cuotas` (1–360), `frecuencia` (`semanal`, `quincenal`,
  `mensual`, `trimestral`, `anual`), `metodo` (`frances`, `capital_fijo`),
  `primera_fecha` (`AAAA-MM-DD`) y `cargos` (lista de `{nombre, monto}`).
- `GET /api/prestamos/<id>` devuelve el préstamo, las cuotas con cargos y su
  historial de pagos. `GET /api/prestamos/cuentas` devuelve cuentas en COP.
- `PUT /api/prestamos/<id>/cuotas/<numero>` ajusta `capital`, `interes` y
  `cargos`. Solo puede cambiarse capital e interés en la primera cuota
  pendiente sin pagos; en cuotas futuras solo se pueden cambiar cargos.
- `POST /api/prestamos/<id>/pagos` recibe `tipo` (`cuota` o `abono`),
  `numero_cuota` para pagos ordinarios, `monto`, `fecha`, `referencia` UUID e
  `id_cuenta` opcional. Una referencia repetida no registra un segundo pago.

La tasa se convierte a periodos iguales (52, 24, 12, 4 o 1 por año); para
quincenal los vencimientos son el día 15 y el último del mes. El plan es una
estimación: no calcula intereses diarios, mora ni variaciones de tasa. Los
pagos ordinarios se aplican en orden a cargos, interés y capital, y no pueden
exceder la cuota. Un abono extraordinario recalcula las cuotas pendientes sin
alterar sus cargos; si cancela el capital, se cancelan las cuotas pendientes y
sus cargos estimados. No se puede abonar mientras exista una cuota parcialmente
pagada. Si se selecciona una cuenta bancaria, se registra el importe completo
como gasto, incluyendo capital, lo cual afecta el dashboard.

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

#### `GET /api/dashboard/meses-con-movimientos`

Requiere autenticación. Devuelve `meses`, una lista de los últimos 12 meses
(incluido el actual) en orden descendente, con `mes` (`AAAA-MM`) y los
conteos `cuentas` y `tarjetas`. `ultimo_mes` contiene el último mes con
movimientos de cada tipo o `null`, incluso si es anterior al periodo mostrado.
Se usan las fechas de los movimientos hasta hoy, no la fecha de carga del
extracto; su presencia no garantiza que todos los extractos estén completos.

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

#### `GET /api/presupuesto/hoja?year=2026&periodo=anual&todas=true`

Obtiene una hoja de presupuesto anual o mensual con líneas de detalle, totales y valor real calculado por categoría. Soporta el parámetro `todas=true` (activo por defecto) que combina automáticamente todas las categorías del catálogo activo del usuario con sus importes reales ejecutados, permitiendo presupuestar directamente en formato grilla. Las líneas diferencian `tipo` (`ingreso` | `egreso`), `es_fijo` (booleano para egresos) y el resumen desglosa `ingresos_estimado`, `ingresos_real`, `egresos_estimado`, `egresos_real`, `fijos_total`, `variables_total`, `flujo_neto_estimado` y `flujo_neto_real`.

El gasto real incluye compras positivas de tarjeta y excluye movimientos bancarios en la categoría `Pagos de Tarjeta de Crédito` para evitar contarlas dos veces. Los abonos no se restan ni se suman, pues no existe una clasificación fiable entre pagos y devoluciones: `abonos_por_revisar` indica los que no se identifican como pagos bancarios evidentes. Revisa esos movimientos antes de interpretar el gasto neto; no se modifican los registros.

#### `POST /api/presupuesto/hoja`

Guarda una hoja de presupuesto con múltiples líneas, diferenciando ingresos y egresos, frecuencia y bandera de gasto fijo. Cada línea puede incluir `id_categoria`; se valida que pertenezca al catálogo disponible para el usuario. Cabecera, detalles y asociaciones se guardan en una única transacción.

```json
{
  "year": 2026,
  "periodo": "mensual",
  "month": 1,
  "nombre": "Enero 2026",
  "descripcion": "Presupuesto mensual derivado",
  "lineas": [
    {
      "categoria": "Salario",
      "tipo": "ingreso",
      "frecuencia": "Mensualmente",
      "importe": 3500000,
      "estimado": 3500000,
      "notas": "Nómina mensual"
    },
    {
      "categoria": "Luz",
      "tipo": "egreso",
      "frecuencia": "Mensualmente",
      "es_fijo": true,
      "importe": 150000,
      "estimado": 150000,
      "notas": "Factura ENEL"
    }
  ]
}
```

#### `GET /api/presupuesto/libre-mes`

Calcula el dinero libre del mes:
`dinero_libre = ingresos_mensuales - gastos_fijos_mensuales - gastos_variables_mensuales - deudas_mensuales (diferidos + préstamos) - otros`.
Toma los ingresos y egresos estimados de la hoja mensual guardada del mes actual, con los egresos separados en `gastos_fijos_mensuales` y `gastos_variables_mensuales`. Los ingresos reales de movimientos no se suman a los presupuestados; si no hay hoja mensual guardada, el ingreso automático es cero. Devuelve `gastos_presupuesto_detalle` y `presupuesto_mensual_guardado` para indicar su origen; `gastos_fijos_detalle` sigue disponible. Cada importe puede modificarse mediante el parámetro correspondiente. Los préstamos incluyen el saldo pendiente de capital, intereses y cargos de cuotas no canceladas con vencimiento en el mes actual. No incluyas esas mismas cuotas ni los diferidos también en el presupuesto o en otros compromisos; la aplicación advierte del posible doble conteo, pero no puede identificarlo automáticamente.

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

Las metas son independientes de los presupuestos. Los aportes y retiros son manuales y no crean transacciones ni modifican saldos bancarios. Para bases existentes aplicar la migración aditiva `base_de_datos/db/02_maintenance/2026-11-06_metas_ahorro.sql`; no convierte ni elimina presupuestos.

#### `GET /api/metas/summary`

Resumen de las metas reales, sus objetivos y su avance global según aportes menos retiros; los campos heredados `gasto_mes` y `presupuesto_vigente` son `null` porque no representan ahorro.

#### `GET /api/metas`

Lista metas del usuario con ahorrado, faltante y progreso. El progreso puede superar el 100%.

#### `POST /api/metas`

Crea una meta con `nombre`, `objetivo` positivo, `fecha_objetivo` opcional (ISO) y `referencia` UUID. Reintentar la misma solicitud con la misma referencia no crea una meta duplicada.

#### `GET /api/metas/<id>`

Devuelve la meta y su historial de movimientos manuales.

#### `PUT /api/metas/<id>`

Actualiza `nombre`, `objetivo` y `fecha_objetivo` sin modificar el historial; se permite un objetivo inferior al saldo.

#### `POST /api/metas/<id>/movimientos`

Registra `tipo` (`aporte` o `retiro`), `monto` positivo, `nota` opcional y `referencia` UUID. Se registra la fecha y hora del servidor. Un retiro no puede superar el ahorro; un reintento con la misma referencia y datos no duplica el registro. No se eliminan movimientos ni metas desde esta API.

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

#### `GET /api/analisis/vista-consumo?meses=<n>`

Datos principales de la pantalla: rango móvil desde la fecha actual menos `n` meses hasta hoy inclusive; ingresos y gastos reales, tendencia, categorías y principales movimientos. Los gastos incluyen compras positivas de tarjeta y excluyen pagos bancarios de tarjeta identificados y abonos. La ejecución compara el mes actual con los importes de egreso de la hoja mensual guardada; la comparativa utiliza el mes actual hasta hoy y el mes anterior completo. Los meses con movimientos no garantizan extractos completos. Los paneles de anomalías, oportunidades, cohortes y fijo/variable aún utilizan únicamente movimientos de cuentas.

#### `GET /api/analisis/score-salud`

Indicador orientativo del mes calendario hasta hoy, independiente del filtro móvil. Usa los ingresos y gastos reales de las mismas fuentes de `vista-consumo` y clasifica los gastos por ID de categoría según la marca `es_fijo` de la última hoja mensual guardada. No infiere clasificaciones por nombre ni por categoría padre. Si falta ingreso o gasto, una categoría no está en la hoja, tiene marcas contradictorias o una tarjeta activa carece de saldo o límite positivo, devuelve `score: null` y `razones`; no trata datos ausentes como cero. Devuelve `inicio`, `fin`, `nivel` y `componentes` (`tasa_ahorro`, `pct_gasto_fijo` y `uso_tarjetas`, este último `null` si no hay tarjetas activas).

La puntuación parte de 100: resta un punto por cada punto porcentual de ahorro bajo el 20%, medio punto por cada punto de gasto fijo sobre el 50% y 0,6 puntos por cada punto de uso promedio de tarjetas activas sobre el 50%; se limita a 0–100. Sin tarjetas activas no se aplica penalización por uso. Se excluye la variación mensual, ya que el mes actual es parcial y no es comparable con el mes anterior completo. La puntuación depende de extractos completos y saldos de tarjeta actualizados.

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

Los endpoints que aceptan `meses` lo validan según sus propios límites. En la pantalla, la opción «Desde enero de 2023 (aprox.)» calcula un número de meses móviles; no representa exactamente el 1 de enero de 2023. Los endpoints heredados de resumen, categoría, tendencia y comparativa no son la fuente principal de la pantalla y pueden usar criterios distintos a `vista-consumo`.

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
