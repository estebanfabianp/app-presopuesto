"""Vista de configuracion modular para la app financiera."""

import flet as ft

try:
    from ..database.db_connector import DatabaseConnector
except ImportError:
    from database.db_connector import DatabaseConnector

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    from sidebar import create_sidebar_menu


class ConfigurationView(ft.View):
    """Componente reutilizable de configuracion con validacion basica."""

    def __init__(self, page: ft.Page) -> None:
        super().__init__(route="/configuracion", padding=0, spacing=0)
        self.page = page
        user_data = self._load_active_user_data()

        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=16,
            user_data=user_data,
            navigation_callback=self.handle_navigation,
        )

        self.current_password = ft.TextField(
            label="Contraseña actual",
            password=True,
            can_reveal_password=False,
            expand=True,
            border_radius=10,
        )
        self.new_password = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=False,
            expand=True,
            border_radius=10,
            helper_text="Mínimo 8 caracteres",
        )
        self.confirm_password = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=False,
            expand=True,
            border_radius=10,
        )

        self.feedback_text = ft.Text(value="", size=12)
        self.notifications_switch = ft.Switch(label="Notificaciones", value=True)
        self.language_dropdown = ft.Dropdown(
            label="Idioma",
            value="es",
            width=260,
            options=[
                ft.dropdown.Option("es", "Español"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("pt", "Português"),
            ],
        )

        self.controls = [self._build_layout()]

    def _load_active_user_data(self) -> dict:
        """Obtiene datos del usuario activo para mostrar en el sidebar."""
        default_data = {
            "name": "Usuario",
            "email": "usuario@demo.com",
            "avatar_initials": "U",
            "avatar_color": "#2196F3",
        }

        db = DatabaseConnector()
        if not db.conn:
            return default_data

        try:
            rows = db.execute_query(
                """
                SELECT nombre, correo_electronico
                FROM persona
                WHERE estado = 1
                ORDER BY COALESCE(fecha_actualizacion, fecha_creacion) DESC, id_persona DESC
                LIMIT 1
                """
            )
            if not rows:
                return default_data

            name = (rows[0].get("nombre") or "Usuario").strip()
            email = (rows[0].get("correo_electronico") or "usuario@demo.com").strip()

            words = [w for w in name.split() if w]
            initials = "".join(w[0].upper() for w in words[:2]) or "U"

            return {
                "name": name,
                "email": email,
                "avatar_initials": initials,
                "avatar_color": "#2196F3",
            }
        finally:
            db.close()

    def _is_password_change_requested(self) -> bool:
        return any([
            bool(self.current_password.value),
            bool(self.new_password.value),
            bool(self.confirm_password.value),
        ])

    def _save_settings(self, e: ft.ControlEvent) -> None:
        """Guarda cambios de configuracion con validacion basica."""
        if self._is_password_change_requested():
            nueva = self.new_password.value or ""
            confirmacion = self.confirm_password.value or ""

            if len(nueva) < 8:
                self.feedback_text.value = "No se guardó: la nueva contraseña debe tener al menos 8 caracteres."
                self.feedback_text.color = ft.Colors.RED_600
                self.page.update()
                return

            if nueva != confirmacion:
                self.feedback_text.value = "No se guardó: la confirmación no coincide."
                self.feedback_text.color = ft.Colors.RED_600
                self.page.update()
                return

        idioma = self.language_dropdown.value or "es"
        notificaciones = "activadas" if self.notifications_switch.value else "desactivadas"

        # Placeholder de persistencia.
        # Aquí se puede conectar a DB/API para guardar preferencias reales.
        self.feedback_text.value = (
            f"Cambios guardados correctamente. Idioma: {idioma}. Notificaciones: {notificaciones}."
        )
        self.feedback_text.color = ft.Colors.GREEN_700
        self.page.update()

    def handle_navigation(self, route: str, index: int) -> None:
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)

    def _toggle_password_visibility(self, field: ft.TextField, icon_button: ft.IconButton) -> None:
        field.password = not field.password
        icon_button.icon = ft.Icons.VISIBILITY_OFF if not field.password else ft.Icons.VISIBILITY
        self.page.update()

    def _password_row(self, field: ft.TextField) -> ft.Row:
        toggle = ft.IconButton(icon=ft.Icons.VISIBILITY, tooltip="Mostrar/Ocultar contraseña")
        toggle.on_click = lambda e: self._toggle_password_visibility(field, toggle)
        return ft.Row([field, toggle], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _validate_password_change(self, e: ft.ControlEvent) -> None:
        nueva = self.new_password.value or ""
        confirmacion = self.confirm_password.value or ""

        if len(nueva) < 8:
            self.feedback_text.value = "La nueva contraseña debe tener al menos 8 caracteres."
            self.feedback_text.color = ft.Colors.RED_600
            self.page.update()
            return

        if nueva != confirmacion:
            self.feedback_text.value = "La confirmación no coincide con la nueva contraseña."
            self.feedback_text.color = ft.Colors.RED_600
            self.page.update()
            return

        self.feedback_text.value = "Contraseña validada correctamente. Puedes guardar cambios."
        self.feedback_text.color = ft.Colors.GREEN_700
        self.page.update()

    def _build_password_card(self) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.BLUE_600),
                            ft.Text("Cambio de contraseña", size=18, weight=ft.FontWeight.BOLD),
                        ]),
                        self._password_row(self.current_password),
                        self._password_row(self.new_password),
                        self._password_row(self.confirm_password),
                        ft.ElevatedButton(
                            "Validar contraseña",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            on_click=self._validate_password_change,
                        ),
                        self.feedback_text,
                    ],
                    spacing=12,
                ),
            )
        )

    def _build_preferences_card(self) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.TUNE, color=ft.Colors.BLUE_600),
                            ft.Text("Preferencias", size=18, weight=ft.FontWeight.BOLD),
                        ]),
                        self.notifications_switch,
                        self.language_dropdown,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Guardar cambios",
                                    icon=ft.Icons.SAVE,
                                    bgcolor=ft.Colors.BLUE_600,
                                    color=ft.Colors.WHITE,
                                    on_click=self._save_settings,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=12,
                ),
            )
        )

    def _build_session_card(self) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_600),
                            ft.Text("Sesión", size=18, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.ElevatedButton(
                            "Cerrar Sesión",
                            icon=ft.Icons.LOGOUT,
                            bgcolor=ft.Colors.RED_600,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: self.page.go("/login"),
                        ),
                    ],
                    spacing=12,
                ),
            )
        )

    def _build_layout(self) -> ft.Control:
        main_content = ft.Container(
            expand=True,
            bgcolor="#F8F9FA",
            padding=24,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Configuración", size=30, weight=ft.FontWeight.BOLD),
                                ft.Text("Gestiona seguridad, preferencias y sesión de tu cuenta."),
                            ],
                            spacing=4,
                        )
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        content=ft.Column(
                            [
                                self._build_password_card(),
                                self._build_preferences_card(),
                                self._build_session_card(),
                            ],
                            width=760,
                            spacing=14,
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
                spacing=14,
            ),
        )

        return ft.Container(
            expand=True,
            content=ft.Row(
                [
                    self.sidebar_menu.create_sidebar(),
                    main_content,
                ],
                expand=True,
                spacing=0,
            ),
        )

def configuracion_view(page: ft.Page) -> ft.View:
    return ConfigurationView(page)

def main(page: ft.Page) -> None:
    """
    Función principal para ejecutar la aplicación de forma independiente.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
    """
    # Configuración de la ventana
    page.title = "App Presupuesto - Configuración"
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
    page.add(configuracion_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)


