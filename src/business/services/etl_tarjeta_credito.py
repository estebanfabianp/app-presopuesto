"""
ETL para carga masiva de transacciones de tarjeta de crédito desde Excel.

Procesa archivos Excel validando estructura, transformando datos y cargando
en movimiento_tarjeta con control transaccional completo.

Reglas de negocio para diferidos:
- Cada fila del extracto mensual debe conservarse en movimiento_tarjeta.
- Si la cuota llega con formato N/X y X > 1, el movimiento se clasifica como diferido.
- El seguimiento consolidado vive en tarjeta_diferido y se actualiza por código
    del extracto cuando dicho código existe, no está vacío y no es 000000.
- Excepción: si código = 000000 y concepto = AMPLIACION DE PLAZO,
    el registro sí participa en seguimiento consolidado.
- El historial mensual no se deduplica: el upsert aplica solo al seguimiento.
"""

from __future__ import annotations

import datetime
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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
    """Resultado de validación de fila de Excel."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    row_number: int = 0
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformResult:
    """Resultado de transformación de datos."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    insert_movimiento_tarjeta: Dict[str, Any] = field(default_factory=dict)


def _q2(value: Any) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def _add_months(base_date: datetime.date, months: int = 1) -> datetime.date:
    year = base_date.year + (base_date.month - 1 + months) // 12
    month = (base_date.month - 1 + months) % 12 + 1
    last_day = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    return datetime.date(year, month, min(base_date.day, last_day))


