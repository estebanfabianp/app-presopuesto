"""Rutas API de presupuesto con soporte de hoja detallada anual y mensual."""

import calendar
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('presupuesto', __name__, url_prefix='/api/presupuesto')
logger = logging.getLogger(__name__)

FRECUENCIAS_VALIDAS = {
    'ninguno', 'diario', 'semanal', 'quincenal', 'mensualmente',
    'bimensual', 'trimestral', 'semestral', 'anual'
}

MONTH_NAMES_ES = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _normalize_periodo(periodo: Optional[str]) -> str:
    periodo_normalizado = (periodo or 'mensual').strip().lower()
    if periodo_normalizado not in {'anual', 'mensual', 'trimestral', 'personalizado'}:
        return 'mensual'
    return periodo_normalizado


def _infer_periodo(fecha_inicio, fecha_fin) -> str:
    if not fecha_inicio or not fecha_fin:
        return 'mensual'
    dias = (fecha_fin - fecha_inicio).days
    if dias <= 35:
        return 'mensual'
    if dias <= 100:
        return 'trimestral'
    if dias <= 370:
        return 'anual'
    return 'personalizado'


def _period_bounds(year: int, periodo: str, month: Optional[int] = None) -> Tuple[date, date]:
    if periodo == 'anual':
        return date(year, 1, 1), date(year, 12, 31)
    if periodo == 'mensual':
        month = int(month or 1)
        month = max(1, min(12, month))
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)
    if periodo == 'trimestral':
        quarter = max(1, min(4, int(month or 1)))
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        last_day = calendar.monthrange(year, end_month)[1]
        return date(year, start_month, 1), date(year, end_month, last_day)
    return date(year, 1, 1), date(year, 12, 31)


def _default_budget_name(periodo: str, year: int, month: Optional[int] = None) -> str:
    if periodo == 'anual':
        return f"Presupuesto {year}"
    if periodo == 'mensual':
        month_idx = max(1, min(12, int(month or 1)))
        month_name = MONTH_NAMES_ES.get(month_idx, 'Mes')
        return f"{month_name} {year}"
    return f"Presupuesto {periodo} {year}"


def _ensure_presupuesto_detalle_schema(db: DatabaseConnector) -> None:
    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS presupuesto_detalle (
            id_detalle INT NOT NULL AUTO_INCREMENT,
            id_presupuesto INT NOT NULL,
            id_categoria INT NULL,
            categoria_nombre VARCHAR(150) NULL,
            frecuencia VARCHAR(30) NOT NULL DEFAULT 'Ninguno',
            tolerancia_pct DECIMAL(6,2) NOT NULL DEFAULT 10.00,
            monto_importe DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            monto_estimado DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            notas TEXT NULL,
            orden INT NOT NULL DEFAULT 0,
            fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id_detalle),
            KEY idx_presupuesto_detalle_presupuesto (id_presupuesto),
            KEY idx_presupuesto_detalle_categoria (id_categoria),
            CONSTRAINT fk_presupuesto_detalle_presupuesto
                FOREIGN KEY (id_presupuesto) REFERENCES presupuesto(id_presupuesto)
                ON DELETE CASCADE,
            CONSTRAINT fk_presupuesto_detalle_categoria
                FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
                ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
    )
    cols = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'presupuesto_detalle'
          AND COLUMN_NAME = 'tolerancia_pct'
        """
    )
    if not cols or int(cols[0].get('total') or 0) == 0:
        db.execute_non_query(
            "ALTER TABLE presupuesto_detalle ADD COLUMN tolerancia_pct DECIMAL(6,2) NOT NULL DEFAULT 10.00 AFTER frecuencia"
        )


def _resolve_categoria_id(db: DatabaseConnector, categoria_nombre: Optional[str]):
    if not categoria_nombre:
        return None
    rows = db.execute_query(
        "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (categoria_nombre.strip(),),
    )
    if rows:
        return rows[0]['id_categoria']
    return db.execute_non_query(
        "INSERT INTO categoria (nombre) VALUES (%s)",
        (categoria_nombre.strip(),),
    )


def _fetch_presupuesto_row(db: DatabaseConnector, user_id: int, presupuesto_id: int):
    rows = db.execute_query(
        """
        SELECT
            p.id_presupuesto,
            p.nombre,
            p.descripcion,
            p.monto_total,
            p.fecha_inicio,
            p.fecha_fin,
            GROUP_CONCAT(c.nombre ORDER BY c.nombre SEPARATOR ', ') AS categorias
        FROM presupuesto p
        LEFT JOIN presupuesto_categoria pc ON p.id_presupuesto = pc.id_presupuesto
        LEFT JOIN categoria c ON pc.id_categoria = c.id_categoria
        WHERE p.id_presupuesto = %s AND p.id_persona = %s
        GROUP BY p.id_presupuesto, p.nombre, p.descripcion, p.monto_total, p.fecha_inicio, p.fecha_fin
        LIMIT 1
        """,
        (presupuesto_id, user_id),
    )
    return rows[0] if rows else None


def _find_presupuesto_by_period(
    db: DatabaseConnector,
    user_id: int,
    start_date: date,
    end_date: date,
):
    rows = db.execute_query(
        """
        SELECT id_presupuesto
        FROM presupuesto
        WHERE id_persona = %s AND fecha_inicio = %s AND fecha_fin = %s
        ORDER BY id_presupuesto DESC
        LIMIT 1
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    if not rows:
        return None
    return _fetch_presupuesto_row(db, user_id, rows[0]['id_presupuesto'])


