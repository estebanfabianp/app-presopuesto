"""
GUÍA DE INTEGRACIÓN: SystemConstantsView con tu aplicación

Este archivo muestra exactamente cómo integrar la vista de constantes
en tu estructura de navegación actual.
"""

# ========================================================================
# OPCIÓN 1: Integración en main.py (si usas routing simple)
# ========================================================================

# En tu main.py, agrega:

from src.views.constante import system_constants_view

def create_app():
    """Crea la aplicación con rutas."""
    
    def on_route_change(route_change_event):
        """Maneja cambios de ruta."""
        new_route = route_change_event.route
        
        # Agregar esta condición
        if new_route == "/constantes":
            page.clean()
            page.add(system_constants_view(page))
            return
        
        # ... otras rutas ...
    
    page.on_route_change = on_route_change


# ========================================================================
# OPCIÓN 2: Integración con sidebar.py
# ========================================================================

# En src/views/sidebar.py, en la lista de items del menú:

class LeftSidebarMenu:
    def __init__(self, selected_index: int = 0, ...):
        # Agregar a MENU_ITEMS o similar:
        
        MENU_ITEMS = [
            ("resumen", "Resumen", ft.Icons.DASHBOARD, "/resumen"),
            ("transacciones", "Transacciones", ft.Icons.CREDIT_CARD, "/transacciones/nueva"),
            ("categorias", "Categorías", ft.Icons.CATEGORY, "/categorias"),
            # ... resta de items ...
            ("constantes", "Configuración", ft.Icons.SETTINGS_SUGGEST, "/constantes"),  # ← NUEVA LÍNEA
            ("logout", "Cerrar Sesión", ft.Icons.LOGOUT, "/login"),
        ]


# ========================================================================
# OPCIÓN 3: Integración con patrón de routing robusto
# ========================================================================

# En router.py (si lo tienes):

from src.views.constante import system_constants_view

class Router:
    ROUTES = {
        "/resumen": "resumen_view",
        "/transacciones/nueva": "nueva_transaccion_view",
        "/categorias": "categorias_view",
        "/constantes": "system_constants_view",  # ← AGREGAR
        "/login": "login_view",
    }
    
    @staticmethod
    def navigate(page: ft.Page, route: str):
        """Navega a una ruta."""
        if route == "/constantes":
            page.clean()
            page.add(system_constants_view(page))
        else:
            # Manejo de otras rutas...
            pass


# ========================================================================
# OPCIÓN 4: Integración en navegación por evento
# ========================================================================

# Si tu menú lateral usa callbacks:

def on_menu_click(route: str, index: int):
    """Callback cuando se hace click en menú."""
    if route == "/constantes":
        page.clean()
        page.add(system_constants_view(page))
    else:
        page.go(route)

# Pasar este callback al sidebar:
sidebar_menu = create_sidebar_menu(
    page=page,
    navigation_callback=on_menu_click  # ← Esta función
)


# ========================================================================
# VERIFICACIÓN: Estructura esperada en la tabla constantes
# ========================================================================

# Ejecuta esto para verificar que tu tabla es compatible:

"""
SELECT 
    id_constante, 
    categoria, 
    nombre, 
    valor, 
    tipo_dato,
    descripcion, 
    es_editable, 
    estado, 
    fecha_actualizacion
FROM constantes
LIMIT 1;

-- Debe devolver una fila con estos campos:
-- id_constante: 1
-- categoria: "FINANCIERO"
-- nombre: "IVA"
-- valor: "0.19"
-- tipo_dato: "DECIMAL"
-- descripcion: "Impuesto al valor agregado"
-- es_editable: 1
-- estado: 1
-- fecha_actualizacion: "2026-04-07 12:00:00"
"""


# ========================================================================
# EJEMPLO COMPLETO: main.py con routing
# ========================================================================

import flet as ft
from src.views.constante import system_constants_view
from src.views.resumen import resumen_view
# ... importar otras vistas

def main(page: ft.Page):
    """Aplicación principal."""
    
    # Configuración
    page.title = "App Presupuesto"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Router
    def route_change(route_event):
        route = route_event.route
        page.clean()
        
        if route == "/constantes":
            page.add(system_constants_view(page))
        elif route == "/resumen":
            page.add(resumen_view(page))
        # ... más rutas ...
        else:
            page.go("/resumen")
    
    page.on_route_change = route_change
    page.go(page.route or "/resumen")

if __name__ == "__main__":
    ft.app(target=main)


# ========================================================================
# TESTING: Script para probar la vista aislada
# ========================================================================

# Crea test_constantes_view.py:

import flet as ft
from src.views.constante import system_constants_view

def test_system_constants_view():
    """Prueba la vista de constantes de forma aislada."""
    
    def main(page: ft.Page):
        page.title = "Test - System Constants View"
        page.window.width = 1400
        page.window.height = 900
        
        # Mostrar la vista
        page.add(system_constants_view(page))
    
    ft.app(target=main)

if __name__ == "__main__":
    test_system_constants_view()

# Ejecutar: python test_constantes_view.py


# ========================================================================
# TROUBLESHOOTING
# ========================================================================

"""
❌ Problema: ImportError: No module named 'src'
✅ Solución: Asegúrate de ejecutar desde la raíz del proyecto
            cd c:\Users\Asus\Documents\GitHub\app-presopuesto
            python main.py

❌ Problema: No aparece constantes en la tabla
✅ Solución: Verifica que la tabla constantes existe:
            SELECT COUNT(*) FROM constantes;
            
❌ Problema: Error al cargar: Table 'db.constantes' doesn't exist
✅ Solución: Ejecuta el script de BD para crear la tabla:
            mysql -u usuario -p basedatos < db/01_core/create/02_create_tables.sql

❌ Problema: Cambios no se guardan
✅ Solución: Verifica conexión a BD y permisos:
            SELECT CURRENT_USER();
            SHOW GRANT FO CURRENT_USER();

❌ Problema: FAB no aparece
✅ Solución: Verifica que el Stack está correctamente anidado
            en la estructura de build()
"""


# ========================================================================
# CHECKLIST DE INTEGRACIÓN
# ========================================================================

"""
✅ Copiar archivo src/views/constante.py
✅ Importar system_constants_view en navegación
✅ Agregar ruta "/constantes" al router
✅ Agregar menú item en sidebar (si aplica)
✅ Verificar estructura BD (tabla constantes)
✅ Probar crear una constante
✅ Probar editar un valor
✅ Probar eliminar una constante
✅ Probar búsqueda por nombre
✅ Probar filtrado por categoría
✅ Revisar logs para errores
"""
