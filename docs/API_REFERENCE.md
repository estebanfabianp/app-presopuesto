# API Reference - App Presupuesto

Documentación completa de la API RESTful del sistema de gestión financiera personal.

---

## 🌐 Información General

### Base URL
```
http://localhost:5000/api/v1
```

### Autenticación
La API utiliza **JWT (JSON Web Tokens)** para autenticación. Incluye el token en el header `Authorization`:

```http
Authorization: Bearer <jwt_token>
```

### Formato de Respuesta
Todas las respuestas siguen el formato JSON estándar:

```json
{
  "success": true,
  "data": {},
  "message": "Operación exitosa",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### Códigos de Estado HTTP
- `200` - OK: Operación exitosa
- `201` - Created: Recurso creado exitosamente
- `400` - Bad Request: Error en la solicitud
- `401` - Unauthorized: Token inválido o expirado
- `403` - Forbidden: Sin permisos para la operación
- `404` - Not Found: Recurso no encontrado
- `422` - Unprocessable Entity: Error de validación
- `500` - Internal Server Error: Error interno del servidor

---

## 🔐 Autenticación y Usuarios

### Registro de Usuario

**POST** `/auth/register`

Registra un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "password": "password123",
  "confirmar_password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "fecha_creacion": "2025-01-20T10:30:00Z"
  },
  "message": "Usuario registrado exitosamente"
}
```

### Login

**POST** `/auth/login`

Autentica un usuario y retorna tokens JWT.

**Request Body:**
```json
{
  "email": "juan@email.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@email.com",
      "rol": "usuario"
    }
  },
  "message": "Login exitoso"
}
```

### Refresh Token

**POST** `/auth/refresh`

Renueva el access token usando el refresh token.

**Headers:**
```http
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Token renovado exitosamente"
}
```

### Logout

**POST** `/auth/logout`

Invalida los tokens del usuario.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logout exitoso"
}
```

---

## 👤 Gestión de Usuarios

### Perfil de Usuario

**GET** `/users/profile`

Obtiene el perfil del usuario autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "rol": "usuario",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_actualizacion": "2025-01-20T10:30:00Z",
    "configuracion": {
      "moneda": "COP",
      "zona_horaria": "America/Bogota",
      "notificaciones_email": true
    }
  }
}
```

### Actualizar Perfil

**PUT** `/users/profile`

Actualiza la información del perfil de usuario.

**Request Body:**
```json
{
  "nombre": "Juan Carlos Pérez",
  "configuracion": {
    "moneda": "USD",
    "notificaciones_email": false
  }
}
```

### Cambiar Contraseña

**PUT** `/users/change-password`

Cambia la contraseña del usuario.

**Request Body:**
```json
{
  "password_actual": "password123",
  "password_nueva": "nuevaPassword456",
  "confirmar_password": "nuevaPassword456"
}
```

---

## 🏦 Gestión de Cuentas

### Listar Cuentas

**GET** `/accounts`

Obtiene todas las cuentas del usuario autenticado.

**Query Parameters:**
- `page` (int, opcional): Página para paginación (default: 1)
- `per_page` (int, opcional): Elementos por página (default: 20)
- `activo` (bool, opcional): Filtrar por estado activo

**Response:**
```json
{
  "success": true,
  "data": {
    "cuentas": [
      {
        "id": 1,
        "nombre": "Cuenta Corriente Bancolombia",
        "tipo": "corriente",
        "saldo_actual": 1500000.00,
        "moneda": "COP",
        "fecha_creacion": "2025-01-15T10:30:00Z",
        "activo": true
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

### Crear Cuenta

**POST** `/accounts`

Crea una nueva cuenta bancaria.

**Request Body:**
```json
{
  "nombre": "Cuenta Ahorros Banco Popular",
  "tipo": "ahorros",
  "saldo_inicial": 500000.00,
  "moneda": "COP",
  "descripcion": "Cuenta de ahorros principal"
}
```

### Obtener Cuenta

**GET** `/accounts/{id}`

Obtiene los detalles de una cuenta específica.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Cuenta Corriente Bancolombia",
    "tipo": "corriente",
    "saldo_inicial": 1000000.00,
    "saldo_actual": 1500000.00,
    "moneda": "COP",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "activo": true,
    "transacciones_recientes": 25
  }
}
```

