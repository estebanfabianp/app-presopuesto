# Referencia de la API — Sistema de Gestión de Presupuestos

Esta referencia describe los principales endpoints REST disponibles en la API.

---

## Autenticación

### POST `/api/login`
Inicia sesión de usuario.
- **Body:** `{ "email": "usuario@correo.com", "password": "..." }`
- **Respuesta:** Token de autenticación o error.

### POST `/api/register`
Registra un nuevo usuario.
- **Body:** `{ "nombre": "...", "email": "...", "password": "..." }`
- **Respuesta:** Usuario creado o error.

---

## Usuarios

### GET `/api/usuarios`
Lista todos los usuarios (requiere permisos de admin).

### GET `/api/usuarios/<id>`
Obtiene los datos de un usuario específico.

### PUT `/api/usuarios/<id>`
Actualiza los datos de un usuario.

### DELETE `/api/usuarios/<id>`
Elimina un usuario.

---

## Cuentas

### GET `/api/cuentas`
Lista todas las cuentas del usuario autenticado.

### POST `/api/cuentas`
Crea una nueva cuenta.
- **Body:** `{ "nombre": "...", "tipo": "...", "saldo_inicial": 0 }`

### PUT `/api/cuentas/<id>`
Actualiza una cuenta existente.

### DELETE `/api/cuentas/<id>`
Elimina una cuenta.

---

## Movimientos

### GET `/api/movimientos`
Lista movimientos filtrados (por cuenta, fecha, categoría, etc.).

### POST `/api/movimientos`
Registra un nuevo movimiento.
- **Body:** `{ "cuenta_id": 1, "monto": 100, "tipo": "gasto", "categoria": "...", "descripcion": "...", "fecha": "YYYY-MM-DD" }`

### PUT `/api/movimientos/<id>`
Actualiza un movimiento.

### DELETE `/api/movimientos/<id>`
Elimina un movimiento.

---

## Presupuestos

### GET `/api/presupuestos`
Lista los presupuestos del usuario.

### POST `/api/presupuestos`
Crea un nuevo presupuesto.
- **Body:** `{ "categoria": "...", "monto": 500, "periodo": "2024-06" }`

### PUT `/api/presupuestos/<id>`
Actualiza un presupuesto.

### DELETE `/api/presupuestos/<id>`
Elimina un presupuesto.

---

## Reportes

### GET `/api/reportes/resumen`
Devuelve un resumen financiero (ingresos, gastos, saldo, etc.).

### GET `/api/reportes/categorias`
Devuelve el total de gastos por categoría.

---

## Otros recursos

- **Préstamos:** `/api/prestamos`
- **Tarjetas de crédito:** `/api/tarjetas`
- **Inversiones:** `/api/inversiones`
- **Activos:** `/api/activos`

---

## Notas

- Todos los endpoints requieren autenticación (token JWT) salvo `/api/login` y `/api/register`.
- Los endpoints pueden variar según la versión y configuración del backend.
- Para detalles sobre parámetros y respuestas, consulta la documentación técnica o el código fuente.

---
