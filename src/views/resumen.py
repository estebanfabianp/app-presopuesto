"""
Módulo de Vista de Resumen Financiero

Este módulo contiene la implementación de la vista principal del resumen financiero
de la aplicación de presupuesto. Utiliza componentes reutilizables para mantener
consistencia en la interfaz.

Clases:
    ResumenView: Vista principal que muestra el resumen financiero completo

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
        sidebar_menu (LeftSidebarMenu): Instancia del menú lateral reutilizable
    """

    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de resumen.

        Args:
            page (ft.Page): La página principal de la aplicación Flet
        """
        self.page = page

        # Crear el menú lateral usando el componente reutilizable
        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=1,  # "Resumen Financiero" está seleccionado
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
        print(f"Navegando desde resumen a: {route} (índice: {index})")

        # Aquí se puede implementar lógica específica de navegación
        # Por ejemplo, guardar estado antes de navegar, validaciones, etc.

        # Navegación por defecto
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)

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
                        on_click=lambda e: self.refresh_data()
                    ),
                    ft.IconButton(
                        icon="notifications",
                        icon_size=20,
                        tooltip="Notificaciones",
                        on_click=lambda e: self.show_notifications()
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
        """Actualiza los datos del dashboard."""
        print("Actualizando datos del resumen...")
        # TODO: Implementar actualización real de datos

    def show_notifications(self) -> None:
        """Muestra el panel de notificaciones."""
        print("Mostrando notificaciones...")
        # TODO: Implementar panel de notificaciones

    def show_help(self) -> None:
        """Muestra el sistema de ayuda."""
        print("Mostrando ayuda...")
        # TODO: Implementar sistema de ayuda

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
        Construye la vista completa del resumen financiero usando componentes reutilizables.

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

def resumen_view(page: ft.Page) -> ft.View:
    """
    Función principal que retorna la vista de resumen financiero.

    Args:
        page (ft.Page): La página principal proporcionada por Flet

    Returns:
        ft.View: Vista del resumen financiero con componentes reutilizables
    """
    # Crear la vista
    resumen = ResumenView(page)

    # Retornar ft.View
    return ft.View(
        route="/resumen",
        controls=[
            resumen.build()
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
    page.add(resumen_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.

    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)
