"""
Componente de Menú Lateral Reutilizable

Este módulo contiene la implementación del menú lateral de navegación que puede
ser utilizado en múltiples vistas de la aplicación. Proporciona navegación
consistente y funcionalidades de usuario.

Clases:
    LeftSidebarMenu: Menú lateral principal con navegación y perfil de usuario

Características:
    - Perfil de usuario con avatar y información
    - Navegación por secciones organizada
    - Badges de notificación configurables
    - Estado de selección visual
    - Callbacks personalizables para navegación
    - Totalmente reutilizable entre vistas

Autor: [esteban patiño]
Fecha: [30-sep-2025]
Versión: 1.0
"""

import flet as ft
from typing import Optional, Callable, Dict, Any


def load_active_user_data() -> Dict[str, Any]:
    """
    Carga datos del usuario activo desde base de datos.

    Returns:
        Dict[str, Any]: Datos del usuario para el sidebar
    """
    default_data = {
        "name": "Usuario",
        "email": "usuario@email.com",
        "avatar_initials": "US",
        "avatar_color": "#2196F3"
    }

    try:
        # Import local para evitar dependencias fuertes al importar el modulo.
        from src.database.db_connector import DatabaseConnector

        db = DatabaseConnector()
        conn = db.conn
        if not conn:
            return default_data

        cursor = conn.cursor(dictionary=True)

        # Obtener usuario con estado activo (1 o 'activo')
        try:
            cursor.execute(
                """
                SELECT id_persona, nombre, apellido, correo_electronico
                FROM persona
                WHERE estado = 1 OR estado = 'activo'
                ORDER BY id_persona DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
        except Exception:
            row = None

        # Si no hay usuario activo, obtener cualquiera
        if not row:
            try:
                cursor.execute(
                    """
                    SELECT id_persona, nombre, apellido, correo_electronico
                    FROM persona
                    ORDER BY id_persona DESC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
            except Exception:
                row = None

        cursor.close()
        conn.close()

        if not row:
            return default_data

        nombre = (row.get("nombre") or "").strip()
        apellido = (row.get("apellido") or "").strip()
        correo = (row.get("correo_electronico") or "usuario@email.com").strip()
        
        # Si el correo es muy corto o malformado, usar default
        if len(correo) < 3 or "@" not in correo:
            correo = "usuario@email.com"
        
        full_name = f"{nombre} {apellido}".strip() or "Usuario"
        initials = "".join([part[0] for part in full_name.split()[:2] if part]).upper() or "US"

        return {
            "name": full_name,
            "email": correo,
            "avatar_initials": initials,
            "avatar_color": "#1976D2"
        }
    except Exception:
        return default_data


class LeftSidebarMenu:
    """
    Componente de menú lateral reutilizable para navegación de la aplicación.
    
    Este componente proporciona un menú lateral completo que incluye:
    - Perfil de usuario con avatar e información
    - Navegación organizada por secciones
    - Badges de notificación
    - Estado visual de selección
    - Callbacks personalizables para manejo de navegación
    
    Attributes:
        page (ft.Page): Referencia a la página principal de Flet
        selected_index (int): Índice del elemento de menú actualmente seleccionado
        user_data (Dict[str, Any]): Información del usuario para mostrar en el perfil
        navigation_callback (Optional[Callable]): Función callback para manejo de navegación
    """
    
    def __init__(
        self, 
        page: ft.Page, 
        selected_index: int = 1,
        user_data: Optional[Dict[str, Any]] = None,
        navigation_callback: Optional[Callable[[str, int], None]] = None
    ) -> None:
        """
        Inicializa el componente de menú lateral.
        
        Args:
            page (ft.Page): La página principal de la aplicación Flet
            selected_index (int): Índice inicial del elemento seleccionado (default: 1)
            user_data (Optional[Dict[str, Any]]): Datos del usuario para mostrar en el perfil
            navigation_callback (Optional[Callable]): Función para manejar navegación personalizada
        """
        self.page = page
        self.selected_index = selected_index
        self.navigation_callback = navigation_callback

        # Reemplaza placeholders por usuario activo real para todas las vistas.
        placeholder_names = {"John Doe", "Usuario Demo", "Usuario"}
        placeholder_emails = {"john.doe@email.com", "usuario@demo.com", "usuario@email.com"}
        should_load_real_user = (
            not user_data
            or user_data.get("name") in placeholder_names
            or user_data.get("email") in placeholder_emails
        )

        self.user_data = load_active_user_data() if should_load_real_user else user_data
        
        # Configuración del menú con badges dinámicos
        self.menu_items = [
            # Sección Principal
            {"type": "section", "title": "PRINCIPAL"},
            {"type": "item", "icon": "dashboard", "title": "Dashboard", "index": 0, "route": "/dashboard"},
            {"type": "item", "icon": "account_balance_wallet", "title": "Resumen Financiero", "index": 1, "route": "/resumen"},
            
            # Sección Transacciones
            {"type": "section", "title": "TRANSACCIONES"},
            {"type": "item", "icon": "add_circle_outline", "title": "Nueva Transacción", "index": 2, "route": "/transacciones/nueva"},
            {"type": "item", "icon": "list_alt", "title": "Historial", "index": 3, "route": "/transacciones/historial", "badge": 5},
            {"type": "item", "icon": "swap_horiz", "title": "Transferencias", "index": 4, "route": "/transferencias"},
            
            # Sección Presupuestos
            {"type": "section", "title": "PRESUPUESTOS"},
            {"type": "item", "icon": "pie_chart", "title": "Presupuestos", "index": 5, "route": "/presupuestos"},
            {"type": "item", "icon": "trending_up", "title": "Metas de Ahorro", "index": 6, "route": "/metas"},
            {"type": "item", "icon": "category", "title": "Categorías", "index": 7, "route": "/categorias"},
            {"type": "item", "icon": "auto_fix_high", "title": "Optimización de Categorías", "index": 18, "route": "/optimizacion-categorias"},
            
            # Sección Cuentas
            {"type": "section", "title": "CUENTAS"},
            {"type": "item", "icon": "account_balance", "title": "Cuentas Bancarias", "index": 8, "route": "/cuentas"},
            {"type": "item", "icon": "credit_card", "title": "Tarjetas de Crédito", "index": 9, "route": "/tarjetas", "badge": 2},
            {"type": "item", "icon": "savings", "title": "Inversiones", "index": 10, "route": "/inversiones"},
            
            # Sección Reportes
            {"type": "section", "title": "REPORTES"},
            {"type": "item", "icon": "analytics", "title": "Análisis", "index": 11, "route": "/analisis"},
            {"type": "item", "icon": "assessment", "title": "Reportes", "index": 12, "route": "/reportes"},
            {"type": "item", "icon": "file_download", "title": "Exportar Datos", "index": 13, "route": "/exportar"},
            
            # Sección Configuración
            {"type": "section", "title": "CONFIGURACIÓN"},
            {"type": "item", "icon": "person", "title": "Perfil", "index": 14, "route": "/perfil"},
            {"type": "item", "icon": "notifications", "title": "Notificaciones", "index": 15, "route": "/notificaciones", "badge": 3},
            {"type": "item", "icon": "settings", "title": "Configuración", "index": 16, "route": "/configuracion"},
            {"type": "item", "icon": "settings", "title": "Constantes", "index": 17, "route": "/constantes"},
        ]
    
    def update_selected_index(self, new_index: int) -> None:
        """
        Actualiza el índice del elemento seleccionado.
        
        Args:
            new_index (int): Nuevo índice a seleccionar
        """
        self.selected_index = new_index
        self.page.update()
    
    def update_user_data(self, user_data: Dict[str, Any]) -> None:
        """
        Actualiza los datos del usuario mostrados en el perfil.
        
        Args:
            user_data (Dict[str, Any]): Nuevos datos del usuario
        """
        self.user_data.update(user_data)
        self.page.update()
    
    def update_badge_count(self, menu_index: int, badge_count: Optional[int]) -> None:
        """
        Actualiza el contador de badge de un elemento específico del menú.
        
        Args:
            menu_index (int): Índice del elemento de menú
            badge_count (Optional[int]): Nuevo contador de badge (None para ocultar)
        """
        for item in self.menu_items:
            if item.get("type") == "item" and item.get("index") == menu_index:
                if badge_count is None or badge_count <= 0:
                    item.pop("badge", None)
                else:
                    item["badge"] = badge_count
                break
        self.page.update()
    
    def create_menu_item(self, item_config: Dict[str, Any]) -> ft.Container:
        """
        Crea un elemento individual del menú lateral basado en la configuración.
        
        Args:
            item_config (Dict[str, Any]): Configuración del elemento de menú
            
        Returns:
            ft.Container: Contenedor con el elemento de menú configurado
        """
        icon = item_config.get("icon")
        title = item_config.get("title")
        index = item_config.get("index")
        badge_count = item_config.get("badge")
        route = item_config.get("route", "")
        
        def on_click(e: ft.ControlEvent) -> None:
            """Maneja el evento de clic en un elemento del menú."""
            self.selected_index = index
            self.page.update()
            
            # Usar callback personalizado si está disponible
            if self.navigation_callback:
                self.navigation_callback(route, index)
            else:
                # Navegación por defecto
                self.default_navigation(title, route)
        
        is_selected = index == self.selected_index
        
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
        
        # Contenedor del ícono con badge opcional
        icon_container = ft.Row([
            ft.Icon(
                icon, 
                size=20, 
                color="#2196F3" if is_selected else "#666666"
            ),
            badge if badge else ft.Container()
        ], tight=True) if badge else ft.Icon(
            icon, 
            size=20, 
            color="#2196F3" if is_selected else "#666666"
        )
        
        return ft.Container(
            content=ft.ListTile(
                leading=icon_container,
                title=ft.Text(
                    title, 
                    size=14,
                    weight="w600" if is_selected else "w400",
                    color="#2196F3" if is_selected else "#333333"
                ),
                on_click=on_click,
            ),
            bgcolor="#E3F2FD" if is_selected else "transparent",
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=8, vertical=1),
            border=ft.border.all(1, "#2196F3") if is_selected else None,
        )
    
    def create_section_divider(self, title: str) -> ft.Container:
        """
        Crea un divisor de sección para agrupar elementos del menú.
        
        Args:
            title (str): Título de la sección
            
        Returns:
            ft.Container: Contenedor con el divisor de sección
        """
        return ft.Container(
            content=ft.Text(
                title.upper(), 
                size=11, 
                color="#666666",
                weight=ft.FontWeight.BOLD
            ),
            margin=ft.margin.only(left=16, top=16, bottom=8)
        )
    
    def default_navigation(self, section: str, route: str) -> None:
        """
        Navegación por defecto cuando no se proporciona callback personalizado.
        
        Args:
            section (str): Nombre de la sección
            route (str): Ruta de navegación
        """
        print(f"Navegando a: {section} ({route})")

        # Mapeo explicito por seccion para garantizar navegacion estable.
        section_to_route = {
            "Dashboard": "/dashboard",
            "Resumen Financiero": "/resumen",
            "Nueva Transacción": "/transacciones/nueva",
            "Historial": "/transacciones/historial",
            "Transferencias": "/transferencias",
            "Presupuestos": "/presupuestos",
            "Metas de Ahorro": "/metas",
            "Categorías": "/categorias",
            "Cuentas Bancarias": "/cuentas",
            "Tarjetas de Crédito": "/tarjetas",
            "Inversiones": "/inversiones",
            "Análisis": "/analisis",
            "Reportes": "/reportes",
            "Exportar Datos": "/exportar",
            "Perfil": "/perfil",
            "Notificaciones": "/notificaciones",
            "Configuración": "/configuracion",
            "Constantes": "/constantes",
            "Cerrar Sesión": "/login",
        }

        # Prioriza la ruta recibida en el item; si no existe, usa la ruta por sección.
        target_route = route or section_to_route.get(section, "")

        # Navegaciones especiales
        if target_route == "/login" or section == "Cerrar Sesión":
            self.page.go("/login")
        elif target_route == "/constantes" or section == "Constantes":
            self.page.go("/constantes")
        elif target_route == "/configuracion" or section == "Configuración":
            self.page.go("/configuracion")
        elif target_route:
            self.page.go(target_route)
    
    def create_user_profile(self) -> ft.Container:
        """
        Crea la sección del perfil de usuario en la parte superior del menú.
        
        Returns:
            ft.Container: Contenedor con el perfil de usuario completo
        """
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        # Avatar circular con iniciales
                        ft.CircleAvatar(
                            content=ft.Text(
                                self.user_data.get("avatar_initials", "UD"), 
                                color="white", 
                                size=16, 
                                weight="bold"
                            ),
                            bgcolor=self.user_data.get("avatar_color", "#2196F3"),
                            radius=24
                        ),
                        # Información del usuario
                        ft.Column([
                            ft.Text(
                                self.user_data.get("name", "Usuario"), 
                                size=16, 
                                weight="bold",
                                color="#333333"
                            ),
                            ft.Text(
                                self.user_data.get("email", "usuario@email.com"), 
                                size=12, 
                                color="#666666"
                            ),
                        ], spacing=2, expand=True),
                        # Botón de opciones del perfil
                        ft.IconButton(
                            icon="more_vert",
                            icon_size=16,
                            icon_color="#666666",
                            tooltip="Opciones del perfil",
                            on_click=lambda e: self.show_profile_menu()
                        )
                    ], alignment="center"),
                    padding=16
                ),
                ft.Divider(height=1, color="#E0E0E0")
            ], spacing=0),
            margin=ft.margin.only(bottom=10)
        )
    
    def show_profile_menu(self) -> None:
        """
        Muestra el menú de opciones del perfil.
        
        TODO: Implementar menú contextual completo
        """
        print("Mostrando menú de perfil")
        # Aquí se implementaría un menú contextual con opciones como:
        # - Ver perfil completo
        # - Editar información
        # - Cambiar foto
        # - Configuración de cuenta
    
    def create_sidebar(self) -> ft.Container:
        """
        Crea el menú lateral completo basado en la configuración de elementos.
        
        Returns:
            ft.Container: Contenedor con el menú lateral completo
        """
        menu_controls = []
        
        # Agregar perfil de usuario
        menu_controls.append(self.create_user_profile())
        
        # Procesar elementos del menú
        for item in self.menu_items:
            if item["type"] == "section":
                menu_controls.append(self.create_section_divider(item["title"]))
            elif item["type"] == "item":
                menu_controls.append(self.create_menu_item(item))
        
        # Agregar logout al final
        menu_controls.extend([
            ft.Container(height=20),
            ft.Divider(height=1, color="#E0E0E0"),
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon("logout", size=20, color="#F44336"),
                    title=ft.Text(
                        "Cerrar Sesión", 
                        size=14,
                        weight="w400",
                        color="#F44336"
                    ),
                    on_click=lambda e: self.handle_logout(),
                ),
                border_radius=8,
                margin=ft.margin.symmetric(horizontal=8, vertical=1),
            )
        ])
        
        return ft.Container(
            width=280,
            bgcolor="#FAFAFA",
            content=ft.Column([
                ft.Container(
                    content=ft.Column(
                        menu_controls,
                        spacing=0
                    ),
                    expand=True,
                    padding=ft.padding.only(bottom=20)
                )
            ], 
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
            ),
            border=ft.border.only(right=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def handle_logout(self) -> None:
        """
        Maneja el evento de cerrar sesión.
        """
        if self.navigation_callback:
            self.navigation_callback("/login", -1)
        else:
            self.page.go("/login")


def create_sidebar_menu(
    page: ft.Page,
    selected_index: int = 1,
    user_data: Optional[Dict[str, Any]] = None,
    navigation_callback: Optional[Callable[[str, int], None]] = None
) -> LeftSidebarMenu:
    """
    Función de conveniencia para crear una instancia del menú lateral.
    
    Args:
        page (ft.Page): La página principal de la aplicación
        selected_index (int): Índice inicial seleccionado
        user_data (Optional[Dict[str, Any]]): Datos del usuario
        navigation_callback (Optional[Callable]): Callback de navegación
        
    Returns:
        LeftSidebarMenu: Instancia configurada del menú lateral
    """
    return LeftSidebarMenu(
        page=page,
        selected_index=selected_index,
        user_data=user_data,
        navigation_callback=navigation_callback
    )
