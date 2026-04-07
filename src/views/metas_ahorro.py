"""
Módulo de Vista de Metas de Ahorro

Este módulo contiene la implementación de la vista de metas de ahorro
de la aplicación de presupuesto. Permite crear y gestionar objetivos financieros.

Clases:
    MetasAhorroView: Vista principal para gestionar metas de ahorro

Autor: [esteban patiño]  
Fecha: [30-sep-2025]
Versión: 1.0 - Vista de metas de ahorro
"""

import flet as ft
import datetime
from typing import List, Optional, Dict, Any

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    from sidebar import create_sidebar_menu


class MetasAhorroView:
    """
    Vista principal de metas de ahorro.
    
    Esta clase gestiona la vista de metas de ahorro que muestra:
    - Lista de metas activas
    - Progreso de cada meta
    - Formulario para crear nuevas metas
    - Estadísticas de cumplimiento
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral reutilizable
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de metas de ahorro.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=6,  # "Metas de Ahorro" está seleccionado

            navigation_callback=self.handle_navigation
        )
    
    def handle_navigation(self, route: str, index: int) -> None:
        """Maneja la navegación desde el menú lateral."""
        print(f"Navegando desde metas de ahorro a: {route} (índice: {index})")
        
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)
    
    def create_header_bar(self) -> ft.Container:
        """
        Crea la barra de encabezado con breadcrumbs y acciones de usuario.
        
        Returns:
            ft.Container: Contenedor con la barra de encabezado completa
        """
        return ft.Container(
            content=ft.Row([
                # Breadcrumbs de navegación
                ft.Row([
                    ft.Icon("home", size=16, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Configuración", size=14, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Metas de Ahorro", size=16, weight="bold", color="#333333"),
                ], tight=True),
                
                # Spacer para empujar los botones a la derecha
                ft.Container(expand=True),
                
                # Acciones de usuario
                ft.Row([
                    ft.IconButton(
                        icon="refresh",
                        icon_size=20,
                        tooltip="Actualizar datos",
                        on_click=lambda e: self.refresh_data()
                    ),
                    ft.IconButton(
                        icon="add_circle",
                        icon_size=20,
                        tooltip="Agregar meta",
                        on_click=lambda e: self.add_meta()
                    ),
                    ft.IconButton(
                        icon="help_outline",
                        icon_size=20,
                        tooltip="Ayuda",
                        on_click=lambda e: self.show_help()
                    ),
                ], tight=True)
            ], alignment="spaceBetween"),
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def refresh_data(self) -> None:
        """Actualiza los datos de las metas de ahorro."""
        print("Actualizando datos de metas de ahorro...")
        # TODO: Implementar actualización real de datos
        
    def add_meta(self) -> None:
        """Abre el diálogo para agregar una nueva meta de ahorro."""
        print("Agregando nueva meta de ahorro...")
        # TODO: Implementar diálogo de agregar meta
        
    def show_help(self) -> None:
        """Muestra el sistema de ayuda."""
        print("Mostrando ayuda...")
        # TODO: Implementar sistema de ayuda

    def create_main_content(self) -> ft.Container:
        """
        Crea el contenido principal de la vista de metas de ahorro.
        
        Returns:
            ft.Container: Contenedor con todo el contenido principal
        """
        return ft.Container(
            content=ft.Column([
                # Header bar
                self.create_header_bar(),
                
                # Contenido principal con scroll
                ft.Container(
                    content=ft.Column([
                        # Título y descripción
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Metas de Ahorro", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    f"Gestión de objetivos y metas financieras - Última actualización: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        # Tabla de metas de ahorro
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Mis Metas de Ahorro",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Aquí se mostrarán tus metas de ahorro",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=8),
                            bgcolor="white",
                            padding=24,
                            border_radius=12,
                            border=ft.border.all(1, "#E0E0E0")
                        )
                    ], spacing=16, scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=24
                )
            ], expand=True, spacing=0)
        )

    def build(self) -> ft.Container:
        """Construye la vista completa de metas de ahorro."""
        return ft.Container(
            content=ft.Row([
                self.sidebar_menu.create_sidebar(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Metas de Ahorro", size=28, weight="bold"),
                        ft.Text("Gestión de objetivos y metas financieras"),
                    ], spacing=16),
                    expand=True,
                    bgcolor="#F8F9FA",
                    padding=24
                )
            ], expand=True, spacing=0),
            expand=True
        )

def metas_ahorro_view(page: ft.Page) -> ft.View:
    """Función principal que retorna la vista de metas de ahorro."""
    vista = MetasAhorroView(page)
    
    return ft.View(
        route="/metas",
        controls=[vista.build()],
        padding=0,
        spacing=0
    )

def main(page: ft.Page) -> None:
    """
    Función principal para ejecutar la aplicación de forma independiente.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
    """
    # Configuración de la ventana
    page.title = "App Presupuesto - Metas de Ahorro"
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 1000
    page.window.min_height = 700
    page.padding = 0
    page.spacing = 0
    
    # Configuración del tema
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Inter")
    
    # Crear y mostrar la vista
    page.add(metas_ahorro_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)