### Actualizar Cuenta

**PUT** `/accounts/{id}`

Actualiza la información de una cuenta.

**Request Body:**
```json
{
  "nombre": "Cuenta Corriente Principal",
  "descripcion": "Cuenta principal para gastos mensuales"
}
```

### Eliminar Cuenta

**DELETE** `/accounts/{id}`

Desactiva una cuenta (soft delete).

**Response:**
```json
{
  "success": true,
  "message": "Cuenta desactivada exitosamente"
}
```

---

## 💰 Gestión de Transacciones

### Listar Transacciones

**GET** `/transactions`

Obtiene las transacciones del usuario.

**Query Parameters:**
- `page` (int): Página para paginación
- `per_page` (int): Elementos por página
- `cuenta_id` (int): Filtrar por cuenta específica
- `categoria_id` (int): Filtrar por categoría
- `tipo` (string): "ingreso", "gasto", "transferencia"
- `fecha_desde` (date): Fecha inicio (YYYY-MM-DD)
- `fecha_hasta` (date): Fecha fin (YYYY-MM-DD)
- `monto_min` (decimal): Monto mínimo
- `monto_max` (decimal): Monto máximo

**Response:**
```json
{
  "success": true,
  "data": {
    "transacciones": [
      {
        "id": 1,
        "monto": -50000.00,
        "descripcion": "Compra supermercado",
        "fecha": "2025-01-20",
        "tipo": "gasto",
        "categoria": {
          "id": 1,
          "nombre": "Alimentación",
          "color": "#FF5722"
        },
        "cuenta": {
          "id": 1,
          "nombre": "Cuenta Corriente"
        },
        "beneficiario": "Supermercado XYZ"
      }
    ],
    "resumen": {
      "total_ingresos": 2000000.00,
      "total_gastos": -450000.00,
      "balance": 1550000.00
    },
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

### Crear Transacción

**POST** `/transactions`

Registra una nueva transacción.

**Request Body:**
```json
{
  "monto": -75000.00,
  "descripcion": "Pago servicios públicos",
  "fecha": "2025-01-20",
  "cuenta_id": 1,
  "categoria_id": 3,
  "beneficiario": "Empresas Públicas de Medellín",
  "numero_referencia": "REF123456",
  "notas": "Pago mensual servicios"
}
```

### Obtener Transacción

**GET** `/transactions/{id}`

Obtiene los detalles de una transacción específica.

### Actualizar Transacción

**PUT** `/transactions/{id}`

Actualiza una transacción existente.

### Eliminar Transacción

**DELETE** `/transactions/{id}`

Elimina una transacción.

---

## 📊 Categorías

### Listar Categorías

**GET** `/categories`

Obtiene todas las categorías disponibles.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Alimentación",
      "descripcion": "Gastos en comida y bebidas",
      "tipo": "gasto",
      "color": "#FF5722",
      "icono": "restaurant",
      "padre_id": null,
      "subcategorias": [
        {
          "id": 10,
          "nombre": "Supermercado",
          "padre_id": 1
        }
      ]
    }
  ]
}
```

### Crear Categoría

**POST** `/categories`

Crea una nueva categoría.

**Request Body:**
```json
{
  "nombre": "Educación",
  "descripcion": "Gastos relacionados con educación",
  "tipo": "gasto",
  "color": "#2196F3",
  "icono": "school",
  "padre_id": null
}
```

---

## 💳 Tarjetas de Crédito

### Listar Tarjetas

**GET** `/credit-cards`

