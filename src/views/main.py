"""
Módulo Principal de la Aplicación de Presupuesto

Este módulo contiene la función principal y el sistema de enrutamiento de la aplicación
de presupuesto personal. Se encarga de gestionar la navegación entre las diferentes
vistas de la aplicación utilizando el framework Flet.

Funcionalidades:
    - Configuración inicial de la aplicación
    - Sistema de enrutamiento entre vistas
    - Gestión del estado de navegación
    - Punto de entrada principal de la aplicación

Rutas disponibles:
    - /login: Vista de autenticación de usuario
    - /constantes: Vista principal de constantes financieras
Dependencias:
    - flet: Framework de UI para Python
    - resumen: Módulo de vista de resumen financiero
    - login: Módulo de vista de autenticación

Autor: [esteban patiño]
Fecha: [30-sep-2025]
Versión: 1.0
"""

import importlib

import flet as ft

try:
    from .resumen import resumen_view
    from .login import login_view
except ImportError:
    # Soporta ejecución directa del archivo: python src/views/main.py
    from resumen import resumen_view
    from login import login_view

def main(page: ft.Page) -> None:
    """
    Función principal de la aplicación de presupuesto.
    
    Esta función configura la aplicación, establece el sistema de enrutamiento
    y define el comportamiento de navegación entre las diferentes vistas.
    
    Configuraciones aplicadas:
        - Título de la ventana de la aplicación
        - Sistema de enrutamiento con manejo de cambios de ruta
        - Vista inicial (login)
        - Gestión del historial de navegación
    
    Args:
        page (ft.Page): Objeto de página principal proporcionado por Flet
                       que representa la ventana de la aplicación
    
    Returns:
        None: La función no retorna valores, modifica el estado de la página
        
    Example:
        >>> # La función se ejecuta automáticamente al iniciar la aplicación
        >>> ft.app(target=main)
    
    Note:
        - La aplicación siempre inicia en la ruta "/login"
        - Cada cambio de ruta limpia las vistas anteriores
        - Las vistas se agregan dinámicamente según la ruta actual
    """
    # Configuración base de la ventana principal
    page.title = "App Presupuesto"

    def create_404_view() -> ft.View:
        return ft.View(
            route="/404",
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Text("404", size=42, weight=ft.FontWeight.BOLD),
                            ft.Text("Ruta no encontrada", size=18),
                            ft.ElevatedButton("Ir a Resumen", on_click=lambda e: page.go("/resumen")),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                )
            ],
        )

    def load_view(module_name: str, function_name: str) -> ft.View | None:
        """Carga una vista dinamicamente y retorna None si no existe."""
        candidates = [f"src.views.{module_name}", module_name]
        for candidate in candidates:
            try:
                module = importlib.import_module(candidate)
                view_fn = getattr(module, function_name, None)
                if callable(view_fn):
                    return view_fn(page)
            except (ImportError, AttributeError, TypeError):
                continue
        return None

    route_map = {
        "/login": [("login", "login_view")],
        "/dashboard": [("dashboard", "dashboard_view")],
        "/resumen": [("resumen", "resumen_view")],
        "/transacciones/nueva": [("nueva_transaccion", "nueva_transaccion_view")],
        "/transacciones/historial": [("historia", "constantes_view")],
        "/transferencias": [("transferencias", "transferencias_view")],
        "/presupuestos": [("presupuesto", "constantes_view")],
        "/metas": [("metas_ahorro", "metas_ahorro_view")],
        "/categorias": [("categoria", "constantes_view")],
        "/cuentas": [("cuenta_bancaria", "constantes_view")],
        "/tarjetas": [("tarjeta", "constantes_view")],
        "/inversiones": [("inversion", "constantes_view")],
        "/analisis": [("analisis", "constantes_view")],
        "/reportes": [("reporte", "constantes_view")],
        "/exportar": [("export", "constantes_view")],
        "/perfil": [("perfil", "perfil_view")],
        "/notificaciones": [("configuracion", "configuracion_view")],
        "/configuracion": [("configuracion", "configuracion_view")],
        "/constantes": [("constante", "system_constants_view")],
        "/optimizacion-categorias": [("optimizacion_categorias", "optimizacion_categorias_view")],
    }

    def route_change(route) -> None:
        """
        Maneja los cambios de ruta en la aplicación.
        
        Esta función es llamada automáticamente cada vez que se produce
        un cambio de ruta en la aplicación. Se encarga de:
        1. Limpiar las vistas existentes
        2. Determinar qué vista mostrar según la ruta
        3. Agregar la vista correspondiente
        4. Actualizar la página
        
        Args:
            route: Parámetro de ruta (no utilizado directamente, se usa page.route)
        
        Returns:
            None: Modifica el estado de la página directamente
            
        Rutas soportadas:
            - "/login": Vista de autenticación
            - "/dashboard": Vista principal del dashboard  
            - "/resumen": Vista de resumen financiero
            - "/constantes": Vista de constantes del sistema
            - "/transacciones/nueva": Vista de nueva transacción
            - "/transferencias": Vista de transferencias
            - "/configuracion": Vista de configuración general
            - "/perfil": Vista de perfil de usuario
            - Otras rutas: Página de error 404
        
        Note:
            - Siempre limpia las vistas anteriores antes de agregar nuevas
            - Cada vista es una función que retorna un objeto ft.View
            - La actualización de la página es necesaria para reflejar cambios
        """
        # Limpiar todas las vistas existentes del historial
        page.views.clear()

        loaded_view = None
        for module_name, function_name in route_map.get(page.route, []):
            loaded_view = load_view(module_name, function_name)
            if loaded_view is not None:
                break

        if loaded_view is None and page.route not in route_map:
            loaded_view = create_404_view()

        if loaded_view is None:
            # Fallback seguro si la ruta existe pero su vista aun no esta implementada.
            loaded_view = resumen_view(page)

        page.views.append(loaded_view)

        # Actualizar la página para reflejar los cambios en la UI
        page.update()

    # Configurar el manejador de cambios de ruta
    page.on_route_change = route_change
    
    # Navegar a la vista inicial (login)
    # Esto activa automáticamente route_change con la ruta "/login"
    page.go("/login")

# Iniciar la aplicación solo cuando este archivo se ejecuta directamente
if __name__ == "__main__":
    ft.app(target=main)

