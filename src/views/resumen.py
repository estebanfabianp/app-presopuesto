"""
Módulo de Vista de Resumen Financiero

Este módulo contiene la implementación de la vista principal del resumen financiero
de la aplicación de presupuesto. Incluye un menú lateral navegable y un dashboard
con información financiera detallada.

Clases:
    LeftSidebarMenu: Gestiona el menú lateral de navegación con perfil de usuario
    ResumenView: Vista principal que muestra el resumen financiero completo

Autor: [Tu nombre]
Fecha: [Fecha actual]
Versión: 1.0
"""

import flet as ft
import datetime
import random
from typing import List, Optional, Dict, Any, Callable


class LeftSidebarMenu:
    """
    Clase para manejar el menú lateral de navegación.
    
    Esta clase gestiona la creación y comportamiento del menú lateral que incluye:
    - Perfil de usuario
    - Navegación por secciones
    - Badges de notificación
    - Estado de selección
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        selected_index (int): Índice del elemento de menú actualmente seleccionado
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa el menú lateral.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        self.selected_index = 1  # Default to "Resumen Financiero"
        
    def create_menu_item(
        self, 
        icon: str, 
        title: str, 
        index: int, 
        badge_count: Optional[int] = None
    ) -> ft.Container:
        """
        Crea un elemento individual del menú lateral.
        
        Args:
            icon (str): Nombre del ícono de Material Design
            title (str): Texto del título del elemento de menú
            index (int): Índice único del elemento para control de selección
            badge_count (Optional[int]): Número a mostrar en el badge de notificación
            
        Returns:
            ft.Container: Contenedor con el elemento de menú configurado
        """
        
        def on_click(e: ft.ControlEvent) -> None:
            """
            Maneja el evento de clic en un elemento del menú.
            
            Args:
                e (ft.ControlEvent): Evento de control de Flet
            """
            self.selected_index = index
            self.update_menu_selection()
            self.navigate_to_section(title)
        
        is_selected = index == self.selected_index
        
        # Crear badge si hay contador
        badge = None
        if badge_count and badge_count > 0:
            badge = ft.Container(
                content=ft.Text(
                    str(badge_count), 
                    size=10, 
                    color="white",
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor="#F44336",  # Color rojo para alertas
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                margin=ft.margin.only(left=5)
            )
        
        # Contenedor del ícono con badge opcional
        icon_container = ft.Row([
            ft.Icon(
                icon, 
                size=20, 
                color="#2196F3" if is_selected else "#666666"  # Azul si está seleccionado
            ),
            badge if badge else ft.Container()
        ], tight=True) if badge else ft.Icon(
            icon, 
            size=20, 
            color="#2196F3" if is_selected else "#666666"
        )
        
        return ft.Container(
            content=ft.ListTile(
                leading=icon_container,
                title=ft.Text(
                    title, 
                    size=14,
                    weight="w600" if is_selected else "w400",  # Negrita si está seleccionado
                    color="#2196F3" if is_selected else "#333333"
                ),
                on_click=on_click,
            ),
            bgcolor="#E3F2FD" if is_selected else "transparent",  # Fondo azul claro si está seleccionado
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=8, vertical=1),
            border=ft.border.all(1, "#2196F3") if is_selected else None,  # Borde azul si está seleccionado
        )
    
    def create_section_divider(self, title: str) -> ft.Container:
        """
        Crea un divisor de sección para agrupar elementos del menú.
        
        Args:
            title (str): Título de la sección
            
        Returns:
            ft.Container: Contenedor con el divisor de sección
        """
        return ft.Container(
            content=ft.Text(
                title.upper(), 
                size=11, 
                color="#666666",
                weight=ft.FontWeight.BOLD
            ),
            margin=ft.margin.only(left=16, top=16, bottom=8)
        )
    
    def update_menu_selection(self) -> None:
        """
        Actualiza la selección visual del menú.
        
        Este método se encarga de refrescar la página para mostrar
        los cambios visuales cuando se selecciona un nuevo elemento.
        """
        # TODO: Implementar lógica más específica para actualizar solo los elementos necesarios
        self.page.update()
    
    def navigate_to_section(self, section: str) -> None:
        """
        Navega a la sección seleccionada.
        
        Args:
            section (str): Nombre de la sección a la cual navegar
            
        Note:
            Por ahora solo imprime el destino. En una implementación completa,
            aquí se manejaría el enrutamiento real de la aplicación.
        """
        print(f"Navegando a: {section}")
        # TODO: Implementar lógica de navegación real entre vistas
        
    def create_user_profile(self) -> ft.Container:
        """
        Crea la sección del perfil de usuario en la parte superior del menú.
        
        Incluye:
        - Avatar del usuario
        - Nombre y email
        - Menú de opciones del perfil
        
        Returns:
            ft.Container: Contenedor con el perfil de usuario completo
        """
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        # Avatar circular con iniciales
                        ft.CircleAvatar(
                            content=ft.Text("JD", color="white", size=16, weight="bold"),
                            bgcolor="#2196F3",
                            radius=24
                        ),
                        # Información del usuario
                        ft.Column([
                            ft.Text(
                                "John Doe", 
                                size=16, 
                                weight="bold",
                                color="#333333"
                            ),
                            ft.Text(
                                "john.doe@email.com", 
                                size=12, 
                                color="#666666"
                            ),
                        ], spacing=2, expand=True),
                        # Botón de opciones del perfil
                        ft.IconButton(
                            icon="more_vert",
                            icon_size=16,
                            icon_color="#666666",
                            on_click=lambda e: print("Profile menu")  # TODO: Implementar menú real
                        )
                    ], alignment="center"),
                    padding=16
                ),
                # Línea divisoria
                ft.Divider(height=1, color="#E0E0E0")
            ], spacing=0),
            margin=ft.margin.only(bottom=10)
        )
    
    def create_sidebar(self) -> ft.Container:
        """
        Crea el menú lateral completo con todas las secciones.
        
        Estructura del menú:
        - Perfil de usuario
        - Sección Principal (Dashboard, Resumen)
        - Sección Transacciones
        - Sección Presupuestos
        - Sección Cuentas
        - Sección Reportes
        - Sección Configuración
        - Logout
        
        Returns:
            ft.Container: Contenedor con el menú lateral completo
        """
        return ft.Container(
            width=280,  # Ancho fijo del sidebar
            bgcolor="#FAFAFA",  # Color de fondo gris claro
            content=ft.Column([
                # Header con perfil de usuario
                self.create_user_profile(),
                
                # Contenido scrolleable del menú
                ft.Container(
                    content=ft.Column([
                        # Sección Principal
                        self.create_section_divider("PRINCIPAL"),
                        self.create_menu_item("dashboard", "Dashboard", 0),
                        self.create_menu_item("account_balance_wallet", "Resumen Financiero", 1),
                        
                        # Sección Transacciones
                        self.create_section_divider("TRANSACCIONES"),
                        self.create_menu_item("add_circle_outline", "Nueva Transacción", 2),
                        self.create_menu_item("list_alt", "Historial", 3, badge_count=5),
                        self.create_menu_item("swap_horiz", "Transferencias", 4),
                        
                        # Sección Presupuestos
                        self.create_section_divider("PRESUPUESTOS"),
                        self.create_menu_item("pie_chart", "Presupuestos", 5),
                        self.create_menu_item("trending_up", "Metas de Ahorro", 6),
                        self.create_menu_item("category", "Categorías", 7),
                        
                        # Sección Cuentas
                        self.create_section_divider("CUENTAS"),
                        self.create_menu_item("account_balance", "Cuentas Bancarias", 8),
                        self.create_menu_item("credit_card", "Tarjetas de Crédito", 9, badge_count=2),
                        self.create_menu_item("savings", "Inversiones", 10),
                        
                        # Sección Reportes
                        self.create_section_divider("REPORTES"),
                        self.create_menu_item("analytics", "Análisis", 11),
                        self.create_menu_item("assessment", "Reportes", 12),
                        self.create_menu_item("file_download", "Exportar Datos", 13),
                        
                        # Sección Configuración
                        self.create_section_divider("CONFIGURACIÓN"),
                        self.create_menu_item("person", "Perfil", 14),
                        self.create_menu_item("notifications", "Notificaciones", 15, badge_count=3),
                        self.create_menu_item("settings", "Configuración", 16),
                        
                        # Espacio adicional
                        ft.Container(height=20),
                        
                        # Logout en la parte inferior
                        ft.Divider(height=1, color="#E0E0E0"),
                        self.create_menu_item("logout", "Cerrar Sesión", 17),
                        
                    ], spacing=0),
                    expand=True,
                    padding=ft.padding.only(bottom=20)
                )
            ], 
            scroll=ft.ScrollMode.AUTO,  # Scroll automático si el contenido es muy largo
            expand=True,
            spacing=0
            ),
            border=ft.border.only(right=ft.BorderSide(1, "#E0E0E0"))  # Borde derecho sutil
        )


class ResumenView:
    """
    Vista principal del resumen financiero.
    
    Esta clase gestiona la vista principal de la aplicación que muestra:
    - Barra de encabezado con breadcrumbs y acciones
    - Tarjetas de resumen financiero
    - Tablas de datos financieros
    - Gráfico de ingresos vs gastos
    - Layout de dos columnas responsivo
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral
    """
    
    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de resumen.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page
        self.sidebar_menu = LeftSidebarMenu(page)
    
    def create_header_bar(self) -> ft.Container:
        """
        Crea la barra de encabezado con breadcrumbs y acciones de usuario.
        
        Incluye:
        - Breadcrumbs de navegación
        - Botones de acción (actualizar, notificaciones, ayuda)
        
        Returns:
            ft.Container: Contenedor con la barra de encabezado completa
        """
        return ft.Container(
            content=ft.Row([
                # Breadcrumbs de navegación
                ft.Row([
                    ft.Icon("home", size=16, color="#666666"),
                    ft.Text(" / ", color="#666666"),
                    ft.Text("Resumen Financiero", size=16, weight="bold", color="#333333"),
                ], tight=True),
                
                # Spacer para empujar los botones a la derecha
                ft.Container(expand=True),
                
                # Acciones de usuario
                ft.Row([
                    ft.IconButton(
                        icon="refresh",
                        icon_size=20,
                        tooltip="Actualizar datos",
                        on_click=lambda e: print("Refresh")  # TODO: Implementar actualización real
                    ),
                    ft.IconButton(
                        icon="notifications",
                        icon_size=20,
                        tooltip="Notificaciones",
                        on_click=lambda e: print("Notifications")  # TODO: Abrir panel de notificaciones
                    ),
                    ft.IconButton(
                        icon="help_outline",
                        icon_size=20,
                        tooltip="Ayuda",
                        on_click=lambda e: print("Help")  # TODO: Abrir sistema de ayuda
                    ),
                ], tight=True)
            ], alignment="spaceBetween"),
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def create_summary_cards(self) -> ft.Container:
        """
        Crea las tarjetas de resumen financiero mejoradas.
        
        Cada tarjeta incluye:
        - Ícono representativo
        - Título del tipo de cuenta
        - Monto principal
        - Indicador de cambio porcentual
        
        Returns:
            ft.Container: Contenedor con todas las tarjetas de resumen
        """
        # Datos de configuración para las tarjetas
        cards_data: List[Dict[str, Any]] = [
            {
                "title": "Cuentas Bancarias",
                "amount": "$12,500.00",
                "icon": "account_balance",
                "color": "#2196F3",  # Azul
                "bg_color": "#E3F2FD",
                "change": "+2.5%",
                "change_positive": True
            },
            {
                "title": "Préstamos",
                "amount": "$5,200.00",
                "icon": "trending_down",
                "color": "#F44336",  # Rojo
                "bg_color": "#FFEBEE",
                "change": "-1.2%",
                "change_positive": False
            },
            {
                "title": "Tarjetas de Crédito",
                "amount": "$2,800.00",
                "icon": "credit_card",
                "color": "#FF9800",  # Naranja
                "bg_color": "#FFF3E0",
                "change": "+5.1%",
                "change_positive": True
            },
            {
                "title": "Fondos",
                "amount": "$8,000.00",
                "icon": "trending_up",
                "color": "#4CAF50",  # Verde
                "bg_color": "#E8F5E9",
                "change": "+8.3%",
                "change_positive": True
            },
        ]
        
        cards: List[ft.Container] = []
        for data in cards_data:
            card = ft.Container(
                content=ft.Column([
                    # Fila superior con ícono e indicador de cambio
                    ft.Row([
                        ft.Icon(
                            data["icon"], 
                            size=24, 
                            color=data["color"]
                        ),
                        ft.Container(expand=True),  # Spacer
                        # Badge de cambio porcentual
                        ft.Container(
                            content=ft.Text(
                                data["change"],
                                size=12,
                                weight="bold",
                                color="#4CAF50" if data["change_positive"] else "#F44336"
                            ),
                            bgcolor="#E8F5E9" if data["change_positive"] else "#FFEBEE",
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ]),
                    # Título de la tarjeta
                    ft.Text(
                        data["title"], 
                        size=14, 
                        weight="w500",
                        color="#666666"
                    ),
                    # Monto principal
                    ft.Text(
                        data["amount"], 
                        size=20, 
                        weight="bold", 
                        color="#333333"
                    ),
                ], 
                spacing=8,
                alignment="start"
                ),
                bgcolor=data["bg_color"],
                border_radius=12,
                padding=20,
                expand=True,
                margin=ft.margin.only(right=16),
                border=ft.border.all(1, "#E0E0E0"),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=3,
                    color="#00000010",  # Sombra sutil
                    offset=ft.Offset(0, 1)
                )
            )
            cards.append(card)
        
        return ft.Container(
            content=ft.Row(cards, spacing=0, expand=False, alignment="center"),
            margin=ft.margin.only(bottom=32)
        )
    
    def create_data_table(
        self, 
        title: str, 
        columns: List[ft.DataColumn], 
        rows: List[ft.DataRow], 
        icon: Optional[str] = None
    ) -> ft.Container:
        """
        Crea una tabla de datos mejorada con header personalizado.
        
        Args:
            title (str): Título de la tabla
            columns (List[ft.DataColumn]): Lista de columnas de la tabla
            rows (List[ft.DataRow]): Lista de filas de datos
            icon (Optional[str]): Ícono opcional para el header
            
        Returns:
            ft.Container: Contenedor con la tabla completa
        """
        return ft.Container(
            content=ft.Column([
                # Header de la tabla con título, ícono y menú de opciones
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=20, color="#2196F3") if icon else ft.Container(),
                        ft.Text(title, size=18, weight="bold", color="#333333"),
                        ft.Container(expand=True),  # Spacer
                        ft.IconButton(
                            icon="more_vert",
                            icon_size=16,
                            icon_color="#666666",
                            on_click=lambda e: print(f"Options for {title}")  # TODO: Implementar menú de opciones
                        )
                    ]),
                    margin=ft.margin.only(bottom=16)
                ),
                
                # Tabla con estilo profesional
                ft.Container(
                    content=ft.DataTable(
                        columns=columns,
                        rows=rows,
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
            ]),
            margin=ft.margin.only(bottom=32)
        )
        
    def create_income_vs_expense_chart(self) -> ft.Container:
        """
        Crea un gráfico visual de ingresos vs gastos de los últimos 30 días.
        
        Si Plotly está disponible, genera datos realistas y configura un gráfico completo.
        Si no está disponible, muestra una representación visual simplificada.
        
        Returns:
            ft.Container: Contenedor con el gráfico o su representación visual
        """
        try:
            import plotly.graph_objects as go
            import plotly.express as px
        except ImportError:
            # Fallback visual cuando Plotly no está disponible
            return ft.Container(
                content=ft.Column([
                    ft.Icon("bar_chart", size=48, color="#FF9800"),
                    ft.Text(
                        "Gráfico no disponible",
                        size=16,
                        weight="bold",
                        color="#333333"
                    ),
                    ft.Text(
                        "Instala plotly para ver el gráfico de ingresos vs gastos",
                        size=12,
                        color="#666666",
                        text_align="center"
                    ),
                ], 
                horizontal_alignment="center",
                spacing=8
                ),
                padding=40,
                bgcolor="white",
                border_radius=12,
                border=ft.border.all(1, "#E0E0E0"),
                height=400,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=3,
                    color="#00000008",
                    offset=ft.Offset(0, 1)
                )
            )

        # Generar datos de ejemplo para los últimos 30 días
        today = datetime.date.today()
        dates: List[str] = []
        ingresos: List[int] = []
        gastos: List[int] = []
        
        for i in range(29, -1, -1):
            date = today - datetime.timedelta(days=i)
            dates.append(date.strftime("%d/%m"))
            
            # Generar datos más realistas con variabilidad
            base_income = random.randint(200, 500)
            base_expense = random.randint(150, 450)
            
            # Añadir variabilidad de fin de semana (más gastos, menos ingresos)
            if date.weekday() >= 5:  # Sábado y domingo
                base_expense = int(base_expense * 1.3)
                base_income = int(base_income * 0.7)
            
            ingresos.append(base_income)
            gastos.append(base_expense)

        # Configuración del gráfico Plotly (código preparado pero no ejecutado en el fallback visual)
        # TODO: Implementar integración real de Plotly cuando sea necesario

        # Representación visual simplificada
        return ft.Container(
            content=ft.Column([
                # Header del gráfico
                ft.Container(
                    content=ft.Row([
                        ft.Icon("trending_up", size=20, color="#2196F3"),
                        ft.Text("Análisis de Flujo de Efectivo", size=18, weight="bold", color="#333333"),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon="fullscreen",
                            icon_size=16,
                            icon_color="#666666",
                            tooltip="Pantalla completa",
                            on_click=lambda e: print("Fullscreen chart")  # TODO: Implementar vista completa
                        )
                    ]),
                    margin=ft.margin.only(bottom=16)
                ),
                
                # Gráfico simplificado usando contenedores
                ft.Container(
                    content=ft.Column([
                        # Simulación visual del gráfico
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ingresos vs Gastos", size=16, weight="bold", color="#333333"),
                                ft.Container(height=10),
                                
                                # Barras de ejemplo para simular el gráfico
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text("Ingresos\nPromedio", size=10, color="white", text_align="center"),
                                        bgcolor="#4CAF50",
                                        height=80,
                                        width=80,
                                        border_radius=8,
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Container(width=20),
                                    ft.Container(
                                        content=ft.Text("Gastos\nPromedio", size=10, color="white", text_align="center"),
                                        bgcolor="#F44336",
                                        height=65,
                                        width=80,
                                        border_radius=8,
                                        alignment=ft.alignment.center
                                    ),
                                ], alignment="center"),
                                
                                ft.Container(height=20),
                                
                                # Estadísticas calculadas
                                ft.Column([
                                    ft.Row([
                                        ft.Text("• ", color="#4CAF50", size=16),
                                        ft.Text("Ingresos promedio: $320/día", size=12, color="#333333")
                                    ], tight=True),
                                    ft.Row([
                                        ft.Text("• ", color="#F44336", size=16),
                                        ft.Text("Gastos promedio: $280/día", size=12, color="#333333")
                                    ], tight=True),
                                    ft.Row([
                                        ft.Text("• ", color="#2196F3", size=16),
                                        ft.Text("Balance promedio: +$40/día", size=12, color="#333333")
                                    ], tight=True),
                                ], spacing=5),
                                
                                ft.Container(height=15),
                                
                                # Indicador de tendencia
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon("trending_up", size=16, color="#4CAF50"),
                                        ft.Text("Tendencia positiva", size=12, color="#4CAF50", weight="bold")
                                    ], tight=True),
                                    bgcolor="#E8F5E9",
                                    border_radius=6,
                                    padding=8
                                )
                            ], 
                            horizontal_alignment="center",
                            spacing=0
                            ),
                            padding=20,
                            alignment=ft.alignment.center
                        )
                    ]),
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#E0E0E0"),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=3,
                        color="#00000008",
                        offset=ft.Offset(0, 1)
                    ),
                    height=280
                )
            ]),
            margin=ft.margin.only(bottom=32)
        )

    def create_main_content(self) -> ft.Container:
        """
        Crea el contenido principal de la vista de resumen.
        
        Estructura del contenido:
        1. Header bar con breadcrumbs y acciones
        2. Título y fecha de última actualización
        3. Tarjetas de resumen financiero
        4. Layout de dos columnas:
           - Izquierda: Tablas de datos financieros
           - Derecha: Gráfico y tablas de resumen
        
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
                                    "Resumen Financiero", 
                                    size=28, 
                                    weight="bold",
                                    color="#333333"
                                ),
                                ft.Text(
                                    f"Última actualización: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=14,
                                    color="#666666"
                                ),
                            ], spacing=4),
                            margin=ft.margin.only(bottom=32)
                        ),
                        
                        # Tarjetas de resumen
                        self.create_summary_cards(),
                        
                        # Layout principal con dos columnas
                        ft.Row([
                            # Columna izquierda - Tablas principales (60% del ancho)
                            ft.Container(
                                content=ft.Column([
                                    # Tabla de Cuentas Bancarias
                                    self.create_data_table(
                                        "Cuentas Bancarias",
                                        [
                                            ft.DataColumn(ft.Text("Cuenta Bancaria", weight="bold")),
                                            ft.DataColumn(ft.Text("Saldo", weight="bold")),
                                            ft.DataColumn(ft.Text("Saldo Conciliado", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Banco Nacional - Cuenta Corriente")),
                                                    ft.DataCell(ft.Text("$7,500.00", weight="w500")),
                                                    ft.DataCell(ft.Text("$7,200.00", weight="w500")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Banco Popular - Caja de Ahorro")),
                                                    ft.DataCell(ft.Text("$5,000.00", weight="w500")),
                                                    ft.DataCell(ft.Text("$4,950.00", weight="w500")),
                                                ]
                                            ),
                                        ],
                                        icon="account_balance"
                                    ),
                                    
                                    # Tabla de Tarjetas de Crédito
                                    self.create_data_table(
                                        "Tarjetas de Crédito",
                                        [
                                            ft.DataColumn(ft.Text("Tarjeta", weight="bold")),
                                            ft.DataColumn(ft.Text("Límite Disponible", weight="bold")),
                                            ft.DataColumn(ft.Text("Saldo Utilizado", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Tarjeta de Crédito - Visa")),
                                                    ft.DataCell(ft.Text("$2,499.00", weight="w500", color="#4CAF50")),
                                                    ft.DataCell(ft.Text("$1,501.00", weight="w500", color="#F44336")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Tarjeta de Crédito - Mastercard")),
                                                    ft.DataCell(ft.Text("$990.00", weight="w500", color="#4CAF50")),
                                                    ft.DataCell(ft.Text("$1,310.00", weight="w500", color="#F44336")),
                                                ]
                                            ),
                                        ],
                                        icon="credit_card"
                                    ),
                                    
                                    # Tabla de Préstamos
                                    self.create_data_table(
                                        "Préstamos",
                                        [
                                            ft.DataColumn(ft.Text("Préstamo", weight="bold")),
                                            ft.DataColumn(ft.Text("Saldo Pendiente", weight="bold")),
                                            ft.DataColumn(ft.Text("Cuota Mensual", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Préstamo Personal - Banco Nacional")),
                                                    ft.DataCell(ft.Text("$3,200.00", weight="w500", color="#F44336")),
                                                    ft.DataCell(ft.Text("$150.00", weight="w500")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Préstamo Auto - Banco Popular")),
                                                    ft.DataCell(ft.Text("$2,000.00", weight="w500", color="#F44336")),
                                                    ft.DataCell(ft.Text("$120.00", weight="w500")),
                                                ]
                                            ),
                                        ],
                                        icon="trending_down"
                                    ),
                                    
                                    # Tabla de Fondos de Inversión
                                    self.create_data_table(
                                        "Fondos de Inversión",
                                        [
                                            ft.DataColumn(ft.Text("Fondo", weight="bold")),
                                            ft.DataColumn(ft.Text("Valor Actual", weight="bold")),
                                            ft.DataColumn(ft.Text("Rendimiento", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Fondo - Renta Variable")),
                                                    ft.DataCell(ft.Text("$5,000.00", weight="w500")),
                                                    ft.DataCell(ft.Text("+$200.00", color="#4CAF50", weight="bold")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Fondo - Renta Fija")),
                                                    ft.DataCell(ft.Text("$3,000.00", weight="w500")),
                                                    ft.DataCell(ft.Text("+$70.00", color="#4CAF50", weight="bold")),
                                                ]
                                            ),
                                        ],
                                        icon="trending_up"
                                    ),   
                                    
                                    # Tabla de Deuda Financiada    
                                    self.create_data_table(
                                        "Deuda Financiada",
                                        [
                                            ft.DataColumn(ft.Text("Entidad", weight="bold")),
                                            ft.DataColumn(ft.Text("Monto", weight="bold")),
                                            ft.DataColumn(ft.Text("Progreso", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Banco Popular")),
                                                    ft.DataCell(ft.Text("$2,000.00", weight="w500")),
                                                    ft.DataCell(ft.Container(
                                                        content=ft.ProgressBar(
                                                            width=120,
                                                            height=8,
                                                            value=0.75,
                                                            color="#4CAF50",
                                                            bgcolor="#E0E0E0"
                                                        ),
                                                        alignment=ft.alignment.center_left
                                                    )),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Luz")),
                                                    ft.DataCell(ft.Text("$150.00", weight="w500")),
                                                    ft.DataCell(ft.Container(
                                                        content=ft.ProgressBar(
                                                            width=120,
                                                            height=8,
                                                            value=0.25,
                                                            color="#FF9800",
                                                            bgcolor="#E0E0E0"
                                                        ),
                                                        alignment=ft.alignment.center_left
                                                    )),
                                                ]
                                            ),
                                        ],
                                        icon="credit_card"
                                    ),
                                ], spacing=0),
                                expand=2,
                                margin=ft.margin.only(right=24)
                            ),
                            
                            # Columna derecha - Gráfico y tablas de resumen (40% del ancho)
                            ft.Container(
                                content=ft.Column([
                                    # Gráfico de ingresos vs gastos
                                    self.create_income_vs_expense_chart(),
                                    
                                    # Tabla de Próxima Transacción 
                                    self.create_data_table(
                                        "Próxima Transacción",
                                        [
                                            ft.DataColumn(ft.Text("Cuenta", weight="bold")),
                                            ft.DataColumn(ft.Text("Importe", weight="bold")),
                                            ft.DataColumn(ft.Text("Días", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Avance")),
                                                    ft.DataCell(ft.Text("$5,000.00", weight="w500")),
                                                    ft.DataCell(ft.Text("2", color="#F44336", weight="bold")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Luz")),
                                                    ft.DataCell(ft.Text("$3,000.00", weight="w500")),
                                                    ft.DataCell(ft.Text("3", color="#FF9800", weight="bold")),
                                                ]
                                            ),
                                        ],
                                        icon="schedule"
                                    ),   
                                    
                                    # Top Categorías del Mes
                                    self.create_data_table(
                                        "Top Categorías del Mes",
                                        [
                                            ft.DataColumn(ft.Text("Categoría", weight="bold")),
                                            ft.DataColumn(ft.Text("Importe", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Banco")),
                                                    ft.DataCell(ft.Text("$5,000.00", weight="w500")),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Servicios")),
                                                    ft.DataCell(ft.Text("$3,000.00", weight="w500")),
                                                ]
                                            ),
                                        ],
                                        icon="category"
                                    ),   
                                    
                                    # Deuda Programada
                                    self.create_data_table(
                                        "Deuda Programada",
                                        [
                                            ft.DataColumn(ft.Text("Categoría", weight="bold")),
                                            ft.DataColumn(ft.Text("Importe", weight="bold")),
                                            ft.DataColumn(ft.Text("Acción", weight="bold")),
                                        ],
                                        [
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Banco")),
                                                    ft.DataCell(ft.Text("$5,000.00", weight="w500")),
                                                    ft.DataCell(ft.IconButton(
                                                        icon="play_circle", 
                                                        icon_color="#4CAF50", 
                                                        tooltip="Iniciar pago", 
                                                        on_click=lambda e: print("Pagar banco")
                                                    )),
                                                ]
                                            ),
                                            ft.DataRow(
                                                cells=[
                                                    ft.DataCell(ft.Text("Luz")),
                                                    ft.DataCell(ft.Text("$3,000.00", weight="w500")),
                                                    ft.DataCell(ft.IconButton(
                                                        icon="pause_circle", 
                                                        icon_color="#FF9800", 
                                                        tooltip="Pausar pago", 
                                                        on_click=lambda e: print("Pausar luz")
                                                    )),
                                                ]
                                            ),
                                        ],
                                        icon="payment"
                                    ),   
                                ], spacing=0),
                                expand=1
                            ),
                        ], spacing=0, expand=True),
                        
                    ], 
                    scroll=ft.ScrollMode.AUTO,  # Scroll automático para contenido largo
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
        Construye la vista completa del resumen financiero.
        
        Combina el menú lateral y el contenido principal en un layout horizontal.
        
        Returns:
            ft.Container: Vista completa lista para ser añadida a la página
        """
        return ft.Container(
            content=ft.Row([
                # Sidebar izquierdo
                self.sidebar_menu.create_sidebar(),
                # Contenido principal
                ft.Container(
                    content=self.create_main_content(),
                    expand=True,
                    bgcolor="#F8F9FA"  # Fondo gris muy claro
                )
            ], expand=True, spacing=0),
            expand=True
        )


def main(page: ft.Page) -> None:
    """
    Función principal de la aplicación.
    
    Configura la página principal de Flet y inicializa la vista de resumen.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
    """
    # Configuración de la ventana
    page.title = "App Presupuesto - Resumen"
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
    resumen_view = ResumenView(page)
    page.add(resumen_view.build())


if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)

