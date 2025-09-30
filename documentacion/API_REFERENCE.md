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

---

## 🚀 Funciones de Configuración

### Configuración de la Aplicación

```python
def setup_app_config():
    """Configura parámetros globales de la aplicación"""
    return {
        'window_width': 400,
        'window_height': 500,
        'window_resizable': False,
        'theme_mode': ft.ThemeMode.LIGHT,
        'title': 'App Presupuesto'
    }
```

### Configuración de Base de Datos

```python
def get_db_config():
    """Obtiene configuración de BD desde variables de entorno"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'presupuesto_db'),
        'user': os.getenv('DB_USER', 'app_user'),
        'password': os.getenv('DB_PASSWORD', '')
    }
```

---

## 🧪 Funciones de Testing

### Funciones Mock para Testing

```python
def mock_autenticar_usuario(username, password):
    """Función mock para testing"""
    if username and password:
        return {
            "id": 1,
            "name": username,
            "email": f"{username}@test.com"
        }, f"Usuario {username} autenticado correctamente"
    return None, "Error: Usuario y contraseña son requeridos"
```

### Datos de Prueba

```python
SAMPLE_USERS = [
    {
        "nombre": "Usuario Test",
        "email": "test@test.com",
        "username": "testuser",
        "password": "test123"
    }
]
```

---

## 📝 Logging y Debugging

### Sistema de Logs

```python
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Loggers especializados
security_logger = logging.getLogger('security')
db_logger = logging.getLogger('database')
ui_logger = logging.getLogger('ui')
```

### Funciones de Debug

```python
def debug_database_connection():
    """Prueba conexión a base de datos"""
    try:
        conn = get_db_connection()
        return "✅ Conexión exitosa"
    except Exception as e:
        return f"❌ Error: {e}"

def debug_user_authentication(username, password):
    """Prueba función de autenticación"""
    try:
        result = autenticar_usuario(username, password)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Error: {e}"
```

---

## 🔮 Módulos Futuros (Planificados)

### Dashboard Controller (v0.6.0)

```python
# Funciones planificadas
def get_dashboard_data(user_id):
    """Obtiene datos para dashboard principal"""
    pass

def get_account_summary(user_id):
    """Resumen de cuentas del usuario"""
    pass

def get_recent_transactions(user_id, limit=10):
    """Transacciones recientes"""
    pass
```

### Transaction Controller (v0.6.0)

```python
# Funciones planificadas
def create_transaction(account_id, amount, description, category_id):
    """Crea nueva transacción"""
    pass

def get_transactions(user_id, filters=None):
    """Lista transacciones con filtros"""
    pass

def update_transaction(transaction_id, data):
    """Actualiza transacción existente"""
    pass
```

---

## 🛠️ Guía para Desarrolladores

### Agregando Nueva Funcionalidad

1. **Crear Controller:**
   ```python
   # src/controllers/nuevo_controller.py
   def nueva_funcion(parametros):
       try:
           # Validar entrada
           # Procesar lógica de negocio
           # Interactuar con BD
           return resultado
       except Exception as e:
           logger.error(f"Error en nueva_funcion: {e}")
           raise
   ```

2. **Crear Vista Flet:**
   ```python
   # src/views/nueva_view.py
   def nueva_vista(page: ft.Page):
       # Configurar componentes UI
       # Conectar con controller
       # Manejar eventos
       pass
   ```

3. **Agregar Tests:**
   ```python
   # tests/unit/test_nuevo_controller.py
   def test_nueva_funcion():
       result = nueva_funcion(test_data)
       assert result == expected_result
   ```

### Convenciones de Código

```python
# Docstrings obligatorios
def funcion_ejemplo(parametro: str) -> dict:
    """
    Descripción breve de la función.
    
    Args:
        parametro: Descripción del parámetro
        
    Returns:
        Descripción del valor retornado
        
    Raises:
        ValueError: Cuando el parámetro es inválido
    """
    pass
```

---

## 📞 Soporte para Desarrolladores

### Recursos Disponibles:
- 📖 [Documentación de Arquitectura](ARCHITECTURE.md)
- 🗄️ [Documentación de Base de Datos](../docs/BASE_DATOS.md)
- 🔒 [Política de Seguridad](SECURITY.md)
- 🧪 [Guía de Testing](../docs/TESTING.md)

### Contacto para Contribuciones:
- **GitHub Issues**: Para bugs y feature requests
- **Email**: estebanfabianp@gmail.com
- **Documentación**: Consulta archivos MD en `/docs/` y `/documentacion/`

---

**💡 Nota Importante:**
Esta aplicación es de **escritorio** (no web). No hay endpoints HTTP, sino funciones Python internas que se comunican directamente con la base de datos a través de la interfaz gráfica Flet.

**Última actualización**: Enero 2025 | **Versión**: 0.5.0 - Sistema de Login Completo