def _serialize_presupuesto_row(row: Optional[dict]) -> Optional[dict]:
    if not row:
        return None
    return {
        'id': row['id_presupuesto'],
        'nombre': row.get('nombre') or f"Presupuesto {row['id_presupuesto']}",
        'descripcion': row.get('descripcion'),
        'categoria': row.get('categorias') or 'General',
        'monto': float(row.get('monto_total') or 0),
        'periodo': _infer_periodo(row.get('fecha_inicio'), row.get('fecha_fin')),
        'fecha_inicio': row.get('fecha_inicio').isoformat() if row.get('fecha_inicio') else None,
        'fecha_fin': row.get('fecha_fin').isoformat() if row.get('fecha_fin') else None,
        'activo': True,
    }


def _normalize_lines(lines: Optional[List[dict]]) -> List[dict]:
    normalized = []
    for idx, line in enumerate(lines or []):
        categoria = (line.get('categoria') or line.get('categoria_nombre') or '').strip()
        frecuencia = (line.get('frecuencia') or 'Ninguno').strip()
        if frecuencia.lower() not in FRECUENCIAS_VALIDAS:
            frecuencia = 'Ninguno'

        importe = float(line.get('importe', line.get('monto_importe', 0)) or 0)
        estimado = float(line.get('estimado', line.get('monto_estimado', importe)) or 0)
        notas = (line.get('notas') or '').strip() or None

        if not categoria and not importe and not estimado and not notas:
            continue

        normalized.append(
            {
                'categoria': categoria or 'Sin categoría',
                'frecuencia': frecuencia.capitalize() if frecuencia.lower() != 'mensualmente' else 'Mensualmente',
                'tolerancia': round(float(line.get('tolerancia', line.get('tolerancia_pct', 10)) or 10), 2),
                'importe': round(importe, 2),
                'estimado': round(estimado, 2),
                'notas': notas,
                'orden': int(line.get('orden', idx)),
            }
        )
    return normalized


def _sync_budget_categories(db: DatabaseConnector, presupuesto_id: int, lines: List[dict]) -> None:
    db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
    seen = set()
    for line in lines:
        categoria = line.get('categoria')
        if not categoria or categoria.lower() == 'sin categoría':
            continue
        categoria_id = _resolve_categoria_id(db, categoria)
        if categoria_id and categoria_id not in seen:
            db.execute_non_query(
                "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                (presupuesto_id, categoria_id),
            )
            seen.add(categoria_id)


