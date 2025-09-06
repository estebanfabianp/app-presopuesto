import flet as ft

container = ft.Container(
    content=ft.Column(
        [
            ft.Text("Hola Mundo", size=30, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY
    ),
    border_radius=20,
    width=320,
    height=500,
    gradient=ft.LinearGradient(
        [
            ft.Colors.GREEN,
            ft.Colors.BLACK
        ]
    )
)

def main(page: ft.Page):
    page.bgcolor = ft.Colors.RED
    page.vertical_alignment = "CENTER"
    page.horizontal_alignment = "CENTER"
    page.add(container)

ft.app(target=main)