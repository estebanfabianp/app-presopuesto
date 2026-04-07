# Guía de Desarrollo - App Presupuesto

## 🛠️ Configuración del Entorno de Desarrollo

### Requisitos Previos

- **Python**: 3.8 o superior
- **Git**: Para control de versiones
- **IDE Recomendado**: Visual Studio Code, PyCharm
- **Terminal**: PowerShell (Windows), Terminal (macOS/Linux)

### Setup Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/app-presopuesto.git
cd app-presopuesto

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Actualizar pip
python -m pip install --upgrade pip

# 5. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 6. Instalar pre-commit hooks
pre-commit install
```

### Dependencias de Desarrollo

```txt
# requirements-dev.txt
flet>=0.10.0
plotly>=5.0.0
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.991
pre-commit>=2.20.0
pytest-cov>=4.0.0
sphinx>=5.0.0
```

## 📋 Estándares de Código

### Estilo de Código

#### PEP 8 Compliance
```python
# ✅ Correcto
def calculate_total_balance(accounts: List[Account]) -> Decimal:
    """Calcula el balance total de todas las cuentas."""
    total = Decimal('0.00')
    for account in accounts:
        total += account.balance
    return total

# ❌ Incorrecto
def calcTotBal(accts):
    tot=0
    for a in accts:tot+=a.bal
    return tot
```

#### Naming Conventions
```python
# Clases: PascalCase
class BankAccount:
    pass

# Funciones y variables: snake_case
def get_user_balance():
    user_account = None

# Constantes: UPPER_SNAKE_CASE
MAX_TRANSACTION_AMOUNT = 10000.00

# Privados: _leading_underscore
class User:
    def _validate_password(self):
        pass
```

### Documentación de Código

#### Docstrings
```python
def authenticate_user(username: str, password: str) -> Tuple[Optional[User], str]:
    """
    Autentica un usuario con sus credenciales.
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña del usuario
        
    Returns:
        Tuple[Optional[User], str]: Tupla con el usuario autenticado (o None) 
                                   y un mensaje de estado
        
    Raises:
        ValueError: Si los parámetros están vacíos
        ConnectionError: Si no se puede conectar a la base de datos
        
    Example:
        >>> user, message = authenticate_user("john_doe", "password123")
        >>> if user:
        ...     print(f"Bienvenido {user.name}")
    """
```

#### Type Hints
```python
from typing import List, Optional, Dict, Union, Tuple
from decimal import Decimal
import flet as ft

def create_summary_cards(
    accounts: List[Dict[str, Union[str, Decimal]]]
) -> ft.Container:
    """Crea tarjetas de resumen con type hints completos."""
    pass
```

## 🏗️ Patrones de Desarrollo

### Estructura de Archivos

```python
# views/ejemplo_view.py
"""
Módulo de Vista de Ejemplo

Este módulo contiene la implementación de...

Clases:
    ExampleView: Vista principal de ejemplo
    ExampleComponent: Componente reutilizable

Autor: [Nombre del desarrollador]
Fecha: [Fecha de creación]
Versión: 1.0
"""

import flet as ft
from typing import List, Optional, Dict, Any

class ExampleView:
    """
    Vista de ejemplo que demuestra las mejores prácticas.
    
    Attributes:
        page (ft.Page): Referencia a la página principal
        state (Dict[str, Any]): Estado local de la vista
    """
    
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.state: Dict[str, Any] = {}
    
    def build(self) -> ft.View:
        """Construye y retorna la vista completa."""
        return ft.View(
            route="/example",
            controls=[self.create_content()],
            padding=0
        )
```

### Manejo de Eventos

```python
def create_action_button(self) -> ft.ElevatedButton:
    """Crea un botón con manejo de eventos estructurado."""
    
    def handle_click(e: ft.ControlEvent) -> None:
        """
        Maneja el evento de click del botón.
        
        Args:
            e (ft.ControlEvent): Evento de control de Flet
        """
        try:
            # Validar estado
            if not self._validate_form():
                self._show_error("Formulario incompleto")
                return
            
            # Procesar acción
            result = self._process_action()
            
            # Actualizar UI
            self._update_ui(result)
            
        except Exception as error:
            self._handle_error(error)
    
    return ft.ElevatedButton(
        text="Procesar",
        on_click=handle_click,
        width=200
    )
```

### Gestión de Estado

```python
class ViewState:
    """Clase para manejar el estado de una vista."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._observers: List[Callable] = []
    
    def set(self, key: str, value: Any) -> None:
        """Actualiza un valor del estado."""
        self._data[key] = value
        self._notify_observers()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor del estado."""
        return self._data.get(key, default)
    
    def subscribe(self, observer: Callable) -> None:
        """Suscribe un observador a cambios de estado."""
        self._observers.append(observer)
    
    def _notify_observers(self) -> None:
        """Notifica a todos los observadores."""
        for observer in self._observers:
            observer(self._data)
