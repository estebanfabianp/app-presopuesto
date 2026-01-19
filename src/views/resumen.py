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
import sys
import os
from typing import List, Optional, Dict, Any

# Importar el componente de sidebar reutilizable
from .sidebar import create_sidebar_menu

# Agregar el path para importar los controladores
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from business.services.producto_controller import obtener_resumen_productos_por_usuario, obtener_productos_por_usuario


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

    def __init__(self, page: ft.Page, user_id: int = 1) -> None:
        """
        Inicializa la vista de resumen.

        Args:
            page (ft.Page): La página principal de la aplicación Flet
            user_id (int): ID del usuario para obtener sus productos
        """
        self.page = page
        self.user_id = user_id
        self.productos_usuario = []
        self.resumen_productos = {}

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
        
        # Cargar datos del usuario al inicializar
        self.cargar_datos_usuario()

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

    def cargar_datos_usuario(self) -> None:
        """
        Carga los datos financieros del usuario desde la base de datos.
        """
        try:
            print(f"Cargando datos para el usuario ID: {self.user_id}")
            
            # Obtener productos del usuario
            self.productos_usuario = obtener_productos_por_usuario(self.user_id)
            
            # Obtener resumen agrupado
            self.resumen_productos = obtener_resumen_productos_por_usuario(self.user_id)
            
            print(f"Productos cargados: {len(self.productos_usuario)}")
            print("Datos cargados exitosamente")
            
        except Exception as e:
            print(f"Error al cargar datos del usuario: {str(e)}")
            # Usar datos de ejemplo en caso de error
            self.productos_usuario = []
            self.resumen_productos = {
                'cuentas_bancarias': {'total': 0, 'cantidad': 0, 'productos': []},
                'tarjetas_credito': {'total': 0, 'cantidad': 0, 'productos': []},
                'prestamos': {'total': 0, 'cantidad': 0, 'productos': []},
                'fondos_inversion': {'total': 0, 'cantidad': 0, 'productos': []},
                'total_patrimonio': 0
            }

    def obtener_productos_usuario_por_tipo(self, tipo_producto: str) -> List[Dict[str, Any]]:
        """
        Obtiene productos específicos del usuario por tipo.
        
        Args:
            tipo_producto (str): Tipo de producto ('cuenta_bancaria', 'tarjeta_credito', 'prestamo', 'fondo_inversion')
        
        Returns:
            List[Dict[str, Any]]: Lista de productos del tipo especificado
        """
        return [p for p in self.productos_usuario if p.get('tipo_producto') == tipo_producto]
        
    def obtener_balance_total_usuario(self) -> Dict[str, float]:
        """
        Calcula el balance total del usuario.
        
        Returns:
            Dict[str, float]: Balance total con activos, pasivos y patrimonio neto
        """
        resumen = self.resumen_productos
        
        activos = (resumen.get('cuentas_bancarias', {}).get('total', 0) + 
                  resumen.get('fondos_inversion', {}).get('total', 0) +
                  resumen.get('tarjetas_credito', {}).get('total', 0))
        
        pasivos = resumen.get('prestamos', {}).get('total', 0)
        
        patrimonio_neto = activos - pasivos
        
        return {
            'activos': activos,
            'pasivos': pasivos,
            'patrimonio_neto': patrimonio_neto
        }

    def refresh_data(self) -> None:
        """Actualiza los datos del dashboard."""
        print("Actualizando datos del resumen...")
        self.cargar_datos_usuario()
        # TODO: Actualizar la UI con los nuevos datos

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
        Crea las tarjetas de resumen financiero mejoradas usando datos reales del usuario.

        Cada tarjeta incluye:
        - Ícono representativo
        - Título del tipo de cuenta
        - Monto principal
        - Indicador de cambio porcentual

        Returns:
            ft.Container: Contenedor con todas las tarjetas de resumen
        """
        # Usar datos reales del usuario o valores por defecto
        resumen = self.resumen_productos
        
        # Datos de configuración para las tarjetas con valores reales
        cards_data: List[Dict[str, Any]] = [
            {
                "title": "Cuentas Bancarias",
                "amount": f"${resumen.get('cuentas_bancarias', {}).get('total', 0):,.2f}",
                "count": resumen.get('cuentas_bancarias', {}).get('cantidad', 0),
                "icon": "account_balance",
                "color": "#2196F3",  # Azul
                "bg_color": "#E3F2FD",
                "change": "+2.5%",  # TODO: Calcular cambio real
                "change_positive": True
            },
            {
                "title": "Préstamos",
                "amount": f"${resumen.get('prestamos', {}).get('total', 0):,.2f}",
                "count": resumen.get('prestamos', {}).get('cantidad', 0),
                "icon": "trending_down",
                "color": "#F44336",  # Rojo
                "bg_color": "#FFEBEE",
                "change": "-1.2%",  # TODO: Calcular cambio real
                "change_positive": False
            },
            {
                "title": "Tarjetas de Crédito",
                "amount": f"${resumen.get('tarjetas_credito', {}).get('total', 0):,.2f}",
                "count": resumen.get('tarjetas_credito', {}).get('cantidad', 0),
                "icon": "credit_card",
                "color": "#FF9800",  # Naranja
                "bg_color": "#FFF3E0",
                "change": "+5.1%",  # TODO: Calcular cambio real
                "change_positive": True
            },
            {
                "title": "Fondos",
                "amount": f"${resumen.get('fondos_inversion', {}).get('total', 0):,.2f}",
                "count": resumen.get('fondos_inversion', {}).get('cantidad', 0),
                "icon": "trending_up",
                "color": "#4CAF50",  # Verde
                "bg_color": "#E8F5E9",
                "change": "+8.3%",  # TODO: Calcular cambio real
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
                    # Título de la tarjeta con contador
                    ft.Row([
                        ft.Text(
                            data["title"],
                            size=14,
                            weight="w500",
                            color="#666666"
                        ),
                        ft.Text(
                            f"({data.get('count', 0)})",
                            size=12,
                            weight="w400",
                            color="#999999"
                        ),
                    ], tight=True),
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

    def create_cuentas_bancarias_table(self) -> ft.Container:
        """
        Crea la tabla de cuentas bancarias usando datos reales del usuario.
        """
        productos_cuentas = self.resumen_productos.get('cuentas_bancarias', {}).get('productos', [])
        
        if not productos_cuentas:
            # Si no hay productos, mostrar mensaje
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay cuentas bancarias registradas", style=ft.TextStyle(italic=True, color="#666666"))),
                        ft.DataCell(ft.Text("--", color="#666666")),
                        ft.DataCell(ft.Text("--", color="#666666")),
                    ]
                )
            ]
        else:
            rows = []
            for producto in productos_cuentas:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(producto.get('nombre', 'Cuenta sin nombre'))),
                            ft.DataCell(ft.Text(f"${producto.get('saldo_actual', 0):,.2f}", weight="w500")),
                            ft.DataCell(ft.Text(f"${producto.get('saldo_disponible', 0):,.2f}", weight="w500")),
                        ]
                    )
                )
        
        return self.create_data_table(
            "Cuentas Bancarias",
            [
                ft.DataColumn(ft.Text("Cuenta Bancaria", weight="bold")),
                ft.DataColumn(ft.Text("Saldo Actual", weight="bold")),
                ft.DataColumn(ft.Text("Saldo Disponible", weight="bold")),
            ],
            rows,
            icon="account_balance"
        )

    def create_tarjetas_credito_table(self) -> ft.Container:
        """
        Crea la tabla de tarjetas de crédito usando datos reales del usuario.
        """
        productos_tarjetas = self.resumen_productos.get('tarjetas_credito', {}).get('productos', [])
        
        if not productos_tarjetas:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay tarjetas de crédito registradas", style=ft.TextStyle(italic=True, color="#666666"))),
                        ft.DataCell(ft.Text("--", color="#666666")),
                        ft.DataCell(ft.Text("--", color="#666666")),
                    ]
                )
            ]
        else:
            rows = []
            for producto in productos_tarjetas:
                limite = producto.get('limite_credito', 0)
                saldo_usado = limite - producto.get('saldo_disponible', 0)
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(producto.get('nombre', 'Tarjeta sin nombre'))),
                            ft.DataCell(ft.Text(f"${producto.get('saldo_disponible', 0):,.2f}", weight="w500", color="#4CAF50")),
                            ft.DataCell(ft.Text(f"${saldo_usado:,.2f}", weight="w500", color="#F44336")),
                        ]
                    )
                )
        
        return self.create_data_table(
            "Tarjetas de Crédito",
            [
                ft.DataColumn(ft.Text("Tarjeta", weight="bold")),
                ft.DataColumn(ft.Text("Límite Disponible", weight="bold")),
                ft.DataColumn(ft.Text("Saldo Utilizado", weight="bold")),
            ],
            rows,
            icon="credit_card"
        )

    def create_prestamos_table(self) -> ft.Container:
        """
        Crea la tabla de préstamos usando datos reales del usuario.
        """
        productos_prestamos = self.resumen_productos.get('prestamos', {}).get('productos', [])
        
        if not productos_prestamos:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay préstamos registrados", style=ft.TextStyle(italic=True, color="#666666"))),
                        ft.DataCell(ft.Text("--", color="#666666")),
                        ft.DataCell(ft.Text("--", color="#666666")),
                    ]
                )
            ]
        else:
            rows = []
            for producto in productos_prestamos:
                # Para préstamos, calcular cuota estimada (esto podría venir de otra tabla)
                cuota_estimada = abs(producto.get('saldo_actual', 0)) * 0.05  # Estimación del 5%
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(producto.get('nombre', 'Préstamo sin nombre'))),
                            ft.DataCell(ft.Text(f"${abs(producto.get('saldo_actual', 0)):,.2f}", weight="w500", color="#F44336")),
                            ft.DataCell(ft.Text(f"${cuota_estimada:,.2f}", weight="w500")),
                        ]
                    )
                )
        
        return self.create_data_table(
            "Préstamos",
            [
                ft.DataColumn(ft.Text("Préstamo", weight="bold")),
                ft.DataColumn(ft.Text("Saldo Pendiente", weight="bold")),
                ft.DataColumn(ft.Text("Cuota Estimada", weight="bold")),
            ],
            rows,
            icon="trending_down"
        )

    def create_fondos_inversion_table(self) -> ft.Container:
        """
        Crea la tabla de fondos de inversión usando datos reales del usuario.
        """
        productos_fondos = self.resumen_productos.get('fondos_inversion', {}).get('productos', [])
        
        if not productos_fondos:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay fondos de inversión registrados", style=ft.TextStyle(italic=True, color="#666666"))),
                        ft.DataCell(ft.Text("--", color="#666666")),
                        ft.DataCell(ft.Text("--", color="#666666")),
                    ]
                )
            ]
        else:
            rows = []
            for producto in productos_fondos:
                # Calcular rendimiento estimado basado en tasa de interés
                tasa = producto.get('tasa_interes', 0)
                saldo = producto.get('saldo_actual', 0)
                rendimiento = saldo * (tasa / 100) / 12  # Rendimiento mensual estimado
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(producto.get('nombre', 'Fondo sin nombre'))),
                            ft.DataCell(ft.Text(f"${saldo:,.2f}", weight="w500")),
                            ft.DataCell(ft.Text(f"+${rendimiento:,.2f}", color="#4CAF50", weight="bold")),
                        ]
                    )
                )
        
        return self.create_data_table(
            "Fondos de Inversión",
            [
                ft.DataColumn(ft.Text("Fondo", weight="bold")),
                ft.DataColumn(ft.Text("Valor Actual", weight="bold")),
                ft.DataColumn(ft.Text("Rendimiento Est.", weight="bold")),
            ],
            rows,
            icon="trending_up"
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
                                    # Tabla de Cuentas Bancarias - Datos reales
                                    self.create_cuentas_bancarias_table(),

                                    # Tabla de Tarjetas de Crédito - Datos reales
                                    self.create_tarjetas_credito_table(),

                                    # Tabla de Préstamos - Datos reales
                                    self.create_prestamos_table(),

                                    # Tabla de Fondos de Inversión - Datos reales
                                    self.create_fondos_inversion_table(),

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

def resumen_view(page: ft.Page, user_id: int = 1) -> ft.View:
    """
    Función principal que retorna la vista de resumen financiero.

    Args:
        page (ft.Page): La página principal proporcionada por Flet
        user_id (int): ID del usuario para obtener sus productos

    Returns:
        ft.View: Vista del resumen financiero con componentes reutilizables
    """
    # Crear la vista con el ID del usuario
    resumen = ResumenView(page, user_id)

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
