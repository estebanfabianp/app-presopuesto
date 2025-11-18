"""
Módulo de Vista de Perfil de Usuario

Este módulo contiene la implementación de la vista del perfil de usuario
de la aplicación de presupuesto.

Clases:
    PerfilView: Vista principal del perfil de usuario

Autor: [esteban patiño]  
Fecha: [30-sep-2025]
Versión: 1.0 - Vista de perfil de usuario
"""

import flet as ft
import datetime
from typing import List, Optional, Dict, Any

from sidebar import create_sidebar_menu


class PerfilView:
    """
    Vista principal del perfil de usuario.
    
    Esta clase gestiona la vista del perfil que incluye:
    - Información personal del usuario
    - Configuraciones de cuenta
    - Foto de perfil
    - Preferencias personales
    """
    
    def __init__(self, page: ft.Page) -> None:
        """Inicializa la vista del perfil."""
        self.page = page
        
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=14,  # "Perfil" está seleccionado
            user_data={
                "name": "John Doe",
                "email": "john.doe@email.com", 
                "avatar_initials": "JD",
                "avatar_color": "#2196F3"
            },
            navigation_callback=self.handle_navigation
        )
    
    def handle_navigation(self, route: str, index: int) -> None:
        """Maneja la navegación desde el menú lateral."""
        print(f"Navegando desde perfil a: {route} (índice: {index})")
        
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)
    
    def create_main_content(self) -> ft.Container:
        """Crea el contenido principal del perfil."""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Perfil de Usuario", size=28, weight="bold"),
                        ft.Text(f"Gestiona tu información personal - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Información Personal", size=20, weight="bold"),
                                ft.Text("Edita tu información de perfil y preferencias"),
                            ], spacing=8),
                            bgcolor="white",
                            padding=24,
                            border_radius=12,
                            border=ft.border.all(1, "#E0E0E0")
                        )
                    ], spacing=16),
                    expand=True,
                    padding=24
                )
            ], expand=True)
        )

    def build(self) -> ft.Container:
        """Construye la vista completa del perfil."""
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

def perfil_view(page: ft.Page) -> ft.View:
    """Función principal que retorna la vista del perfil."""
    vista = PerfilView(page)
    
    return ft.View(
        route="/perfil",
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
    page.title = "App Presupuesto - Perfil de Usuario"
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
    page.add(perfil_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)


