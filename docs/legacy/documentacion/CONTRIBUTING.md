# Guía de Contribución — App Presupuesto (Flet Desktop)

¡Gracias por tu interés en contribuir a este proyecto de aplicación de escritorio! Esta guía te ayudará a empezar a contribuir de manera efectiva.

---

## 🌟 Bienvenido/a

**App Presupuesto** es una aplicación de escritorio desarrollada con **Flet y Python** que utiliza **arquitectura MVC** y **MySQL** como base de datos. Es un proyecto **open source** bajo licencia MIT que busca democratizar la gestión financiera personal.

### ¿Por qué contribuir?
- 💰 **Impacto Real**: Ayuda a personas a gestionar mejor sus finanzas
- 🎓 **Aprendizaje**: Experimenta con Flet, MySQL, IA y arquitectura MVC
- 🤝 **Comunidad**: Forma parte de un proyecto de código abierto
- 📈 **Portfolio**: Contribuye a un proyecto con documentación profesional

---

## 🚀 Primeros Pasos

### 1. Preparar el Entorno de Desarrollo

```bash
# Hacer fork del repositorio en GitHub
# Luego clonar tu fork
git clone https://github.com/TU_USUARIO/app-presopuesto.git
cd app-presupuesto

# Configurar remote upstream
git remote add upstream https://github.com/usuario-original/app-presopuesto.git

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configurar Base de Datos de Desarrollo

```bash
# Copiar configuración de ejemplo
copy .env.example .env.dev

# Editar .env.dev con configuración local
# DB_NAME=presupuesto_dev
# DEBUG=True

# Inicializar base de datos
database\scripts\init_db.bat
```

### 3. Ejecutar la Aplicación

```bash
# Verificar que todo funciona
python src/views/user_view.py

