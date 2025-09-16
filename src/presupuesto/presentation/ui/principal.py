import flet as ft


def transacciones_table(transacciones):
    """
    Devuelve un DataTable con los detalles de las transacciones.
    """
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Categoría")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(tx["fecha"])),
                    ft.DataCell(ft.Text(tx["descripcion"])),
                    ft.DataCell(ft.Text(f"${tx['monto']:.2f}")),
                    ft.DataCell(ft.Text(tx["categoria"])),
                ]
            )
            for tx in transacciones
        ]
    )


def main(page: ft.Page):
    # Ejemplo de transacciones
    transacciones = [
        {"fecha": "2024-06-10", "descripcion": "Supermercado", "monto": 150.75, "categoria": "Alimentación"},
        {"fecha": "2024-06-11", "descripcion": "Gasolina", "monto": 60.00, "categoria": "Transporte"},
        {"fecha": "2024-06-12", "descripcion": "Internet", "monto": 45.00, "categoria": "Servicios"},
    ]

    # Otra grilla de ejemplo
    transacciones_recientes = [
        {"fecha": "2024-06-13", "descripcion": "Farmacia", "monto": 30.00, "categoria": "Salud"},
        {"fecha": "2024-06-14", "descripcion": "Restaurante", "monto": 80.00, "categoria": "Ocio"},
    ]

    # Helper para mostrar texto en el snack_bar
    def open_and_show_text(text):
        page.snack_bar = ft.SnackBar(ft.Text(f"Opción seleccionada: {text}"))
        page.snack_bar.open = True
        page.update()
    # Asignar helper a la página para uso en los botones
    page.open_and_show_text = open_and_show_text

    page.appbar = ft.AppBar(
        title=ft.Text("Menú Principal"),
        bgcolor=ft.Colors.BLUE,
        actions=[
            ft.IconButton(ft.Icons.HOME, tooltip="Inicio", on_click=lambda e: page.open_and_show_text("Inicio")),
            ft.IconButton(ft.Icons.LIST, tooltip="Transacciones", on_click=lambda e: page.open_and_show_text("Transacciones")),
            ft.IconButton(ft.Icons.PIE_CHART, tooltip="Reportes", on_click=lambda e: page.open_and_show_text("Reportes")),
            ft.IconButton(ft.Icons.ACCOUNT_BALANCE_WALLET, tooltip="Cuentas", on_click=lambda e: page.open_and_show_text("Cuentas")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Configuración", on_click=lambda e: page.open_and_show_text("Configuración")),
        ]
    )

    page.add(
        ft.Column(
            [
                ft.Text("Detalles de Transacciones", size=20, weight="bold", color=ft.Colors.RED),
                transacciones_table(transacciones),
                ft.Text("Transacciones Recientes", size=18, weight="bold", color=ft.Colors.BLUE),
                transacciones_table(transacciones_recientes)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=30
        )
    )


ft.app(target=main)



