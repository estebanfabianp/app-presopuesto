import sys
import os

# Fix import path
try:
    from ..controllers.persona_controller import autenticar_usuario
except ImportError:
    # Fallback if relative import fails
    try:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from controllers.persona_controller import autenticar_usuario
    except ImportError:
        print("Warning: No se pudo importar autenticar_usuario 1")
        # Mock fallback function
        def autenticar_usuario(username, password):
            if username and password:
                return {"name": username}, f"Usuario {username} autenticado correctamente"
            return None, "Error: Usuario y contraseña son requeridos"


import flet as ft 

def user_app(page: ft.Page):
    # Configuración de la página
    page.title = "Login de Usuario"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 500
    page.window_resizable = False

    # Remove incorrect controller instantiation
    # controller = autenticar_usuario()  # This line was wrong

    # Campos de entrada con mejor alineación
    name_input = ft.TextField(
        label="Nombre de Usuario",
        width=300,
        border_radius=8,
        prefix_icon=ft.Icon(ft.Icons.PERSON)
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        width=300,
        border_radius=8,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icon(ft.Icons.LOCK)
    )
    
    result_text = ft.Text(
        value="",
        color="green",
        text_align=ft.TextAlign.CENTER,
        size=14
    )

    # Función de manejo de login
    def on_login_click(e):
        # Call autenticar_usuario directly with parameters
        user, msg = autenticar_usuario(name_input.value, password_input.value)
        if user:
            result_text.value = f"¡Bienvenido {user['name']}!"
            result_text.color = "green"
        else:
            result_text.value = msg
            result_text.color = "red"
        page.update()

    # Botón de login estilizado
    login_button = ft.ElevatedButton(
        "Iniciar Sesión",
        on_click=on_login_click,
        width=300,
        height=45,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
    )

    # Contenedor principal centrado y estilizado
    main_container = ft.Container(
        content=ft.Column(
            controls=[
                # Icono principal
                ft.Icon(
                    ft.Icons.LOGIN,
                    size=60,
                    color=ft.Colors.BLUE
                ),
                # Título
                ft.Text(
                    "Inicio de Sesión",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                # Espaciado
                ft.Container(height=20),
                # Campo usuario
                name_input,
                # Espaciado pequeño
                ft.Container(height=10),
                # Campo contraseña
                password_input,
                # Espaciado
                ft.Container(height=20),
                # Botón login
                login_button,
                # Espaciado pequeño
                ft.Container(height=10),
                # Texto resultado
                result_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            tight=True
        ),
        padding=ft.Padding(30, 30, 30, 30),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        width=350,
        height=450
    )

    # Agregar a la página con centrado perfecto
    page.add(
        ft.Container(
            content=main_container,
            alignment=ft.alignment.center,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=user_app)