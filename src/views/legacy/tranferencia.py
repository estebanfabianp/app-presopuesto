"""
Módulo de Vista de Transferencias

Este módulo contiene la implementación de la vista de transferencias bancarias
y entre cuentas de la aplicación de presupuesto.

Clases:
    TransferenciasView: Vista principal para gestionar transferencias

Autor: [esteban patiño]  
Fecha: [30-sep-2025]
Versión: 1.0 - Vista de transferencias bancarias
"""

import flet as ft
import datetime
from typing import List, Optional, Dict, Any

from sidebar import create_sidebar_menu


class TransferenciasView:
    """
    Vista principal de transferencias.
    
    Esta clase gestiona la vista de transferencias que muestra:
    - Formulario de nueva transferencia
    - Historial de transferencias
    - Cuentas disponibles
    - Validaciones de saldo
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de transferencias.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=4,  # "Transferencias" está seleccionado
            navigation_callback=self.handle_navigation
        )
    
    def handle_navigation(self, route: str, index: int) -> None:
        """Maneja la navegación desde el menú lateral."""
        print(f"Navegando desde transferencias a: {route} (índice: {index})")
        
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)
    
    def create_header_bar(self) -> ft.Container:
        """Crea la barra de encabezado de transferencias."""
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon("home", size=16, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Transacciones", size=14, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Transferencias", size=16, weight="bold", color="#333333"),
                ], tight=True),
                
                ft.Container(expand=True),
                
                ft.Row([
                    ft.IconButton(
                        icon="add_circle",
                        icon_size=20,
                        tooltip="Nueva transferencia",
                        on_click=lambda e: self.nueva_transferencia()
                    ),
                    ft.IconButton(
                        icon="history",
                        icon_size=20,
                        tooltip="Historial",
                        on_click=lambda e: self.ver_historial()
                    ),
                ], tight=True)
            ], alignment="spaceBetween"),
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def nueva_transferencia(self) -> None:
        """Abre el formulario para nueva transferencia."""
        print("Nueva transferencia...")
        
    def ver_historial(self) -> None:
        """Muestra el historial de transferencias."""
        print("Ver historial...")
    
    def create_main_content(self) -> ft.Container:
        """Crea el contenido principal de transferencias."""
        return ft.Container(
            content=ft.Column([
                self.create_header_bar(),
                
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Transferencias", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    f"Gestión de transferencias entre cuentas - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Formulario de Transferencia",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Realiza transferencias entre tus cuentas bancarias",
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
        """Construye la vista completa de transferencias."""
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

def transferencias_view(page: ft.Page) -> ft.View:
    """Función principal que retorna la vista de transferencias."""
    vista = TransferenciasView(page)
    
    return ft.View(
        route="/transferencias",
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
    page.title = "App Presupuesto - Transferencias"
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
    page.add(transferencias_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)



