# Arquitectura del Sistema — App Presupuesto (Flet Desktop)

Documentación completa de la arquitectura de la aplicación de escritorio desarrollada con Flet, Python y MySQL.

---

## 🏗️ Visión General de la Arquitectura

### Tipo de Aplicación
**App Presupuesto** es una **aplicación de escritorio nativa** que utiliza:
- **Frontend**: Flet (Python GUI Framework)
- **Backend**: Python con arquitectura MVC
- **Base de Datos**: MySQL local
- **Distribución**: Ejecutable standalone

### Principios Arquitectónicos
1. **Separación de Responsabilidades**: Patrón MVC estricto
2. **Seguridad por Diseño**: Múltiples capas de protección
3. **Escalabilidad Local**: Optimizado para un solo usuario/familia
4. **Mantenibilidad**: Código limpio y bien documentado
5. **Extensibilidad**: Preparado para módulos futuros

---

## 🧩 Arquitectura de Componentes

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICACIÓN FLET DESKTOP                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │    VIEWS    │ -> │ CONTROLLERS  │ -> │     MODELS      │    │
│  │ (Flet UI)   │    │ (Business)   │    │ (Data Entities) │    │
│  │             │    │              │    │                 │    │
│  │ • user_view │    │ • persona_c  │    │ • persona.py    │    │
│  │ • dashboard │    │ • budget_c   │    │ • cuenta.py     │    │
│  │ • budget_v  │    │ • trans_c    │    │ • transaccion.py│    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│         │                    │                     │           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │ VALIDATORS  │    │   SECURITY   │    │    DATABASE     │    │
│  │ • Input Val │    │ • Auth/Hash  │    │ • Connection    │    │
│  │ • Business  │    │ • Encryption │    │ • Pool Mgmt     │    │
│  │ • UI Rules  │    │ • Audit Log  │    │ • Query Opt     │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   UTILS     │    │     AI/ML    │    │     REPORTS     │    │
│  │ • Helpers   │    │ • Categories │    │ • Generators    │    │
│  │ • Formatters│    │ • Predictions│    │ • Exporters     │    │
│  │ • Converters│    │ • Learning   │    │ • Charts        │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌─────────────────────┐
                    │   MYSQL DATABASE    │
                    │  (Local Instance)   │
                    │                     │
                    │ • Pool Connections  │
                    │ • ACID Transactions │
                    │ • Backup/Recovery   │
                    │ • Performance Opt   │
                    └─────────────────────┘
```

---

## 📱 Capa de Presentación (Views)

### Framework Flet
**Ubicación**: `/src/views/`

**Características de Flet**:
- Framework Python para UI nativas multiplataforma
- Basado en Flutter engine para rendimiento superior
- Componentes reactivos con estado gestionado
- Hot reload para desarrollo rápido
- Soporte nativo para desktop (Windows, macOS, Linux)

### Estructura de Vistas

```
src/views/
├── __init__.py
├── user_view.py          # ✅ Login y autenticación (v0.5.0)
├── dashboard_view.py     # 📊 Dashboard principal (v0.6.0)
├── accounts_view.py      # 🏦 Gestión de cuentas (v0.6.0)
├── transactions_view.py  # 💰 Registro de transacciones (v0.6.0)
├── budgets_view.py       # 📋 Gestión de presupuestos (v0.6.0)
├── categories_view.py    # 📂 Configuración de categorías (v0.6.0)
├── reports_view.py       # 📈 Reportes y gráficos (v0.8.0)
├── investments_view.py   # 💎 Gestión de inversiones (v0.9.0)
├── settings_view.py      # ⚙️ Configuración de usuario (v0.7.0)
└── components/           # 🧩 Componentes reutilizables
    ├── forms.py          # Formularios comunes
    ├── charts.py         # Gráficos con Flet
    ├── dialogs.py        # Diálogos modales
    └── widgets.py        # Widgets personalizados
```

### Configuración de Ventana Principal

```python
# Configuración estándar para todas las vistas
def configure_page(page: ft.Page):
    page.title = "App Presupuesto"
    page.window_width = 400
    page.window_height = 500
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
```

### Componentes UI Estándar

```python
# Componentes reutilizables para consistencia
class StandardComponents:
    @staticmethod
    def create_text_field(label, width=300, password=False):
        return ft.TextField(
            label=label,
            width=width,
            border_radius=8,
            password=password,
            can_reveal_password=password
        )
    
    @staticmethod
    def create_button(text, on_click, primary=True):
        return ft.ElevatedButton(
            text,
            on_click=on_click,
            width=300,
            height=45,
            bgcolor=ft.Colors.BLUE if primary else ft.Colors.GREY,
            color=ft.Colors.WHITE
        )
