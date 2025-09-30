import flet as ft
import datetime
import random

class LeftSidebarMenu:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_index = 0
        
    def create_menu_item(self, icon, title, index, badge_count=None):
        """Crear un elemento del menú lateral"""
        
        def on_click(e):
            self.selected_index = index
            self.update_menu_selection()
            self.navigate_to_section(title)
        
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
                bgcolor="#F44336",
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                margin=ft.margin.only(left=5)
            )
        
        # Contenedor del ícono con badge
        icon_container = ft.Row([
            ft.Icon(icon, size=20),
            badge if badge else ft.Container()
        ], tight=True) if badge else ft.Icon(icon, size=20)
        
        return ft.Container(
            content=ft.ListTile(
                leading=icon_container,
                title=ft.Text(
                    title, 
                    size=14,
                    weight="w500"
                ),
                selected=index == self.selected_index,
                on_click=on_click,
            ),
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=8, vertical=2),
        )
    
    def create_section_divider(self, title):
        """Crear divisor de sección"""
        return ft.Container(
            content=ft.Text(
                title.upper(), 
                size=11, 
                color="#666666",
                weight=ft.FontWeight.BOLD
            ),
            margin=ft.margin.only(left=16, top=16, bottom=8)
        )
    
    def update_menu_selection(self):
        """Actualizar la selección visual del menú"""
        # Aquí puedes agregar lógica para actualizar el estado visual
        self.page.update()
    
    def navigate_to_section(self, section):
        """Navegar a la sección seleccionada"""
        print(f"Navegando a: {section}")
        # Aquí implementarías la lógica de navegación real
        
    def create_user_profile(self):
        """Crear el perfil de usuario en la parte superior"""
        return ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.CircleAvatar(
                        content=ft.Text("JD", color="white"),
                        bgcolor="#2196F3",
                        radius=20
                    ),
                    title=ft.Text(
                        "John Doe", 
                        size=16, 
                        weight="bold"
                    ),
                    subtitle=ft.Text(
                        "john.doe@email.com", 
                        size=12, 
                        color="#666666"
                    ),
                ),
                ft.Divider(height=1, color="#E0E0E0")
            ], spacing=0),
            margin=ft.margin.only(bottom=10)
        )
    
    def create_sidebar(self):
        """Crear el menú lateral completo"""
        return ft.Container(
            width=280,
            bgcolor="#F5F5F5",
            content=ft.Column([
                # Header con perfil de usuario
                self.create_user_profile(),
                
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
                
                # Spacer para empujar el logout hacia abajo
                ft.Container(expand=True),
                
                # Logout en la parte inferior
                ft.Divider(height=1, color="#E0E0E0"),
                self.create_menu_item("logout", "Cerrar Sesión", 17),
                
            ], 
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
            ),
            border=ft.border.only(right=ft.BorderSide(1, "#E0E0E0"))
        )

