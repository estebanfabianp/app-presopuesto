# main.py
import flet as ft
from resumen import resumen_view
from login import login_view

def main(page: ft.Page):
    page.title = "App con navegación entre vistas"

    def route_change(route):
        page.views.clear()

        if page.route == "/login":
            page.views.append(login_view(page))
        elif page.route == "/resumen":
            page.views.append(resumen_view(page))

        page.update()

    page.on_route_change = route_change
    page.go("/login")  # Comienza en login

ft.app(target=main)
ft.app(target=main)
