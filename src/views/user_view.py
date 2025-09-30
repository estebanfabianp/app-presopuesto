import sys
import os

# Configurar el path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(src_dir)

# Añadir directorios al path si no están
for path in [src_dir, project_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

import flet as ft

# Mock temporal del UserController hasta resolver las importaciones
class UserController:
    def save_user(self, name, email):
        # Mock implementation para testing
        if name and email:
            user = {"name": name, "email": email}
            return user, "Usuario guardado exitosamente"
        else:
            return None, "Error: Nombre y email son requeridos"

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
