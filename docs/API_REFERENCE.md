# Referencia de Funciones Internas — App Presupuesto

Esta referencia describe las principales funciones y módulos internos de la aplicación de escritorio desarrollada con Flet.

---

## 🖥️ Información General

### Arquitectura de la Aplicación
La aplicación **App Presupuesto** es una **aplicación de escritorio** desarrollada con Flet (no es una API web). Esta referencia documenta las funciones internas y módulos principales para desarrolladores que deseen contribuir o extender la funcionalidad.

### Estructura de Módulos
```
src/
├── views/          # Interfaces gráficas Flet
├── controllers/    # Lógica de negocio
├── models/         # Modelos de datos
├── database/       # Acceso a base de datos
└── utils/          # Utilidades y helpers
```

### Formato de Datos Interno
Todas las funciones manejan datos en formato Python nativo:

```python
# Ejemplo de estructura de usuario
{
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "fecha_creacion": datetime.datetime(...),
    "activo": True
}
```

---

## 🔐 Módulo de Autenticación (`persona_controller.py`)

### `autenticar_usuario(username, password)`

Autentica un usuario en el sistema.

**Parámetros:**
- `username` (str): Nombre de usuario o email
- `password` (str): Contraseña en texto plano

**Retorna:**
- `tuple`: (user_data, message)
  - `user_data` (dict): Datos del usuario si es exitoso, None si falla
  - `message` (str): Mensaje descriptivo del resultado

**Ejemplo de uso:**
```python
from src.controllers.persona_controller import autenticar_usuario

user, msg = autenticar_usuario("juan@email.com", "password123")
if user:
    print(f"Bienvenido {user['name']}")
else:
    print(f"Error: {msg}")
```

**Validaciones implementadas:**
- ✅ Sanitización de entrada (strip, validación de caracteres)
- ✅ Verificación de hash bcrypt
- ✅ Control de intentos fallidos
- ✅ Logging de eventos de seguridad

### `crear_usuario(nombre, email, password)`

Registra un nuevo usuario en el sistema.

**Parámetros:**
- `nombre` (str): Nombre completo del usuario
- `email` (str): Correo electrónico único
- `password` (str): Contraseña que se hasheará automáticamente

**Retorna:**
- `tuple`: (user_id, message)

**Validaciones:**
- Email único en el sistema
- Contraseña mínimo 6 caracteres
- Nombre no vacío

---

## 🖼️ Módulo de Vistas (`user_view.py`)

### `user_app(page: ft.Page)`

Función principal de la aplicación Flet que configura la vista de login.

**Parámetros:**
- `page` (ft.Page): Objeto página de Flet

**Configuración aplicada:**
```python
page.title = "Login de Usuario"
page.window_width = 400
page.window_height = 500
page.window_resizable = False
page.theme_mode = ft.ThemeMode.LIGHT
```

**Componentes principales:**
- `name_input`: TextField para usuario con validación
- `password_input`: TextField para contraseña con opción de mostrar/ocultar
- `login_button`: Botón que ejecuta autenticación
- `result_text`: Texto para feedback visual

### Validación en Tiempo Real

```python
def on_login_click(e):
    # Validación de campos vacíos
    if not name_input.value or not name_input.value.strip():
        result_text.value = "Por favor, ingrese un nombre de usuario"
        result_text.color = "red"
        return
    
    # Llamada al controlador
    user, msg = autenticar_usuario(
        name_input.value.strip(), 
        password_input.value.strip()
    )
```

---

## 🗄️ Módulo de Base de Datos (`connection.py`)

### `DatabaseManager`

Clase principal para manejo de conexiones a la base de datos.

#### `get_connection()`

Obtiene una conexión del pool de conexiones.

**Retorna:**
- `mysql.connector.connection`: Conexión activa a la BD

**Ejemplo de uso:**
```python
from src.database.connection import db_manager

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE activo = TRUE")
    results = cursor.fetchall()
finally:
    conn.close()
```

#### Configuración del Pool

```python
config = {
    'pool_name': 'flet_app_pool',
    'pool_size': 20,
    'pool_reset_session': True,
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

---

## 🔧 Módulo de Utilidades

### Módulo de Seguridad (`utils/security.py`)

#### `hash_password(password)`

Genera hash bcrypt de una contraseña.

**Parámetros:**
- `password` (str): Contraseña en texto plano

**Retorna:**
- `str`: Hash bcrypt de la contraseña

#### `verify_password(password, hash)`

Verifica una contraseña contra su hash.

**Parámetros:**
- `password` (str): Contraseña a verificar
- `hash` (str): Hash almacenado

**Retorna:**
- `bool`: True si coincide, False si no

#### `sanitize_input(data)`

Sanitiza entrada de usuario.

**Parámetros:**
- `data` (str): Datos de entrada

**Retorna:**
- `str`: Datos sanitizados

**Sanitización aplicada:**
```python
def sanitize_input(data):
    if isinstance(data, str):
        # Eliminar espacios
        data = data.strip()
        # Remover caracteres peligrosos
        data = re.sub(r'[<>"\';]', '', data)
        # Validar longitud
        if len(data) > MAX_INPUT_LENGTH:
            raise ValueError("Entrada demasiado larga")
    return data
```

### Módulo de Validadores (`utils/validators.py`)

#### `validate_email(email)`

Valida formato de email.

#### `validate_password_strength(password)`

Valida fortaleza de contraseña.

#### `validate_required_fields(**fields)`

Valida que campos requeridos no estén vacíos.

---

## 📊 Módulos de Datos (Models)

### Modelo Usuario (`models/persona.py`)

```python
class Persona:
    def __init__(self, id=None, nombre=None, email=None, password=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.fecha_creacion = None
        self.activo = True
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'fecha_creacion': self.fecha_creacion,
            'activo': self.activo
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea objeto desde diccionario"""
        return cls(**data)
```

---

## 🔄 Flujos de Trabajo Principales

### Flujo de Autenticación

```python
# 1. Usuario ingresa credenciales en UI
username = name_input.value
password = password_input.value

# 2. Vista valida formato básico
if not username or not password:
    show_error("Campos requeridos")
    return

# 3. Controlador procesa autenticación
user, message = autenticar_usuario(username, password)

# 4. Vista muestra resultado
if user:
    result_text.value = f"¡Bienvenido {user['name']}!"
    result_text.color = "green"
    # Navegar a dashboard (v0.6.0)
else:
    result_text.value = message
    result_text.color = "red"

page.update()
```

### Flujo de Validación

```python
# Cadena de validación implementada
def validate_user_input(username, password):
    # 1. Validación de formato
    username = sanitize_input(username)
    password = sanitize_input(password)
    
    # 2. Validación de reglas de negocio
    if len(username) < 3:
        raise ValueError("Usuario muy corto")
    
    if len(password) < 6:
        raise ValueError("Contraseña muy corta")
    
    # 3. Validación de existencia en BD
    # (implementado en persona_controller)
    
    return username, password
```
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
