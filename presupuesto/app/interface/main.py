import flet as ft

# Creamos un contenedor principal con un fondo degradado y bordes redondeados.
container = ft.Container(
    content=ft.Column(
        [
            # Título del formulario de inicio de sesión
            ft.Container(
                ft.Text(
                    "Presupuesto\ninicio de sesion",
                    width=320,
                    size=30,
                    color=ft.Colors.WHITE,
                    text_align="center",
                    weight="w900"
                ),
                padding=ft.padding.only(20, 20)
            ),
            # Campo de texto para el usuario
            ft.Container(
                ft.TextField(
                    label="Usuario",
                    width=280,
                    height=40,
                    border="underline",
                    color="white",
                    prefix_icon=ft.Icons.PERSON,
                    hint_text="Usuario"
                ),
                padding=ft.padding.only(20, 10)
            ),
            # Campo de texto para la contraseña
            ft.Container(
                ft.TextField(
                    label="Contraseña",
                    width=280,
                    height=40,
                    border="underline",
                    color="white",
                    prefix_icon=ft.Icons.LOCK,
                    hint_text="Contraseña",
                    password=True,  # Oculta el texto
                    can_reveal_password=True  # Permite mostrar/ocultar la contraseña
                ),
                padding=ft.padding.only(20, 10)
            ),
            # Checkbox para recordar al usuario
            ft.Container(
                ft.Checkbox(
                    label="Recordarme",
                    check_color="white"
                ),
                padding=ft.padding.only(20, 10)
            ),
            # Botón para iniciar sesión
            ft.Container(
                ft.ElevatedButton(
                    text="Iniciar Sesión",
                    width=280,
                    height=40,
                    bgcolor=ft.Colors.GREEN
                ),
                padding=ft.padding.only(20, 10)
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,  # Espaciado uniforme entre los elementos
    ),
    border_radius=20,
    width=320,
    height=500,
    gradient=ft.LinearGradient(
        [
            ft.Colors.GREEN,
            ft.Colors.BLACK,
        ]
    ),
)

def main(page: ft.Page):
    """
    Función principal que configura la página de la aplicación Flet.
    Cambia el color de fondo y centra el contenedor en la pantalla.
    """
    page.bgcolor = ft.Colors.RED
    page.vertical_alignment = "CENTER"
    page.horizontal_alignment = "CENTER"
    page.add(container)

# Ejecuta la aplicación Flet usando la función main como punto de entrada.
ft.app(target=main)