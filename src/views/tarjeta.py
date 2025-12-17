"""
Módulo de Vista de Constantes Financieras

Este módulo contiene la implementación de la vista de constantes financieras
de la aplicación de presupuesto. Utiliza componentes reutilizables para mantener
consistencia en la interfaz.

Clases:
    ConstantesView: Vista principal que muestra las constantes financieras

Autor: [esteban patiño]  
Fecha: [30-sep-2025]
Versión: 2.0 - Refactorizado con componentes reutilizables
"""

import flet as ft
import datetime
import random
from typing import List, Optional, Dict, Any

# Importar el componente de sidebar reutilizable
from sidebar import create_sidebar_menu


class ConstantesView:
    """
    Vista principal de constantes financieras.
    
    Esta clase gestiona la vista de constantes del sistema que muestra:
    - Barra de encabezado con breadcrumbs y acciones
    - Tabla de constantes del sistema
    - Configuraciones financieras
    - Parámetros de cálculo
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral reutilizable
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de constantes.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        
        # Crear el menú lateral usando el componente reutilizable
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=16,  # "Configuración" está seleccionado para constantes
            user_data={
                "name": "John Doe",
                "email": "john.doe@email.com", 
                "avatar_initials": "JD",
                "avatar_color": "#2196F3"
            },
            navigation_callback=self.handle_navigation
        )
    
    def handle_navigation(self, route: str, index: int) -> None:
        """
        Maneja la navegación desde el menú lateral.
        
        Args:
            route (str): Ruta de destino
            index (int): Índice del elemento seleccionado
        """
        print(f"Navegando desde constantes a: {route} (índice: {index})")
        
        # Navegación por defecto
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
                    ft.Text("Constantes del Sistema", size=16, weight="bold", color="#333333"),
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
                        tooltip="Agregar constante",
                        on_click=lambda e: self.add_constant()
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
        """Actualiza los datos de las constantes."""
        print("Actualizando datos de constantes...")
        # TODO: Implementar actualización real de datos
        
    def add_constant(self) -> None:
        """Abre el diálogo para agregar una nueva constante."""
        print("Agregando nueva constante...")
        # TODO: Implementar diálogo de agregar constante
        
    def show_help(self) -> None:
        """Muestra el sistema de ayuda."""
        print("Mostrando ayuda...")
        # TODO: Implementar sistema de ayuda

    def create_main_content(self) -> ft.Container:
        """
        Crea el contenido principal de la vista de constantes.
        
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
                                    "Constantes del Sistema", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    f"Configuración de parámetros y constantes financieras - Última actualización: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        # Tabla de constantes
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Tabla de Constantes",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Aquí se mostrarán las constantes del sistema",
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
        """
        Construye la vista completa de constantes usando componentes reutilizables.
        
        Returns:
            ft.Container: Vista completa lista para ser añadida a la página
        """
        return ft.Container(
            content=ft.Row([
                # Sidebar izquierdo usando componente reutilizable
                self.sidebar_menu.create_sidebar(),
                # Contenido principal
                ft.Container(
                    content=self.create_main_content(),
                    expand=True,
                    bgcolor="#F8F9FA"
                )
            ], expand=True, spacing=0),
            expand=True
        )

def constantes_view(page: ft.Page) -> ft.View:
    """
    Función principal que retorna la vista de constantes del sistema.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
        
    Returns:
        ft.View: Vista de constantes con componentes reutilizables
    """
    # Crear la vista
    constantes = ConstantesView(page)
    
    # Retornar ft.View
    return ft.View(
        route="/constantes",
        controls=[
            constantes.build()
        ],
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
    page.title = "App Presupuesto - Constantes del Sistema"
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
    page.add(constantes_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)