# Ejecutar tests
python -m pytest tests/ -v
```

---

## 🔄 Flujo de Contribución

### Proceso Recomendado

1. **Explorar Issues Existentes**
   - Revisa [GitHub Issues](https://github.com/usuario/app-presopuesto/issues)
   - Busca etiquetas `good-first-issue` o `help-wanted`
   - Comenta en el issue para indicar que trabajarás en él

2. **Crear Nueva Funcionalidad**
   ```bash
   # Sincronizar con upstream
   git fetch upstream
   git checkout main
   git merge upstream/main
   
   # Crear rama para tu feature
   git checkout -b feature/nombre-descriptivo
   ```

3. **Desarrollar y Probar**
   ```bash
   # Hacer cambios siguiendo las convenciones
   # Ejecutar tests frecuentemente
   python -m pytest tests/ -v
   
   # Verificar linting
   flake8 src/
   black src/
   isort src/
   ```

4. **Commit y Push**
   ```bash
   # Commits descriptivos en español
   git add .
   git commit -m "feat: agregar validación de email en registro"
   
   # Push a tu fork
   git push origin feature/nombre-descriptivo
   ```

5. **Crear Pull Request**
   - Usar el template de PR en GitHub
   - Describir claramente los cambios
   - Incluir screenshots si hay cambios de UI
   - Referenciar issues relacionados

---

## 📋 Tipos de Contribuciones

### 🐛 Corrección de Bugs
**¿Qué necesitamos?**
- Identificación y corrección de errores
- Mejoras en manejo de excepciones
- Optimización de rendimiento

**Ejemplo de áreas:**
- Errores en validación de entrada
- Problemas de conexión a BD
- Memory leaks en la UI Flet
- Bugs en cálculos financieros

### ✨ Nuevas Funcionalidades
**Próximas funcionalidades prioritarias:**
- **Dashboard principal** (v0.6.0)
- **CRUD de cuentas bancarias** (v0.6.0)
- **Registro de transacciones** (v0.6.0)
- **Categorización automática con IA** (v0.7.0)

### 📚 Documentación
**Áreas de mejora:**
- Tutoriales paso a paso
- Ejemplos de código
- Traducción a otros idiomas
- Videos explicativos
- Documentación de API interna

### 🧪 Testing
**Necesidades actuales:**
- Tests de integración para UI Flet
- Tests de base de datos
- Tests de rendimiento
- Datos de prueba más realistas

### 🎨 UI/UX
**Oportunidades:**
- Mejoras en diseño Flet
- Nuevos componentes reutilizables
- Iconografía y colores
- Accesibilidad

---

## 🛠️ Estándares de Código

### Convenciones de Python

```python
# ✅ Correcto: Nombres en español para el dominio
class ControladorPresupuesto:
    def crear_presupuesto(self, nombre: str, monto: Decimal) -> dict:
        """
        Crea un nuevo presupuesto.
        
        Args:
            nombre: Nombre descriptivo del presupuesto
            monto: Monto total asignado
            
        Returns:
            dict: Datos del presupuesto creado
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        pass

# ✅ Docstrings obligatorios en formato Google
# ✅ Type hints en todas las funciones públicas
# ✅ Nombres descriptivos y en español para dominio
```

### Estructura de Archivos

```python
# src/controllers/nuevo_controller.py
import logging
from typing import Dict, List, Optional
from src.models.nuevo_modelo import NuevoModelo
from src.utils.validators import validar_entrada

class NuevoController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def nueva_operacion(self, data: Dict) -> Dict:
        try:
            # Validar entrada
            data_validada = validar_entrada(data)
            
            # Lógica de negocio
            resultado = self._procesar_datos(data_validada)
            
            self.logger.info(f"Operación exitosa: {resultado['id']}")
            return {"success": True, "data": resultado}
            
        except Exception as e:
            self.logger.error(f"Error en nueva_operacion: {e}")
            return {"success": False, "error": str(e)}
```

### UI con Flet

```python
# src/views/nueva_view.py
import flet as ft
from src.controllers.nuevo_controller import NuevoController

def nueva_vista(page: ft.Page):
    # Configurar página
    page.title = "Nueva Vista"
    page.window_width = 400
    page.window_height = 500
    
    controller = NuevoController()
    
    # Componentes UI
    titulo = ft.Text("Nueva Funcionalidad", 
                    size=24, 
                    weight=ft.FontWeight.BOLD)
    
    input_field = ft.TextField(
        label="Campo de entrada",
        width=300,
        border_radius=8
    )
    
    def on_submit(e):
        # Lógica de manejo
        resultado = controller.nueva_operacion({"valor": input_field.value})
        # Actualizar UI basado en resultado
        page.update()
    
    boton = ft.ElevatedButton("Enviar", on_click=on_submit)
    
    # Layout
    page.add(ft.Column([titulo, input_field, boton],
                      alignment=ft.MainAxisAlignment.CENTER))
```

### Tests

```python
# tests/unit/test_nuevo_controller.py
import pytest
from src.controllers.nuevo_controller import NuevoController

class TestNuevoController:
    def setup_method(self):
        self.controller = NuevoController()
    
    def test_nueva_operacion_exitosa(self):
        # Arrange
        data = {"nombre": "Test", "valor": 100}
        
        # Act
        resultado = self.controller.nueva_operacion(data)
        
        # Assert
        assert resultado["success"] is True
        assert "data" in resultado
    
    def test_nueva_operacion_error_validacion(self):
        # Arrange
        data = {"nombre": "", "valor": -100}  # Datos inválidos
        
        # Act
        resultado = self.controller.nueva_operacion(data)
        
        # Assert
        assert resultado["success"] is False
        assert "error" in resultado
```

---

## 🗄️ Trabajando con Base de Datos

### Agregar Nueva Tabla

```sql
-- database/scripts/create/nueva_tabla.sql
CREATE TABLE nueva_entidad (
    id_entidad INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    INDEX idx_nombre (nombre),
    INDEX idx_activo (activo)
);
```

### Crear Modelo Correspondiente

```python
# src/models/nueva_entidad.py
from typing import Optional
from datetime import datetime

class NuevaEntidad:
    def __init__(self, id_entidad: Optional[int] = None,
                 nombre: str = "", descripcion: str = ""):
        self.id_entidad = id_entidad
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_creacion = None
        self.activo = True
    
    def to_dict(self) -> dict:
        return {
            'id_entidad': self.id_entidad,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NuevaEntidad':
        return cls(**data)
```

---

## 🧪 Testing y Calidad

### Ejecutar Tests

```bash
# Tests unitarios
python -m pytest tests/unit/ -v

# Tests de integración
python -m pytest tests/integration/ -v

# Tests con cobertura
python -m pytest tests/ --cov=src/ --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html  # En navegador
```

### Linting y Formateo

```bash
# Verificar estilo
flake8 src/ tests/

# Formatear código automáticamente
black src/ tests/
isort src/ tests/

# Verificar type hints
mypy src/
```

### Tests de UI (Flet)

```python
# tests/integration/test_ui.py
import flet as ft
from src.views.user_view import user_app

def test_login_view_components():
    """Test que la vista de login tiene todos los componentes necesarios"""
    page = ft.Page()
    user_app(page)
    
    # Verificar que los componentes existen
    # (Implementar según la API de testing de Flet)
    assert page.title == "Login de Usuario"
    assert page.window_width == 400
    assert page.window_height == 500
```

---

## 📚 Contribuciones de Documentación

### Agregar Nueva Documentación

```markdown
<!-- docs/NUEVA_GUIA.md -->
# Nueva Guía — App Presupuesto

Descripción clara de la nueva funcionalidad o proceso.

## 📋 Requisitos Previos
- Lista de requisitos
- Conocimientos necesarios

## 🚀 Pasos a Seguir
1. Paso uno con ejemplo
2. Paso dos con código
3. Resultado esperado

## 🔧 Ejemplos Prácticos
\```python
# Código de ejemplo bien comentado
def ejemplo_funcion():
    pass
\```

## 🐛 Problemas Comunes
- Problema X: Solución Y
- Error Z: Verificar configuración A

## 📞 Soporte
Links a recursos adicionales
```