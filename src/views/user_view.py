import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import flet as ft
from controllers.user_controller import UserController

def user_app(page: ft.Page):
    page.title = "Ejemplo MVC con Flet y MySQL"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    controller = UserController()

    name_input = ft.TextField(label="Nombre", width=300)
    email_input = ft.TextField(label="Correo", width=300)
    result_text = ft.Text(value="", color="green")

    def on_save_click(e):
        user, msg = controller.save_user(name_input.value, email_input.value)
        if user:
            result_text.value = f"{msg}: {user['name']} ({user['email']})"
            result_text.color = "green"
        else:
            result_text.value = msg
            result_text.color = "red"
        page.update()

    save_button = ft.ElevatedButton("Guardar usuario", on_click=on_save_click)

    page.add(
        ft.Column(
            [
                ft.Text("Registro de Usuario", size=20, weight="bold"),
                name_input,
                email_input,
                save_button,
                result_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=user_app)
