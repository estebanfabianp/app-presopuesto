# API Reference - App Presupuesto

## 🔗 Controllers API

### PersonaController

#### `autenticar_usuario(username: str, password: str) -> Tuple[Optional[Dict], str]`

Autentica un usuario en el sistema.

**Parámetros:**
- `username` (str): Nombre de usuario
- `password` (str): Contraseña del usuario

**Retorna:**
- `Tuple[Optional[Dict], str]`: Usuario autenticado y mensaje de estado

**Ejemplo:**
```python
user, message = autenticar_usuario("john_doe", "password123")
if user:
    print(f"Bienvenido {user['name']}")
```

## 🎨 Views API

### LoginView

#### `login_view(page: ft.Page) -> ft.View`

Crea la vista de inicio de sesión.

**Parámetros:**
- `page` (ft.Page): Instancia de la página Flet

**Retorna:**
- `ft.View`: Vista configurada para login

### ResumenView

#### `resumen_view(page: ft.Page) -> ft.View`

Crea la vista del dashboard financiero.

**Componentes incluidos:**
- Menu lateral navegable
- Tarjetas de resumen
- Tablas de datos
- Gráficos de análisis

## 🛠️ Utils API

### Validators

#### `validate_amount(amount: str) -> bool`
Valida que un monto sea válido.

#### `validate_email(email: str) -> bool`
Valida formato de email.

### Formatters

#### `format_currency(amount: Decimal) -> str`
Formatea cantidades monetarias.

#### `format_date(date: datetime) -> str`
Formatea fechas para visualización.