class ETLTarjetaCredito:
    """
    ETL para procesamiento de transacciones de tarjeta de crédito desde Excel.
    
    Flujo:
    1. Validar archivo Excel
    2. Extraer y validar datos
    3. Transformar a formato de base de datos
    4. Cargar en transacción
    5. Reportar errores
    """
    
    # Columnas esperadas en Excel (case-insensitive)

    EXPECTED_COLUMNS = {
        'fecha': [
            'fecha', 'date', 'date_transaction', 'fecha movimiento',
            'fecha transaccion', 'fecha de transaccion', 'fecha de tran'
        ],
        'concepto': [
            'concepto', 'description', 'descripcion', 'transaccion',
            'movimientos', 'movimiento', 'detalle', 'descripcion sucursal'
        ],
        'monto': [
            'monto', 'amount', 'valor', 'quantity', 'valor movimiento', 'valor movimie',
            'cargos y abonos', 'cargos abonos'
        ],
        'valor_original': [
            'valor original'
        ],
        'cuotas': ['cuotas', 'quotas', 'installments', 'nro_cuotas', 'numero de cuotas', 'numero de cu'],
        'categoria': ['categoria', 'category', 'categoría'],
        'referencia': [
            'referencia', 'reference', 'ref', 'numero_referencia',
            'numero de autorizacion', 'numero de au', 'autorizacion'
        ],
        'valor_cuota': ['valor cuota', 'valor cuota/al', 'valor cuota al', 'valor_cuota'],
        'interes_mensual': ['interes mensual', 'interes mensu', 'tasa mensual', 'interes mes', 'tasa pactada'],
        'interes_anual': ['interes anual', 'tasa anual'],
        'saldo_pendiente': [
            'saldo pendiente',
            'saldo pendiente capital',
            'saldo restante',
            'saldo a diferir',
            'saldo diferir',
            'saldo por diferir',
        ],
        'cargos_abonos': ['cargos y abonos'],
    }

    REQUIRED_COLUMNS = ('fecha', 'concepto', 'monto')

    INSERT_MOVIMIENTO_TARJETA_SQL = (
        "INSERT INTO movimiento_tarjeta "
        "(id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, "
        "id_categoria, id_beneficiario, saldo, cuotas) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    
    def __init__(self, db: Optional[DatabaseConnector] = None):
        """
        Inicializa el ETL.
        
        Args:
            db: Conexión a base de datos. Si no se proporciona, se crea una nueva.
        """
        self.db = db or DatabaseConnector()
        self.logger = logging.getLogger(__name__)
        self.validation_errors: List[Dict[str, Any]] = []
        self.processed_count = 0
        self.error_count = 0

    def _assert_tarjeta_activa(self, id_persona: int, id_tarjeta: int) -> None:
        rows = self.db.execute_query(
            """
            SELECT tc.id_tarjeta, COALESCE(LOWER(et.nombre), 'activa') AS estado
            FROM tarjeta_credito tc
            LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
            WHERE tc.id_tarjeta = %s AND tc.id_persona = %s
            LIMIT 1
            """,
            (id_tarjeta, id_persona),
        )

        if not rows:
            raise ValueError('Tarjeta no encontrada o no pertenece al usuario')

        estado = str(rows[0].get('estado') or 'activa').strip().lower()
        if estado != 'activa':
            raise ValueError('La tarjeta seleccionada esta inactiva. Activala para importar por ETL')

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
        trailing_negative = raw.endswith('-')
        leading_negative = raw.startswith('-')

        cleaned = raw.replace('(', '').replace(')', '')
        if trailing_negative:
            cleaned = cleaned[:-1]
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
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

        amount = abs(float(cleaned))
        if negative or trailing_negative or leading_negative:
            amount *= -1
        return amount

    @staticmethod
    def _parse_installments(value: Any) -> int:
        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            return 1

        normalized = raw.replace(' ', '')
        if '/' in normalized:
            first_part = normalized.split('/', 1)[0]
            if first_part:
                normalized = first_part

        installments = int(float(normalized))
        if installments < 1 or installments > 36:
            raise ValueError('Cuotas debe estar entre 1 y 36')
        return installments

    @classmethod
    def _parse_installment_progress(cls, value: Any) -> Tuple[int, int]:
        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            return 1, 1

        normalized = raw.replace(' ', '')
        if '/' in normalized:
            current_part, total_part = normalized.split('/', 1)
            current_installment = cls._parse_installments(current_part or '1')
            total_installments = cls._parse_installments(total_part or current_part or '1')
            if current_installment > total_installments:
                raise ValueError('Cuotas inválida: progreso mayor al total')
            return current_installment, total_installments

        total_installments = cls._parse_installments(normalized)
        return 1, total_installments

    @classmethod
    def _parse_optional_amount(cls, value: Any) -> Optional[float]:
        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            return None
        return cls._parse_amount(raw)

    @classmethod
    def _parse_optional_rate(cls, monthly_value: Any, annual_value: Any) -> Optional[float]:
        monthly_rate = cls._parse_optional_amount(monthly_value)
        annual_rate = cls._parse_optional_amount(annual_value)

        rate = monthly_rate
        if rate is None and annual_rate is not None:
            rate = annual_rate / 12.0

        if rate is None:
            return None

        rate = abs(float(rate))
        # Normalizar a porcentaje mensual (ej. 3.0352), que es el formato
        # esperado por tarjeta_diferido y por los endpoints de tarjetas.
        if rate <= 1:
            rate = rate * 100.0
        return rate

    @staticmethod
    def _is_valid_tracking_code(value: Any) -> bool:
        raw = str(value or '').strip().upper()
        if not raw or raw.lower() == 'nan':
            return False
        if raw in {'000000', '0'}:
            return False
        # Evitar usar IDs sintéticos internos como código de autorización.
        if raw.startswith('TRX-'):
            return False
        return bool(re.fullmatch(r'[A-Z0-9]{4,30}', raw))

    @classmethod
    def _is_tracking_exception_ampliacion_plazo(cls, tracking_code: Any, description: Any) -> bool:
        raw_code = str(tracking_code or '').strip().upper()
        if raw_code != '000000':
            return False
        normalized_description = cls._normalize_text(description)
        return normalized_description == 'ampliacion de plazo'

    @staticmethod
    def _normalize_reference(value: Any) -> str:
        """Normaliza número de autorización para matching estable en ETL."""
        raw = str(value or '').strip()
        if not raw or raw.lower() == 'nan':
            return ''

        normalized = raw.replace(' ', '')
        if re.fullmatch(r'\d+\.0+', normalized):
            normalized = normalized.split('.', 1)[0]

        return normalized.upper()

    def _ensure_diferidos_tables(self) -> None:
        self.db.execute_non_query(
            """
            CREATE TABLE IF NOT EXISTS tarjeta_diferido (
                id_diferido INT AUTO_INCREMENT PRIMARY KEY,
                id_tarjeta INT NOT NULL,
                id_persona INT NOT NULL,
                id_movimiento_tarjeta INT NULL,
                descripcion VARCHAR(255) NOT NULL,
                valor_total DECIMAL(15,2) NOT NULL,
                numero_cuotas INT NOT NULL,
                tasa_mensual DECIMAL(10,6) NOT NULL DEFAULT 0,
                sin_interes TINYINT(1) NOT NULL DEFAULT 0,
                cuota_mensual DECIMAL(15,2) NOT NULL,
                total_intereses DECIMAL(15,2) NOT NULL DEFAULT 0,
                total_pagado_estimado DECIMAL(15,2) NOT NULL,
                cuotas_pagadas INT NOT NULL DEFAULT 0,
                saldo_pendiente DECIMAL(15,2) NOT NULL,
                fecha_compra DATE NOT NULL,
                fecha_proximo_pago DATE NULL,
                estado VARCHAR(20) NOT NULL DEFAULT 'activo',
                numero_transaccion VARCHAR(60) NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_td_persona (id_persona),
                INDEX idx_td_tarjeta (id_tarjeta),
                INDEX idx_td_estado (estado)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def _sync_diferido_tracking(self, mov_tarjeta_data: Dict[str, Any], id_movimiento_tarjeta: int) -> None:
        """Mantiene actualizado el seguimiento consolidado sin perder el historial mensual.

        Regla central:
        - movimiento_tarjeta conserva cada cuota reportada en el extracto.
        - tarjeta_diferido consolida el estado de la compra y hace upsert por código
          válido del extracto para evitar duplicados en seguimiento.
        """
        tracking_code = mov_tarjeta_data.get('tracking_code')
        is_exception_ampliacion = self._is_tracking_exception_ampliacion_plazo(
            tracking_code,
            mov_tarjeta_data.get('nota'),
        )
        total_installments = int(mov_tarjeta_data.get('tracking_total_installments') or 1)
        current_installment = int(mov_tarjeta_data.get('tracking_current_installment') or 1)
        should_track = bool(mov_tarjeta_data.get('tracking_should_track'))

        if not should_track or total_installments <= 1:
            return

        self._ensure_diferidos_tables()


        # Ajuste: priorizar datos del extracto para diferidos.
        # - valor_total: valor original de la compra cuando esté disponible
        # - cuota_mensual: valor de cuota/reportado en extracto (si existe)
        valor_total = abs(float(mov_tarjeta_data.get('tracking_original_value') or mov_tarjeta_data['valor']))
        pago_extracto = mov_tarjeta_data.get('tracking_payment_value')
        if pago_extracto is not None and abs(float(pago_extracto)) > 0:
            cuota_mensual = round(abs(float(pago_extracto)), 2)
        else:
            cuota_mensual = round(valor_total / total_installments, 2)
        cuotas_pagadas = max(current_installment - 1, 0)
        saldo_pendiente = round(valor_total - (cuota_mensual * cuotas_pagadas), 2)
        # Si el extracto trae saldo pendiente, se respeta ese valor reportado.
        saldo_pendiente_extracto = mov_tarjeta_data.get('tracking_remaining_balance')
        if saldo_pendiente_extracto is not None:
            try:
                saldo_pendiente_extracto = abs(float(saldo_pendiente_extracto))
                saldo_pendiente = saldo_pendiente_extracto
            except Exception:
                pass

        tasa_mensual = mov_tarjeta_data.get('tracking_monthly_rate')
        tasa_mensual = abs(float(tasa_mensual)) if tasa_mensual is not None else 0.0
        cuotas_pagadas = max(current_installment - 1, 0)
        fecha_compra = mov_tarjeta_data['fecha']
        fecha_proximo_pago = None if saldo_pendiente <= 0.01 or cuotas_pagadas >= total_installments else _add_months(fecha_compra, 1)
        estado = 'pagado' if saldo_pendiente <= 0.01 or cuotas_pagadas >= total_installments else 'activo'

        estimated_total = max(valor_total, saldo_pendiente + (cuota_mensual * cuotas_pagadas))
        total_pagado_estimado = cuota_mensual * total_installments if cuota_mensual > 0 else estimated_total
        total_intereses = max(total_pagado_estimado - valor_total, 0)

        cursor = self.db.conn.cursor(dictionary=True)
        try:
            existing = None
            if self._is_valid_tracking_code(tracking_code) or is_exception_ampliacion:
                cursor.execute(
                    """
                    SELECT id_diferido, tasa_mensual
                    FROM tarjeta_diferido
                    WHERE id_persona = %s AND id_tarjeta = %s AND numero_transaccion = %s
                    LIMIT 1
                    """,
                    (mov_tarjeta_data['id_persona'], mov_tarjeta_data['id_tarjeta'], tracking_code),
                )
                existing = cursor.fetchone()

            if existing:
                current_rate = float(existing.get('tasa_mensual') or 0)
                new_rate = tasa_mensual if tasa_mensual and abs(tasa_mensual - current_rate) > 0.000001 else current_rate
                # Update del seguimiento: no toca el historial ya insertado en movimiento_tarjeta.
                cursor.execute(
                    """
                    UPDATE tarjeta_diferido
                    SET id_movimiento_tarjeta = %s,
                        descripcion = %s,
                        valor_total = %s,
                        numero_cuotas = %s,
                        cuotas_pagadas = %s,
                        cuota_mensual = %s,
                        tasa_mensual = %s,
                        saldo_pendiente = %s,
                        fecha_proximo_pago = %s,
                        estado = %s
                    WHERE id_diferido = %s
                    """,
                    (
                        id_movimiento_tarjeta,
                        mov_tarjeta_data['nota'],
                        float(_q2(estimated_total)),
                        total_installments,
                        cuotas_pagadas,
                        float(_q2(cuota_mensual)),
                        new_rate,
                        float(_q2(saldo_pendiente)),
                        fecha_proximo_pago,
                        estado,
                        int(existing['id_diferido']),
                    ),
                )
                return

            cursor.execute(
                """
                INSERT INTO tarjeta_diferido
                    (id_tarjeta, id_persona, id_movimiento_tarjeta, descripcion, valor_total,
                     numero_cuotas, tasa_mensual, sin_interes, cuota_mensual, total_intereses,
                     total_pagado_estimado, cuotas_pagadas, saldo_pendiente, fecha_compra,
                     fecha_proximo_pago, estado, numero_transaccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    mov_tarjeta_data['id_tarjeta'],
                    mov_tarjeta_data['id_persona'],
                    id_movimiento_tarjeta,
                    mov_tarjeta_data['nota'],
                    float(_q2(estimated_total)),
                    total_installments,
                    tasa_mensual,
                    1 if tasa_mensual == 0 else 0,
                    float(_q2(cuota_mensual)),
                    float(_q2(total_intereses)),
                    float(_q2(total_pagado_estimado)),
                    cuotas_pagadas,
                    float(_q2(saldo_pendiente)),
                    fecha_compra,
                    fecha_proximo_pago,
                    estado,
                    tracking_code if (self._is_valid_tracking_code(tracking_code) or is_exception_ampliacion) else None,
                ),
            )
        finally:
            cursor.close()

    @classmethod
    def _validate_structure_static(cls, columns: List[str]) -> None:
        required_found = {k: False for k in cls.REQUIRED_COLUMNS}

        normalized_aliases = {
            key: {cls._normalize_text(alias) for alias in aliases}
            for key, aliases in cls.EXPECTED_COLUMNS.items()
        }

        for col in columns:
            col_normalized = cls._normalize_text(col)
            for key in cls.REQUIRED_COLUMNS:
                if col_normalized in normalized_aliases[key]:
                    required_found[key] = True

        missing = [k for k, v in required_found.items() if not v]
        if missing:
            raise ValueError(f"Columnas faltantes en Excel: {', '.join(missing)}")
    
    def process_file(
        self, 
        file_path: str,
        id_persona: int,
        id_tarjeta: int,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Procesa archivo Excel completo.
        
        Args:
            file_path: Ruta del archivo Excel
            id_persona: ID de la persona propietaria
            id_tarjeta: ID de la tarjeta de crédito
        
        Returns:
            Tupla (cantidad_insertada, lista_de_errores)
        """
        if not pd:
            raise ImportError("pandas es requerido para procesar archivos Excel")

        self._assert_tarjeta_activa(id_persona, id_tarjeta)
        
        try:
            # Detectar hoja correcta (puede haber varias hojas con cabecera en fila 0 o con filas de encabezado)
            df = self._read_best_sheet(file_path)
            if df is None or df.empty:
                return 0, [{"error": "Archivo Excel vacío o sin hojas con datos válidos"}]
            
            # Validar estructura
            self._validate_excel_structure(df.columns)
            
            # Mapear columnas
            col_map = self._map_columns(df.columns)
            
            # Procesar filas
            rows_to_insert: List[Dict[str, Any]] = []
            
            for idx, (_, row) in enumerate(df.iterrows(), start=2):  # start=2 para fila de header
                validation = self._validate_row(row, col_map, idx)
                
                if not validation.is_valid:
                    # Algunas entidades bancarias incluyen filas informativas con monto 0.
                    # Se omiten para no bloquear la carga mensual.
                    only_zero_amount = (
                        bool(validation.errors)
                        and all(err == "Monto debe ser diferente de cero" for err in validation.errors)
                    )
                    if only_zero_amount:
                        self.logger.info("[ETL] Fila %s omitida por monto igual a cero", idx)
                        continue

                    self.validation_errors.append({
                        "row": idx,
                        "errors": validation.errors,
                        "data": validation.data
                    })
                    self.error_count += 1
                    continue
                
                # Transformar datos
                transform = self._transform_row(
                    validation.data,
                    id_persona,
                    id_tarjeta,
                    idx
                )
                
                if not transform.is_valid:
                    self.validation_errors.append({
                        "row": idx,
                        "errors": transform.errors,
                        "data": validation.data
                    })
                    self.error_count += 1
                    continue
                
                rows_to_insert.append(transform.insert_movimiento_tarjeta)
            
            # Insertar en base de datos (transacción)
            if rows_to_insert:
                self._load_data(rows_to_insert)
                self.processed_count = len(rows_to_insert)
                self._reconcile_missing_diferidos(rows_to_insert, id_persona, id_tarjeta)

            # Auto-categorizar los movimientos recién insertados
            if self.processed_count > 0:
                self._auto_categorize(id_persona)

            return self.processed_count, self.validation_errors
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo: {e}")
            return 0, [{"error": f"Error de procesamiento: {str(e)}"}]

    def _reconcile_missing_diferidos(
        self,
        rows_to_insert: List[Dict[str, Any]],
        id_persona: int,
        id_tarjeta: int,
    ) -> None:
        """
        Cierra diferidos activos no reportados en el extracto importado.

        Reglas aplicadas:
        - Se validan únicamente códigos de autorización de filas realmente diferidas
          (tracking_should_track=True).
        - Si un diferido activo no aparece en esos códigos, se marca como pagado.
        - Si el ETL no trae ninguna fila diferida, se cierran todos los activos,
          asumiendo que ya no hay diferidos vigentes en el extracto.
        """
        if not rows_to_insert:
            return

        has_diferido_rows = any(bool(r.get('tracking_should_track')) for r in rows_to_insert)

        seen_codes: Set[str] = set()
        for r in rows_to_insert:
            if not r.get('tracking_should_track'):
                continue
            code = r.get('tracking_code')
            if self._is_valid_tracking_code(code) or bool(r.get('tracking_exception_ampliacion_plazo')):
                seen_codes.add(str(code).strip().upper())

        if has_diferido_rows and not seen_codes:
            # Llegaron filas diferidas pero sin código válido de autorización;
            # no se puede conciliar por ausencia de código sin riesgo.
            self.logger.warning(
                "[ETL] Diferidos detectados sin código de autorización válido; se omite conciliación por código"
            )
            return

        cursor = self.db.conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id_diferido, numero_transaccion
                FROM tarjeta_diferido
                WHERE id_persona = %s
                  AND id_tarjeta = %s
                  AND estado = 'activo'
                  AND numero_transaccion IS NOT NULL
                  AND numero_transaccion <> ''
                """,
                (id_persona, id_tarjeta),
            )
            candidates = cursor.fetchall() or []

            to_close_ids: List[int] = []
            for row in candidates:
                code = str(row[1] or '').strip().upper()
                if not code:
                    continue
                if not has_diferido_rows:
                    to_close_ids.append(int(row[0]))
                elif code not in seen_codes:
                    to_close_ids.append(int(row[0]))

            if to_close_ids:
                cursor.executemany(
                    """
                    UPDATE tarjeta_diferido
                    SET estado = 'pagado',
                        saldo_pendiente = 0,
                        fecha_proximo_pago = NULL,
                        cuotas_pagadas = numero_cuotas
                    WHERE id_diferido = %s
                    """,
                    [(x,) for x in to_close_ids],
                )
                self.logger.info(
                    "[ETL] Conciliacion diferidos: %d registro(s) cerrados como pagados",
                    len(to_close_ids),
                )
            self.db.conn.commit()
        finally:
            cursor.close()
    
    @classmethod
    def _read_best_sheet(cls, file_path: str):
        """Lee la hoja del Excel que contenga las columnas requeridas.
        
        Algunos extractos bancarios tienen varias hojas (DOLARES, PESOS, etc.).
        Intenta cada hoja y retorna el primer DataFrame con columnas válidas.
        También intenta detectar si el encabezado no está en la fila 0.
        """
        xl = pd.ExcelFile(file_path)
        first_non_empty = None
        for sheet in xl.sheet_names:
            # Intentar leer con header en fila 0
            df = pd.read_excel(file_path, sheet_name=sheet)
            if first_non_empty is None and not df.empty:
                first_non_empty = df
            if not df.empty:
                try:
                    cls._validate_structure_static(list(df.columns))
                    return df  # Esta hoja tiene columnas válidas
                except ValueError:
                    pass
            # Intentar con header en la primera fila que no sea NaN
            df_raw = pd.read_excel(file_path, sheet_name=sheet, header=None)
            if first_non_empty is None and not df_raw.empty and df_raw.notna().any().any():
                first_non_empty = df_raw
            for i in range(min(10, len(df_raw))):
                row_vals = [str(v).strip() for v in df_raw.iloc[i].tolist() if str(v) != 'nan']
                if not row_vals:
                    continue
                df_attempt = pd.read_excel(file_path, sheet_name=sheet, header=i)
                if first_non_empty is None and not df_attempt.empty:
                    first_non_empty = df_attempt
                try:
                    cls._validate_structure_static(list(df_attempt.columns))
                    return df_attempt
                except ValueError:
                    continue
        # Fallback: si hay datos pero no se detectó estructura perfecta,
        # retornar la primera hoja no vacía para generar errores más precisos.
        return first_non_empty

    def _validate_excel_structure(self, columns: List[str]) -> None:
        """Valida que el Excel tenga las columnas requeridas."""
        self._validate_structure_static(columns)
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Mapea las columnas del Excel a nombres estándar.
        
        Returns:
            Dict con mapeo: {'fecha': 'columna_encontrada', ...}
        """
        col_map = {}
        col_lower_list = [self._normalize_text(c) for c in columns]
        
        for standard_name, aliases in self.EXPECTED_COLUMNS.items():
            normalized_aliases = {self._normalize_text(alias) for alias in aliases}
            for i, col_lower in enumerate(col_lower_list):
                if col_lower in normalized_aliases:
                    col_map[standard_name] = columns[i]
                    break
        
        return col_map
    
    def _validate_row(
        self,
        row: Any,
        col_map: Dict[str, str],
        row_number: int
    ) -> ValidationResult:
        """Valida una fila individual del Excel."""
        result = ValidationResult(row_number=row_number)
        
        # Extraer valores

        fecha_str = str(row.get(col_map.get('fecha', ''), '')).strip()
        concepto = str(row.get(col_map.get('concepto', ''), '')).strip()
        # Valor original de la deuda
        valor_original_str = str(row.get(col_map.get('valor_original', ''), '')).strip()
        monto_str = str(row.get(col_map.get('monto', ''), '')).strip()
        cuotas_str = str(row.get(col_map.get('cuotas', '1'), '1')).strip()
        categoria = str(row.get(col_map.get('categoria', ''), '')).strip()
        referencia = self._normalize_reference(row.get(col_map.get('referencia', ''), ''))
        valor_cuota_raw = row.get(col_map.get('valor_cuota', ''), None)
        interes_mensual_raw = row.get(col_map.get('interes_mensual', ''), None)
        interes_anual_raw = row.get(col_map.get('interes_anual', ''), None)
        saldo_pendiente_raw = row.get(col_map.get('saldo_pendiente', ''), None)
        cargos_abonos_raw = row.get(col_map.get('cargos_abonos', ''), None)
        
        # Validar campos obligatorios
        if not concepto or concepto.lower() == 'nan':
            result.is_valid = False
            result.errors.append("Concepto es obligatorio")
        
        if not monto_str or monto_str.lower() == 'nan':
            result.is_valid = False
            result.errors.append("Monto es obligatorio")
        else:
            try:
                monto = self._parse_amount(monto_str)
                if monto == 0:
                    result.is_valid = False
                    result.errors.append("Monto debe ser diferente de cero")
            except ValueError:
                result.is_valid = False
                result.errors.append(f"Monto inválido: '{monto_str}'")
        
        # Validar fecha
        fecha = None
        if fecha_str and fecha_str.lower() != 'nan':
            try:
                # Intentar parseo
                if isinstance(row.get(col_map.get('fecha', '')), pd.Timestamp):
                    fecha = pd.Timestamp(row.get(col_map.get('fecha', ''))).date()
                else:
                    fecha = pd.to_datetime(fecha_str, dayfirst=True).date()
            except Exception:
                result.is_valid = False
                result.errors.append(f"Fecha inválida: '{fecha_str}'")
        else:
            fecha = datetime.date.today()
        
        # Validar cuotas
        try:
            cuota_actual, cuotas = self._parse_installment_progress(cuotas_str)
        except ValueError as exc:
            result.is_valid = False
            if str(exc) in ('Cuotas debe estar entre 1 y 36', 'Cuotas inválida: progreso mayor al total'):
                result.errors.append(str(exc))
            else:
                result.errors.append(f"Cuotas inválida: '{cuotas_str}'")
            cuota_actual = 1
            cuotas = 1

        try:
            valor_cuota = self._parse_optional_amount(valor_cuota_raw)
        except ValueError:
            result.is_valid = False
            result.errors.append(f"Valor cuota inválido: '{valor_cuota_raw}'")
            valor_cuota = None

        try:
            tasa_mensual = self._parse_optional_rate(interes_mensual_raw, interes_anual_raw)
        except ValueError:
            result.is_valid = False
            result.errors.append("Tasa de interés inválida")
            tasa_mensual = None

        try:
            saldo_pendiente = self._parse_optional_amount(saldo_pendiente_raw)
        except ValueError:
            result.is_valid = False
            result.errors.append(f"Saldo pendiente inválido: '{saldo_pendiente_raw}'")
            saldo_pendiente = None
        
        # Validar categoría
        if not categoria or categoria.lower() == 'nan':
            categoria = None
        
        if result.is_valid:
            result.data = {
                'fecha': fecha,
                'concepto': concepto,
                'monto': monto,
                'valor_original': valor_original_str,
                'cuota_actual': cuota_actual,
                'cuotas': cuotas,
                'categoria': categoria,
                'referencia': referencia,
                'valor_cuota': valor_cuota,
                'tasa_mensual': tasa_mensual,
                'saldo_pendiente': saldo_pendiente,
                'cargos_abonos': cargos_abonos_raw,
            }
        
        return result
    
    def _transform_row(
        self,
        validated_data: Dict[str, Any],
        id_persona: int,
        id_tarjeta: int,
        row_number: int
    ) -> TransformResult:
        """Transforma datos validados a formato de base de datos."""
        result = TransformResult()
        
        try:
            # Generar códigos únicos
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            referencia_raw = validated_data.get('referencia')
            nota = validated_data['concepto']
            is_exception_ampliacion = self._is_tracking_exception_ampliacion_plazo(referencia_raw, nota)
            tracking_code = referencia_raw if (self._is_valid_tracking_code(referencia_raw) or is_exception_ampliacion) else None
            numero_transaccion = tracking_code or f"TRX-{timestamp}-{row_number}"
            # La descripción debe conservar únicamente el concepto del extracto.
            is_diferido = float(validated_data['monto']) > 0 and int(validated_data['cuotas']) > 1
            # Para consolidar diferidos y cambiar estado correctamente, el número de autorización es obligatorio.
            should_track_diferido = is_diferido and (tracking_code is not None)
            estado_movimiento = 'diferido' if is_diferido else ('compra' if float(validated_data['monto']) > 0 else 'abono')

            if is_diferido and tracking_code is None:
                self.logger.warning(
                    "[ETL] Diferido sin número de autorización válido en fila %s; se carga movimiento sin tracking consolidado",
                    row_number,
                )
            
            # Usar siempre el valor original cuando sea válido para el tracking consolidado.
            # Algunos extractos traen formato bancario (ej. 215,000.00-), por eso se parsea igual que monto.
            valor_base = validated_data.get('monto')
            valor_original_raw = validated_data.get('valor_original')
            if valor_original_raw not in (None, '', 'nan', 'NaN'):
                try:
                    valor_base = self._parse_amount(valor_original_raw)
                except ValueError:
                    # Si valor_original no es parseable, conservar monto ya validado.
                    pass

            valor_original_num = abs(float(valor_base))
            # Para la grilla de movimientos, el valor debe reflejar la cuota/cargo reportado
            # por el extracto (monto), no el saldo a diferir acumulado.
            valor_movimiento = abs(float(validated_data['monto']))

            # Preparar INSERT para tabla movimiento_tarjeta
            result.insert_movimiento_tarjeta = {
                'id_tarjeta': id_tarjeta,
                'id_persona': id_persona,
                'fecha': validated_data['fecha'],
                'valor': valor_movimiento,
                'estado': estado_movimiento,
                'nota': nota,
                'numero_transaccion': numero_transaccion,
                'id_categoria': None,
                'id_beneficiario': None,
                'saldo': valor_movimiento,
                'cuotas': validated_data['cuotas'],
                'tracking_should_track': should_track_diferido,
                'tracking_code': tracking_code,
                'tracking_exception_ampliacion_plazo': is_exception_ampliacion,
                'tracking_current_installment': validated_data.get('cuota_actual') or 1,
                'tracking_total_installments': validated_data['cuotas'],
                'tracking_payment_value': validated_data.get('valor_cuota') or abs(float(validated_data['monto'])),
                'tracking_original_value': valor_original_num,
                'tracking_monthly_rate': validated_data.get('tasa_mensual'),
                'tracking_remaining_balance': validated_data.get('saldo_pendiente'),
            }
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Error transformando datos: {str(e)}")
        
        return result
    
    def _load_data(self, rows: List[Dict[str, Any]]) -> None:
        """
        Carga datos en base de datos con transacción.
        
        Args:
            rows: Lista de registros para movimiento_tarjeta
        """
        cursor = None
        try:
            cursor = self.db.conn.cursor()
            
            for mov_tarjeta_data in rows:
                # INSERT en movimiento_tarjeta (SQL estático para evitar construcción dinámica)
                tarjeta_values = (
                    mov_tarjeta_data['id_tarjeta'],
                    mov_tarjeta_data['id_persona'],
                    mov_tarjeta_data['fecha'],
                    mov_tarjeta_data['valor'],
                    mov_tarjeta_data['estado'],
                    mov_tarjeta_data['nota'],
                    mov_tarjeta_data['numero_transaccion'],
                    mov_tarjeta_data['id_categoria'],
                    mov_tarjeta_data['id_beneficiario'],
                    mov_tarjeta_data['saldo'],
                    mov_tarjeta_data['cuotas'],
                )

                cursor.execute(self.INSERT_MOVIMIENTO_TARJETA_SQL, tarjeta_values)
                id_movimiento_tarjeta = int(cursor.lastrowid)

                self._sync_diferido_tracking(mov_tarjeta_data, id_movimiento_tarjeta)
            
            self.db.conn.commit()
            self.logger.info(f"Cargados {len(rows)} registros exitosamente")
            
        except Exception as e:
            self.db.conn.rollback()
            self.logger.error(f"Error durante carga de datos: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def _auto_categorize(self, id_persona: int) -> None:
        """Aplica las reglas de optimización tras cada importación (silencioso)."""
        try:
            from .optimizacion_categorias import OptimizacionCategoriasService
            svc = OptimizacionCategoriasService(self.db)
            updated = svc.aplicar_reglas(id_persona)
            if updated:
                self.logger.info(
                    "[ETL] Auto-categorización: %d movimiento(s) actualizados", updated
                )
        except Exception as exc:
            self.logger.warning("[ETL] Auto-categorización omitida: %s", exc)

    def process_folder(
        self,
        folder_path: str,
        id_persona: int,
        id_tarjeta: int,
    ) -> Dict[str, Any]:
        """
        Procesa todos los archivos Excel de una carpeta en orden cronológico.

        Ordena los archivos por nombre (ej. 3495_JUN2024.xlsx, 3495_JUL2024.xlsx...)
        Ignora archivos que no sean .xlsx / .xls.

        Returns:
            Dict con resumen: { total_archivos, total_insertados, total_errores, detalle }
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            return {'error': f'La carpeta no existe: {folder_path}'}

        try:
            self._assert_tarjeta_activa(id_persona, id_tarjeta)
        except ValueError as exc:
            return {'error': str(exc)}

        archivos = sorted(
            [f for f in folder.iterdir() if f.suffix.lower() in ('.xlsx', '.xls')],
            key=lambda f: f.name
        )

        if not archivos:
            return {'error': 'No se encontraron archivos Excel en la carpeta'}

        resumen: Dict[str, Any] = {
            'total_archivos': len(archivos),
            'total_insertados': 0,
            'total_errores': 0,
            'detalle': [],
        }

        for archivo in archivos:
            self.validation_errors = []
            self.processed_count = 0
            self.error_count = 0

            try:
                insertados, errores = self.process_file(
                    str(archivo), id_persona, id_tarjeta
                )
                resumen['total_insertados'] += insertados
                resumen['total_errores'] += len(errores)
                resumen['detalle'].append({
                    'archivo': archivo.name,
                    'insertados': insertados,
                    'errores': len(errores),
                    'detalle_errores': errores[:5],
                })
                self.logger.info(
                    "[ETL folder] %s -> %d insertados, %d errores",
                    archivo.name, insertados, len(errores)
                )
            except Exception as exc:
                resumen['total_errores'] += 1
                resumen['detalle'].append({
                    'archivo': archivo.name,
                    'insertados': 0,
                    'errores': 1,
                    'detalle_errores': [{'error': str(exc)}],
                })
                self.logger.error("[ETL folder] Error en %s: %s", archivo.name, exc)

        return resumen


def validate_excel_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validación rápida de archivo Excel.
    
    Returns:
        Tupla (is_valid, list_of_errors)
    """
    if not pd:
        return False, ["pandas es requerido"]
    
    errors = []
    
    try:
        df = ETLTarjetaCredito._read_best_sheet(file_path)
        
        if df is None or df.empty:
            errors.append("Archivo Excel vacío o sin hojas con datos válidos")
            return False, errors
        
        return True, []
        
    except Exception as e:
        return False, [f"Error leyendo archivo: {str(e)}"]
