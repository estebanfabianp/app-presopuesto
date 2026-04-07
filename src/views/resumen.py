"""
Vista principal financiera (Resumen).

Implementa:
- Encabezado con breadcrumbs y acciones
- Tarjetas KPI
- Tablas de productos financieros
- Visualizacion comparativa Ingresos vs Gastos con componentes Flet
- Layout responsivo de dos columnas
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from typing import Any, Dict, List

import flet as ft
import pandas as pd

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    create_sidebar_menu = None

try:
    from ..business.services.producto_controller import (
        obtener_productos_por_usuario,
        obtener_resumen_productos_por_usuario,
    )
except ImportError:
    src_path = os.path.dirname(os.path.dirname(__file__))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from business.services.producto_controller import (  # type: ignore
        obtener_productos_por_usuario,
        obtener_resumen_productos_por_usuario,
    )


class ResumenView:
    """Vista principal financiera con layout responsivo y datos tabulares limpios."""

    def __init__(self, page: ft.Page, user_id: int = 1) -> None:
        self.page = page
        self.user_id = user_id
        self.resumen_productos: Dict[str, Any] = {}
        self.productos_df = pd.DataFrame()

        self.sidebar_menu = None
        if create_sidebar_menu:
            self.sidebar_menu = create_sidebar_menu(
                page=page,
                selected_index=1,
                navigation_callback=self.handle_navigation,
            )

        self._load_data()

    def handle_navigation(self, route: str, _index: int) -> None:
        if route:
            self.page.go(route)

    def _load_data(self) -> None:
        """Carga datos desde el controlador y normaliza productos en DataFrame."""
        try:
            productos = obtener_productos_por_usuario(self.user_id)
            self.resumen_productos = obtener_resumen_productos_por_usuario(self.user_id)
        except Exception:
            productos = []
            self.resumen_productos = {}

        self.productos_df = self._normalize_products_df(productos)

    def _normalize_products_df(self, productos: List[Dict[str, Any]]) -> pd.DataFrame:
        base_columns = [
            "nombre",
            "tipo_producto",
            "tipo_display",
            "saldo_actual",
            "saldo_disponible",
            "limite_credito",
            "tasa_interes",
        ]

        if not productos:
            return pd.DataFrame(columns=base_columns)

        df = pd.DataFrame(productos)
        for col in base_columns:
            if col not in df.columns:
                df[col] = 0 if col in {"saldo_actual", "saldo_disponible", "limite_credito", "tasa_interes"} else ""

        for col in ["saldo_actual", "saldo_disponible", "limite_credito", "tasa_interes"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        df["nombre"] = df["nombre"].fillna("Producto")
        df["tipo_producto"] = df["tipo_producto"].fillna("")
        df["tipo_display"] = df["tipo_display"].fillna(df["tipo_producto"])
        return df[base_columns]

    def _money(self, value: float) -> str:
        return f"${value:,.2f}"

    def _totals(self) -> Dict[str, float]:
        """Calcula totales por tipo en base al DataFrame."""
        df = self.productos_df
        if df.empty:
            return {
                "cuentas": 0.0,
                "tarjetas_usado": 0.0,
                "prestamos": 0.0,
                "fondos": 0.0,
            }

        cuentas = df.loc[df["tipo_producto"] == "cuenta_bancaria", "saldo_actual"].sum()
        fondos = df.loc[df["tipo_producto"] == "fondo_inversion", "saldo_actual"].sum()
        prestamos = df.loc[df["tipo_producto"] == "prestamo", "saldo_actual"].abs().sum()

        df_tc = df.loc[df["tipo_producto"] == "tarjeta_credito"].copy()
        if df_tc.empty:
            tarjetas_usado = 0.0
        else:
            tarjetas_usado = (df_tc["limite_credito"] - df_tc["saldo_disponible"]).clip(lower=0).sum()

        return {
            "cuentas": float(cuentas),
            "tarjetas_usado": float(tarjetas_usado),
            "prestamos": float(prestamos),
            "fondos": float(fondos),
        }

    def _kpi_values(self) -> Dict[str, float]:
        totals = self._totals()

        ingresos_mes = (totals["cuentas"] * 0.002) + (totals["fondos"] * 0.012)
        gastos_mes = (totals["tarjetas_usado"] * 0.05) + (totals["prestamos"] * 0.03)
        pagos_pendientes = (totals["tarjetas_usado"] * 0.15) + (totals["prestamos"] * 0.08)
        saldo_total = (totals["cuentas"] + totals["fondos"]) - (totals["tarjetas_usado"] + totals["prestamos"])

        return {
            "ingresos_mes": float(max(0, ingresos_mes)),
            "gastos_mes": float(max(0, gastos_mes)),
            "pagos_pendientes": float(max(0, pagos_pendientes)),
            "saldo_total": float(saldo_total),
        }

    def _build_header(self) -> ft.Container:
        return ft.Container(
            bgcolor="white",
            border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB")),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.HOME_ROUNDED, size=16, color="#6B7280"),
                            ft.Text("/", color="#9CA3AF"),
                            ft.Text("Panel financiero", weight=ft.FontWeight.W_600, color="#111827"),
                        ],
                        tight=True,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.REFRESH_ROUNDED, tooltip="Actualizar", on_click=lambda e: self.refresh_data()),
                            ft.IconButton(icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED, tooltip="Notificaciones"),
                            ft.IconButton(icon=ft.Icons.HELP_OUTLINE_ROUNDED, tooltip="Ayuda"),
                        ],
                        spacing=4,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _build_kpi_card(self, title: str, amount: float, icon: str, color: str) -> ft.Container:
        return ft.Container(
            col={"xs": 12, "sm": 6, "lg": 3},
            bgcolor="white",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=14,
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=36,
                                height=36,
                                border_radius=10,
                                bgcolor=f"{color}22",
                                alignment=ft.alignment.center,
                                content=ft.Icon(icon, size=18, color=color),
                            ),
                            ft.Container(expand=True),
                            ft.Text(title, size=12, color="#6B7280"),
                        ]
                    ),
                    ft.Text(self._money(amount), size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                ],
                spacing=10,
            ),
        )

    def _build_kpi_section(self) -> ft.ResponsiveRow:
        kpi = self._kpi_values()
        return ft.ResponsiveRow(
            controls=[
                self._build_kpi_card("Ingresos (mes)", kpi["ingresos_mes"], ft.Icons.ARROW_UPWARD_ROUNDED, "#16A34A"),
                self._build_kpi_card("Gastos (mes)", kpi["gastos_mes"], ft.Icons.ARROW_DOWNWARD_ROUNDED, "#DC2626"),
                self._build_kpi_card("Pagos pendientes", kpi["pagos_pendientes"], ft.Icons.PENDING_ACTIONS_ROUNDED, "#D97706"),
                self._build_kpi_card("Saldo total", kpi["saldo_total"], ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "#2563EB"),
            ],
            run_spacing=12,
            spacing=12,
        )

    def _table_rows_for(self, tipo: str, extra_cols: List[str]) -> List[ft.DataRow]:
        df = self.productos_df.loc[self.productos_df["tipo_producto"] == tipo].copy()
        if df.empty:
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Sin registros", color="#6B7280")),
                        ft.DataCell(ft.Text("--", color="#6B7280")),
                        ft.DataCell(ft.Text("--", color="#6B7280")),
                    ]
                )
            ]

        rows: List[ft.DataRow] = []
        for _, row in df.iterrows():
            cells: List[ft.DataCell] = [
                ft.DataCell(ft.Text(str(row["nombre"]))),
                ft.DataCell(ft.Text(self._money(float(row["saldo_actual"])))),
            ]
            for col in extra_cols:
                value = float(row[col]) if col in row else 0.0
                cells.append(ft.DataCell(ft.Text(self._money(value))))
            rows.append(ft.DataRow(cells=cells))
        return rows

    def _build_product_table(self, title: str, tipo: str, extra_cols: List[str], extra_titles: List[str], icon: str) -> ft.Container:
        columns = [
            ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Saldo actual", weight=ft.FontWeight.BOLD)),
        ]
        for extra_title in extra_titles:
            columns.append(ft.DataColumn(ft.Text(extra_title, weight=ft.FontWeight.BOLD)))

        return ft.Container(
            margin=ft.margin.only(bottom=14),
            padding=16,
            bgcolor="white",
            border_radius=14,
            border=ft.border.all(1, "#E5E7EB"),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, size=18, color="#2563EB"),
                            ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#111827"),
                        ],
                        spacing=8,
                    ),
                    ft.DataTable(
                        columns=columns,
                        rows=self._table_rows_for(tipo, extra_cols),
                        heading_row_color="#F3F4F6",
                        heading_row_height=44,
                        data_row_min_height=42,
                        border=ft.border.all(1, "#E5E7EB"),
                        border_radius=8,
                        horizontal_lines=ft.BorderSide(1, "#F3F4F6"),
                        vertical_lines=ft.BorderSide(1, "#F3F4F6"),
                        column_spacing=20,
                    ),
                ],
                spacing=10,
            ),
        )

    def _build_products_section(self) -> ft.Column:
        return ft.Column(
            controls=[
                self._build_product_table(
                    title="Tarjetas de credito",
                    tipo="tarjeta_credito",
                    extra_cols=["saldo_disponible"],
                    extra_titles=["Saldo disponible"],
                    icon=ft.Icons.CREDIT_CARD_ROUNDED,
                ),
                self._build_product_table(
                    title="Cuentas de ahorro",
                    tipo="cuenta_bancaria",
                    extra_cols=["saldo_disponible"],
                    extra_titles=["Saldo disponible"],
                    icon=ft.Icons.ACCOUNT_BALANCE_ROUNDED,
                ),
                self._build_product_table(
                    title="Prestamos",
                    tipo="prestamo",
                    extra_cols=["tasa_interes"],
                    extra_titles=["Tasa (%)"],
                    icon=ft.Icons.TRENDING_DOWN_ROUNDED,
                ),
                self._build_product_table(
                    title="Fondos de inversion",
                    tipo="fondo_inversion",
                    extra_cols=["tasa_interes"],
                    extra_titles=["Tasa (%)"],
                    icon=ft.Icons.SHOW_CHART_ROUNDED,
                ),
            ],
            spacing=0,
        )

    def _build_cashflow_df(self) -> pd.DataFrame:
        """Genera serie mensual para comparativo de ingresos vs gastos."""
        kpi = self._kpi_values()
        base_ing = max(kpi["ingresos_mes"], 1.0)
        base_gas = max(kpi["gastos_mes"], 1.0)

        months: List[str] = []
        ingresos: List[float] = []
        gastos: List[float] = []

        now = dt.date.today().replace(day=1)
        factors_ing = [0.80, 0.92, 1.00, 1.08, 0.98, 1.12]
        factors_gas = [0.85, 0.95, 1.02, 1.06, 1.00, 1.10]

        for idx in range(6):
            d = (now - pd.DateOffset(months=5 - idx)).date()
            months.append(d.strftime("%b"))
            ingresos.append(base_ing * factors_ing[idx])
            gastos.append(base_gas * factors_gas[idx])

        return pd.DataFrame({"mes": months, "ingresos": ingresos, "gastos": gastos})

    def _build_income_vs_expense_chart(self) -> ft.Container:
        """Grafico comparativo en Flet usando barras custom con contenedores."""
        df = self._build_cashflow_df()
        max_value = float(max(df["ingresos"].max(), df["gastos"].max(), 1))

        bars: List[ft.Control] = []
        for _, row in df.iterrows():
            h_ing = int((float(row["ingresos"]) / max_value) * 160)
            h_gas = int((float(row["gastos"]) / max_value) * 160)
            bars.append(
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(width=14, height=h_ing, bgcolor="#16A34A", border_radius=4),
                                ft.Container(width=6),
                                ft.Container(width=14, height=h_gas, bgcolor="#DC2626", border_radius=4),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                        ),
                        ft.Text(str(row["mes"]), size=11, color="#6B7280"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                )
            )

        legend = ft.Row(
            controls=[
                ft.Row([ft.Container(width=10, height=10, bgcolor="#16A34A", border_radius=2), ft.Text("Ingresos", size=12)], tight=True),
                ft.Row([ft.Container(width=10, height=10, bgcolor="#DC2626", border_radius=2), ft.Text("Gastos", size=12)], tight=True),
            ],
            spacing=16,
        )

        return ft.Container(
            bgcolor="white",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=14,
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Text("Ingresos vs Gastos", size=18, weight=ft.FontWeight.W_600, color="#111827"),
                    legend,
                    ft.Container(height=8),
                    ft.Row(controls=bars, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ],
                spacing=8,
            ),
        )

    def refresh_data(self) -> None:
        self._load_data()
        self.page.go(self.page.route)

    def build(self) -> ft.Container:
        content = ft.Container(
            expand=True,
            bgcolor="#F8FAFC",
            content=ft.Column(
                controls=[
                    self._build_header(),
                    ft.Container(
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=20, vertical=16),
                        content=ft.Column(
                            controls=[
                                ft.Text("Vista principal financiera", size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                                ft.Text(
                                    f"Actualizado: {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                    size=12,
                                    color="#6B7280",
                                ),
                                ft.Container(height=4),
                                self._build_kpi_section(),
                                ft.Container(height=8),
                                ft.ResponsiveRow(
                                    controls=[
                                        ft.Container(col={"xs": 12, "md": 8}, content=self._build_products_section()),
                                        ft.Container(col={"xs": 12, "md": 4}, content=self._build_income_vs_expense_chart()),
                                    ],
                                    run_spacing=14,
                                    spacing=14,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                ),
                            ],
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                ],
                spacing=0,
            ),
        )

        if self.sidebar_menu:
            return ft.Container(
                expand=True,
                content=ft.Row(
                    controls=[
                        self.sidebar_menu.create_sidebar(),
                        content,
                    ],
                    spacing=0,
                    expand=True,
                ),
            )

        return content


def resumen_view(page: ft.Page, user_id: int = 1) -> ft.View:
    view = ResumenView(page, user_id=user_id)
    return ft.View(route="/resumen", controls=[view.build()], padding=0, spacing=0)


def main(page: ft.Page) -> None:
    page.title = "App Presupuesto - Resumen"
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 1000
    page.window.min_height = 700
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(resumen_view(page))


if __name__ == "__main__":
    ft.app(target=main)