```

## 🧪 Testing

### Estructura de Tests

```
tests/
├── __init__.py
├── unit/
│   ├── test_models.py
│   ├── test_controllers.py
│   └── test_utils.py
├── integration/
│   ├── test_authentication.py
│   └── test_navigation.py
└── fixtures/
    ├── sample_data.py
    └── mock_responses.py
```

### Ejemplos de Tests

```python
# tests/unit/test_controllers.py
import pytest
from unittest.mock import Mock, patch
from src.controllers.persona_controller import autenticar_usuario

class TestPersonaController:
    """Tests para el controlador de persona."""
    
    def test_autenticar_usuario_exitoso(self):
        """Test de autenticación exitosa."""
        # Arrange
        username = "test_user"
        password = "password123"
        
        # Act
        user, message = autenticar_usuario(username, password)
        
        # Assert
        assert user is not None
        assert user["name"] == username
        assert "autenticado correctamente" in message
    
    def test_autenticar_usuario_credenciales_vacias(self):
        """Test con credenciales vacías."""
        # Act
        user, message = autenticar_usuario("", "")
        
        # Assert
        assert user is None
        assert "requeridos" in message
    
    @patch('src.controllers.persona_controller.database')
    def test_autenticar_usuario_error_base_datos(self, mock_db):
        """Test con error de base de datos."""
        # Arrange
        mock_db.side_effect = ConnectionError("Database error")
        
        # Act & Assert
        with pytest.raises(ConnectionError):
            autenticar_usuario("user", "pass")
```

### Cobertura de Tests

```bash
# Ejecutar tests con cobertura
pytest --cov=src --cov-report=html tests/

# Ver reporte de cobertura
open htmlcov/index.html
```

## 🔄 Workflow de Desarrollo

### Git Flow

```bash
# 1. Crear nueva feature
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios y commits
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 3. Push y crear PR
git push origin feature/nueva-funcionalidad

# 4. Merge después de review
git checkout main
git pull origin main
git branch -d feature/nueva-funcionalidad
```

### Conventional Commits

```bash
# Tipos de commits
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de formato
refactor: refactorización de código
test: agregar o modificar tests
chore: tareas de mantenimiento

# Ejemplos
git commit -m "feat: agregar vista de transacciones"
git commit -m "fix: corregir cálculo de balance"
git commit -m "docs: actualizar README con nueva instalación"
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
```

## 🐛 Debugging

### Logging

```python
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Uso en código
def authenticate_user(username: str, password: str):
    logger.info(f"Intento de autenticación para usuario: {username}")
    
    try:
        # Lógica de autenticación
        result = perform_auth(username, password)
        logger.info(f"Autenticación exitosa para: {username}")
        return result
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        raise
```

### Debug de Flet

```python
# Habilitar debug mode
def main(page: ft.Page):
    # Debug info
    page.on_error = lambda e: print(f"Error: {e}")
    
    # Hot reload durante desarrollo
    if os.getenv("DEBUG"):
        page.update()

# Ejecutar con debug
ft.app(target=main, view=ft.AppView.FLET_APP)
```

## 📦 Build y Deploy

### Build para Producción

```bash
# Instalar dependencias de build
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed main.py

# El ejecutable estará en dist/
```

### Optimización

```python
# Lazy loading de componentes pesados
def create_chart(self):
    if not hasattr(self, '_chart'):
        self._chart = self._create_expensive_chart()
    return self._chart

# Memoización de cálculos
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_balance(account_id: str) -> Decimal:
    # Cálculo costoso
    pass
```

## 🔒 Seguridad

### Validación de Input

```python
def validate_amount(amount: str) -> bool:
    """Valida que el monto sea un número válido."""
    try:
        value = Decimal(amount)
        return 0 < value <= Decimal('999999.99')
    except (ValueError, TypeError):
        return False

def sanitize_input(user_input: str) -> str:
    """Limpia input del usuario."""
    return user_input.strip()[:100]  # Limitar longitud
```

### Manejo de Credenciales

```python
import os
from cryptography.fernet import Fernet

# Nunca hardcodear credenciales
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key())

# Hashear contraseñas
import hashlib

def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', 
                              password.encode('utf-8'), 
                              b'salt', 100000).hex()
```

## 📊 Performance

### Profiling

```python
import cProfile
import pstats

def profile_function():
    """Profiling de funciones críticas."""
    pr = cProfile.Profile()
    pr.enable()
    
    # Código a profilear
    expensive_operation()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Métricas

- **Tiempo de carga**: < 2 segundos
- **Uso de memoria**: < 100MB
- **Tamaño de ejecutable**: < 50MB

---

Siguiendo estas guías aseguramos código de alta calidad y mantenible.
