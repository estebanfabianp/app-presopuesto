# Guía de Usuario

La aplicación está disponible como interfaz web Flask. La versión de escritorio Flet sigue operativa como legado.

## 1. Arranque

### Web Flask (modo principal)

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

### Escritorio Flet (modo legado)

```powershell
python main.py
```

## 2. Acceso web

Abre el navegador en:

```text
http://127.0.0.1:5000/
```

La aplicación redirige a login.

## 3. Login

La autenticación usa usuarios almacenados en la tabla `persona`.

Pasos:

1. ingresar correo o usuario,
2. ingresar contraseña,
3. si las credenciales son válidas se emite un JWT y se accede al dashboard.

## 4. Módulos web disponibles

### Dashboard (`/dashboard`)

Resumen financiero ampliado:

- KPIs del mes: ingresos, gastos, flujo del mes y **saldo total en cuentas** (patrimonio real acumulado en cuentas bancarias, calculado desde `v_cuenta_saldos`).
- Tasa de ahorro y estado de presupuestos activos.
- Alertas de presupuesto y flujo mensual.
- Gráficos de dona por categoría, tendencia mensual y flujo semanal.
- Rankings de categorías/beneficiarios y próximos compromisos programados.
- Meses recientes con presencia de movimientos bancarios y de tarjeta. Esta presencia no confirma que los extractos estén completos.

### Transacciones (`/transacciones`)

- Historial de movimientos con búsqueda y filtro por tipo.
- Crear, editar y eliminar movimientos.

### Presupuesto (`/presupuesto`)

- Usa la hoja anual o mensual y despliega cada categoría para revisar sus subcategorías.
- Guarda la hoja mensual para actualizar los valores utilizados en otras pantallas.
- La ejecución incluye compras positivas de tarjeta y excluye pagos bancarios identificados como `Pagos de Tarjeta de Crédito` para evitar duplicados. Los abonos se excluyen; posibles devoluciones requieren revisión.

### Dinero libre del mes (`/presupuesto/libre-mes`)

- Usa automáticamente ingresos y gastos fijos y variables de la hoja mensual guardada, más diferidos y cuotas pendientes de préstamos.
- Permite ajustar las cifras para simular otros escenarios. Es una proyección basada en presupuesto, no el saldo bancario real.
- La gráfica muestra la proporción comprometida y advierte si los compromisos superan los ingresos.
- No vuelvas a incluir en la hoja o en otros compromisos las mismas cuotas de préstamos o diferidos ya sumadas automáticamente: se contarían dos veces.

### Reportes (`/reportes`)

- Tendencia de balance mensual.
- Distribución de gastos por categoría con gráficos.

### Tarjetas de crédito (`/tarjetas`)

- KPIs: saldo total, disponible, cuotas diferidas del mes.
- Grilla de movimientos con filtros (búsqueda, tipo, rango de fechas).
- Tabla de compras diferidas con badge de vencimiento próximo.
- Modal por compra diferida con:
  - **Amortización**: tabla cuota a cuota.
  - **Histórico**: pagos realizados.
  - **Simulador**: comparativa de 3 escenarios de plazos.
  - **Pago Anticipado**: cálculo de ahorro en intereses.
  - **Historial**: log de cambios de tasa/cuotas.
- Registrar nueva compra diferida, modificar tasa/cuotas, pagar cuota, liquidar.

### Inversiones (`/inversiones`)

KPIs de inversiones activas: monto total, rendimiento estimado y próximos vencimientos.

### Préstamos (`/prestamos`)

1. Crea un préstamo con acreedor, capital, tasa efectiva anual, número y frecuencia de cuotas y fecha inicial.
2. Agrega seguros u otros cargos por cuota y consulta el plan estimado.
3. Registra pagos parciales o abonos a capital. Los pagos ordinarios se aplican primero a cargos, después a interés y por último a capital.
4. Opcionalmente registra el pago en una cuenta bancaria; el importe completo se registra como gasto. Evita duplicarlo si ya importaste el movimiento.

Las cuotas son una estimación: no incluyen intereses diarios, mora ni cambios automáticos de tasa.

### Metas de Ahorro (`/metas`)

1. Crea una meta con nombre, monto objetivo y fecha opcional.
2. Abre **Ver detalle** para registrar aportes o retiros y consultar su historial.
3. Consulta el ahorro acumulado, el monto faltante y el porcentaje de avance; el objetivo y la fecha se pueden editar.

Las metas son independientes de los presupuestos. Los movimientos se registran manualmente con fecha y hora actuales y **no transfieren dinero ni modifican cuentas bancarias**. Un retiro no puede superar el ahorro acumulado. Por ahora no se pueden eliminar metas ni movimientos; para corregir un importe se puede registrar un movimiento contrario.

### Mis Productos (`/productos`)

Vista consolidada de todos los productos financieros del usuario.

### Cuentas Bancarias (`/cuentas-bancarias`)