def _save_budget_lines(db: DatabaseConnector, presupuesto_id: int, lines: List[dict]) -> float:
    _ensure_presupuesto_detalle_schema(db)
    db.execute_non_query("DELETE FROM presupuesto_detalle WHERE id_presupuesto = %s", (presupuesto_id,))

    total_estimado = 0.0
    for idx, line in enumerate(lines):
        categoria_id = None
        categoria = line.get('categoria') or 'Sin categoría'
        if categoria.lower() != 'sin categoría':
            categoria_id = _resolve_categoria_id(db, categoria)

        importe = float(line.get('importe') or 0)
        estimado = float(line.get('estimado', importe) or 0)
        total_estimado += estimado

        db.execute_non_query(
            """
            INSERT INTO presupuesto_detalle (
                id_presupuesto, id_categoria, categoria_nombre, frecuencia,
                tolerancia_pct, monto_importe, monto_estimado, notas, orden
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                presupuesto_id,
                categoria_id,
                categoria,
                line.get('frecuencia') or 'Ninguno',
                float(line.get('tolerancia', 10) or 10),
                importe,
                estimado,
                line.get('notas'),
                int(line.get('orden', idx)),
            ),
        )

    _sync_budget_categories(db, presupuesto_id, lines)
    return round(total_estimado, 2)


def _fetch_real_totals(db: DatabaseConnector, user_id: int, start_date: date, end_date: date) -> Dict[str, float]:
    totals: Dict[str, float] = {}

    movimiento_rows = db.execute_query(
        """
        SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
        WHERE cu.id_persona = %s
          AND LOWER(tm.nombre) = 'gasto'
          AND DATE(m.fecha_creacion) BETWEEN %s AND %s
        GROUP BY COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    for row in movimiento_rows or []:
        key = (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    tarjeta_rows = db.execute_query(
        """
        SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(ABS(mt.valor)), 0) AS total
        FROM movimiento_tarjeta mt
        LEFT JOIN categoria c ON c.id_categoria = mt.id_categoria
        WHERE mt.id_persona = %s
          AND DATE(mt.fecha) BETWEEN %s AND %s
        GROUP BY COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    for row in tarjeta_rows or []:
        key = (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    return totals


def _fetch_budget_lines(
    db: DatabaseConnector,
    presupuesto_id: int,
    user_id: int,
    start_date: date,
    end_date: date,
) -> List[dict]:
    _ensure_presupuesto_detalle_schema(db)
    rows = db.execute_query(
        """
        SELECT
            pd.id_detalle,
            pd.id_categoria,
            pd.categoria_nombre,
            pd.frecuencia,
            pd.tolerancia_pct,
            pd.monto_importe,
            pd.monto_estimado,
            pd.notas,
            pd.orden,
            c.nombre AS categoria_catalogo
        FROM presupuesto_detalle pd
        LEFT JOIN categoria c ON c.id_categoria = pd.id_categoria
        WHERE pd.id_presupuesto = %s
        ORDER BY pd.orden, pd.id_detalle
        """,
        (presupuesto_id,),
    )
    reales = _fetch_real_totals(db, user_id, start_date, end_date)

    lines = []
    for row in rows or []:
        categoria = row.get('categoria_catalogo') or row.get('categoria_nombre') or 'Sin categoría'
        real = round(reales.get(categoria.strip().lower(), 0.0), 2)
        estimado = float(row.get('monto_estimado') or 0)
        lines.append(
            {
                'id_detalle': row['id_detalle'],
                'id_categoria': row.get('id_categoria'),
                'categoria': categoria,
                'frecuencia': row.get('frecuencia') or 'Ninguno',
                'tolerancia': float(row.get('tolerancia_pct') or 10),
                'importe': float(row.get('monto_importe') or 0),
                'estimado': estimado,
                'real': real,
                'diferencia': round(estimado - real, 2),
                'notas': row.get('notas') or '',
                'orden': int(row.get('orden') or 0),
            }
        )
    return lines


def _sheet_response(
    db: DatabaseConnector,
    user_id: int,
    row: Optional[dict],
    year: int,
    periodo: str,
    month: Optional[int] = None,
    derived_from: Optional[dict] = None,
) -> dict:
    start_date, end_date = _period_bounds(year, periodo, month)
    serialized = _serialize_presupuesto_row(row)
    if row:
        lines = _fetch_budget_lines(db, row['id_presupuesto'], user_id, start_date, end_date)
    elif derived_from:
        annual_lines = _fetch_budget_lines(db, derived_from['id_presupuesto'], user_id, date(year, 1, 1), date(year, 12, 31))
        real_totals = _fetch_real_totals(db, user_id, start_date, end_date)
        lines = []
        for idx, line in enumerate(annual_lines):
            estimado = round(float(line['estimado']) / 12, 2)
            importe = round(float(line['importe']) / 12, 2)
            categoria = line['categoria']
            real = round(real_totals.get(categoria.strip().lower(), 0.0), 2)
            lines.append(
                {
                    'id_detalle': None,
                    'id_categoria': line.get('id_categoria'),
                    'categoria': categoria,
                    'frecuencia': line.get('frecuencia') or 'Mensualmente',
                    'importe': importe,
                    'estimado': estimado,
                    'real': real,
                    'diferencia': round(estimado - real, 2),
                    'notas': line.get('notas') or '',
                    'orden': idx,
                }
            )
    else:
        lines = []

    resumen = {
        'importe_total': round(sum(float(line.get('importe') or 0) for line in lines), 2),
        'estimado_total': round(sum(float(line.get('estimado') or 0) for line in lines), 2),
        'real_total': round(sum(float(line.get('real') or 0) for line in lines), 2),
    }
    resumen['diferencia_total'] = round(resumen['estimado_total'] - resumen['real_total'], 2)

    return {
        'presupuesto': serialized,
        'periodo': periodo,
        'year': year,
        'month': month,
        'fecha_inicio': start_date.isoformat(),
        'fecha_fin': end_date.isoformat(),
        'nombre_sugerido': serialized['nombre'] if serialized else _default_budget_name(periodo, year, month),
        'lineas': lines,
        'resumen': resumen,
        'derivado_desde_anual': _serialize_presupuesto_row(derived_from) if derived_from else None,
    }


@bp.route('', methods=['GET'])
def list_presupuestos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            """
            SELECT
                p.id_presupuesto,
                p.nombre,
                p.descripcion,
                p.monto_total,
                p.fecha_inicio,
                p.fecha_fin,
                GROUP_CONCAT(c.nombre ORDER BY c.nombre SEPARATOR ', ') AS categorias
            FROM presupuesto p
            LEFT JOIN presupuesto_categoria pc ON p.id_presupuesto = pc.id_presupuesto
            LEFT JOIN categoria c ON pc.id_categoria = c.id_categoria
            WHERE p.id_persona = %s
            GROUP BY p.id_presupuesto, p.nombre, p.descripcion, p.monto_total, p.fecha_inicio, p.fecha_fin
            ORDER BY p.fecha_inicio DESC, p.id_presupuesto DESC
            """,
            (user_id,),
        )
        return jsonify([_serialize_presupuesto_row(row) for row in rows]), 200
    except Exception as e:
        logger.error("Error listando presupuestos: %s", e)
        return jsonify({'message': 'Error al listar presupuestos'}), 500
    finally:
        db.close()


@bp.route('/hoja', methods=['GET'])
def get_presupuesto_sheet():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        year = int(request.args.get('year', date.today().year))
        periodo = _normalize_periodo(request.args.get('periodo', 'anual'))
        month = request.args.get('month', type=int)

        start_date, end_date = _period_bounds(year, periodo, month)
        row = _find_presupuesto_by_period(db, user_id, start_date, end_date)
        derived_from = None
        if not row and periodo == 'mensual':
            derived_from = _find_presupuesto_by_period(db, user_id, date(year, 1, 1), date(year, 12, 31))
        return jsonify(_sheet_response(db, user_id, row, year, periodo, month, derived_from)), 200
    except Exception as e:
        logger.error("Error obteniendo hoja de presupuesto: %s", e)
        return jsonify({'message': 'Error al obtener hoja de presupuesto'}), 500
    finally:
        db.close()


@bp.route('/hoja', methods=['POST'])
def save_presupuesto_sheet():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        periodo = _normalize_periodo(payload.get('periodo', 'anual'))
        year = int(payload.get('year') or date.today().year)
        month = payload.get('month')
        month = int(month) if month not in (None, '') else None
        start_date, end_date = _period_bounds(year, periodo, month)
        normalized_lines = _normalize_lines(payload.get('lineas'))

        presupuesto_id = payload.get('presupuesto_id')
        existing = None
        if presupuesto_id:
            existing = _fetch_presupuesto_row(db, user_id, int(presupuesto_id))
        if not existing:
            existing = _find_presupuesto_by_period(db, user_id, start_date, end_date)

        nombre = (payload.get('nombre') or '').strip() or _default_budget_name(periodo, year, month)
        descripcion = (payload.get('descripcion') or '').strip() or None
        total_estimado = round(sum(float(line.get('estimado') or 0) for line in normalized_lines), 2)

        if existing:
            presupuesto_id = existing['id_presupuesto']
            db.execute_non_query(
                """
                UPDATE presupuesto
                SET nombre = %s,
                    descripcion = %s,
                    monto_total = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s
                WHERE id_presupuesto = %s AND id_persona = %s
                """,
                (nombre, descripcion, total_estimado, start_date.isoformat(), end_date.isoformat(), presupuesto_id, user_id),
            )
        else:
            presupuesto_id = db.execute_non_query(
                """
                INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (nombre, descripcion, total_estimado, start_date.isoformat(), end_date.isoformat(), user_id),
            )
            if not presupuesto_id:
                return jsonify({'message': 'No se pudo guardar la hoja de presupuesto'}), 500

        total_guardado = _save_budget_lines(db, presupuesto_id, normalized_lines)
        db.execute_non_query(
            "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
            (total_guardado, presupuesto_id, user_id),
        )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_sheet_response(db, user_id, row, year, periodo, month)), 200
    except Exception as e:
        logger.error("Error guardando hoja de presupuesto: %s", e)
        return jsonify({'message': 'Error al guardar hoja de presupuesto'}), 500
    finally:
        db.close()


@bp.route('/hoja/derivar', methods=['POST'])
def derive_monthly_sheet():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        year = int(payload.get('year') or date.today().year)
        month = int(payload.get('month') or date.today().month)
        overwrite = bool(payload.get('overwrite', False))

        annual_row = _find_presupuesto_by_period(db, user_id, date(year, 1, 1), date(year, 12, 31))
        if not annual_row:
            return jsonify({'message': 'No existe un presupuesto anual para ese año'}), 404

        annual_lines = _fetch_budget_lines(db, annual_row['id_presupuesto'], user_id, date(year, 1, 1), date(year, 12, 31))
        if not annual_lines:
            return jsonify({'message': 'El presupuesto anual no tiene líneas para derivar'}), 400

        start_date, end_date = _period_bounds(year, 'mensual', month)
        monthly_row = _find_presupuesto_by_period(db, user_id, start_date, end_date)
        if monthly_row and not overwrite:
            return jsonify({'message': 'El presupuesto mensual ya existe para ese periodo'}), 409

        derived_lines = []
        for idx, line in enumerate(annual_lines):
            derived_lines.append(
                {
                    'categoria': line['categoria'],
                    'frecuencia': line.get('frecuencia') or 'Mensualmente',
                    'importe': round(float(line['importe']) / 12, 2),
                    'estimado': round(float(line['estimado']) / 12, 2),
                    'notas': line.get('notas') or '',
                    'orden': idx,
                }
            )

        nombre = payload.get('nombre') or _default_budget_name('mensual', year, month)
        descripcion = payload.get('descripcion') or f"Derivado de {_serialize_presupuesto_row(annual_row)['nombre']}"

        if monthly_row:
            presupuesto_id = monthly_row['id_presupuesto']
            db.execute_non_query(
                """
                UPDATE presupuesto
                SET nombre = %s,
                    descripcion = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s
                WHERE id_presupuesto = %s AND id_persona = %s
                """,
                (nombre, descripcion, start_date.isoformat(), end_date.isoformat(), presupuesto_id, user_id),
            )
        else:
            presupuesto_id = db.execute_non_query(
                """
                INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (nombre, descripcion, 0, start_date.isoformat(), end_date.isoformat(), user_id),
            )

        total_guardado = _save_budget_lines(db, presupuesto_id, derived_lines)
        db.execute_non_query(
            "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
            (total_guardado, presupuesto_id, user_id),
        )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_sheet_response(db, user_id, row, year, 'mensual', month)), 200
    except Exception as e:
        logger.error("Error derivando presupuesto mensual: %s", e)
        return jsonify({'message': 'Error al derivar presupuesto mensual'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['GET'])
def get_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        row = _fetch_presupuesto_row(db, _get_user_id(), presupuesto_id)
        if not row:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error obteniendo presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al obtener presupuesto'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_presupuesto():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        nombre = payload.get('nombre') or f"Presupuesto {date.today().isoformat()}"
        descripcion = payload.get('descripcion')
        monto = float(payload.get('monto', payload.get('monto_total', 0)) or 0)
        periodo = _normalize_periodo(payload.get('periodo'))

        fecha_inicio = payload.get('fecha_inicio') or date.today().isoformat()
        if payload.get('fecha_fin'):
            fecha_fin = payload['fecha_fin']
        elif periodo == 'trimestral':
            fecha_fin = (date.today() + timedelta(days=90)).isoformat()
        elif periodo == 'anual':
            fecha_fin = (date.today() + timedelta(days=365)).isoformat()
        else:
            fecha_fin = (date.today() + timedelta(days=30)).isoformat()

        presupuesto_id = db.execute_non_query(
            """
            INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (nombre, descripcion, monto, fecha_inicio, fecha_fin, user_id),
        )
        if not presupuesto_id:
            return jsonify({'message': 'No se pudo crear el presupuesto'}), 500

        lineas = _normalize_lines(payload.get('lineas'))
        if lineas:
            total_guardado = _save_budget_lines(db, presupuesto_id, lineas)
            db.execute_non_query(
                "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
                (total_guardado, presupuesto_id, user_id),
            )
        else:
            categoria_nombre = payload.get('categoria')
            categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
            if categoria_id:
                db.execute_non_query(
                    "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                    (presupuesto_id, categoria_id),
                )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error creando presupuesto: %s", e)
        return jsonify({'message': 'Error al crear presupuesto'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['PUT'])
def update_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        existing = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        if not existing:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

        db.execute_non_query(
            """
            UPDATE presupuesto
            SET nombre = COALESCE(%s, nombre),
                descripcion = COALESCE(%s, descripcion),
                monto_total = COALESCE(%s, monto_total),
                fecha_inicio = COALESCE(%s, fecha_inicio),
                fecha_fin = COALESCE(%s, fecha_fin)
            WHERE id_presupuesto = %s AND id_persona = %s
            """,
            (
                payload.get('nombre'),
                payload.get('descripcion'),
                payload.get('monto'),
                payload.get('fecha_inicio'),
                payload.get('fecha_fin'),
                presupuesto_id,
                user_id,
            ),
        )

        lineas = _normalize_lines(payload.get('lineas'))
        if lineas:
            total_guardado = _save_budget_lines(db, presupuesto_id, lineas)
            db.execute_non_query(
                "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
                (total_guardado, presupuesto_id, user_id),
            )
        else:
            categoria_nombre = payload.get('categoria')
            categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
            if categoria_id:
                db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
                db.execute_non_query(
                    "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                    (presupuesto_id, categoria_id),
                )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error actualizando presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al actualizar presupuesto'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['DELETE'])
def delete_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        if not exists:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

        _ensure_presupuesto_detalle_schema(db)
        db.execute_non_query("DELETE FROM presupuesto_detalle WHERE id_presupuesto = %s", (presupuesto_id,))
        db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
        db.execute_non_query(
            "DELETE FROM presupuesto WHERE id_presupuesto = %s AND id_persona = %s",
            (presupuesto_id, user_id),
        )
        return jsonify({'message': 'Presupuesto eliminado'}), 200
    except Exception as e:
        logger.error("Error eliminando presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al eliminar presupuesto'}), 500
    finally:
        db.close()
