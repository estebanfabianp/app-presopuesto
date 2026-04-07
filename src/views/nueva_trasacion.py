"""Vista de registro de transacciones con carga individual y masiva desde Excel."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, List

import flet as ft
import pandas as pd

try:
    from ..database.db_connector import DatabaseConnector
except ImportError:
    from database.db_connector import DatabaseConnector

try:
    from .sidebar import create_sidebar_menu
except ImportError:
    from sidebar import create_sidebar_menu

try:
    from ..business.services.etl_tarjeta_credito import ETLTarjetaCredito, validate_excel_file
except ImportError:
    from business.services.etl_tarjeta_credito import ETLTarjetaCredito, validate_excel_file


class NuevaTransaccionView(ft.View):
    """Vista principal para registrar transacciones financieras."""

    def __init__(self, page: ft.Page) -> None:
        super().__init__(route="/transacciones/nueva", padding=0, spacing=0)
        self.page = page
        self._picker_mode = ""
        self.grid_rows: List[Dict[str, Any]] = []
        self._active_user_id: int | None = None

        self.sidebar_menu = create_sidebar_menu(
            page=page,
            selected_index=2,
            navigation_callback=self.handle_navigation,
        )

        self.file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)

        # Configuracion para carga masiva por origen de pago
        self.massive_mode_group = ft.RadioGroup(
            value="cuenta_bancaria",
            on_change=self._on_massive_mode_change,
            content=ft.Row(
                [
                    ft.Radio(value="cuenta_bancaria", label="Carga a Cuenta Bancaria"),
                    ft.Radio(value="tarjeta_credito", label="Carga a Tarjeta de Crédito"),
                ],
                spacing=20,
            ),
        )
        self.account_dropdown = ft.Dropdown(label="Selecciona cuenta bancaria", width=330)
        self.card_dropdown = ft.Dropdown(label="Selecciona tarjeta de crédito", width=330, disabled=True)

        # Formulario individual
        self.concepto_input = ft.TextField(label="Concepto", width=420)
        self.monto_input = ft.TextField(label="Monto", width=180, on_change=lambda e: self._sanitize_decimal(self.monto_input))
        self.categoria_input = ft.TextField(label="Categoría", width=200)
        self.medio_pago_input = ft.Dropdown(
            label="Medio de pago",
            width=200,
            value="Cuenta",
            options=[
                ft.dropdown.Option("Cuenta"),
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Tarjeta de crédito"),
            ],
            on_change=self._on_form_payment_change,
        )
        self.cuotas_input = ft.TextField(
            label="Nro. cuotas",
            width=140,
            value="1",
            disabled=True,
            on_change=lambda e: self._sanitize_integer(self.cuotas_input, min_value=1, max_value=36),
        )

        self.status_text = ft.Text(value="", size=12)
        self.table_container = ft.Container()

        self._load_payment_sources()

        self._add_empty_row()
        self._refresh_table()

        self.controls = [self._build_layout()]

    def handle_navigation(self, route: str, index: int) -> None:
        if route == "/login":
            self.page.go("/login")
        elif route:
            self.page.go(route)

    def _load_payment_sources(self) -> None:
        """Carga cuentas y tarjetas del usuario activo para carga masiva."""
        db = DatabaseConnector()
        if not db.conn:
            self._show_message("No se pudo cargar cuentas/tarjetas (sin conexión BD).", ft.Colors.RED_600)
            return

        try:
            user_rows = db.execute_query(
                """
                SELECT id_persona
                FROM persona
                WHERE estado = 1
                ORDER BY COALESCE(fecha_actualizacion, fecha_creacion) DESC, id_persona DESC
                LIMIT 1
                """
            )
            if not user_rows:
                return

            self._active_user_id = int(user_rows[0]["id_persona"])

            account_rows = db.execute_query(
                "SELECT id_cuenta, nombre FROM cuenta WHERE id_persona = %s ORDER BY id_cuenta",
                (self._active_user_id,),
            )
            account_options = [
                ft.dropdown.Option(str(r["id_cuenta"]), f"#{r['id_cuenta']} - {r['nombre']}")
                for r in account_rows
            ]
            self.account_dropdown.options = account_options
            if account_options:
                self.account_dropdown.value = account_options[0].key

            card_rows = db.execute_query(
                """
                SELECT tc.id_tarjeta, tc.numero_tarjeta
                FROM tarjeta_credito tc
                WHERE EXISTS (
                    SELECT 1
                    FROM movimiento_tarjeta mt
                    WHERE mt.id_tarjeta = tc.id_tarjeta AND mt.id_persona = %s
                )
                ORDER BY tc.id_tarjeta
                """,
                (self._active_user_id,),
            )
            card_options = [
                ft.dropdown.Option(
                    str(r["id_tarjeta"]),
                    f"#{r['id_tarjeta']} - ****{str(r['numero_tarjeta'])[-4:] if r['numero_tarjeta'] else '----'}",
                )
                for r in card_rows
            ]
            self.card_dropdown.options = card_options
            if card_options:
                self.card_dropdown.value = card_options[0].key

        finally:
            db.close()

    def _on_massive_mode_change(self, e: ft.ControlEvent) -> None:
        is_account = self.massive_mode_group.value == "cuenta_bancaria"
        self.account_dropdown.disabled = not is_account
        self.card_dropdown.disabled = is_account
        self.page.update()

    def _show_message(self, message: str, color: str = ft.Colors.BLUE_700) -> None:
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()

    def _sanitize_decimal(self, field: ft.TextField) -> None:
        raw = (field.value or "").replace(",", ".")
        cleaned = ""
        dot_used = False
        for ch in raw:
            if ch.isdigit():
                cleaned += ch
            elif ch == "." and not dot_used:
                cleaned += ch
                dot_used = True
        field.value = cleaned

    def _sanitize_integer(self, field: ft.TextField, min_value: int | None = None, max_value: int | None = None) -> None:
        digits = "".join(ch for ch in (field.value or "") if ch.isdigit())
        if digits:
            value = int(digits)
            if min_value is not None:
                value = max(min_value, value)
            if max_value is not None:
                value = min(max_value, value)
            field.value = str(value)
        else:
            field.value = ""

    def _on_form_payment_change(self, e: ft.ControlEvent) -> None:
        is_credit = self.medio_pago_input.value == "Tarjeta de crédito"
        self.cuotas_input.disabled = not is_credit
        if not is_credit:
            self.cuotas_input.value = "1"
        self.page.update()

    def _on_grid_payment_change(self, row: Dict[str, Any]) -> None:
        is_credit = row["medio_pago"].value == "Tarjeta de crédito"
        row["cuotas"].disabled = not is_credit
        if not is_credit:
            row["cuotas"].value = "1"
        self.page.update()

    def _create_grid_row(self, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        data = data or {}
        row: Dict[str, Any] = {
            "concepto": ft.TextField(value=str(data.get("concepto", "")), border=ft.InputBorder.NONE),
            "monto": ft.TextField(value=str(data.get("monto", "")), border=ft.InputBorder.NONE),
            "categoria": ft.TextField(value=str(data.get("categoria", "")), border=ft.InputBorder.NONE),
            "medio_pago": ft.Dropdown(
                value=str(data.get("medio_pago", "Cuenta")),
                border=ft.InputBorder.NONE,
                options=[
                    ft.dropdown.Option("Cuenta"),
                    ft.dropdown.Option("Efectivo"),
                    ft.dropdown.Option("Tarjeta de crédito"),
                ],
            ),
            "cuotas": ft.TextField(value=str(data.get("cuotas", "1")), border=ft.InputBorder.NONE),
            "id_cuenta_override": data.get("id_cuenta_override"),
            "id_tarjeta_override": data.get("id_tarjeta_override"),
        }

        row["monto"].on_change = lambda e: self._sanitize_decimal(row["monto"])
        row["cuotas"].on_change = lambda e: self._sanitize_integer(row["cuotas"], min_value=1, max_value=36)
        row["medio_pago"].on_change = lambda e: self._on_grid_payment_change(row)

        self._on_grid_payment_change(row)
        return row

    def _add_empty_row(self, e: ft.ControlEvent | None = None) -> None:
        self.grid_rows.append(self._create_grid_row())

    def _add_row_from_form(self, e: ft.ControlEvent) -> None:
        data = {
            "concepto": self.concepto_input.value or "",
            "monto": self.monto_input.value or "",
            "categoria": self.categoria_input.value or "",
            "medio_pago": self.medio_pago_input.value or "Cuenta",
            "cuotas": self.cuotas_input.value or "1",
        }

        if not data["concepto"]:
            self._show_message("Debes ingresar un concepto para agregar la fila.", ft.Colors.RED_600)
            return

        self.grid_rows.append(self._create_grid_row(data))
        self.concepto_input.value = ""
        self.monto_input.value = ""
        self.categoria_input.value = ""
        self.medio_pago_input.value = "Cuenta"
        self.cuotas_input.value = "1"
        self.cuotas_input.disabled = True
        self._refresh_table()
        self._show_message("Fila agregada correctamente.", ft.Colors.GREEN_700)

    def _remove_row(self, index: int) -> None:
        if 0 <= index < len(self.grid_rows):
            self.grid_rows.pop(index)
            if not self.grid_rows:
                self._add_empty_row()
            self._refresh_table()

    def _refresh_table(self) -> None:
        rows: List[ft.DataRow] = []
        for idx, row in enumerate(self.grid_rows):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(row["concepto"]),
                        ft.DataCell(row["monto"]),
                        ft.DataCell(row["categoria"]),
                        ft.DataCell(row["medio_pago"]),
                        ft.DataCell(row["cuotas"]),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_500,
                                tooltip="Eliminar fila",
                                on_click=lambda e, i=idx: self._remove_row(i),
                            )
                        ),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Concepto")),
                ft.DataColumn(ft.Text("Monto")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Medio")),
                ft.DataColumn(ft.Text("Cuotas")),
                ft.DataColumn(ft.Text("Acción")),
            ],
            rows=rows,
            border=ft.border.all(1, "#E0E0E0"),
            border_radius=10,
            horizontal_lines=ft.BorderSide(1, "#F0F0F0"),
            vertical_lines=ft.BorderSide(1, "#F0F0F0"),
            column_spacing=16,
            heading_row_color="#F8F9FA",
        )
        self.table_container.content = ft.Container(content=table, padding=8, bgcolor="white", border_radius=12)
        self.page.update()

    def _on_file_picker_result(self, e: ft.FilePickerResultEvent) -> None:
        if self._picker_mode == "load":
            if not e.files:
                return
            file_path = Path(e.files[0].path)
            
            selected_mode = self.massive_mode_group.value or "cuenta_bancaria"
            
            # Validar que se haya seleccionado cuenta/tarjeta
            if selected_mode == "cuenta_bancaria" and not self.account_dropdown.value:
                self._show_message("Debes seleccionar una cuenta bancaria para la carga masiva.", ft.Colors.RED_600)
                return
            if selected_mode == "tarjeta_credito" and not self.card_dropdown.value:
                self._show_message("Debes seleccionar una tarjeta de crédito para la carga masiva.", ft.Colors.RED_600)
                return
            
            # Para tarjeta de crédito, usar ETL
            if selected_mode == "tarjeta_credito":
                self._load_excel_with_etl(file_path)
            else:
                # Para cuenta bancaria, usar lógica existente
                self._load_excel_legacy(file_path, selected_mode)
        
        elif self._picker_mode == "save_template":
            if not e.path:
                return
            output_path = Path(e.path)
            if output_path.suffix.lower() != ".xlsx":
                output_path = output_path.with_suffix(".xlsx")

            template_df = pd.DataFrame(
                [
                    {
                        "Fecha": datetime.date.today(),
                        "Concepto": "Supermercado",
                        "Monto": 120000,
                        "Categoría": "Compras",
                        "Cuotas": 3,
                        "Referencia": "Ref-001",
                    },
                    {
                        "Fecha": datetime.date.today(),
                        "Concepto": "Gasolina",
                        "Monto": 80000,
                        "Categoría": "Transporte",
                        "Cuotas": 1,
                        "Referencia": "Ref-002",
                    },
                ]
            )

            try:
                template_df.to_excel(output_path, index=False, sheet_name="Transacciones")
                self._show_message(f"Plantilla generada: {output_path}", ft.Colors.GREEN_700)
            except Exception as ex:
                self._show_message(f"No se pudo generar la plantilla: {ex}", ft.Colors.RED_600)
    
    def _load_excel_with_etl(self, file_path: Path) -> None:
        """Carga Excel usando ETL para tarjeta de crédito."""
        try:
            # Validar archivo
            is_valid, errors = validate_excel_file(str(file_path))
            if not is_valid:
                self._show_message(f"Archivo inválido: {'; '.join(errors)}", ft.Colors.RED_600)
                return
            
            # Obtener usuario activo
            db = DatabaseConnector()
            user_rows = db.execute_query(
                """
                SELECT id_persona
                FROM persona
                WHERE estado = 1
                ORDER BY COALESCE(fecha_actualizacion, fecha_creacion) DESC, id_persona DESC
                LIMIT 1
                """
            )
            
            if not user_rows:
                self._show_message("No hay usuario activo.", ft.Colors.RED_600)
                db.close()
                return
            
            id_persona = int(user_rows[0]['id_persona'])
            id_tarjeta = int(self.card_dropdown.value)
            
            # Ejecutar ETL
            etl = ETLTarjetaCredito(db)
            processed_count, validation_errors = etl.process_file(
                str(file_path),
                id_persona,
                id_tarjeta
            )
            
            db.close()
            
            # Reportar resultados
            if processed_count > 0:
                self._show_message(
                    f"✓ Carga completada: {processed_count} transacción(es) registrada(s).",
                    ft.Colors.GREEN_700
                )
            
            if validation_errors:
                error_msg = "Filas con errores:\n"
                for err in validation_errors[:5]:  # Mostrar máximo 5 errores
                    error_msg += f"\nFila {err.get('row', '?')}: {'; '.join(err.get('errors', ['Error desconocido']))}"
                
                if len(validation_errors) > 5:
                    error_msg += f"\n... y {len(validation_errors) - 5} error(es) más"
                
                self._show_message(error_msg, ft.Colors.ORANGE_700)
        
        except Exception as ex:
            self._show_message(f"Error procesando archivo: {ex}", ft.Colors.RED_600)
    
    def _load_excel_legacy(self, file_path: Path, selected_mode: str) -> None:
        """Carga Excel para cuentas bancarias (lógica existente)."""
        try:
            df = pd.read_excel(file_path)
        except Exception as ex:
            self._show_message(f"No se pudo leer el archivo: {ex}", ft.Colors.RED_600)
            return

        col_map = {c.lower().strip(): c for c in df.columns}
        rows_added = 0
        selected_account = self.account_dropdown.value

        for _, row in df.iterrows():
            data = {
                "concepto": str(row.get(col_map.get("concepto", ""), "") or ""),
                "monto": str(row.get(col_map.get("monto", ""), "") or ""),
                "categoria": str(row.get(col_map.get("categoría", col_map.get("categoria", "")), "") or ""),
                "medio_pago": "Tarjeta de crédito" if selected_mode == "tarjeta_credito" else "Cuenta",
                "cuotas": str(row.get(col_map.get("cuotas", ""), "1") or "1"),
                "id_cuenta_override": int(selected_account) if selected_mode == "cuenta_bancaria" and selected_account else None,
                "id_tarjeta_override": None,
            }
            if not data["concepto"] and not data["monto"] and not data["categoria"]:
                continue
            self.grid_rows.append(self._create_grid_row(data))
            rows_added += 1

        if rows_added == 0:
            self._show_message("No se encontraron filas válidas en el Excel.", ft.Colors.RED_600)
            return

        self._refresh_table()
        self._show_message(f"Carga masiva completada. Filas agregadas: {rows_added}", ft.Colors.GREEN_700)

    def _open_massive_upload(self, e: ft.ControlEvent) -> None:
        self._picker_mode = "load"
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xlsx", "xls"],
            dialog_title="Selecciona el archivo Excel de transacciones",
        )

    def _download_template(self, e: ft.ControlEvent) -> None:
        self._picker_mode = "save_template"
        self.file_picker.save_file(
            dialog_title="Guardar plantilla Excel",
            file_name=f"plantilla_transacciones_{datetime.date.today().isoformat()}.xlsx",
            allowed_extensions=["xlsx"],
        )

    def _clear_table(self, e: ft.ControlEvent) -> None:
        self.grid_rows = []
        self._add_empty_row()
        self._refresh_table()
        self._show_message("Tabla reiniciada.", ft.Colors.BLUE_700)

    def _save_all(self, e: ft.ControlEvent) -> None:
        normalized_rows: List[Dict[str, Any]] = []
        for row in self.grid_rows:
            concepto = (row["concepto"].value or "").strip()
            categoria = (row["categoria"].value or "").strip()
            monto_txt = (row["monto"].value or "").replace(",", ".")
            cuotas_txt = row["cuotas"].value or "1"
            medio_pago = row["medio_pago"].value or "Cuenta"
            id_cuenta_override = row.get("id_cuenta_override")
            id_tarjeta_override = row.get("id_tarjeta_override")

            if not concepto and not categoria and not monto_txt:
                continue

            try:
                monto = float(monto_txt)
            except ValueError:
                self._show_message(f"Monto inválido en fila con concepto '{concepto or 'sin concepto'}'.", ft.Colors.RED_600)
                return

            if monto <= 0:
                self._show_message("El monto debe ser mayor que cero.", ft.Colors.RED_600)
                return

            cuotas = 1
            if medio_pago == "Tarjeta de crédito":
                try:
                    cuotas = int(cuotas_txt)
                except ValueError:
                    self._show_message("Las cuotas deben ser numéricas.", ft.Colors.RED_600)
                    return
                if cuotas < 1 or cuotas > 36:
                    self._show_message("Las cuotas para tarjeta deben estar entre 1 y 36.", ft.Colors.RED_600)
                    return

            normalized_rows.append(
                {
                    "concepto": concepto,
                    "categoria": categoria or "Compras",
                    "monto": monto,
                    "medio_pago": medio_pago,
                    "cuotas": cuotas,
                    "id_cuenta_override": id_cuenta_override,
                    "id_tarjeta_override": id_tarjeta_override,
                }
            )

        if not normalized_rows:
            self._show_message("No hay filas válidas para guardar.", ft.Colors.RED_600)
            return

        db = DatabaseConnector()
        if not db.conn:
            self._show_message("No se pudo conectar a la base de datos.", ft.Colors.RED_600)
            return

        try:
            with db.conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id_persona
                    FROM persona
                    WHERE estado = 1
                    ORDER BY COALESCE(fecha_actualizacion, fecha_creacion) DESC, id_persona DESC
                    LIMIT 1
                    """
                )
                user_row = cursor.fetchone()
                if not user_row:
                    self._show_message("No hay usuario activo para guardar transacciones.", ft.Colors.RED_600)
                    return
                id_persona = int(user_row["id_persona"])

                cursor.execute(
                    "SELECT id_cuenta FROM cuenta WHERE id_persona = %s ORDER BY id_cuenta LIMIT 1",
                    (id_persona,),
                )
                account_row = cursor.fetchone()
                if not account_row:
                    self._show_message("El usuario no tiene cuenta asociada para registrar movimientos.", ft.Colors.RED_600)
                    return
                id_cuenta = int(account_row["id_cuenta"])

                cursor.execute("SELECT id_tipo, LOWER(nombre) AS nombre FROM tipo_movimiento")
                tipo_map = {r["nombre"]: int(r["id_tipo"]) for r in cursor.fetchall()}
                id_tipo_ingreso = tipo_map.get("ingreso")
                id_tipo_gasto = tipo_map.get("gasto")
                if not id_tipo_ingreso or not id_tipo_gasto:
                    self._show_message("No existen tipos de movimiento 'ingreso' y 'gasto'.", ft.Colors.RED_600)
                    return

                cursor.execute("SELECT id_estado FROM estado_movimiento ORDER BY id_estado LIMIT 1")
                estado_row = cursor.fetchone()
                if not estado_row:
                    self._show_message("No existe estado_movimiento para registrar transacciones.", ft.Colors.RED_600)
                    return
                id_estado = int(estado_row["id_estado"])

                cursor.execute("SELECT id_categoria, nombre FROM categoria")
                categoria_map = {str(r["nombre"]).strip().lower(): int(r["id_categoria"]) for r in cursor.fetchall()}

                cursor.execute(
                    """
                    SELECT tc.id_tarjeta
                    FROM tarjeta_credito tc
                    JOIN movimiento_tarjeta mt ON mt.id_tarjeta = tc.id_tarjeta
                    WHERE mt.id_persona = %s
                    ORDER BY tc.id_tarjeta
                    LIMIT 1
                    """,
                    (id_persona,),
                )
                tarjeta_row = cursor.fetchone()
                id_tarjeta = int(tarjeta_row["id_tarjeta"]) if tarjeta_row else None

                saved_count = 0
                for idx, item in enumerate(normalized_rows, start=1):
                    categoria_key = item["categoria"].strip().lower()
                    id_categoria = categoria_map.get(categoria_key)
                    if not id_categoria:
                        cursor.execute("INSERT INTO categoria (nombre) VALUES (%s)", (item["categoria"],))
                        id_categoria = int(cursor.lastrowid)
                        categoria_map[categoria_key] = id_categoria

                    is_income = "ingres" in categoria_key
                    id_tipo = id_tipo_ingreso if is_income else id_tipo_gasto

                    numero_transaccion = f"MAN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{idx}"
                    codigo = f"MOV-{datetime.datetime.now().strftime('%Y%m%d')}-{idx}"

                    cursor.execute(
                        """
                        INSERT INTO movimiento
                        (codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario,
                         numero_transaccion, nota, fecha_creacion, id_cuenta)
                        VALUES (%s, %s, %s, %s, %s, %s, NULL, %s, %s, NOW(), %s)
                        """,
                        (
                            codigo,
                            item["monto"],
                            id_tipo,
                            id_estado,
                            (item.get("id_tarjeta_override") or id_tarjeta)
                            if item["medio_pago"] == "Tarjeta de crédito"
                            else None,
                            id_categoria,
                            numero_transaccion,
                            item["concepto"],
                            item.get("id_cuenta_override") or id_cuenta,
                        ),
                    )

                    if item["medio_pago"] == "Tarjeta de crédito":
                        id_tarjeta_item = item.get("id_tarjeta_override") or id_tarjeta
                        if not id_tarjeta_item:
                            self._show_message(
                                "No existe tarjeta de crédito asociada para el usuario activo.",
                                ft.Colors.RED_600,
                            )
                            db.conn.rollback()
                            return

                        cursor.execute(
                            """
                            INSERT INTO movimiento_tarjeta
                            (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion,
                             id_categoria, id_beneficiario, saldo, cuotas)
                            VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s, NULL, %s, %s)
                            """,
                            (
                                id_tarjeta_item,
                                id_persona,
                                item["monto"],
                                "compra",
                                item["concepto"],
                                numero_transaccion,
                                id_categoria,
                                item["monto"],
                                item["cuotas"],
                            ),
                        )

                    saved_count += 1

                db.conn.commit()
                self._show_message(
                    f"Guardado exitoso. Se registraron {saved_count} transacciones.",
                    ft.Colors.GREEN_700,
                )

        except Exception as ex:
            db.conn.rollback()
            self._show_message(f"Error guardando transacciones: {ex}", ft.Colors.RED_600)
        finally:
            db.close()

    def _build_form_card(self) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(ft.Icons.EDIT_NOTE, color=ft.Colors.BLUE_700),
                            ft.Text("Registro individual", size=18, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.ResponsiveRow(
                            [
                                ft.Container(content=self.concepto_input, col={"xs": 12, "md": 6, "lg": 5}),
                                ft.Container(content=self.monto_input, col={"xs": 6, "md": 3, "lg": 2}),
                                ft.Container(content=self.categoria_input, col={"xs": 6, "md": 3, "lg": 3}),
                                ft.Container(content=self.medio_pago_input, col={"xs": 8, "md": 4, "lg": 3}),
                                ft.Container(content=self.cuotas_input, col={"xs": 4, "md": 2, "lg": 2}),
                            ],
                            run_spacing=8,
                            spacing=10,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Agregar a tabla",
                                    icon=ft.Icons.ADD,
                                    on_click=self._add_row_from_form,
                                ),
                                ft.OutlinedButton(
                                    "Agregar fila vacía",
                                    icon=ft.Icons.POST_ADD,
                                    on_click=lambda e: (self._add_empty_row(), self._refresh_table()),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            wrap=True,
                            spacing=10,
                        ),
                    ],
                    spacing=12,
                ),
            )
        )

    def _build_toolbar(self) -> ft.Container:
        return ft.Container(
            bgcolor="white",
            padding=16,
            border_radius=12,
            border=ft.border.all(1, "#E0E0E0"),
            content=ft.Column(
                [
                    ft.Text("Configuración de carga masiva", size=14, weight=ft.FontWeight.BOLD),
                    self.massive_mode_group,
                    ft.Row(
                        [
                            self.account_dropdown,
                            self.card_dropdown,
                        ],
                        wrap=True,
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton("Guardar Todo", icon=ft.Icons.SAVE, on_click=self._save_all),
                            ft.OutlinedButton("Limpiar Tabla", icon=ft.Icons.CLEANING_SERVICES, on_click=self._clear_table),
                            ft.OutlinedButton("Descargar Plantilla Excel", icon=ft.Icons.DOWNLOAD, on_click=self._download_template),
                            ft.ElevatedButton("Carga masiva Excel", icon=ft.Icons.UPLOAD_FILE, on_click=self._open_massive_upload),
                        ],
                        wrap=True,
                        run_spacing=8,
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
        )

    def _build_main_content(self) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor="#F8F9FA",
            padding=24,
            content=ft.Column(
                [
                    ft.Container(
                        alignment=ft.alignment.top_center,
                        content=ft.Column(
                            [
                                ft.Text("Registro de Transacciones Financieras", size=28, weight=ft.FontWeight.BOLD),
                                ft.Text("Carga individual o masiva desde Excel y edita en grilla interactiva."),
                                self._build_form_card(),
                                self._build_toolbar(),
                                self.status_text,
                            ],
                            spacing=12,
                            width=1120,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        content=ft.Container(
                            width=1120,
                            height=420,
                            padding=ft.padding.only(top=4),
                            content=ft.Column(
                                [
                                    ft.Text("Grilla Interactiva", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(content=self.table_container, expand=True),
                                ],
                                spacing=8,
                                expand=True,
                            ),
                        ),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        )

    def _build_layout(self) -> ft.Control:
        return ft.Container(
            expand=True,
            content=ft.Row(
                [
                    self.sidebar_menu.create_sidebar(),
                    self._build_main_content(),
                ],
                spacing=0,
                expand=True,
            ),
        )


def nueva_transaccion_view(page: ft.Page) -> ft.View:
    return NuevaTransaccionView(page)

def main(page: ft.Page) -> None:
    """
    Función principal para ejecutar la aplicación de forma independiente.
    
    Args:
        page (ft.Page): La página principal proporcionada por Flet
    """
    # Configuración de la ventana
    page.title = "App Presupuesto - Nueva Transacción"
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
    page.add(nueva_transaccion_view(page))

if __name__ == "__main__":
    """
    Punto de entrada de la aplicación.
    
    Inicia la aplicación Flet con la función main como target.
    """
    ft.app(target=main)


