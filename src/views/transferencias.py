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
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral reutilizable
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
                    ft.Text("Transferencias", size=16, weight="bold", color="#333333"),
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
        """Actualiza los datos de las transferencias."""
        print("Actualizando datos de transferencias...")
        # TODO: Implementar actualización real de datos
        
    def show_help(self) -> None:
        """Muestra el sistema de ayuda."""
        print("Mostrando ayuda...")
        # TODO: Implementar sistema de ayuda

    def create_main_content(self) -> ft.Container:
        """
        Crea el contenido principal de la vista de transferencias.
        
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
                                    "Transferencias", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Gestión de transferencias entre cuentas bancarias",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        # Formulario de nueva transferencia
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Nueva Transferencia",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Row([
                                    # Campo de selección de cuenta de origen
                                    ft.Column([
                                        ft.Text("Cuenta de Origen", size=12, color="#666666"),
                                        ft.Dropdown(
                                            options=[
                                                ft.dropdown.Option("Banco Nacional - Cuenta Corriente"),
                                                ft.dropdown.Option("Banco Popular - Caja de Ahorro"),
                                            ],
                                            placeholder="Seleccione una cuenta",
                                            width=300,
                                            height=48,
                                            border_radius=8,
                                            border=ft.border.all(1, "#2196F3"),
                                            on_change=lambda e: print(f"Cuenta de origen: {e.control.value}"),
                                        ),
                                    ], expand=True),
                                    
                                    ft.Container(width=16),
                                    
                                    # Campo de selección de cuenta de destino
                                    ft.Column([
                                        ft.Text("Cuenta de Destino", size=12, color="#666666"),
                                        ft.Dropdown(
                                            options=[
                                                ft.dropdown.Option("Banco Nacional - Cuenta Ahorro"),
                                                ft.dropdown.Option("Banco Popular - Cuenta Corriente"),
                                            ],
                                            placeholder="Seleccione una cuenta",
                                            width=300,
                                            height=48,
                                            border_radius=8,
                                            border=ft.border.all(1, "#2196F3"),
                                            on_change=lambda e: print(f"Cuenta de destino: {e.control.value}"),
                                        ),
                                    ], expand=True),
                                ], alignment="center"),
                                
                                ft.Container(height=16),
                                
                                # Campo de importe
                                ft.Row([
                                    ft.Column([
                                        ft.Text("Importe", size=12, color="#666666"),
                                        ft.TextField(
                                            placeholder="Ingrese el importe",
                                            width=620,
                                            height=48,
                                            border_radius=8,
                                            border=ft.border.all(1, "#2196F3"),
                                            prefix_text="$",
                                            on_change=lambda e: print(f"Importe: {e.control.value}"),
                                        ),
                                    ], expand=True),
                                ], alignment="center"),
                                
                                ft.Container(height=16),
                                
                                # Botón de realizar transferencia
                                ft.Row([
                                    ft.ElevatedButton(
                                        "Realizar Transferencia",
                                        on_click=lambda e: print("Transferencia realizada"),
                                        bgcolor="#4CAF50",
                                        color="white",
                                        width=200,
                                        height=48,
                                        border_radius=8,
                                        icon="arrow_forward",
                                        spacing=8,
                                    ),
                                ], alignment="center"),
                            ], spacing=16),
                            bgcolor="white",
                            padding=24,
                            border_radius=12,
                            border=ft.border.all(1, "#E0E0E0")
                        ),
                        
                        ft.Container(height=32),
                        
                        # Historial de transferencias
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Historial de Transferencias",
                                    size=20,
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    "Últimas transferencias realizadas",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=8),
                            margin=ft.margin.only(bottom=16)
                        ),
                        
                        # Tabla de historial de transferencias
                        ft.Container(
                            content=ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Fecha", weight="bold")),
                                    ft.DataColumn(ft.Text("Cuenta Origen", weight="bold")),
                                    ft.DataColumn(ft.Text("Cuenta Destino", weight="bold")),
                                    ft.DataColumn(ft.Text("Importe", weight="bold")),
                                    ft.DataColumn(ft.Text("Estado", weight="bold")),
                                ],
                                rows=[
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text("01/10/2025")),
                                            ft.DataCell(ft.Text("Banco Nacional - Cuenta Corriente")),
                                            ft.DataCell(ft.Text("Banco Popular - Caja de Ahorro")),
                                            ft.DataCell(ft.Text("$1,000.00")),
                                            ft.DataCell(ft.Text("Completada", weight="bold", color="#4CAF50")),
                                        ]
                                    ),
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text("30/09/2025")),
                                            ft.DataCell(ft.Text("Banco Popular - Cuenta Corriente")),
                                            ft.DataCell(ft.Text("Banco Nacional - Cuenta Ahorro")),
                                            ft.DataCell(ft.Text("$500.00")),
                                            ft.DataCell(ft.Text("Pendiente", weight="bold", color="#FF9800")),
                                        ]
                                    ),
                                ],
                                border=ft.border.all(1, "#E0E0E0"),
                                border_radius=8,
                                vertical_lines=ft.BorderSide(1, "#F5F5F5"),
                                horizontal_lines=ft.BorderSide(1, "#F5F5F5"),
                                heading_row_color="#F8F9FA",
                                heading_row_height=50,
                                data_row_min_height=45,
                                column_spacing=20,
                            ),
                            bgcolor="white",
                            border_radius=8,
                            padding=0,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=3,
                                color="#00000008",
                                offset=ft.Offset(0, 1)
                            )
                        )
                    ], 
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0
                    ),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=24, vertical=16)
                )
            ], spacing=0),
            expand=True
        )

    def build(self) -> ft.Container:
        """
        Construye la vista completa de transferencias usando componentes reutilizables.
        
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

def transferencias_view(page: ft.Page) -> ft.View:
    """
    Función principal que retorna la vista de transferencias.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
        
    Returns:
        ft.View: Vista de transferencias con componentes reutilizables
    """
    # Crear la vista
    transferencias = TransferenciasView(page)
    
    # Retornar ft.View
    return ft.View(
        route="/transferencias",
        controls=[
            transferencias.build()
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
