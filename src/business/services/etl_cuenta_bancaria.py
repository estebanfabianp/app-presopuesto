"""ETL para carga masiva de movimientos de cuenta bancaria desde Excel."""

from __future__ import annotations

import datetime
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from ...database.db_connector import DatabaseConnector
except ImportError:
    try:
        from src.database.db_connector import DatabaseConnector
    except ImportError:
        from database.db_connector import DatabaseConnector


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    row_number: int = 0
    data: Dict[str, Any] = field(default_factory=dict)


class ETLCuentaBancaria:
    """ETL para extractos bancarios con formato FECHA / DESCRIPCION / DCTO / VALOR / SALDO."""

    EXPECTED_COLUMNS = {
        'fecha': ['fecha', 'date', 'fecha movimiento'],
        'descripcion': ['descripcion sucursal', 'descripcion', 'descripcionsucursal', 'concepto', 'detalle'],
        'dcto': ['dcto', 'dcto.', 'tipo', 'debito credito', 'debito/credito'],
        'valor': ['valor', 'monto', 'importe', 'amount'],
        'saldo': ['saldo', 'balance'],
    }

    INSERT_MOVIMIENTO_SQL = (
        "INSERT INTO movimiento "
        "(codigo, monto, id_tipo, id_estado, id_categoria, id_beneficiario, "
        "fecha_creacion, id_cuenta, nota, numero_transaccion) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    def __init__(self, db: Optional[DatabaseConnector] = None):
        self.db = db or DatabaseConnector()
        self.logger = logging.getLogger(__name__)
        self.validation_errors: List[Dict[str, Any]] = []
        self.processed_count = 0

    @staticmethod
    def _normalize_text(value: Any) -> str:
        text = str(value or '').strip().lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r'[^a-z0-9]+', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def _parse_amount(value: Any) -> float:
        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            raise ValueError('Monto vacio')

        negative = raw.startswith('(') and raw.endswith(')')
        cleaned = raw.replace('(', '').replace(')', '')
        cleaned = re.sub(r'[^0-9,.-]', '', cleaned)

        if cleaned.count(',') > 0 and cleaned.count('.') > 0:
            if cleaned.rfind(',') > cleaned.rfind('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif cleaned.count(',') > 1:
            cleaned = cleaned.replace(',', '')
        elif cleaned.count('.') > 1:
            cleaned = cleaned.replace('.', '')
        else:
            cleaned = cleaned.replace(',', '.')

        amount = float(cleaned)
        if negative:
            amount *= -1
        return amount

    @staticmethod
    def _parse_date(value: Any) -> datetime.date:
        if pd is None:
            return datetime.date.today()

        if isinstance(value, pd.Timestamp):
            return value.date()

        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            return datetime.date.today()

        if re.match(r'^\d{1,2}/\d{1,2}$', raw):
            raw = f"{raw}/{datetime.date.today().year}"

        parsed = pd.to_datetime(raw, errors='coerce', dayfirst=True)
        if pd.isna(parsed):
            raise ValueError(f"Fecha invalida: '{value}'")
        return parsed.date()

    @staticmethod
    def _infer_tipo(dcto: str, amount: float) -> str:
        token = ETLCuentaBancaria._normalize_text(dcto)
        if any(k in token for k in ['abono', 'credito', 'dep', 'ingreso', 'transferencia recibida']):
            return 'ingreso'
        if any(k in token for k in ['cargo', 'debito', 'compra', 'retiro', 'pago']):
            return 'gasto'
        return 'ingreso' if amount >= 0 else 'gasto'

    def process_file(self, file_path: str, id_persona: int, id_cuenta: int) -> Tuple[int, List[Dict[str, Any]]]:
        if not pd:
            raise ImportError('pandas es requerido para procesar archivos Excel')

        try:
            df = pd.read_excel(file_path)
            if df.empty:
                return 0, [{'error': 'Archivo Excel vacio'}]

            original_columns = list(df.columns)
            normalized_columns = [self._normalize_text(col) for col in original_columns]
            self._validate_excel_structure(normalized_columns)
            col_map = self._map_columns(original_columns)

            rows_to_insert: List[Dict[str, Any]] = []
            for idx, (_, row) in enumerate(df.iterrows(), start=2):
                validation = self._validate_row(row, col_map, idx)
                if not validation.is_valid:
                    self.validation_errors.append({
                        'row': idx,
                        'errors': validation.errors,
                    })
                    continue

                try:
                    transformed = self._transform_row(validation.data, id_persona, id_cuenta, idx)
                    rows_to_insert.append(transformed)
                except Exception as te:
                    self.logger.error('Error transformando fila %s: %s', idx, te)
                    self.validation_errors.append({
                        'row': idx,
                        'errors': [f'Error interno al procesar fila: {str(te)}'],
                    })
                    continue

            if rows_to_insert:
                self._load_data(rows_to_insert)
                self.processed_count = len(rows_to_insert)

            return self.processed_count, self.validation_errors
        except Exception as e:
            self.logger.error('Error procesando extracto bancario: %s', e)
            return 0, [{'error': f'Error de procesamiento: {str(e)}'}]

    def _validate_excel_structure(self, columns: List[str]) -> None:
        required = ['fecha', 'descripcion', 'valor']
        found = {k: False for k in required}

        for col in columns:
            for key, aliases in self.EXPECTED_COLUMNS.items():
                if col in [self._normalize_text(alias) for alias in aliases] and key in found:
                    found[key] = True

        missing = [k for k, ok in found.items() if not ok]
        if missing:
            raise ValueError(f"Columnas faltantes en Excel: {', '.join(missing)}")

    @classmethod
    def _validate_structure_static(cls, normalized_columns: List[str]) -> None:
        """Valida estructura sin necesitar instancia (no abre conexión BD)."""
        required = ['fecha', 'descripcion', 'valor']
        found = {k: False for k in required}

        for col in normalized_columns:
            for key, aliases in cls.EXPECTED_COLUMNS.items():
                if col in [cls._normalize_text(alias) for alias in aliases] and key in found:
                    found[key] = True

        missing = [k for k, ok in found.items() if not ok]
        if missing:
            raise ValueError(f"Columnas faltantes en Excel: {', '.join(missing)}")

    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        col_map: Dict[str, str] = {}
        normalized = [self._normalize_text(c) for c in columns]

        for standard_name, aliases in self.EXPECTED_COLUMNS.items():
            normalized_aliases = [self._normalize_text(a) for a in aliases]
            for i, col in enumerate(normalized):
                if col in normalized_aliases:
                    col_map[standard_name] = columns[i]
                    break

        return col_map

    def _validate_row(self, row: Any, col_map: Dict[str, str], row_number: int) -> ValidationResult:
        result = ValidationResult(row_number=row_number)

        def get(col_key: str):
            col_name = col_map.get(col_key)
            return row.get(col_name, None) if col_name else None

        raw_fecha = get('fecha')
        raw_desc = get('descripcion')
        raw_dcto = get('dcto')
        raw_valor = get('valor')
        raw_saldo = get('saldo')

        desc = str(raw_desc or '').strip()
        if not desc or desc.lower() == 'nan':
            result.is_valid = False
            result.errors.append('Descripcion obligatoria')

        try:
            fecha = self._parse_date(raw_fecha)
        except Exception as exc:
            result.is_valid = False
            result.errors.append(str(exc))
            fecha = datetime.date.today()

        try:
            valor = self._parse_amount(raw_valor)
            if abs(valor) <= 0:
                raise ValueError('Valor debe ser distinto de 0')
        except Exception:
            result.is_valid = False
            result.errors.append(f"Valor invalido: '{raw_valor}'")
            valor = 0.0

        saldo_val = None
        if raw_saldo is not None and str(raw_saldo).strip() and str(raw_saldo).strip().lower() != 'nan':
            try:
                saldo_val = self._parse_amount(raw_saldo)
            except Exception:
                result.errors.append(f"Saldo invalido en fila {row_number}; se omitira")

        if result.is_valid:
            result.data = {
                'fecha': fecha,
                'descripcion': desc,
                'dcto': str(raw_dcto or '').strip(),
                'valor': valor,
                'saldo': saldo_val,
            }

        return result

    def _resolve_tipo_id(self, tipo: str) -> int:
        cursor = self.db.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                'SELECT id_tipo FROM tipo_movimiento WHERE LOWER(nombre) = %s LIMIT 1',
                (tipo.lower(),),
            )
            row = cursor.fetchone()
            if row:
                return int(row['id_tipo'])

            cursor.execute('INSERT INTO tipo_movimiento (nombre) VALUES (%s)', (tipo,))
            return int(cursor.lastrowid)
        finally:
            cursor.close()

    def _resolve_categoria_id(self, categoria: str, id_persona: int) -> int:
        cursor = self.db.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                'SELECT id_categoria FROM categoria WHERE LOWER(nombre) = %s AND id_persona = %s LIMIT 1',
                (categoria.lower(), id_persona),
            )
            row = cursor.fetchone()
            if row:
                return int(row['id_categoria'])

            cursor.execute('INSERT INTO categoria (nombre, id_persona) VALUES (%s, %s)', (categoria, id_persona))
            return int(cursor.lastrowid)
        finally:
            cursor.close()

    def _resolve_estado_id(self) -> int:
        cursor = self.db.conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id_estado FROM estado_movimiento ORDER BY id_estado LIMIT 1')
            row = cursor.fetchone()
            return int(row['id_estado']) if row else 1
        finally:
            cursor.close()

    def _transform_row(self, validated_data: Dict[str, Any], id_persona: int, id_cuenta: int, row_number: int) -> Dict[str, Any]:
        valor = float(validated_data['valor'])
        tipo = self._infer_tipo(validated_data.get('dcto', ''), valor)
        id_tipo = self._resolve_tipo_id(tipo)
        id_estado = self._resolve_estado_id()

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        numero_transaccion = f"BNK-{timestamp}-{row_number}"

        # Nota: solo descripción (sin dcto ni saldo para mantener limpio)
        nota = validated_data['descripcion']

        return {
            'codigo': f"MOV-BNK-{timestamp}-{row_number}",
            'monto': abs(valor),
            'id_tipo': id_tipo,
            'id_estado': id_estado,
            'id_categoria': None,  # Dejar sin categoría para que el usuario la seleccione después
            'id_beneficiario': None,
            'fecha_creacion': validated_data['fecha'],
            'id_cuenta': id_cuenta,
            'nota': nota,
            'numero_transaccion': numero_transaccion,
        }

    def _load_data(self, rows: List[Dict[str, Any]]) -> None:
        cursor = None
        try:
            cursor = self.db.conn.cursor()
            for mov in rows:
                values = (
                    mov['codigo'],
                    mov['monto'],
                    mov['id_tipo'],
                    mov['id_estado'],
                    mov['id_categoria'],
                    mov['id_beneficiario'],
                    mov['fecha_creacion'],
                    mov['id_cuenta'],
                    mov['nota'],
                    mov['numero_transaccion'],
                )
                cursor.execute(self.INSERT_MOVIMIENTO_SQL, values)

            self.db.conn.commit()
        except Exception:
            self.db.conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()


def validate_bank_excel_file(file_path: str) -> Tuple[bool, List[str]]:
    if not pd:
        return False, ['pandas es requerido']

    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return False, ['Archivo Excel vacio']

        # Usar métodos estáticos directamente, sin crear conexión BD
        normalized_cols = [ETLCuentaBancaria._normalize_text(c) for c in df.columns]
        ETLCuentaBancaria._validate_structure_static(normalized_cols)
        return True, []
    except Exception as exc:
        return False, [str(exc)]
