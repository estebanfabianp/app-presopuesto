# -*- coding: utf-8 -*-
"""
Vista de Optimización de Categorías.

Secciones:
    1. Reglas         — conceptos con categoría única (automáticas + confirmadas).
    2. Conflictos     — conceptos con múltiples categorías históricas.
    3. Sin Categoría  — movimientos pendientes de clasificar.

Acciones disponibles:
    - "Aplicar reglas" (header): actualiza todos los mov. sin categoría.
    - Confirmar/Limpiar una regla automática.
    - Resolver un conflicto eligiendo la categoría correcta.
    - Asignar categoría a movimientos individuales.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

import flet as ft

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    from sidebar import create_sidebar_menu

try:
    from ..business.services.optimizacion_categorias import OptimizacionCategoriasService
    from ..database.db_connector import DatabaseConnector
except ImportError:
    _src = os.path.dirname(os.path.dirname(__file__))
    if _src not in sys.path:
        sys.path.insert(0, _src)
    from business.services.optimizacion_categorias import OptimizacionCategoriasService  # type: ignore
    from database.db_connector import DatabaseConnector  # type: ignore


# ---------------------------------------------------------------------------
# Colores / constantes de diseño
# ---------------------------------------------------------------------------
_BG     = "#F8F9FA"
_WHITE  = "#FFFFFF"
_BORDER = "#E0E0E0"
_TEXT1  = "#212121"
_TEXT2  = "#616161"
_ACCENT = "#1976D2"
_GREEN  = "#2E7D32"
_AMBER  = "#F57F17"
_RED    = "#C62828"
_CHIP_AUTO   = "#E3F2FD"
_CHIP_CONF   = "#E8F5E9"


class OptimizacionCategoriasView:
    """Vista principal del módulo de Optimización de Categorías."""

    SIDEBAR_INDEX = 18

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.db   = DatabaseConnector()
        self.svc  = OptimizacionCategoriasService(self.db)

        # Detecta usuario activo (placeholder simple)
        self.id_persona: int = self._resolve_user()

        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=self.SIDEBAR_INDEX,
            navigation_callback=self._handle_navigation,
        )

        # Datos (cargados en _load_data)
        self.reglas:        List[Dict] = []
        self.conflictos:    List[Dict] = []
        self.sin_categoria: List[Dict] = []
        self.categorias:    List[Dict] = []
        self.stats:         Dict       = {}

        # Tab activa
        self._active_tab: int = 0

        # Refs de contenedores que se redibujan
        self._tab_content_ref: Optional[ft.Column] = None
        self._stats_row_ref:   Optional[ft.Row]    = None
        self._snack_ref:       Optional[ft.SnackBar] = None

        self._load_data()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _resolve_user(self) -> int:
        rows = self.db.execute_query(
            "SELECT id_persona FROM persona WHERE estado = 1 ORDER BY id_persona DESC LIMIT 1"
        )
        return int(rows[0]["id_persona"]) if rows else 1

    def _handle_navigation(self, route: str, index: int) -> None:
        if route:
            self.page.go(route)

    def _load_data(self) -> None:
        self.reglas        = self.svc.get_reglas(self.id_persona)
        self.conflictos    = self.svc.get_conflictos(self.id_persona)
        self.sin_categoria = self.svc.get_sin_categoria(self.id_persona)
        self.categorias    = self.svc.get_categorias(self.id_persona)
        self.stats         = self.svc.get_stats(self.id_persona)

    def _refresh(self) -> None:
        """Recarga datos y actualiza la UI en el tab activo."""
        self._load_data()
        self._rebuild_tab()
        self._rebuild_stats()
        self.page.update()

    def _show_snack(self, message: str, color: str = _GREEN) -> None:
        if self._snack_ref:
            self._snack_ref.content = ft.Text(message, color="white")
            self._snack_ref.bgcolor = color
            self._snack_ref.open = True
            self.page.update()

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon("home", size=16, color=_TEXT2),
                            ft.Text(" / ", color=_TEXT2),
                            ft.Text("Presupuestos", size=14, color=_TEXT2),
                            ft.Text(" / ", color=_TEXT2),
                            ft.Text(
                                "Optimización de Categorías",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=_TEXT1,
                            ),
                        ],
                        tight=True,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Aplicar reglas",
                                icon="auto_fix_high",
                                bgcolor=_ACCENT,
                                color="white",
                                on_click=self._on_aplicar_reglas,
                                tooltip="Aplica todas las reglas a movimientos sin categoría",
                            ),
                            ft.IconButton(
                                icon="refresh",
                                icon_size=20,
                                tooltip="Actualizar",
                                on_click=lambda _: self._refresh(),
                            ),
                        ],
                        tight=True,
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=_WHITE,
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
        )

    # ------------------------------------------------------------------
    # Tarjetas de estadísticas
    # ------------------------------------------------------------------

    def _stat_card(self, label: str, value: int, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(str(value), size=32, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=13, color=_TEXT2),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=_WHITE,
            border_radius=12,
            border=ft.border.all(1, _BORDER),
            padding=ft.padding.symmetric(horizontal=28, vertical=18),
            expand=True,
            alignment=ft.alignment.center,
        )

    def _build_stats_row(self) -> ft.Row:
        s = self.stats
        row = ft.Row(
            [
                self._stat_card("Reglas disponibles",     s.get("reglas", 0),       _ACCENT),
                self._stat_card("Conflictos pendientes",  s.get("conflictos", 0),   _AMBER),
                self._stat_card("Sin categoría",          s.get("sin_categoria", 0), _RED),
            ],
            spacing=16,
        )
        self._stats_row_ref = row
        return row

    def _rebuild_stats(self) -> None:
        if self._stats_row_ref:
            s = self.stats
            cards = [
                self._stat_card("Reglas disponibles",    s.get("reglas", 0),       _ACCENT),
                self._stat_card("Conflictos pendientes", s.get("conflictos", 0),   _AMBER),
                self._stat_card("Sin categoría",         s.get("sin_categoria", 0), _RED),
            ]
            self._stats_row_ref.controls.clear()
            self._stats_row_ref.controls.extend(cards)

    # ------------------------------------------------------------------
    # Tab 1 — Reglas
    # ------------------------------------------------------------------

    def _build_tab_reglas(self) -> ft.Control:
        if not self.reglas:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("rule", size=48, color="#BDBDBD"),
                        ft.Text(
                            "Sin reglas disponibles.",
                            color=_TEXT2, size=15
                        ),
                        ft.Text(
                            "Categoriza algunos movimientos para que el sistema aprenda.",
                            color=_TEXT2, size=13,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=48,
            )

        headers = ["Concepto", "Categoría", "Movimientos", "Origen", "Acciones"]
        rows: List[ft.DataRow] = []
        for r in self.reglas:
            fuente_chip = ft.Container(
                content=ft.Text(
                    "Confirmada" if r["fuente"] == "confirmada" else "Automática",
                    size=12,
                    color=_GREEN if r["fuente"] == "confirmada" else _ACCENT,
                    weight=ft.FontWeight.W_500,
                ),
                bgcolor=_CHIP_CONF if r["fuente"] == "confirmada" else _CHIP_AUTO,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=3),
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["concepto"] or "—", size=13)),
                        ft.DataCell(ft.Text(r["nombre_categoria"] or "—", size=13)),
                        ft.DataCell(ft.Text(str(r["total_movimientos"]), size=13)),
                        ft.DataCell(fuente_chip),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Confirmar",
                                        icon="check_circle_outline",
                                        style=ft.ButtonStyle(color=_GREEN),
                                        on_click=lambda e, reg=r: self._on_confirmar_regla(reg),
                                        tooltip="Guardar como regla permanente",
                                    ),
                                    ft.TextButton(
                                        "Limpiar",
                                        icon="delete_outline",
                                        style=ft.ButtonStyle(color=_RED),
                                        on_click=lambda e, reg=r: self._on_limpiar_regla(reg),
                                        tooltip="Eliminar regla confirmada",
                                        disabled=(r["fuente"] != "confirmada"),
                                    ),
                                ],
                                tight=True,
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        return ft.Column(
            [
                ft.Text(
                    f"Reglas de categorización ({len(self.reglas)})",
                    size=16, weight=ft.FontWeight.BOLD, color=_TEXT1,
                ),
                ft.Text(
                    "Conceptos que siempre se han asociado a la misma categoría "
                    "o que has confirmado manualmente.",
                    size=13, color=_TEXT2,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD))
                            for h in headers
                        ],
                        rows=rows,
                        column_spacing=20,
                        horizontal_lines=ft.BorderSide(1, _BORDER),
                        heading_row_color={"default": "#F5F5F5"},
                    ),
                    bgcolor=_WHITE,
                    border_radius=12,
                    border=ft.border.all(1, _BORDER),
                    padding=0,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
            ],
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------
    # Tab 2 — Conflictos
    # ------------------------------------------------------------------

    def _build_tab_conflictos(self) -> ft.Control:
        if not self.conflictos:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("check_circle", size=48, color=_GREEN),
                        ft.Text("¡Sin conflictos!", color=_TEXT2, size=15),
                        ft.Text(
                            "Todos los conceptos tienen una categoría única o regla definida.",
                            color=_TEXT2, size=13,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=48,
            )

        cat_options = [
            ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
            for c in self.categorias
        ]

        cards: List[ft.Control] = []
        for c in self.conflictos:
            concepto = c["concepto"]
            dd = ft.Dropdown(
                options=cat_options,
                hint_text="Elegir categoría",
                width=260,
                text_size=13,
            )

            def _make_resolver(con: str, dropdown: ft.Dropdown):
                def handler(e):
                    if not dropdown.value:
                        self._show_snack("Selecciona una categoría primero", _AMBER)
                        return
                    ok = self.svc.confirmar_regla(con, int(dropdown.value), self.id_persona)
                    if ok:
                        self._show_snack(f"Regla guardada para «{con}»")
                        self._refresh()
                    else:
                        self._show_snack("Error al guardar la regla", _RED)
                return handler

            def _make_ignorar(con: str):
                def handler(e):
                    self.svc.ignorar_concepto(con, self.id_persona)
                    self._show_snack(f"«{con}» marcado como ignorado")
                    self._refresh()
                return handler

            cat_chips = ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            f"{cat['nombre']} ({cat['total']})",
                            size=12, color=_TEXT1,
                        ),
                        bgcolor="#FFF8E1",
                        border_radius=12,
                        padding=ft.padding.symmetric(horizontal=10, vertical=3),
                    )
                    for cat in c["categorias"]
                ],
                wrap=True,
                spacing=6,
            )

            cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon("warning_amber", color=_AMBER, size=18),
                                    ft.Text(
                                        concepto, size=14,
                                        weight=ft.FontWeight.BOLD, color=_TEXT1,
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Text(
                                "Este concepto ha sido categorizado de distintas formas:",
                                size=12, color=_TEXT2,
                            ),
                            cat_chips,
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    dd,
                                    ft.ElevatedButton(
                                        "Confirmar",
                                        icon="check",
                                        bgcolor=_ACCENT,
                                        color="white",
                                        on_click=_make_resolver(concepto, dd),
                                    ),
                                    ft.OutlinedButton(
                                        "Ignorar siempre",
                                        icon="block",
                                        on_click=_make_ignorar(concepto),
                                        tooltip="No auto-clasificar nunca este concepto",
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=6,
                    ),
                    bgcolor=_WHITE,
                    border_radius=12,
                    border=ft.border.all(1, _BORDER),
                    padding=16,
                )
            )

        return ft.Column(
            [
                ft.Text(
                    f"Conflictos de categorización ({len(self.conflictos)})",
                    size=16, weight=ft.FontWeight.BOLD, color=_TEXT1,
                ),
                ft.Text(
                    "Elige la categoría correcta para cada concepto ambiguo.",
                    size=13, color=_TEXT2,
                ),
                ft.Container(height=8),
                *cards,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------
    # Tab 3 — Sin categoría
    # ------------------------------------------------------------------

    def _build_tab_sin_categoria(self) -> ft.Control:
        if not self.sin_categoria:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon("check_circle", size=48, color=_GREEN),
                        ft.Text("Todos los movimientos tienen categoría.", color=_TEXT2, size=15),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=48,
            )

        cat_options = [
            ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
            for c in self.categorias
        ]

        headers = ["Fecha", "Concepto", "Valor", "Asignar categoría", ""]
        rows: List[ft.DataRow] = []
        for m in self.sin_categoria:
            dd = ft.Dropdown(
                options=cat_options,
                hint_text="Categoría...",
                width=200,
                text_size=12,
            )

            def _make_asignar(mov: Dict, dropdown: ft.Dropdown):
                def handler(e):
                    if not dropdown.value:
                        self._show_snack("Selecciona una categoría", _AMBER)
                        return
                    ok = self.svc.asignar_categoria_movimiento(
                        mov["id_movimiento_tarjeta"], int(dropdown.value), self.id_persona
                    )
                    if ok:
                        self._show_snack("Categoría asignada")
                        self._refresh()
                    else:
                        self._show_snack("Error al asignar", _RED)
                return handler

            fecha_txt = str(m.get("fecha", "—"))
            valor_txt = f"${float(m.get('valor', 0)):,.0f}"
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(fecha_txt, size=13)),
                        ft.DataCell(ft.Text(m.get("concepto") or "—", size=13)),
                        ft.DataCell(ft.Text(valor_txt, size=13, color=_RED)),
                        ft.DataCell(dd),
                        ft.DataCell(
                            ft.IconButton(
                                icon="check_circle",
                                icon_color=_GREEN,
                                tooltip="Asignar",
                                on_click=_make_asignar(m, dd),
                            )
                        ),
                    ]
                )
            )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"Movimientos sin categoría ({len(self.sin_categoria)})",
                            size=16, weight=ft.FontWeight.BOLD, color=_TEXT1,
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Aplicar reglas automáticas",
                            icon="auto_fix_high",
                            bgcolor=_ACCENT,
                            color="white",
                            on_click=self._on_aplicar_reglas,
                        ),
                    ]
                ),
                ft.Text(
                    "Asigna la categoría correcta a cada movimiento.",
                    size=13, color=_TEXT2,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD))
                            for h in headers
                        ],
                        rows=rows,
                        column_spacing=16,
                        horizontal_lines=ft.BorderSide(1, _BORDER),
                        heading_row_color={"default": "#F5F5F5"},
                    ),
                    bgcolor=_WHITE,
                    border_radius=12,
                    border=ft.border.all(1, _BORDER),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
            ],
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _tab_button(self, label: str, icon: str, index: int) -> ft.Container:
        is_active = self._active_tab == index

        def on_click(e, idx=index):
            self._active_tab = idx
            self._rebuild_top_tabs()
            self._rebuild_tab()
            self.page.update()

        return ft.Container(
            content=ft.Row(
                [ft.Icon(icon, size=16, color=_ACCENT if is_active else _TEXT2),
                 ft.Text(label, size=13, color=_ACCENT if is_active else _TEXT2,
                         weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL)],
                tight=True, spacing=6,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(2, _ACCENT if is_active else "transparent")),
            on_click=on_click,
            ink=True,
        )

    def _build_top_tabs(self) -> ft.Row:
        row = ft.Row(
            [
                self._tab_button("Reglas", "rule", 0),
                self._tab_button(
                    f"Conflictos ({len(self.conflictos)})", "warning_amber", 1
                ),
                self._tab_button(
                    f"Sin categoría ({len(self.sin_categoria)})", "help_outline", 2
                ),
            ],
            spacing=0,
        )
        self._top_tabs_row = row
        return row

    def _rebuild_top_tabs(self) -> None:
        if hasattr(self, "_top_tabs_row"):
            new = self._build_top_tabs()
            self._top_tabs_row.controls = new.controls

    def _build_tab_content(self) -> ft.Column:
        mapping = {
            0: self._build_tab_reglas,
            1: self._build_tab_conflictos,
            2: self._build_tab_sin_categoria,
        }
        col = ft.Column(
            [mapping[self._active_tab]()],
            expand=True,
        )
        self._tab_content_ref = col
        return col

    def _rebuild_tab(self) -> None:
        if self._tab_content_ref is None:
            return
        mapping = {
            0: self._build_tab_reglas,
            1: self._build_tab_conflictos,
            2: self._build_tab_sin_categoria,
        }
        self._tab_content_ref.controls = [mapping[self._active_tab]()]

    # ------------------------------------------------------------------
    # Handlers de acciones
    # ------------------------------------------------------------------

    def _on_aplicar_reglas(self, e) -> None:
        n = self.svc.aplicar_reglas(self.id_persona)
        self._show_snack(
            f"Se actualizaron {n} movimiento(s) con las reglas." if n > 0
            else "No hay movimientos que actualizar."
        )
        self._refresh()

    def _on_confirmar_regla(self, regla: Dict) -> None:
        ok = self.svc.confirmar_regla(
            regla["concepto"], regla["id_categoria"], self.id_persona
        )
        if ok:
            self._show_snack(f"Regla confirmada para «{regla['concepto']}»")
            self._refresh()
        else:
            self._show_snack("Error al confirmar la regla", _RED)

    def _on_limpiar_regla(self, regla: Dict) -> None:
        ok = self.svc.limpiar_regla(regla["concepto"], self.id_persona)
        if ok:
            self._show_snack(f"Regla eliminada para «{regla['concepto']}»")
            self._refresh()
        else:
            self._show_snack("No hay regla confirmada para limpiar", _AMBER)

    # ------------------------------------------------------------------
    # Build principal
    # ------------------------------------------------------------------

    def _build_main_content(self) -> ft.Container:
        snack = ft.SnackBar(content=ft.Text(""), bgcolor=_GREEN)
        self._snack_ref = snack
        self.page.overlay.append(snack)

        top_tabs = self._build_top_tabs()

        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Container(
                        content=ft.Column(
                            [
                                # Título
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Optimización de Categorías",
                                                size=26,
                                                weight=ft.FontWeight.BOLD,
                                                color=_TEXT1,
                                            ),
                                            ft.Text(
                                                "Automatiza la clasificación de tus gastos en base al historial.",
                                                size=14, color=_TEXT2,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                    margin=ft.margin.only(bottom=16),
                                ),
                                # Stats
                                self._build_stats_row(),
                                ft.Container(height=12),
                                # Tabs barra
                                ft.Container(
                                    content=top_tabs,
                                    bgcolor=_WHITE,
                                    border_radius=ft.border_radius.only(
                                        top_left=12, top_right=12
                                    ),
                                    border=ft.border.only(
                                        bottom=ft.BorderSide(1, _BORDER)
                                    ),
                                    padding=ft.padding.only(left=8),
                                ),
                                # Contenido del tab
                                ft.Container(
                                    content=self._build_tab_content(),
                                    bgcolor=_WHITE,
                                    border_radius=ft.border_radius.only(
                                        bottom_left=12, bottom_right=12
                                    ),
                                    border=ft.border.only(
                                        left=ft.BorderSide(1, _BORDER),
                                        right=ft.BorderSide(1, _BORDER),
                                        bottom=ft.BorderSide(1, _BORDER),
                                    ),
                                    padding=20,
                                    expand=True,
                                ),
                            ],
                            spacing=0,
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                        padding=24,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    self.sidebar_menu.create_sidebar(),
                    ft.Container(
                        content=self._build_main_content(),
                        expand=True,
                        bgcolor=_BG,
                    ),
                ],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def optimizacion_categorias_view(page: ft.Page) -> ft.View:
    """Retorna ft.View lista para ser añadida al router de main.py."""
    view_obj = OptimizacionCategoriasView(page)
    return ft.View(
        route="/optimizacion-categorias",
        controls=[view_obj.build()],
        padding=0,
        spacing=0,
    )


if __name__ == "__main__":
    ft.app(target=lambda page: page.go("/optimizacion-categorias"))