- CRUD de cuentas bancarias con tipo, moneda y saldo inicial.
- **Panel de saldos actuales**: muestra el saldo real de cada cuenta (saldo_inicial + movimientos) con card individual y card de total consolidado. Botón de refresco manual.
- Tabla de movimientos con paginación (25 por página por defecto, configurable a 10/25/50/100).
- La descripción del movimiento prioriza el campo `nota` sobre el `codigo`.

### Categorías (`/categorias`)

Administrar el catálogo de categorías usado en movimientos y presupuestos.

### Beneficiarios (`/beneficiarios`)

Administrar el catálogo de beneficiarios para transacciones.

### Constantes (`/constantes`)

Administrar constantes y parámetros del sistema.

### Transacciones Programadas (`/programadas`)

Gestión de pagos recurrentes y cobros automáticos:

- KPIs: total registradas, monto en gastos, monto en ingresos y próximas en 7 días.
- Filtro por texto y tipo (gasto / ingreso).
- Tabla con badge de alerta cuando la próxima ejecución es inminente.
- Crear, editar y eliminar transacciones programadas.
- Campos: tipo de movimiento, fecha de ejecución, monto, número de referencia, categoría, beneficiario y número de repeticiones (0 = ilimitado).

### Análisis de Consumo (`/analisis`)

Dashboard analítico con períodos móviles hasta hoy (1, 3, 6, 12, 24, 36 meses o desde enero de 2023 de forma aproximada):

- **KPIs**: ingresos, gastos, ahorro neto con tasa de ahorro, y ejecución del presupuesto vigente.
- **Gasto por categoría**: gráfico donut interactivo con las principales categorías del periodo.
- **Tendencia mensual**: gráfico de líneas comparando ingresos, gastos y ahorro mes a mes.
- **Comparativa mes actual vs anterior**: tabla por categoría con indicador de variación (↑↓).
- **Top gastos**: las 10 transacciones de mayor monto en el periodo seleccionado.
- **Uso de tarjetas**: cards por tarjeta con barra de capacidad utilizada, gasto del mes y diferidos activos.
- **Presupuesto por categoría**: importes de egreso de la hoja mensual guardada y gastos reales del mes, con subcategorías desplegables.
- **Salud financiera**: indicador orientativo del mes actual hasta hoy, independiente del filtro móvil. Usa ingresos y gastos reales, la marca de fijo o variable de cada categoría en la hoja mensual y el uso de tarjetas activas. Si faltan datos o clasificaciones consistentes, explica qué falta en lugar de dar una puntuación.

Las cifras principales incluyen cuentas y compras positivas de tarjeta; excluyen pagos bancarios de tarjeta identificados y abonos. La comparación enfrenta el mes actual parcial con el mes anterior completo. La proyección de fin de mes es lineal y puede ser inexacta. Anomalías, oportunidades, cohortes y fijo/variable aún se calculan solo con cuentas; la clasificación fijo/variable de esa sección es aproximada por nombre.

### Optimización de Clasificación (`/optimizacion-categorias`)

Módulo de clasificación automática de movimientos:

**Pestaña Reglas (categorías)**:
- Lista de reglas automáticas derivadas del historial de descripciones.
- Confirmar una regla la fija permanentemente; ignorar la excluye de la automatización.
- Botón **Aplicar reglas** para clasificar masivamente todos los movimientos pendientes.

**Pestaña Conflictos**:
- Descripciones con múltiples categorías distintas en el historial.
- Seleccionar la categoría correcta y confirmar para resolver.

**Pestaña Sin categoría**:
- Movimientos sin clasificar de tarjeta y cuenta bancaria.
- Filtros por origen, periodo y texto libre.
- Asignación individual o masiva con checkbox.

**Pestaña Beneficiarios**:
- Gestión equivalente para el campo beneficiario: reglas, conflictos y pendientes.
- Botón **Aplicar todo lo seguro** ejecuta simultamente reglas de categoría y beneficiario.

## 5. Navegación lateral (sidebar)

El menú lateral agrupa los módulos en secciones:

- **Principal**: Dashboard, Transacciones, Presupuesto, Dinero libre del mes, Reportes, Transacciones Programadas y Análisis.
- **Productos**: Mis Productos, Cuentas Bancarias, Tarjetas, Préstamos, Inversiones y Metas de Ahorro.
- **Catálogos**: Categorías, Optimización de Clasificación, Beneficiarios y Constantes.
- **Cuenta**: Perfil, Configuración.

## 6. ETL de tarjeta de crédito

El ETL de carga masiva desde Excel está disponible desde:

- interfaz web en `/transacciones` (pestaña Importar),
- interfaz de escritorio Flet (flujo legado).

Consulta `docs/ETL_TARJETA_CREDITO.md` para el formato de tarjetas y `docs/ETL_CUENTA_BANCARIA.md` para extractos bancarios.

## 7. Limitaciones conocidas

- La instalación Flet no está sincronizada con todas las mejoras recientes de la web.
- Los scripts SQL históricos pueden requerir saneamiento adicional en algunos entornos MariaDB.
- Algunas funciones avanzadas siguen dependiendo del flujo heredado.
