"""
Módulo de Vista de Constantes del Sistema - SystemConstantsView

Gestión profesional de variables globales y parámetros de configuración 
de la aplicación financiera. Implementación Senior Level con:
- CRUD completo (Create, Read, Update, Delete)
- Validación de tipos de datos
- Búsqueda y filtrado por categoría
- Edición en BottomSheet
- FAB para crear nuevas constantes
- Auditoría de cambios

Clases:
    SystemConstantsView: Vista profesional de gestión de constantes
    Constant: Dataclass que representa una constante
    ConstantType: Enum de tipos de datos soportados

Autor: Senior Developer
Fecha: 2026-04-07
Versión: 3.0 - Senior Level Implementation
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List

import flet as ft

try:
    from ..database.db_connector import DatabaseConnector
except ImportError:
    from database.db_connector import DatabaseConnector

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    from sidebar import create_sidebar_menu


# ========================================================================
# TIPOS Y ENUMERACIONES
# ========================================================================

class ConstantType(str, Enum):
    """Tipos de datos soportados para constantes."""
    STRING = "STRING"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    DATE = "DATE"


@dataclass
class Constant:
    """Representa una constante del sistema con su metadata."""
    id_constante: int
    categoria: str
    nombre: str
    valor: str
    tipo_dato: ConstantType
    descripcion: str
    es_editable: bool
    estado: bool
    fecha_actualizacion: Optional[str] = None


# ========================================================================
# VISTA PRINCIPAL - SENIOR LEVEL
# ========================================================================

class SystemConstantsView:
    """
    Vista profesional y escalable para gestión de constantes del sistema.
    
    Características principales:
    ✅ Tabla interactiva con constantes desde BD
    ✅ Edición in-place en BottomSheet con validación
    ✅ Creación de nuevas constantes via FAB
    ✅ Búsqueda full-text en nombre y descripción
    ✅ Filtrado por categoría
    ✅ Validación de tipos (STRING, INTEGER, DECIMAL, BOOLEAN, JSON, DATE)
    ✅ Soft delete con auditoría
    ✅ Formateo inteligente de valores según tipo
    ✅ Manejo de errores con rollback automático
    
    Arquitectura:
    - Separación clara entre lógica de BD y UI
    - CRUD completamente encapsulado
    - Inyección de dependencias (DatabaseConnector)
    - Métodos privados para operaciones internas
    - Logging detallado de todas las operaciones
    
    Attributes:
        page (ft.Page): Referencia a página Flet
        db (DatabaseConnector): Conexión a BD con manejo de pool
        constants (List[Constant]): Caché de constantes cargadas
        filtered_constants (List[Constant]): Constantes filtradas actualmente
        logger (logging.Logger): Logger de aplicación
    """
    
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.db = DatabaseConnector()
        self.logger = logging.getLogger(__name__)
        self.debug_terminal = True
        
        # Estado interno
        self.constants: List[Constant] = []
        self.filtered_constants: List[Constant] = []
        self.selected_constant: Optional[Constant] = None
        self.categories: List[str] = []
        
        # Sidebar
        try:
            self.sidebar_menu = create_sidebar_menu(
                page=page,
                selected_index=16,
                navigation_callback=self.handle_navigation
            )
        except Exception as e:
            self.logger.warning(f"Error creando sidebar: {e}")
            self.sidebar_menu = None
        
        # Tarjeta fija de datos; su contenido se reemplaza en cada refresh.
        self.table_card = ft.Container(
            bgcolor="white",
            border_radius=8,
            padding=12,
            border=ft.border.all(1, "#E0E0E0"),
        )
        
        self.search_field = ft.TextField(
            label="Buscar constante...",
            width=300,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Filtrar por categoría",
            width=250,
            on_change=self._on_category_filter
        )
        
        self.status_text = ft.Text(value="", size=12, color=ft.Colors.RED_600)
        self.summary_text = ft.Text(value="", size=12, color="#6B7280")
        self.debug_text = ft.Text(value="DEBUG: iniciando...", size=12, color="#7C2D12")
        self.debug_simple_grid = True
        
        # Cargar datos iniciales
        self._load_constants()
        self._load_categories()
        self._debug_terminal("view initialized")
        
        self.logger.info("SystemConstantsView inicializada correctamente")

    def _debug_terminal(self, message: str) -> None:
        """Imprime trazas de depuración en terminal para seguimiento de la vista."""
        if self.debug_terminal:
            print(f"[DEBUG CONST] {message}", flush=True)
    
    def handle_navigation(self, route: str, index: int) -> None:
        """Maneja navegación desde el sidebar."""
        self.logger.debug(f"Navegación: ruta={route}, index={index}")
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)
    
    # ====================================================================
    # OPERACIONES DE CARGA (READ)
    # ====================================================================
    
    def _ensure_constants_table_exists(self) -> bool:
        """
        Verifica si la tabla constantes existe, si no, la crea.
        
        Returns:
            bool: True si la tabla existe o fue creada, False si hay error
        """
        try:
            # Intentar crear la tabla si no existe
            create_sql = """
            CREATE TABLE IF NOT EXISTS constantes (
                id_constante INT AUTO_INCREMENT PRIMARY KEY,
                categoria VARCHAR(50) NOT NULL,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                valor TEXT NOT NULL,
                tipo_dato ENUM('STRING','INTEGER','DECIMAL','BOOLEAN','JSON','DATE') NOT NULL,
                descripcion TEXT,
                es_editable TINYINT(1) DEFAULT 1,
                estado TINYINT(1) DEFAULT 1,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_categoria_estado (categoria, estado),
                INDEX idx_nombre_estado (nombre, estado)
            )
            """
            
            conn = self.db.conn
            if conn:
                cursor = conn.cursor()
                cursor.execute(create_sql)
                conn.commit()
                cursor.close()
                self.logger.info("Tabla constantes verificada/creada correctamente")
                return True
        except Exception as e:
            self.logger.warning(f"No se pudo crear tabla constantes: {e}")
        
        return False
    
    def _load_constants(self) -> None:
        """
        Carga todas las constantes activas de la BD.
        
        Implementa caché local para mejorar performance.
        Las constantes se ordenan por categoría y nombre.
        """
        try:
            # Asegurar que la tabla existe
            self._ensure_constants_table_exists()
            
            rows = self.db.execute_query(
                """
                SELECT id_constante, categoria, nombre, valor, tipo_dato,
                       descripcion, es_editable, estado, fecha_actualizacion
                FROM constantes
                WHERE estado = 1
                ORDER BY categoria, nombre
                """
            ) or []
            
            self.constants = []
            for r in rows:
                try:
                    constant = Constant(
                        id_constante=int(r['id_constante']),
                        categoria=str(r['categoria']),
                        nombre=str(r['nombre']),
                        valor=str(r['valor']),
                        tipo_dato=ConstantType(r['tipo_dato']),
                        descripcion=str(r['descripcion'] or ''),
                        es_editable=bool(r['es_editable']),
                        estado=bool(r['estado']),
                        fecha_actualizacion=r.get('fecha_actualizacion')
                    )
                    self.constants.append(constant)
                except Exception as row_error:
                    self.logger.warning(f"Error cargando constante {r.get('nombre')}: {row_error}")
            
            self.filtered_constants = self.constants.copy()
            self.debug_text.value = (
                f"DEBUG load: constants={len(self.constants)} filtered={len(self.filtered_constants)}"
            )
            self._debug_terminal(
                f"load_constants -> constants={len(self.constants)} filtered={len(self.filtered_constants)}"
            )
            self.logger.info(f"Cargadas {len(self.constants)} constantes")
            
        except Exception as e:
            self.logger.error(f"Error cargando constantes: {e}", exc_info=True)
            self._show_message(f"⚠️ Error cargando datos: {str(e)}", ft.Colors.ORANGE_700)
    
    def _load_categories(self) -> None:
        """
        Carga las categorías disponibles para el dropdown de filtro.
        """
        try:
            rows = self.db.execute_query(
                """
                SELECT DISTINCT categoria
                FROM constantes
                WHERE estado = 1
                ORDER BY categoria
                """
            )
            
            self.categories = [str(r['categoria']) for r in rows]
            
            # Actualizar dropdown
            self.category_dropdown.options = [
                ft.dropdown.Option("TODAS", "Todas las categorías"),
                *[ft.dropdown.Option(cat, cat) for cat in self.categories]
            ]
            self.category_dropdown.value = "TODAS"
            
            self.logger.debug(f"Cargadas {len(self.categories)} categorías")
            
        except Exception as e:
            self.logger.error(f"Error cargando categorías: {e}")
    
    # ====================================================================
    # BÚSQUEDA Y FILTRADO
    # ====================================================================
    
    def _on_search_change(self, e: Optional[ft.ControlEvent] = None) -> None:
        """
        Callback para búsqueda de texto.
        Aplica filtro en tiempo real sobre nombre y descripción.
        """
        search_term = (self.search_field.value or "").lower().strip()
        category = self.category_dropdown.value or "TODAS"
        
        self.filtered_constants = [
            c for c in self.constants
            if (search_term in c.nombre.lower() or 
                search_term in c.descripcion.lower()) and
               (category == "TODAS" or c.categoria == category)
        ]
        
        self._refresh_table()
        self.logger.debug(f"Search: term='{search_term}', found={len(self.filtered_constants)}")
    
    def _on_category_filter(self, e: Optional[ft.ControlEvent] = None) -> None:
        """Callback para filtrado por categoría."""
        self._on_search_change()

    def _find_constant_by_name(self, name: str) -> Optional[Constant]:
        """Busca una constante por nombre (exacto, case-insensitive)."""
        normalized = (name or "").strip().lower()
        if not normalized:
            return None

        for const in self.constants:
            if const.nombre.strip().lower() == normalized:
                return const
        return None

    def _open_constant_manager_dialog(self) -> None:
        """Abre ventana para gestionar una constante por nombre."""
        search_field = ft.TextField(
            label="Nombre de la constante",
            hint_text="Ej: IVA",
            autofocus=True,
        )
        result_text = ft.Text("", size=12, color="#6B7280")
        selected: Dict[str, Optional[Constant]] = {"constant": None}

        edit_btn = ft.ElevatedButton("Modificar", icon=ft.Icons.EDIT, disabled=True)
        delete_btn = ft.ElevatedButton(
            "Eliminar",
            icon=ft.Icons.DELETE_OUTLINE,
            disabled=True,
            bgcolor="#DC2626",
            color="white",
        )

        def _refresh_action_buttons() -> None:
            const = selected["constant"]
            can_manage = const is not None
            edit_btn.disabled = not can_manage
            delete_btn.disabled = not can_manage

        def _search_constant(_: Optional[ft.ControlEvent] = None) -> None:
            const = self._find_constant_by_name(search_field.value or "")
            selected["constant"] = const

            if const:
                result_text.value = (
                    f"Encontrada: {const.nombre} | Categoria: {const.categoria} | "
                    f"Tipo: {const.tipo_dato.value} | Valor: {const.valor}"
                )
                result_text.color = "#065F46"
            else:
                result_text.value = "No se encontró una constante con ese nombre"
                result_text.color = "#B91C1C"

            _refresh_action_buttons()
            self.page.update()

        def _open_create(_: ft.ControlEvent) -> None:
            dialog.open = False
            self.page.update()
            self._show_create_constantsheet()

        def _open_edit(_: ft.ControlEvent) -> None:
            const = selected["constant"]
            if not const:
                return
            dialog.open = False
            self.page.update()
            self._edit_constant_bottomsheet(const)

        def _open_delete(_: ft.ControlEvent) -> None:
            const = selected["constant"]
            if not const:
                return
            dialog.open = False
            self.page.update()
            self._delete_constant(const)

        search_field.on_submit = _search_constant
        edit_btn.on_click = _open_edit
        delete_btn.on_click = _open_delete

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gestionar Constante"),
            content=ft.Container(
                width=560,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Consulta por nombre y luego selecciona una acción.",
                            size=12,
                            color="#6B7280",
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(expand=True, content=search_field),
                                ft.ElevatedButton(
                                    "Consultar",
                                    icon=ft.Icons.SEARCH,
                                    on_click=_search_constant,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Container(
                            content=result_text,
                            padding=10,
                            border_radius=8,
                            border=ft.border.all(1, "#E5E7EB"),
                            bgcolor="#F9FAFB",
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=_open_create),
                                edit_btn,
                                delete_btn,
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=12,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: setattr(dialog, "open", False)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        _refresh_action_buttons()
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    # ====================================================================
    # INTERFAZ DE TABLA (PRESENTACIÓN)
    # ====================================================================
    
    def _build_grid_cell(
        self,
        content: ft.Control,
        width: int,
        *,
        padding: int | tuple[int, int] = 12,
        alignment: Optional[ft.Alignment] = None,
    ) -> ft.Container:
        """Crea una celda de la grilla manual con ancho fijo."""
        if isinstance(padding, tuple):
            cell_padding = ft.padding.symmetric(horizontal=padding[0], vertical=padding[1])
        else:
            cell_padding = ft.padding.all(padding)

        return ft.Container(
            content=content,
            width=width,
            padding=cell_padding,
            alignment=alignment,
        )

    def _build_grid_header(self) -> ft.Container:
        """Construye el encabezado de la grilla manual."""
        return ft.Container(
            bgcolor="#F5F7FA",
            border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB")),
            content=ft.Row(
                controls=[
                    self._build_grid_cell(ft.Text("Nombre", weight="bold", size=12, color="#374151"), 280),
                    self._build_grid_cell(ft.Text("Valor", weight="bold", size=12, color="#374151"), 220),
                    self._build_grid_cell(ft.Text("Tipo", weight="bold", size=12, color="#374151"), 130),
                    self._build_grid_cell(ft.Text("Descripción", weight="bold", size=12, color="#374151"), 330),
                    self._build_grid_cell(ft.Text("Acciones", weight="bold", size=12, color="#374151"), 130),
                ],
                spacing=0,
            ),
        )

    def _build_grid_row(self, const: Constant, index: int) -> ft.Container:
        """Construye una fila de la grilla manual."""
        value_text = self._format_constant_value(const)
        description = const.descripcion[:70] + "..." if len(const.descripcion) > 70 else const.descripcion
        row_bgcolor = "#FFFFFF" if index % 2 == 0 else "#FAFBFC"

        return ft.Container(
            bgcolor=row_bgcolor,
            border=ft.border.only(bottom=ft.BorderSide(1, "#EEF2F7")),
            content=ft.Row(
                controls=[
                    self._build_grid_cell(
                        ft.Column([
                            ft.Text(const.nombre, weight="bold", size=13, color="#111827"),
                            ft.Text(const.categoria, size=11, color="#6B7280"),
                        ], spacing=2, tight=True),
                        280,
                    ),
                    self._build_grid_cell(
                        ft.Text(value_text, size=13, color="#111827", selectable=True),
                        220,
                    ),
                    self._build_grid_cell(
                        ft.Container(
                            content=ft.Text(const.tipo_dato.value, size=11, color="white", weight="bold"),
                            bgcolor=self._get_type_color(const.tipo_dato),
                            border_radius=999,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        ),
                        130,
                    ),
                    self._build_grid_cell(
                        ft.Text(description or "Sin descripción", size=11, color="#4B5563"),
                        330,
                    ),
                    self._build_grid_cell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=18,
                                tooltip="Editar" if const.es_editable else "No editable",
                                icon_color="#2563EB" if const.es_editable else "#D1D5DB",
                                on_click=lambda e, c=const: self._edit_constant_bottomsheet(c) if c.es_editable else None,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                tooltip="Eliminar",
                                icon_color="#DC2626",
                                on_click=lambda e, c=const: self._delete_constant(c),
                            ),
                        ], spacing=0, tight=True),
                        130,
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _build_grid_table(self) -> ft.Control:
        """Construye la grilla completa con scroll horizontal."""
        table_content = ft.Container(
            width=1090,
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "#E5E7EB"),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                controls=[
                    self._build_grid_header(),
                    *[
                        self._build_grid_row(const, index)
                        for index, const in enumerate(self.filtered_constants)
                    ],
                ],
                spacing=0,
            ),
        )

        return ft.Row(
            controls=[table_content],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )
    
    def _refresh_table(self) -> None:
        """Actualiza el contenido de table_list en el árbol de controles."""
        self.summary_text.value = f"{len(self.filtered_constants)} constante(s) cargada(s)"
        first_name = self.filtered_constants[0].nombre if self.filtered_constants else "N/A"
        self.debug_text.value = (
            f"DEBUG refresh: rows={len(self.filtered_constants)} first={first_name} "
            f"mode={'simple' if self.debug_simple_grid else 'grid'} "
            f"time={datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        self._debug_terminal(
            f"refresh_table -> rows={len(self.filtered_constants)} first={first_name} "
            f"mode={'simple' if self.debug_simple_grid else 'grid'}"
        )
        
        if not self.filtered_constants:
            self.table_card.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color="#CCCCCC"),
                    ft.Text("No hay constantes que mostrar", size=18, color="#999999", weight="w500"),
                    ft.Text("Crea una nueva constante con el botón +", size=13, color="#BBBBBB")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.alignment.center,
                height=300
            )
        else:
            simple_rows = [
                ft.Container(
                    content=ft.Text(
                        f"{idx + 1}. {const.nombre} | {const.categoria} | {const.tipo_dato.value} | {const.valor}",
                        size=12,
                        color="#111827",
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    bgcolor="#FFFFFF" if idx % 2 == 0 else "#F9FAFB",
                    border=ft.border.only(bottom=ft.BorderSide(1, "#EEF2F7")),
                )
                for idx, const in enumerate(self.filtered_constants)
            ]

            self.table_card.content = ft.Column(
                controls=[
                    ft.Text(
                        "Listado de Constantes",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#374151",
                    ),
                    ft.Divider(height=12, color="#E5E7EB"),
                    *simple_rows,
                ],
                spacing=0,
            )
        
        try:
            self.page.update()
        except Exception as refresh_error:
            self.logger.debug(f"No se pudo actualizar la página durante refresh: {refresh_error}")
    
    # ====================================================================
    # EDICIÓN (UPDATE)
    # ====================================================================
    
    def _edit_constant_bottomsheet(self, constant: Constant) -> None:
        """
        Abre BottomSheet para editar una constante existente.
        
        Características:
        - Validación de tipo en tiempo real
        - Nombre de solo lectura (no se puede cambiar)
        - Descripción editableMult-línea
        - Retroalimentación visual de validación
        
        Args:
            constant: Constante a editar
        """
        self.selected_constant = constant
        
        nombre_field = ft.TextField(
            label="Nombre",
            value=constant.nombre,
            read_only=True,
            disabled=True
        )
        
        valor_field = ft.TextField(
            label=f"Valor ({constant.tipo_dato.value})",
            value=constant.valor,
            multiline=False,
            on_change=self._on_valor_change
        )
        
        tipo_field = ft.Text(
            f"Tipo: {constant.tipo_dato.value}",
            weight="bold",
            color=self._get_type_color(constant.tipo_dato)
        )
        
        descripcion_field = ft.TextField(
            label="Descripción",
            value=constant.descripcion,
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        validation_message = ft.Text(value="", size=11)
        
        def _on_valor_change_local(e):
            """Validación en tiempo real mientras se edita."""
            is_valid, error_msg = self._validate_constant_value(
                valor_field.value,
                constant.tipo_dato
            )
            
            if is_valid:
                validation_message.value = "✓ Valor válido"
                validation_message.color = ft.Colors.GREEN_700
            else:
                validation_message.value = f"✗ {error_msg}"
                validation_message.color = ft.Colors.RED_600
            
            self.page.update()
        
        valor_field.on_change = _on_valor_change_local
        
        def save_changes():
            # Validación final
            is_valid, error_msg = self._validate_constant_value(
                valor_field.value,
                constant.tipo_dato
            )
            
            if not is_valid:
                self._show_message(f"Validación fallida: {error_msg}", ft.Colors.RED_600)
                return
            
            # Actualizar en BD
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """
                    UPDATE constantes
                    SET valor = %s,
                        descripcion = %s,
                        fecha_actualizacion = NOW()
                    WHERE id_constante = %s
                    """,
                    (valor_field.value, descripcion_field.value, constant.id_constante)
                )
                self.db.conn.commit()
                cursor.close()
                
                self.logger.info(f"Constante {constant.nombre} actualizada")
                self._show_message(
                    f"✓ Constante '{constant.nombre}' actualizada",
                    ft.Colors.GREEN_700
                )
                self.page.bottom_sheet.open = False
                self._load_constants()
                
            except Exception as e:
                self.logger.error(f"Error guardando constante: {e}")
                self._show_message(f"Error guardando: {str(e)}", ft.Colors.RED_600)
        
        bottom_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    # Encabezado
                    ft.Row([
                        ft.Text("Editar Constante", size=20, weight="bold"),
                        ft.IconButton(
                            ft.Icons.CLOSE,
                            on_click=lambda e: setattr(self.page.bottom_sheet, 'open', False)
                        )
                    ], alignment="spaceBetween"),
                    
                    ft.Divider(),
                    
                    # Campos
                    nombre_field,
                    tipo_field,
                    valor_field,
                    validation_message,
                    descripcion_field,
                    
                    ft.Divider(),
                    
                    # Botones
                    ft.Row([
                        ft.OutlinedButton(
                            "Cancelar",
                            on_click=lambda e: setattr(self.page.bottom_sheet, 'open', False)
                        ),
                        ft.ElevatedButton(
                            "Guardar Cambios",
                            on_click=lambda e: save_changes()
                        ),
                    ], alignment="end", spacing=8),
                ], spacing=16),
                padding=24
            ),
            enable_drag=False,
        )
        
        self.page.bottom_sheet = bottom_sheet
        bottom_sheet.open = True
        self.page.update()
    
    def _on_valor_change(self, e: ft.ControlEvent) -> None:
        """Placeholder para validación en tiempo real."""
        pass
    
    # ====================================================================
    # CREACIÓN (CREATE)
    # ====================================================================
    
    def _show_create_constantsheet(self) -> None:
        """
        Abre BottomSheet para crear una nueva constante.
        
        Incluye:
        - Validación de nombre único
        - Dropdown de categorías existentes + opción de crear nueva
        - Selector de tipo de dato
        - Validación de valor según tipo
        - Descripción opcional
        """
        
        nombre_field = ft.TextField(
            label="Nombre de la constante",
            on_change=lambda e: self._validate_unique_name(e.control.value)
        )
        
        categoria_field = ft.Dropdown(
            label="Categoría",
            options=[ft.dropdown.Option(cat) for cat in self.categories] +
                   [ft.dropdown.Option("__NEW__", "➕ Nueva categoría")]
        )
        
        nueva_categoria_field = ft.TextField(
            label="Nombre de la nueva categoría",
            visible=False
        )
        
        def _on_categoria_change(e):
            if categoria_field.value == "__NEW__":
                nueva_categoria_field.visible = True
            else:
                nueva_categoria_field.visible = False
            self.page.update()
        
        categoria_field.on_change = _on_categoria_change
        
        tipo_dropdown = ft.Dropdown(
            label="Tipo de dato",
            options=[
                ft.dropdown.Option(t.value, t.value)
                for t in ConstantType
            ]
        )
        
        valor_field = ft.TextField(label="Valor inicial")
        
        descripcion_field = ft.TextField(
            label="Descripción (opcional)",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        validation_message = ft.Text(value="", size=11)
        
        def _on_valor_field_change(e):
            """Validación de valor en tiempo real."""
            if not tipo_dropdown.value:
                return
            
            tipo = ConstantType(tipo_dropdown.value)
            is_valid, error_msg = self._validate_constant_value(valor_field.value, tipo)
            
            if is_valid and valor_field.value:
                validation_message.value = "✓ Valor válido"
                validation_message.color = ft.Colors.GREEN_700
            elif valor_field.value:
                validation_message.value = f"✗ {error_msg}"
                validation_message.color = ft.Colors.RED_600
            else:
                validation_message.value = ""
            
            self.page.update()
        
        valor_field.on_change = _on_valor_field_change
        
        def save_new_constant():
            # Validaciones
            if not nombre_field.value:
                self._show_message("El nombre es obligatorio", ft.Colors.RED_600)
                return
            
            categoria = nueva_categoria_field.value if categoria_field.value == "__NEW__" else categoria_field.value
            
            if not categoria:
                self._show_message("Selecciona o crea una categoría", ft.Colors.RED_600)
                return
            
            if not tipo_dropdown.value:
                self._show_message("Selecciona un tipo de dato", ft.Colors.RED_600)
                return
            
            if not valor_field.value:
                self._show_message("Ingresa un valor", ft.Colors.RED_600)
                return
            
            # Validar tipo
            tipo = ConstantType(tipo_dropdown.value)
            is_valid, error_msg = self._validate_constant_value(valor_field.value, tipo)
            
            if not is_valid:
                self._show_message(f"Validación de valor fallida: {error_msg}", ft.Colors.RED_600)
                return
            
            # Insertar en BD
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO constantes
                    (categoria, nombre, valor, tipo_dato, descripcion, es_editable, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        categoria,
                        nombre_field.value,
                        valor_field.value,
                        tipo.value,
                        descripcion_field.value or "",
                        1,
                        1
                    )
                )
                self.db.conn.commit()
                cursor.close()
                
                self.logger.info(f"Constante creada: {nombre_field.value}")
                self._show_message(
                    f"✓ Constante '{nombre_field.value}' creada",
                    ft.Colors.GREEN_700
                )
                self.page.bottom_sheet.open = False
                self._load_constants()
                self._load_categories()
                
            except Exception as e:
                self.logger.error(f"Error creando constante: {e}")
                self._show_message(f"Error creando: {str(e)}", ft.Colors.RED_600)
        
        bottom_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    # Encabezado
                    ft.Row([
                        ft.Text("Crear Nueva Constante", size=20, weight="bold"),
                        ft.IconButton(
                            ft.Icons.CLOSE,
                            on_click=lambda e: setattr(self.page.bottom_sheet, 'open', False)
                        )
                    ], alignment="spaceBetween"),
                    
                    ft.Divider(),
                    
                    # Campos
                    nombre_field,
                    categoria_field,
                    nueva_categoria_field,
                    tipo_dropdown,
                    valor_field,
                    validation_message,
                    descripcion_field,
                    
                    ft.Divider(),
                    
                    # Botones
                    ft.Row([
                        ft.OutlinedButton(
                            "Cancelar",
                            on_click=lambda e: setattr(self.page.bottom_sheet, 'open', False)
                        ),
                        ft.ElevatedButton(
                            "Crear Constante",
                            on_click=lambda e: save_new_constant()
                        ),
                    ], alignment="end", spacing=8),
                ], spacing=16, expand=True),
                padding=24
            ),
            enable_drag=False,
        )
        
        self.page.bottom_sheet = bottom_sheet
        bottom_sheet.open = True
        self.page.update()
    
    # ====================================================================
    # ELIMINACIÓN (DELETE - SOFT DELETE)
    # ====================================================================
    
    def _delete_constant(self, constant: Constant) -> None:
        """
        Elimina una constante (soft delete - actualiza estado a 0).
        
        Args:
            constant: Constante a eliminar
        """
        
        def confirm_delete():
            try:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "UPDATE constantes SET estado = 0 WHERE id_constante = %s",
                    (constant.id_constante,)
                )
                self.db.conn.commit()
                cursor.close()
                
                self.logger.info(f"Constante eliminada: {constant.nombre}")
                self._show_message(
                    f"✓ Constante '{constant.nombre}' eliminada",
                    ft.Colors.GREEN_700
                )
                self._load_constants()
                
            except Exception as e:
                self.logger.error(f"Error eliminando constante: {e}")
                self._show_message(f"Error eliminando: {str(e)}", ft.Colors.RED_600)
        
        # Diálogo de confirmación
        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar la constante '{constant.nombre}'?"),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: close_dialog()
                ),
                ft.TextButton(
                    "Eliminar",
                    on_click=lambda e: (confirm_delete(), close_dialog())
                ),
            ],
        )
        
        def close_dialog():
            dlg.open = False
            self.page.update()
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    # ====================================================================
    # VALIDACIÓN
    # ====================================================================
    
    def _validate_constant_value(self, value: str, tipo: ConstantType) -> tuple[bool, str]:
        """
        Valida que el valor sea válido según su tipo de dato.
        
        Args:
            value: Valor a validar
            tipo: Tipo de dato esperado
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        try:
            if tipo == ConstantType.INTEGER:
                int(value)
            elif tipo == ConstantType.DECIMAL:
                float(value.replace(',', '.'))
            elif tipo == ConstantType.BOOLEAN:
                if value.lower() not in ['true', 'false', '1', '0', 'si', 'no', 'yes', 'no']:
                    return False, "Boolean debe ser: true, false, 1, 0, si, no"
            elif tipo == ConstantType.DATE:
                datetime.datetime.strptime(value, '%Y-%m-%d')
            elif tipo == ConstantType.JSON:
                import json
                json.loads(value)
            # STRING acepta cualquier valor
            
            return True, ""
        
        except ValueError as e:
            return False, f"Tipo {tipo.value}: {str(e)}"
        except Exception as e:
            return False, str(e)
    
    def _validate_unique_name(self, name: str) -> bool:
        """Valida que el nombre de la constante sea único."""
        if not name:
            return True
        
        existing = any(c.nombre == name for c in self.constants)
        return not existing
    
    def _format_constant_value(self, constant: Constant) -> str:
        """
        Formatea el valor para presentación según su tipo.
        
        Args:
            constant: Constante a formatear
        
        Returns:
            Valor formateado como string
        """
        try:
            if constant.tipo_dato == ConstantType.DECIMAL:
                return f"{float(constant.valor):,.2f}"
            elif constant.tipo_dato == ConstantType.INTEGER:
                return f"{int(constant.valor):,}"
            else:
                return constant.valor
        except:
            return constant.valor
    
    def _get_type_color(self, tipo: ConstantType) -> str:
        """Retorna color hex según tipo de dato."""
        colors = {
            ConstantType.STRING: "#2196F3",
            ConstantType.INTEGER: "#4CAF50",
            ConstantType.DECIMAL: "#FF9800",
            ConstantType.BOOLEAN: "#9C27B0",
            ConstantType.JSON: "#F44336",
            ConstantType.DATE: "#00BCD4",
        }
        return colors.get(tipo, "#757575")
    
    # ====================================================================
    # UTILIDADES UI
    # ====================================================================
    
    def _show_message(self, message: str, color: str = ft.Colors.BLUE_700) -> None:
        """
        Muestra mensaje de estado temporalmente.
        
        Args:
            message: Mensaje a mostrar
            color: Color del texto
        """
        try:
            self.status_text.value = message
            self.status_text.color = color
            self.page.update()
        except Exception as e:
            self.logger.debug(f"Error mostrando mensaje: {e}")
    
    def _build_header(self) -> ft.Container:
        """Construye la barra de encabezado."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Constantes del Sistema [DEBUG-V7]",
                    size=28,
                    weight="bold",
                    color="#333333"
                ),
                ft.Text(
                    "Gestión de variables globales y parámetros de configuración",
                    size=14,
                    color="#666666"
                ),
            ], spacing=4),
            padding=24,
            bgcolor="white",
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )
    
    def _build_toolbar(self) -> ft.Container:
        """Construye la barra de herramientas con búsqueda y filtros."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.search_field,
                    self.category_dropdown,
                    ft.ElevatedButton(
                        "Gestionar constante",
                        icon=ft.Icons.MANAGE_SEARCH,
                        on_click=lambda e: self._open_constant_manager_dialog(),
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Actualizar",
                        on_click=lambda e: self._reload_data()
                    ),
                ], alignment="start", wrap=True),
                ft.Container(
                    content=self.debug_text,
                    bgcolor="#FEF3C7",
                    border=ft.border.all(1, "#F59E0B"),
                    border_radius=8,
                    padding=8,
                ),
            ], spacing=10),
            padding=16,
            bgcolor="#F8F9FA",
            border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
        )

    def _reload_data(self) -> None:
        """Recarga datos y refresca la grilla visible."""
        self._load_constants()
        self._load_categories()
        self._refresh_table()
    
    def _build_main_content(self) -> ft.Container:
        """Construye el contenido principal – sin expand (lo añade build())."""
        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    self._build_toolbar(),
                    ft.Container(
                        height=620,
                        padding=ft.padding.symmetric(horizontal=20, vertical=16),
                        content=ft.Column(
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                self.status_text,
                                self.summary_text,
                                self.table_card,
                            ],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )

    # ====================================================================
    # CONSTRUCCIÓN FINAL
    # ====================================================================

    def build(self) -> ft.Container:
        """Construye la vista completa lista para ser insertada en ft.View."""
        self._refresh_table()

        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor="#2196F3",
            on_click=lambda e: self._show_create_constantsheet(),
            tooltip="Nueva constante"
        )

        content = self._build_main_content()

        row_controls = []
        if self.sidebar_menu:
            row_controls.append(self.sidebar_menu.create_sidebar())
        row_controls.append(
            ft.Container(
                content=content,
                expand=True,
                bgcolor="#F8F9FA",
            )
        )

        return ft.Container(
            content=ft.Row(row_controls, expand=True, spacing=0),
            expand=True,
        )


# ========================================================================
# FUNCIONES EXPORTADAS
# ========================================================================

def system_constants_view(page: ft.Page) -> ft.View:
    """Función de entrada para navegación a /constantes."""
    print("[DEBUG CONST] system_constants_view called", flush=True)
    view = SystemConstantsView(page)
    built = view.build()
    return ft.View(
        route="/constantes",
        controls=[built],
        padding=0,
        spacing=0,
        floating_action_button=page.floating_action_button,
    )


def main(page: ft.Page) -> None:
    """
    Función principal para ejecutar la aplicación de forma independiente.
    
    Útil para desarrollo y debug.
    
    Args:
        page (ft.Page): Página Flet principal
    """
    page.title = "App Presupuesto - Constantes del Sistema"
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 1000
    page.window.min_height = 700
    page.padding = 0
    page.spacing = 0
    
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Inter")
    
    page.add(system_constants_view(page))


if __name__ == "__main__":
    """Punto de entrada para ejecución independiente."""
    ft.app(target=main)