Obtiene las tarjetas de crédito del usuario.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "numero_enmascarado": "**** **** **** 1234",
      "banco": "Bancolombia",
      "limite_credito": 5000000.00,
      "saldo_actual": 1200000.00,
      "saldo_disponible": 3800000.00,
      "fecha_corte": 15,
      "fecha_pago": 5,
      "tasa_interes": 2.5,
      "estado": "activa"
    }
  ]
}
```

### Crear Tarjeta

**POST** `/credit-cards`

Registra una nueva tarjeta de crédito.

**Request Body:**
```json
{
  "numero_tarjeta": "1234567890123456",
  "banco": "Banco Popular",
  "limite_credito": 3000000.00,
  "fecha_corte": 20,
  "fecha_pago": 10,
  "tasa_interes": 3.0
}
```

---

## 🏠 Préstamos

### Listar Préstamos

**GET** `/loans`

Obtiene los préstamos del usuario.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "entidad": "Banco de Bogotá",
      "tipo": "vivienda",
      "monto_inicial": 100000000.00,
      "saldo_actual": 85000000.00,
      "tasa_interes": 8.5,
      "plazo_meses": 240,
      "cuota_mensual": 850000.00,
      "fecha_inicio": "2023-01-15",
      "fecha_fin": "2043-01-15",
      "estado": "activo"
    }
  ]
}
```

---

## 📈 Presupuestos

### Listar Presupuestos

**GET** `/budgets`

Obtiene los presupuestos del usuario.

**Query Parameters:**
- `activo` (bool): Filtrar por estado
- `año` (int): Filtrar por año
- `mes` (int): Filtrar por mes

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Presupuesto Enero 2025",
      "monto_total": 2000000.00,
      "monto_gastado": 1200000.00,
      "porcentaje_usado": 60.0,
      "fecha_inicio": "2025-01-01",
      "fecha_fin": "2025-01-31",
      "categorias": [
        {
          "categoria_id": 1,
          "nombre": "Alimentación",
          "monto_asignado": 400000.00,
          "monto_gastado": 350000.00,
          "porcentaje_usado": 87.5
        }
      ]
    }
  ]
}
```

### Crear Presupuesto

**POST** `/budgets`

Crea un nuevo presupuesto.

**Request Body:**
```json
{
  "nombre": "Presupuesto Febrero 2025",
  "fecha_inicio": "2025-02-01",
  "fecha_fin": "2025-02-28",
  "categorias": [
    {
      "categoria_id": 1,
      "monto_asignado": 450000.00
    },
    {
      "categoria_id": 2,
      "monto_asignado": 200000.00
    }
  ]
}
```

---

## 📊 Reportes y Análisis

### Resumen Financiero

**GET** `/reports/summary`

Obtiene un resumen financiero general.

**Query Parameters:**
- `periodo` (string): "mes", "trimestre", "año"
- `fecha` (date): Fecha de referencia

**Response:**
```json
{
  "success": true,
  "data": {
    "ingresos_totales": 3000000.00,
    "gastos_totales": 2200000.00,
    "balance_neto": 800000.00,
    "patrimonio_total": 15000000.00,
    "deudas_totales": 5000000.00,
    "patrimonio_neto": 10000000.00,
    "distribucion_gastos": [
      {
        "categoria": "Alimentación",
        "monto": 400000.00,
        "porcentaje": 18.2
      }
    ],
    "tendencia_mensual": [
      {
        "mes": "2024-12",
        "ingresos": 2800000.00,
        "gastos": 2100000.00
      }
    ]
  }
}
```

### Reporte por Categorías

**GET** `/reports/categories`

Análisis de gastos por categorías.

**Query Parameters:**
- `fecha_desde` (date): Fecha inicio
- `fecha_hasta` (date): Fecha fin
- `tipo` (string): "gasto", "ingreso"

### Flujo de Caja

**GET** `/reports/cash-flow`

Reporte de flujo de caja proyectado.

**Query Parameters:**
- `meses` (int): Número de meses a proyectar (default: 6)

### Exportar Datos

**GET** `/reports/export`

Exporta datos en diferentes formatos.

**Query Parameters:**
- `formato` (string): "csv", "excel", "pdf"
- `tipo` (string): "transacciones", "presupuestos", "resumen"
- `fecha_desde` (date): Fecha inicio
- `fecha_hasta` (date): Fecha fin

---

## 🔔 Notificaciones

### Listar Notificaciones

**GET** `/notifications`

Obtiene las notificaciones del usuario.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "titulo": "Presupuesto excedido",
      "mensaje": "Has superado el 90% del presupuesto de Alimentación",
      "tipo": "warning",
      "leida": false,
      "fecha_creacion": "2025-01-20T10:30:00Z"
    }
  ]
}
```

