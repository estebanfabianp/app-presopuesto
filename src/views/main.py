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

import flet as ft
from resumen import resumen_view
from login import login_view
from constante import constantes_view

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
    # Configuración del título de la ventana principal
    page.title = "App con navegación entre vistas"

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

        # Determinar qué vista mostrar según la ruta actual
        if page.route == "/login":
            # Mostrar vista de autenticación
            page.views.append(login_view(page))
        elif page.route == "/dashboard":
            try:
                from dasvorad import dashboard_view
                page.views.append(dashboard_view(page))
            except ImportError:
                print("Error: No se pudo importar dashboard_view")
                page.views.append(create_404_view(page))
        elif page.route == "/resumen":
            # Mostrar vista de resumen financiero
            page.views.append(resumen_view(page))
        elif page.route == "/constantes":
            # Mostrar vista de constantes financiero
            page.views.append(constantes_view(page))
        elif page.route == "/transacciones/nueva":
            try:
                from nueva_trasacion import nueva_transaccion_view
                page.views.append(nueva_transaccion_view(page))
            except ImportError:
                print("Error: No se pudo importar nueva_transaccion_view")
                page.views.append(create_404_view(page))
        elif page.route == "/transferencias":
            try:
                from tranferencia import transferencias_view
                page.views.append(transferencias_view(page))
            except ImportError:
                print("Error: No se pudo importar transferencias_view")
                page.views.append(create_404_view(page))
        elif page.route == "/configuracion":
            try:
                from configuracion import configuracion_view
                page.views.append(configuracion_view(page))
            except ImportError:
                print("Error: No se pudo importar configuracion_view")
                page.views.append(create_404_view(page))
        elif page.route == "/perfil":
            try:
                from perfil import perfil_view
                page.views.append(perfil_view(page))
            except ImportError:
                print("Error: No se pudo importar perfil_view")
                page.views.append(create_404_view(page))
        else:
            # Manejo de rutas no encontradas (404)
            page.views.append(create_404_view(page))

        # Actualizar la página para reflejar los cambios en la UI
        page.update()

    def create_404_view(page: ft.Page) -> ft.View:
        """
        Crea una vista de error 404 para rutas no encontradas.
        
        Args:
            page (ft.Page): Referencia a la página principal de Flet
            
        Returns:
            ft.View: Vista de error 404 con opción de regresar al login
        """
        return ft.View(
            route="/404",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.ERROR_OUTLINE,
                            size=80,
                            color=ft.Colors.RED_400
                        ),
                        ft.Text(
                            "404",
                            size=48,
                            weight=ft.FontWeight.BOLD,
                            color="#333333"
                        ),
                        ft.Text(
                            "Página no encontrada",
                            size=20,
                            color="#666666"
                        ),
                        ft.Text(
                            f"La ruta  no existe",
                            size=14,
                            color="#999999"
                        ),
                        ft.Container(height=30),
                        ft.ElevatedButton(
                            "Ir al Login",
                            on_click=lambda e: page.go("/login"),
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            width=200,
                            height=40
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    # Configurar el manejador de cambios de ruta
    page.on_route_change = route_change
    
    # Navegar a la vista inicial (login)
    # Esto activa automáticamente route_change con la ruta "/login"
    page.go("/login")

# Iniciar la aplicación Flet con la función main como punto de entrada
# Esta línea ejecuta la aplicación y abre la ventana principal
ft.app(target=main)

