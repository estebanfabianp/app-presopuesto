# Guía de Resolución de Problemas

## 🐛 Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'flet'"

**Síntomas:**
```
ModuleNotFoundError: No module named 'flet'
```

**Solución:**
```bash
# Verificar que el entorno virtual esté activado
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar flet
pip install flet
```

### Error: "ImportError: cannot import name 'autenticar_usuario'"

**Síntomas:**
```
ImportError: cannot import name 'autenticar_usuario' from 'controllers.persona_controller'
```

**Causas posibles:**
1. Archivo `persona_controller.py` no existe
2. Función no está definida
3. Error en el path de importación

**Solución:**
1. Verificar que existe `src/controllers/persona_controller.py`
2. Verificar que la función está definida correctamente
3. Usar importación relativa: `from ..controllers.persona_controller import autenticar_usuario`

### Error: "AttributeError: 'ResumenView' object has no attribute 'build'"

**Síntomas:**
```
AttributeError: 'ResumenView' object has no attribute 'build'
```

**Solución:**
Asegurar que la clase `ResumenView` tiene el método `build()`:
```python
def build(self) -> ft.Container:
    return ft.Container(...)
```

### Aplicación no se abre o se cierra inmediatamente

**Causas posibles:**
1. Error en el código principal
2. Dependencias faltantes
3. Conflictos de versiones

**Diagnóstico:**
```bash
# Ejecutar con output de errores
python main.py

# Verificar dependencias
pip list
pip check
```

## 🔧 Herramientas de Debug

### Logging Detallado

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# En funciones críticas
logger.debug(f"Autenticando usuario: {username}")
```

### Verificación de Entorno

```bash
# Verificar versión de Python
python --version

# Verificar pip
pip --version

# Verificar entorno virtual
which python  # Linux/macOS
where python   # Windows
```

## 💡 Tips de Performance

### Aplicación Lenta

1. **Reducir carga inicial:**
   - Implementar lazy loading
   - Cargar datos bajo demanda

2. **Optimizar renderizado:**
   - Evitar re-renders innecesarios
   - Usar componentes ligeros

### Alto Uso de Memoria

1. **Liberar recursos:**
   - Cerrar conexiones no utilizadas
   - Limpiar referencias circulares

2. **Optimizar datos:**
   - Paginar tablas grandes
   - Comprimir imágenes