### Marcar como Leída

**PUT** `/notifications/{id}/read`

Marca una notificación como leída.

---

## ⚙️ Configuración

### Obtener Configuración

**GET** `/settings`

Obtiene la configuración del usuario.

### Actualizar Configuración

**PUT** `/settings`

Actualiza la configuración del usuario.

**Request Body:**
```json
{
  "moneda": "USD",
  "zona_horaria": "America/New_York",
  "notificaciones": {
    "email": true,
    "push": false,
    "presupuesto_excedido": true,
    "pagos_programados": true
  },
  "privacidad": {
    "mostrar_saldos": true,
    "compartir_estadisticas": false
  }
}
```

---

## 📈 Inversiones

### Listar Inversiones

**GET** `/investments`

Obtiene las inversiones del usuario.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "tipo": "accion",
      "simbolo": "ECOPETROL",
      "nombre": "Ecopetrol S.A.",
      "cantidad": 100,
      "precio_compra": 2500.00,
      "precio_actual": 2800.00,
      "valor_total": 280000.00,
      "ganancia_perdida": 30000.00,
      "porcentaje_cambio": 12.0,
      "fecha_compra": "2024-06-15"
    }
  ]
}
```

---

## ❌ Manejo de Errores

### Formato de Error Estándar

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error de validación",
    "details": {
      "email": ["El email es requerido"],
      "password": ["La contraseña debe tener al menos 8 caracteres"]
    }
  },
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### Códigos de Error Comunes

- `VALIDATION_ERROR` - Error de validación de datos
- `AUTHENTICATION_FAILED` - Fallo en autenticación
- `AUTHORIZATION_FAILED` - Sin permisos para la operación
- `RESOURCE_NOT_FOUND` - Recurso no encontrado
- `DUPLICATE_RESOURCE` - Recurso duplicado
- `BUSINESS_RULE_VIOLATION` - Violación de regla de negocio
- `EXTERNAL_SERVICE_ERROR` - Error en servicio externo
- `RATE_LIMIT_EXCEEDED` - Límite de peticiones excedido

---

## 🔄 Versionado de API

La API utiliza versionado en la URL:
- `/api/v1/` - Versión actual estable
- `/api/v2/` - Próxima versión (en desarrollo)

### Política de Deprecación

Las versiones se mantienen por al menos 12 meses después de deprecarse. Se notifica con 6 meses de anticipación.

---

## 📝 Notas Adicionales

### Rate Limiting
- **Límite general**: 1000 requests/hora por usuario
- **Autenticación**: 20 intentos/hora por IP
- **Reportes**: 10 exports/hora por usuario

### Paginación
Los endpoints que retornan listas soportan paginación:
- `page`: Número de página (empezando en 1)
- `per_page`: Elementos por página (max: 100)

### Filtrado y Ordenamiento
- `sort_by`: Campo para ordenar
- `sort_order`: "asc" o "desc"
- `filter[campo]`: Filtros específicos

### Webhooks (Próximamente)
Notificaciones automáticas para eventos importantes:
- Transacciones grandes
- Presupuestos excedidos
- Vencimiento de pagos

---

**💡 ¿Necesitas ayuda?**
- 📧 **Email**: estebanfabianp@gmail.com
- 📋 **Issues**: [GitHub Issues](https://github.com/tu-usuario/app-presopuesto/issues)
- 📚 **Documentación**: [Documentación completa](../README.md)

**Última actualización**: Enero 2025 | **Versión API**: v1.0.0
