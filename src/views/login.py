"""
Módulo de Vista de Inicio de Sesión

Este módulo contiene la implementación de la vista de autenticación de usuarios
para la aplicación de presupuesto. Proporciona una interfaz gráfica limpia y
moderna para el proceso de login.

Funcionalidades:
    - Validación de credenciales de usuario
    - Interfaz de usuario responsiva y centrada
    - Manejo de errores de autenticación
    - Redirección automática tras login exitoso
    - Fallback para importaciones de controladores

Dependencias:
    - flet: Framework de UI para Python
    - persona_controller: Controlador de autenticación (opcional)

Autor: [esteban patiño]
Fecha: [30-sep-2025]
Versión: 1.1
"""

import sys
import os
import flet as ft

# Sistema de importación simplificado
try:
    from ..controllers.persona_controller import iniciar_sesion
except ImportError as e1:
    try:
        src_path = os.path.dirname(os.path.dirname(__file__))
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from controllers.persona_controller import iniciar_sesion
    except ImportError:
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            src_path = os.path.join(project_root, "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from controllers.persona_controller import iniciar_sesion
        except ImportError:
            raise ImportError("No se puede encontrar el módulo persona_controller") from e1

def login_view(page: ft.Page) -> ft.View:
    """
    Crea y retorna la vista de inicio de sesión.
    
    Esta función construye una interfaz de usuario completa para el proceso de
    autenticación, incluyendo campos de entrada, validación y manejo de errores.
    
    Args:
        page (ft.Page): Referencia a la página principal de Flet para navegación
        
    Returns:
        ft.View: Vista completa del formulario de login lista para mostrar
    """
    
    # Campos de entrada con mejor alineación
    name_input = ft.TextField(
        label="Nombre de Usuario",
        width=300,
        border_radius=8,
        prefix_icon=ft.Icon(ft.Icons.PERSON),
        autofocus=True,
        hint_text="Ingresa tu nombre de usuario",
        helper_text="Ejemplo: juan.perez",
        max_length=50
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        width=300,
        border_radius=8,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icon(ft.Icons.LOCK),
        hint_text="Ingresa tu contraseña",
        helper_text="Mínimo 6 caracteres",
        max_length=100
    )
    
    # Texto para mostrar resultados de autenticación
    result_text = ft.Text(
        value="",
        color="green",
        text_align=ft.TextAlign.CENTER,
        size=14,
        weight=ft.FontWeight.BOLD
    )

    def on_login_click(e: ft.ControlEvent) -> None:
        """
        Maneja el evento de clic en el botón de inicio de sesión.
        """
        # Limpiar mensaje anterior
        result_text.value = ""
        result_text.color = "green"
        
        # Validación básica de campos
        username = name_input.value.strip() if name_input.value else ""
        password = password_input.value.strip() if password_input.value else ""
        
        if not username or not password:
            result_text.value = "Por favor, completa todos los campos"
            result_text.color = "red"
            page.update()
            return

        try:
            # Llamar al controlador de autenticación con los parámetros correctos
            success, message, user_data = iniciar_sesion(username, password)

            if success:
                # Autenticación exitosa
                result_text.value = "¡Login exitoso! Redirigiendo..."
                result_text.color = "green"
                page.update()
                
                # Pequeña pausa para mostrar el mensaje de éxito
                import time
                time.sleep(0.5)
                
                # Navegar a la vista principal
                page.go("/resumen")
            else:
                # Error de autenticación
                result_text.value = message or "Credenciales incorrectas"
                result_text.color = "red"
                
                # Limpiar campo de contraseña por seguridad
                password_input.value = ""
                
        except Exception as ex:
            # Manejo de errores inesperados
            result_text.value = f"Error del sistema: {str(ex)}"
            result_text.color = "red"
            
        finally:
            # Siempre actualizar la página
            page.update()

    def on_text_field_submit(e: ft.ControlEvent) -> None:
        """Maneja el evento de presionar Enter en los campos de texto."""
        on_login_click(e)

    # Configurar eventos de Enter en los campos
    name_input.on_submit = on_text_field_submit
    password_input.on_submit = on_text_field_submit

    # Botón de login estilizado
    login_button = ft.ElevatedButton(
        "Iniciar Sesión",
        on_click=on_login_click,
        width=300,
        height=45,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        # Estilo adicional para mejor apariencia
        elevation=3,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(
                size=16,
                weight=ft.FontWeight.BOLD
            )
        )
    )

    # Contenedor principal centrado y estilizado
    main_container = ft.Container(
        content=ft.Column(
            controls=[
                # Icono principal de la aplicación
                ft.Icon(
                    ft.Icons.LOGIN,
                    size=60,
                    color=ft.Colors.BLUE
                ),
                # Título de la aplicación
                ft.Text(
                    "Inicio de Sesión",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color="#333333"
                ),
                # Subtítulo descriptivo
                ft.Text(
                    "Accede a tu cuenta de presupuesto",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color="#666666"
                ),
                # Espaciado entre header y formulario
                ft.Container(height=20),
                # Campo de nombre de usuario
                name_input,
                # Espaciado pequeño entre campos
                ft.Container(height=10),
                # Campo de contraseña
                password_input,
                # Espaciado antes del botón
                ft.Container(height=20),
                # Botón de inicio de sesión
                login_button,
                # Espaciado pequeño antes del resultado
                ft.Container(height=10),
                # Texto de resultado (éxito/error)
                result_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            tight=True
        ),
        # Estilo del contenedor principal
        padding=ft.Padding(30, 30, 30, 30),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        width=350,
        height=450,
        # Sombra para efecto elevado
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#00000020",
            offset=ft.Offset(0, 2)
        )
    )

    # Retornar vista completa en lugar de agregar a la página
    return ft.View(
        route="/login",
        controls=[
            # Contenedor wrapper para centrado perfecto
            ft.Container(
                content=main_container,
                alignment=ft.alignment.center,
                expand=True,
                # Fondo degradado sutil
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["#F8F9FA", "#E9ECEF"]
                )
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0,
        spacing=0
    )

