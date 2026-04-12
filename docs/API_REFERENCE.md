# Referencia API

Esta referencia cubre la capa web Flask actualmente disponible en el proyecto.

## Base URL

En desarrollo local:

```text
http://127.0.0.1:5000
```

Prefijo API:

```text
/api
```

## Autenticación

La API usa JWT.

Encabezado esperado:

```text
Authorization: Bearer <token>
```

## Endpoints

### Salud del servicio

#### `GET /health`

Valida que la aplicación Flask esté levantada.

Respuesta esperada:

```json
{"status":"ok","app":"presopuesto-flask"}
```

### Auth

#### `POST /api/auth/login`

Body:

```json
{
  "email": "usuario@correo.com",
  "password": "clave"
}
```

Respuesta exitosa:

```json
{
  "token": "jwt-token",
  "user": {
    "id": 1,
    "email": "usuario@correo.com",
    "nombre": "Usuario",
    "username": "usuario"
  }
}
```

Notas:

- La autenticación se resuelve con `PersonaModel`.
- El `identity` del JWT se emite como string por compatibilidad.
- Si la contraseña está en formato legacy, puede migrarse automáticamente al primer login.

#### `GET /api/auth/me`

Devuelve el usuario autenticado a partir del token.

#### `POST /api/auth/logout`

Respuesta simple de cierre de sesión del lado cliente.

### Dashboard

#### `GET /api/dashboard/summary`

Entrega resumen del dashboard web.

Estado actual:

- endpoint operativo,
- aún usa parte de datos demo.

#### `GET /api/dashboard/gastos-por-categoria`

Entrega estructura para gráficos de categorías.

Estado actual:

- endpoint operativo,
- aún usa parte de datos demo.

### Presupuesto

#### `GET /api/presupuesto`

Lista presupuestos del usuario autenticado.

#### `GET /api/presupuesto/<id>`

Obtiene un presupuesto específico.

#### `POST /api/presupuesto`

Crea presupuesto.

Campos comunes:

```json
{
  "nombre": "Presupuesto abril",
  "descripcion": "Control mensual",
  "monto": 1500000,
  "periodo": "mensual",
  "categoria": "Alimentación",
  "fecha_inicio": "2026-04-01",
  "fecha_fin": "2026-04-30"
}
```

#### `PUT /api/presupuesto/<id>`

Actualiza presupuesto existente.

#### `DELETE /api/presupuesto/<id>`

Elimina presupuesto y su relación en `presupuesto_categoria`.

### Transacciones

#### `GET /api/transacciones`

Lista movimientos del usuario.

Query params soportados actualmente:

- `limit`

#### `POST /api/transacciones`

Crea una transacción.

Campos comunes:

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

Actualiza una transacción existente.

#### `DELETE /api/transacciones/<id>`

Elimina la transacción.

### Reportes

#### `GET /api/reportes/data`

Devuelve:

- `months`
- `balance_trend`
- `categories`

Fuente:

- agregaciones SQL sobre `movimiento`, `cuenta`, `tipo_movimiento` y `categoria`.

## Códigos de respuesta comunes

- `200`: operación exitosa.
- `201`: recurso creado.
- `400`: petición inválida.
- `401`: token ausente, inválido o expirado.
- `404`: recurso no encontrado.
- `500`: error interno.

## Limitaciones actuales

- La API web aún no cubre todos los módulos existentes en Flet.
- El dashboard necesita terminar de conectarse a datos reales.
- No hay documentación OpenAPI formal en el repositorio actual.