```

---

## 🎯 Capa de Lógica de Negocio (Controllers)

### Responsabilidades de Controllers
**Ubicación**: `/src/controllers/`

1. **Procesamiento de Entrada**: Validación y sanitización de datos de UI
2. **Reglas de Negocio**: Implementación de lógica financiera
3. **Coordinación**: Interacción entre vistas y modelos
4. **Manejo de Errores**: Captura y procesamiento de excepciones
5. **Logging**: Registro de operaciones para auditoría

### Estructura de Controllers

```
src/controllers/
├── __init__.py
├── base_controller.py        # Clase base común
├── persona_controller.py     # ✅ Autenticación (v0.5.0)
├── account_controller.py     # 🏦 Gestión de cuentas (v0.6.0)
├── transaction_controller.py # 💰 Transacciones (v0.6.0)
├── budget_controller.py      # 📋 Presupuestos (v0.6.0)
├── category_controller.py    # 📂 Categorías (v0.6.0)
├── report_controller.py      # 📈 Reportes (v0.8.0)
└── investment_controller.py  # 💎 Inversiones (v0.9.0)
```

### Patrón de Controller Base

```python
# src/controllers/base_controller.py
import logging
from typing import Tuple, Any, Optional

class BaseController:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute_with_error_handling(self, operation, *args, **kwargs) -> Tuple[Any, str]:
        """
        Ejecuta operación con manejo estándar de errores
        
        Returns:
            Tuple[result, message]: Resultado y mensaje descriptivo
        """
        try:
            result = operation(*args, **kwargs)
            return result, "Operación exitosa"
        except ValidationError as e:
            self.logger.warning(f"Error de validación: {e}")
            return None, f"Error de validación: {str(e)}"
        except DatabaseError as e:
            self.logger.error(f"Error de base de datos: {e}")
            return None, "Error interno del sistema"
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return None, "Error interno del sistema"
```

---

## 🗄️ Capa de Datos (Models)

### Diseño de Modelos
**Ubicación**: `/src/models/`

Los modelos representan entidades de datos y encapsulan la lógica de validación y serialización.

### Estructura de Models

```python
# ...existing code...
```

---

## ⚙️ Configuración y Deployment

### Configuración por Ambientes

```
config/
├── development.env         # Desarrollo local
├── testing.env            # Pruebas automatizadas
├── production.env          # Producción (template)
└── docker.env             # Contenedores (futuro)
```

### Deployment Strategy

1. **Desktop Application:**
   - Empaquetado con PyInstaller
   - Instalador para Windows/Mac/Linux
   - Auto-updater integrado

2. **Base de Datos:**
   - Scripts de migración automática
   - Backup/restore integrado
   - Verificación de integridad

---

## 📚 Documentación y Standards

### Estándares de Código

```python
# Convenciones seguidas:
- PEP 8 para estilo de código Python
- Docstrings en formato Google
- Type hints obligatorios
- Nombres descriptivos en español
- Comentarios en código complejo
```

### Arquitectura de Documentación

```
docs/                       # Documentación técnica
documentacion/              # Documentación de usuario
README.md                   # Guía principal
CHANGELOG.md               # Historial de cambios
```

---

## 🌟 Ventajas de la Arquitectura Actual

### ✅ Fortalezas Implementadas

1. **Separación Clara:** MVC bien definido y respetado
2. **Seguridad Robusta:** Múltiples capas de protección
3. **Escalabilidad:** Arquitectura preparada para crecimiento
4. **Mantenibilidad:** Código limpio y bien documentado
5. **Performance:** Optimizaciones desde el diseño
6. **Testing:** Cobertura amplia y pruebas automatizadas

### 🔄 Áreas de Mejora Continua

1. **Cache Layer:** Implementar Redis para cache distribuido
2. **Message Queue:** Agregar Celery para tareas asíncronas
3. **Microservices:** Preparar para arquitectura distribuida
4. **API Gateway:** Implementar para integraciones futuras

---

## 👨‍💻 Información del Proyecto

**Arquitecto Principal:** Esteban Fabián Patiño Montealegre  
**Email:** estebanfabianp@gmail.com  
**Versión Arquitectura:** 2.0 (Flet-based)  
**Última Revisión:** Enero 2025  

---

**🏗️ Estado de Implementación:**
- ✅ **MVC Architecture**: 100% implementado
- ✅ **Security Layer**: 100% funcional
- ✅ **Database Layer**: 100% optimizado
- 🚧 **Business Logic**: 60% completado (login listo)
- 📋 **UI Components**: 20% completado (dashboard pendiente)
- 🔮 **AI Integration**: 0% (planificado v0.7.0)

**¡La arquitectura está sólida y lista para el siguiente nivel de desarrollo! 🚀**