class ResumenView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sidebar_menu = LeftSidebarMenu(page)
        
    def create_main_content(self):
        """Crear el contenido principal"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Resumen Financiero", 
                    size=24, 
                    weight="bold"
                ),
                ft.Text(
                    "Bienvenido a tu panel de control financiero",
                    size=16,
                    color="#666666"
                ),
                # Aquí agregar más contenido principal
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Cuentas Bancarias", size=14, weight="bold"),
                            ft.Text("Total: $12,500.00", size=18, weight="bold", color="#2196F3"),
                        ], alignment="center"),
                        bgcolor="#E3F2FD",
                        border_radius=8,
                        padding=16,
                        expand=True,
                        margin=ft.margin.only(right=8)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Préstamos", size=14, weight="bold"),
                            ft.Text("Total: $5,200.00", size=18, weight="bold", color="#F44336"),
                        ], alignment="center"),
                        bgcolor="#FFEBEE",
                        border_radius=8,
                        padding=16,
                        expand=True,
                        margin=ft.margin.only(right=8)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Tarjetas de Crédito", size=14, weight="bold"),
                            ft.Text("Total: $2,800.00", size=18, weight="bold", color="#FF9800"),
                        ], alignment="center"),
                        bgcolor="#FFF3E0",
                        border_radius=8,
                        padding=16,
                        expand=True,
                        margin=ft.margin.only(right=8)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Fondos", size=14, weight="bold"),
                            ft.Text("Total: $8,000.00", size=18, weight="bold", color="#4CAF50"),
                        ], alignment="center"),
                        bgcolor="#E8F5E9",
                        border_radius=8,
                        padding=16,
                        expand=True
                    ),
                ], spacing=0, expand=False, alignment="center"),
               
                # Sección de resumen con tarjetas
                ft.Container(
                    content=ft.Text(
                        "Detalle por Tipo de Cuenta", 
                        size=20, 
                        weight="bold"
                    ),
                    margin=ft.margin.only(top=32, bottom=16)
                ),
                
                # Tabla de Cuentas Bancarias
                ft.Container(
                    content=ft.Text("Cuentas Bancarias", size=16, weight="bold"),
                    margin=ft.margin.only(bottom=8)
                ),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Cuenta Bancaria")),
                            ft.DataColumn(ft.Text("Saldo")),
                            ft.DataColumn(ft.Text("Saldo Conciliado")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Banco Nacional - Cuenta Corriente")),
                                    ft.DataCell(ft.Text("$7,500.00")),
                                    ft.DataCell(ft.Text("$7,200.00")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Banco Popular - Caja de Ahorro")),
                                    ft.DataCell(ft.Text("$5,000.00")),
                                    ft.DataCell(ft.Text("$4,950.00")),
                                ]
                            ),
                        ],
                    ),
                    margin=ft.margin.only(bottom=24),
                    bgcolor="#FAFAFA",
                    border_radius=8,
                    padding=16,
                ),
                
                # Tabla de Tarjetas de Crédito
                ft.Container(
                    content=ft.Text("Tarjetas de Crédito", size=16, weight="bold"),
                    margin=ft.margin.only(bottom=8)
                ),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Tarjeta")),
                            ft.DataColumn(ft.Text("Límite Disponible")),
                            ft.DataColumn(ft.Text("Saldo Utilizado")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Tarjeta de Crédito - Visa")),
                                    ft.DataCell(ft.Text("$2,499.00")),
                                    ft.DataCell(ft.Text("$1,501.00")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Tarjeta de Crédito - Mastercard")),
                                    ft.DataCell(ft.Text("$990.00")),
                                    ft.DataCell(ft.Text("$1,310.00")),
                                ]
                            ),
                        ],
                    ),
                    margin=ft.margin.only(bottom=24),
                    bgcolor="#FAFAFA",
                    border_radius=8,
                    padding=16,
                ),
                
                # Tabla de Fondos de Inversión
                ft.Container(
                    content=ft.Text("Fondos de Inversión", size=16, weight="bold"),
                    margin=ft.margin.only(bottom=8)
                ),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Fondo")),
                            ft.DataColumn(ft.Text("Valor Actual")),
                            ft.DataColumn(ft.Text("Rendimiento")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Fondo de Inversión - Renta Variable")),
                                    ft.DataCell(ft.Text("$5,000.00")),
                                    ft.DataCell(ft.Text("+$200.00", color="#4CAF50")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Fondo de Inversión - Renta Fija")),
                                    ft.DataCell(ft.Text("$3,000.00")),
                                    ft.DataCell(ft.Text("+$70.00", color="#4CAF50")),
                                ]
                            ),
                        ],
                    ),
                    margin=ft.margin.only(bottom=24),
                    bgcolor="#FAFAFA",
                    border_radius=8,
                    padding=16,
                ),
                
                # Tabla de Préstamos
                ft.Container(
                    content=ft.Text("Préstamos", size=16, weight="bold"),
                    margin=ft.margin.only(bottom=8)
                ),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Préstamo")),
                            ft.DataColumn(ft.Text("Saldo Pendiente")),
                            ft.DataColumn(ft.Text("Cuota Mensual")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Préstamo Personal - Banco Nacional")),
                                    ft.DataCell(ft.Text("$3,200.00")),
                                    ft.DataCell(ft.Text("$150.00")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Préstamo Auto - Banco Popular")),
                                    ft.DataCell(ft.Text("$2,000.00")),
                                    ft.DataCell(ft.Text("$120.00")),
                                ]
                            ),
                        ],
                    ),
                    margin=ft.margin.only(bottom=24),
                    bgcolor="#FAFAFA",
                    border_radius=8,
                    padding=16,
                ),
            ], 
            scroll=ft.ScrollMode.AUTO,
            spacing=0
            ),
            expand=True,
            padding=20
        )
    def create_income_vs_expense_chart(self):
        """Crear un gráfico de ejemplo de ingresos vs gastos de los últimos 30 días"""
        try:
            import flet.plotly_chart as fpc
            import plotly.graph_objs as go
        except ImportError:
            return ft.Container(
                content=ft.Text(
                    "Instala plotly y flet-plotly-chart para ver el gráfico.",
                    color="#F44336"
                ),
                padding=20,
                bgcolor="#FFF3E0",
                border_radius=8,
                margin=ft.margin.only(left=16, top=20)
            )

        # Datos de ejemplo
        today = datetime.date.today()
        days = [(today - datetime.timedelta(days=i)).strftime("%d/%m") for i in range(29, -1, -1)]
        ingresos = [random.randint(100, 300) for _ in range(30)]
        gastos = [random.randint(80, 320) for _ in range(30)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=ingresos, mode='lines+markers', name='Ingresos', line=dict(color='#4CAF50')))
        fig.add_trace(go.Scatter(x=days, y=gastos, mode='lines+markers', name='Gastos', line=dict(color='#F44336')))
        fig.update_layout(
            title="Ingresos vs Gastos (últimos 30 días)",
            xaxis_title="Fecha",
            yaxis_title="Monto ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            height=350,
            plot_bgcolor="#FAFAFA"
        )

        return ft.Container(
            content=fpc.PlotlyChart(fig, expand=True),
            bgcolor="#FFFFFF",
            border_radius=8,
            padding=16,
            margin=ft.margin.only(left=16, top=20),
            expand=True,
            height=400
        )
    def build(self):
        """Construir la vista completa"""
        return ft.Row([
            # Sidebar izquierdo
            self.sidebar_menu.create_sidebar(),
            # Contenido principal
            ft.Container(
                content=self.create_main_content(),
                expand=True
            )
        ], expand=True)

def main(page: ft.Page):
    page.title = "App Presupuesto - Resumen"
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    
    # Configurar tema
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Crear y mostrar la vista
    resumen_view = ResumenView(page)
    page.add(resumen_view.build())

if __name__ == "__main__":
    ft.app(target=main)

