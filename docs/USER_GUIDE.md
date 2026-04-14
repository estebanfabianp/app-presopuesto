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

- KPIs del mes con variación vs mes anterior (ingresos, gastos, saldo).
- Tasa de ahorro y estado de presupuestos activos.
- Alertas de presupuesto y flujo mensual.
- Gráficos de dona por categoría, tendencia mensual y flujo semanal.
- Rankings de categorías/beneficiarios y próximos compromisos programados.

### Transacciones (`/transacciones`)

- Historial de movimientos con búsqueda y filtro por tipo.
- Crear, editar y eliminar movimientos.

### Presupuesto (`/presupuesto`)

- Listado de presupuestos con avance de ejecución.
- Crear, editar y eliminar presupuestos.
- Asociar categorías a cada presupuesto.

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

### Metas de Ahorro (`/metas`)

Crear y seguir metas de ahorro vinculadas a presupuestos. Ver progreso y metas por vencer.

### Mis Productos (`/productos`)

Vista consolidada de todos los productos financieros del usuario.

### Cuentas Bancarias (`/cuentas-bancarias`)

CRUD de cuentas bancarias con saldo y tipo de cuenta.

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

Dashboard analítico con selector de periodo (1, 3, 6 o 12 meses):

- **KPIs**: ingresos, gastos, ahorro neto con tasa de ahorro, y ejecución del presupuesto vigente.
- **Gasto por categoría**: gráfico donut interactivo con las principales categorías del periodo.
- **Tendencia mensual**: gráfico de líneas comparando ingresos, gastos y ahorro mes a mes.
- **Comparativa mes actual vs anterior**: tabla por categoría con indicador de variación (↑↓).
- **Top gastos**: las 10 transacciones de mayor monto en el periodo seleccionado.
- **Uso de tarjetas**: cards por tarjeta con barra de capacidad utilizada, gasto del mes y diferidos activos.

## 5. Navegación lateral (sidebar)

El menú lateral agrupa los módulos en secciones:

- **Principal**: Dashboard, Transacciones, Presupuesto, Reportes, Transacciones Programadas, Análisis.
- **Productos**: Mis Productos, Cuentas Bancarias, Tarjetas, Inversiones, Metas de Ahorro.
- **Catálogos**: Categorías, Beneficiarios, Constantes.
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
