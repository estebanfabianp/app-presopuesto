"""
Módulo de Vista de Dashboard Principal

Este módulo contiene la implementación de la vista del dashboard principal
de la aplicación de presupuesto. Proporciona una vista general del estado
financiero y métricas clave.

Clases:
    DashboardView: Vista principal del dashboard con métricas y resúmenes

Autor: [esteban patiño]  
Fecha: [30-sep-2025]
Versión: 1.0 - Vista de dashboard principal
"""

import flet as ft
import datetime
from typing import List, Optional, Dict, Any

# Importar el componente de sidebar reutilizable
from sidebar import create_sidebar_menu


class DashboardView:
    """
    Vista principal del dashboard.
    
    Esta clase gestiona la vista del dashboard que muestra:
    - Métricas financieras principales
    - Gráficos de resumen
    - Alertas y notificaciones
    - Vista general del estado financiero
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral reutilizable
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista del dashboard.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        
        # Crear el menú lateral usando el componente reutilizable
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=0,  # "Dashboard" está seleccionado
            navigation_callback=self.handle_navigation
        )
    
    def handle_navigation(self, route: str, index: int) -> None:
        """
        Maneja la navegación desde el menú lateral.
        
        Args:
            route (str): Ruta de destino
            index (int): Índice del elemento seleccionado
        """
        print(f"Navegando desde dashboard a: {route} (índice: {index})")
        
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)
    
    def create_header_bar(self) -> ft.Container:
        """
        Crea la barra de encabezado del dashboard.
        
        Returns:
            ft.Container: Contenedor con la barra de encabezado
        """
        return ft.Container(
            content=ft.Row([
                # Breadcrumbs de navegación
                ft.Row([
                    ft.Icon("home", size=16, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Dashboard", size=16, weight="bold", color="#333333"),
                ], tight=True),
                
                ft.Container(expand=True),
                
                # Acciones de usuario
                ft.Row([
                    ft.IconButton(
                        icon="refresh",
                        icon_size=20,
                        tooltip="Actualizar dashboard",
                        on_click=lambda e: self.refresh_dashboard()
                    ),
                    ft.IconButton(
                        icon="settings",
                        icon_size=20,
                        tooltip="Configurar dashboard",
                        on_click=lambda e: self.configure_dashboard()
                    ),
                ], tight=True)
            ], alignment="spaceBetween"),
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def refresh_dashboard(self) -> None:
        """Actualiza los datos del dashboard."""
        print("Actualizando dashboard...")
        
    def configure_dashboard(self) -> None:
        """Abre configuración del dashboard."""
        print("Configurando dashboard...")
    
    def create_main_content(self) -> ft.Container:
        """
        Crea el contenido principal del dashboard.
        
        Returns:
            ft.Container: Contenedor con todo el contenido principal
        """
        return ft.Container(
            content=ft.Column([
                self.create_header_bar(),
                
                ft.Container(
                    content=ft.Column([
                        # Título y descripción
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Dashboard Principal", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    f"Vista general de tu situación financiera - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        # Contenido del dashboard
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Métricas Principales",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Aquí se mostrarán las métricas principales del dashboard",
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
        Construye la vista completa del dashboard.
        
        Returns:
            ft.Container: Vista completa lista para ser añadida a la página
        """
        return ft.Container(
            content=ft.Row([
                self.sidebar_menu.create_sidebar(),
                ft.Container(
                    content=self.create_main_content(),
                    expand=True,
                    bgcolor="#F8F9FA"
                )
            ], expand=True, spacing=0),
            expand=True
        )

def dashboard_view(page: ft.Page) -> ft.View:
    """
    Función principal que retorna la vista del dashboard.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
        
    Returns:
        ft.View: Vista del dashboard
    """
    dashboard = DashboardView(page)
    
    return ft.View(
        route="/dashboard",
        controls=[dashboard.build()],
        padding=0,
        spacing=0
    )

def main(page: ft.Page) -> None:
    """
    Función principal para ejecutar la vista independientemente.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
    """
    page.title = "App Presupuesto - Dashboard"
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 1000
    page.window.min_height = 700
    page.padding = 0
    page.spacing = 0
    
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Inter")
    
    page.add(dashboard_view(page))

if __name__ == "__main__":
    ft.app(target=main)

