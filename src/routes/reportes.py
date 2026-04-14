"""Rutas API de Reportes con datos reales desde MySQL."""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')

logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _parse_int_arg(name: str) -> Optional[int]:
    value = request.args.get(name)
    if value in (None, '', 'null', 'undefined'):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_iso_date(value: Optional[str], fallback: date) -> date:
    if not value:
        return fallback
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return fallback


def _normalize_filters():
    today = date.today()
    year = int(request.args.get('year', today.year))
    default_start = date(year, 1, 1)
    default_end = date(year, 12, 31)

    raw_start = request.args.get('start_date') or None
    raw_end = request.args.get('end_date') or None
    explicit_range = bool(raw_start or raw_end)

    start_dt = _parse_iso_date(raw_start, default_start)
    end_dt = _parse_iso_date(raw_end, default_end)
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt

    if explicit_range:
        total_days = (end_dt - start_dt).days + 1
        compare_end_dt = start_dt - timedelta(days=1)
        compare_start_dt = compare_end_dt - timedelta(days=total_days - 1)
        compare_label = 'vs periodo anterior'
    else:
        compare_start_dt = date(year - 1, 1, 1)
        compare_end_dt = date(year - 1, 12, 31)
        compare_label = f'vs {year - 1}'

    return {
        'year': year,
        'start_date': start_dt.isoformat(),
        'end_date': end_dt.isoformat(),
        'compare_start_date': compare_start_dt.isoformat(),
        'compare_end_date': compare_end_dt.isoformat(),
        'compare_label': compare_label,
        'cuenta_id': _parse_int_arg('cuenta_id'),
        'categoria_id': _parse_int_arg('categoria_id'),
        'beneficiario_id': _parse_int_arg('beneficiario_id'),
    }


def _pct_change(current: float, previous: float):
    current = float(current or 0)
    previous = float(previous or 0)
    if abs(previous) < 1e-9:
        return 0.0 if abs(current) < 1e-9 else None
    return round(((current - previous) / abs(previous)) * 100, 2)


def _movement_conditions(filters, user_id: int, start_key='start_date', end_key='end_date'):
    conditions = [
        'c.id_persona = %s',
        'DATE(m.fecha_creacion) BETWEEN %s AND %s',
    ]
    params = [user_id, filters[start_key], filters[end_key]]

    if filters.get('cuenta_id'):
        conditions.append('c.id_cuenta = %s')
        params.append(filters['cuenta_id'])
    if filters.get('categoria_id'):
        conditions.append('m.id_categoria = %s')
        params.append(filters['categoria_id'])
    if filters.get('beneficiario_id'):
        conditions.append('m.id_beneficiario = %s')
        params.append(filters['beneficiario_id'])

    return conditions, params


def _card_conditions(filters, user_id: int, start_key='start_date', end_key='end_date'):
    conditions = [
        'mt.id_persona = %s',
        'DATE(mt.fecha) BETWEEN %s AND %s',
    ]
    params = [user_id, filters[start_key], filters[end_key]]

    if filters.get('categoria_id'):
        conditions.append('mt.id_categoria = %s')
        params.append(filters['categoria_id'])
    if filters.get('beneficiario_id'):
        conditions.append('mt.id_beneficiario = %s')
        params.append(filters['beneficiario_id'])

    return conditions, params


def _summary_totals(db: DatabaseConnector, user_id: int, filters, start_key='start_date', end_key='end_date'):
    conditions, params = _movement_conditions(filters, user_id, start_key, end_key)
    rows = db.execute_query(
        f"""  # nosec B608
        SELECT
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END), 0) AS ingresos_total,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gastos_total
        FROM movimiento m
        INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
        LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        WHERE {' AND '.join(conditions)}
        """,
        tuple(params),
    )
    row = rows[0] if rows else {}
    ingresos_total = float(row.get('ingresos_total') or 0)
    gastos_total = float(row.get('gastos_total') or 0)
    return {
        'ingresos_total': round(ingresos_total, 2),
        'gastos_total': round(gastos_total, 2),
        'saldo_total': round(ingresos_total - gastos_total, 2),
    }


def _monthly_series(db: DatabaseConnector, user_id: int, filters):
    conditions, params = _movement_conditions(filters, user_id)
    rows = db.execute_query(
        f"""  # nosec B608
        SELECT
            DATE_FORMAT(m.fecha_creacion, '%Y-%m') AS periodo,
            DATE_FORMAT(m.fecha_creacion, '%b') AS mes,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END), 0) AS ingresos,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gastos
        FROM movimiento m
        INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
        LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        WHERE {' AND '.join(conditions)}
        GROUP BY DATE_FORMAT(m.fecha_creacion, '%Y-%m'), DATE_FORMAT(m.fecha_creacion, '%b')
        ORDER BY periodo ASC
        """,
        tuple(params),
    )
    return rows or []


def _category_totals(db: DatabaseConnector, user_id: int, filters, movement_type: str, start_key='start_date', end_key='end_date'):
    conditions, params = _movement_conditions(filters, user_id, start_key, end_key)
    conditions.append("LOWER(CONVERT(tm.nombre USING utf8mb4)) = %s")
    params.append(movement_type)

    rows = db.execute_query(
        f"""  # nosec B608
        SELECT
            COALESCE(cat.nombre, 'Sin categoria') AS categoria,
            COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
        LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria cat ON cat.id_categoria = m.id_categoria
        WHERE {' AND '.join(conditions)}
        GROUP BY COALESCE(cat.nombre, 'Sin categoria')
        ORDER BY total DESC
        LIMIT 12
        """,
        tuple(params),
    )
    return rows or []


def _beneficiary_totals(db: DatabaseConnector, user_id: int, filters, start_key='start_date', end_key='end_date'):
    conditions, params = _movement_conditions(filters, user_id, start_key, end_key)
    rows = db.execute_query(
        f"""  # nosec B608
        SELECT
            COALESCE(b.nombre, 'Sin beneficiario') AS beneficiario,
            COUNT(*) AS movimientos,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gasto_total
        FROM movimiento m
        INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
        LEFT JOIN beneficiario b ON b.id_beneficiario = m.id_beneficiario
        LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        WHERE {' AND '.join(conditions)}
        GROUP BY COALESCE(b.nombre, 'Sin beneficiario')
        ORDER BY movimientos DESC, gasto_total DESC
        LIMIT 10
        """,
        tuple(params),
    )
    return rows or []


def _account_totals(db: DatabaseConnector, user_id: int, filters, start_key='start_date', end_key='end_date'):
    join_conditions = ['m.id_cuenta = c.id_cuenta', 'DATE(m.fecha_creacion) BETWEEN %s AND %s']
    join_params = [filters[start_key], filters[end_key]]

    if filters.get('categoria_id'):
        join_conditions.append('m.id_categoria = %s')
        join_params.append(filters['categoria_id'])
    if filters.get('beneficiario_id'):
        join_conditions.append('m.id_beneficiario = %s')
        join_params.append(filters['beneficiario_id'])

    where_conditions = ['c.id_persona = %s']
    where_params = [user_id]
    if filters.get('cuenta_id'):
        where_conditions.append('c.id_cuenta = %s')
        where_params.append(filters['cuenta_id'])

    rows = db.execute_query(
        f"""  # nosec B608
        SELECT
            c.nombre AS cuenta,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END), 0) AS ingresos,
            COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gastos
        FROM cuenta c
        LEFT JOIN movimiento m ON {' AND '.join(join_conditions)}
        LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        WHERE {' AND '.join(where_conditions)}
        GROUP BY c.id_cuenta, c.nombre
        ORDER BY c.nombre
        """,
        tuple(join_params + where_params),
    )
    return [
        {
            'cuenta': r.get('cuenta'),
            'ingresos': float(r.get('ingresos') or 0),
            'gastos': float(r.get('gastos') or 0),
            'saldo': round(float(r.get('ingresos') or 0) - float(r.get('gastos') or 0), 2),
        }
        for r in (rows or [])
    ]


def _merge_dimension_rows(current_rows, previous_rows, label_key):
    previous_map = {
        str(r.get(label_key) or '').strip().lower(): float(r.get('total') or 0)
        for r in previous_rows
    }
    total_current = sum(float(r.get('total') or 0) for r in current_rows)

    merged = []
    for row in current_rows:
        label = row.get(label_key)
        total = float(row.get('total') or 0)
        prev_total = previous_map.get(str(label or '').strip().lower(), 0.0)
        merged.append(
            {
                label_key: label,
                'total': total,
                'pct': round((total / total_current) * 100, 2) if total_current > 0 else 0,
                'previous_total': round(prev_total, 2),
                'delta_total': round(total - prev_total, 2),
                'delta_pct': _pct_change(total, prev_total),
            }
        )
    return merged


def _comparison_payload(current_summary, previous_summary, compare_label):
    return {
        'label': compare_label,
        'ingresos': {
            'actual': current_summary['ingresos_total'],
            'anterior': previous_summary['ingresos_total'],
            'delta_total': round(current_summary['ingresos_total'] - previous_summary['ingresos_total'], 2),
            'delta_pct': _pct_change(current_summary['ingresos_total'], previous_summary['ingresos_total']),
        },
        'gastos': {
            'actual': current_summary['gastos_total'],
            'anterior': previous_summary['gastos_total'],
            'delta_total': round(current_summary['gastos_total'] - previous_summary['gastos_total'], 2),
            'delta_pct': _pct_change(current_summary['gastos_total'], previous_summary['gastos_total']),
        },
        'saldo': {
            'actual': current_summary['saldo_total'],
            'anterior': previous_summary['saldo_total'],
            'delta_total': round(current_summary['saldo_total'] - previous_summary['saldo_total'], 2),
            'delta_pct': _pct_change(current_summary['saldo_total'], previous_summary['saldo_total']),
        },
    }


def _real_totals_by_category(db: DatabaseConnector, user_id: int, filters, start_key='start_date', end_key='end_date'):
    totals = {}

    conditions, params = _movement_conditions(filters, user_id, start_key, end_key)
    mov_rows = db.execute_query(
        f"""  # nosec B608
        SELECT COALESCE(ca.nombre, 'Sin categoria') AS categoria, COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria ca ON ca.id_categoria = m.id_categoria
        WHERE {' AND '.join(conditions)}
          AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
        GROUP BY COALESCE(ca.nombre, 'Sin categoria')
        """,
        tuple(params),
    )
    for row in mov_rows or []:
        key = (row.get('categoria') or 'Sin categoria').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    if not filters.get('cuenta_id'):
        card_conditions, card_params = _card_conditions(filters, user_id, start_key, end_key)
        tarjeta_rows = db.execute_query(
            f"""  # nosec B608
            SELECT COALESCE(ca.nombre, 'Sin categoria') AS categoria, COALESCE(SUM(ABS(mt.valor)), 0) AS total
            FROM movimiento_tarjeta mt
            LEFT JOIN categoria ca ON ca.id_categoria = mt.id_categoria
            WHERE {' AND '.join(card_conditions)}
            GROUP BY COALESCE(ca.nombre, 'Sin categoria')
            """,
            tuple(card_params),
        )
        for row in tarjeta_rows or []:
            key = (row.get('categoria') or 'Sin categoria').strip().lower()
            totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    return totals


def _budget_summary(db: DatabaseConnector, user_id: int, filters):
    presupuesto_rows = db.execute_query(
        """
        SELECT id_presupuesto, nombre
        FROM presupuesto
        WHERE id_persona = %s
          AND fecha_inicio <= %s
          AND fecha_fin >= %s
        ORDER BY fecha_inicio DESC, id_presupuesto DESC
        LIMIT 1
        """,
        (user_id, filters['end_date'], filters['start_date']),
    )

    performance = {
        'nombre': None,
        'estimado_total': 0.0,
        'real_total': 0.0,
        'ejecucion_pct': 0.0,
    }
    category_summary = []

    if not presupuesto_rows:
        return performance, category_summary

    presupuesto = presupuesto_rows[0]
    performance['nombre'] = presupuesto.get('nombre')

    detalle_rows = db.execute_query(
        """
        SELECT
            COALESCE(c.nombre, pd.categoria_nombre, 'Sin categoria') AS categoria,
            COALESCE(pd.monto_estimado, 0) AS estimado
        FROM presupuesto_detalle pd
        LEFT JOIN categoria c ON c.id_categoria = pd.id_categoria
        WHERE pd.id_presupuesto = %s
        ORDER BY pd.orden, pd.id_detalle
        """,
        (presupuesto['id_presupuesto'],),
    )

    real_by_category = _real_totals_by_category(db, user_id, filters)
    estimated_total = 0.0
    real_total = 0.0
    for row in detalle_rows or []:
        categoria = row.get('categoria') or 'Sin categoria'
        estimado = float(row.get('estimado') or 0)
        real = float(real_by_category.get(categoria.strip().lower(), 0.0))
        estimated_total += estimado
        real_total += real
        category_summary.append(
            {
                'categoria': categoria,
                'estimado': estimado,
                'real': real,
                'diferencia': round(estimado - real, 2),
                'ejecucion_pct': round((real / estimado) * 100, 2) if estimado > 0 else 0,
            }
        )

    performance['estimado_total'] = round(estimated_total, 2)
    performance['real_total'] = round(real_total, 2)
    performance['ejecucion_pct'] = round((real_total / estimated_total) * 100, 2) if estimated_total > 0 else 0
    return performance, category_summary


@bp.route('/metadata', methods=['GET'])
def get_report_metadata():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        cuentas = db.execute_query(
            "SELECT id_cuenta, nombre FROM cuenta WHERE id_persona = %s ORDER BY nombre",
            (user_id,),
        )
        categorias = db.execute_query(
            "SELECT id_categoria, nombre FROM categoria WHERE estado = 1 ORDER BY nombre"
        )
        beneficiarios = db.execute_query(
            "SELECT id_beneficiario, nombre FROM beneficiario WHERE estado = 1 ORDER BY nombre"
        )
        return jsonify(
            {
                'cuentas': cuentas or [],
                'categorias': categorias or [],
                'beneficiarios': beneficiarios or [],
            }
        ), 200
    except Exception as e:
        logger.error('Error cargando metadata de reportes: %s', e)
        return jsonify({'message': 'Error al cargar filtros de reportes'}), 500
    finally:
        db.close()


@bp.route('/detalle-movimientos', methods=['GET'])
def get_report_detail():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        filters = _normalize_filters()
        limit = min(int(request.args.get('limit', 150)), 300)
        period = request.args.get('period') or None
        movement_type = (request.args.get('movement_type') or '').strip().lower() or None
        category_name = (request.args.get('category_name') or '').strip() or None

        conditions, params = _movement_conditions(filters, user_id)
        if period:
            conditions.append("DATE_FORMAT(m.fecha_creacion, '%Y-%m') = %s")
            params.append(period)
        if movement_type:
            conditions.append("LOWER(CONVERT(tm.nombre USING utf8mb4)) = %s")
            params.append(movement_type)
        if category_name:
            conditions.append("LOWER(COALESCE(cat.nombre, 'Sin categoria')) = LOWER(%s)")
            params.append(category_name)

        rows = db.execute_query(
            f"""  # nosec B608
            SELECT
                DATE(m.fecha_creacion) AS fecha,
                c.nombre AS cuenta,
                LOWER(CONVERT(tm.nombre USING utf8mb4)) AS tipo,
                COALESCE(cat.nombre, 'Sin categoria') AS categoria,
                COALESCE(b.nombre, 'Sin beneficiario') AS beneficiario,
                COALESCE(m.numero_transaccion, m.nota, '') AS detalle,
                COALESCE(m.monto, 0) AS monto
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria cat ON cat.id_categoria = m.id_categoria
            LEFT JOIN beneficiario b ON b.id_beneficiario = m.id_beneficiario
            WHERE {' AND '.join(conditions)}
            ORDER BY m.fecha_creacion DESC, m.id_movimiento DESC
            LIMIT %s
            """,
            tuple(params + [limit]),
        )

        return jsonify(
            {
                'filters': {
                    'period': period,
                    'movement_type': movement_type,
                    'category_name': category_name,
                },
                'movimientos': [
                    {
                        'fecha': str(r.get('fecha')) if r.get('fecha') else None,
                        'cuenta': r.get('cuenta'),
                        'tipo': r.get('tipo'),
                        'categoria': r.get('categoria'),
                        'beneficiario': r.get('beneficiario'),
                        'detalle': r.get('detalle') or '',
                        'monto': float(r.get('monto') or 0),
                    }
                    for r in (rows or [])
                ],
            }
        ), 200
    except Exception as e:
        logger.error('Error generando detalle de movimientos: %s', e)
        return jsonify({'message': 'Error al cargar detalle de movimientos'}), 500
    finally:
        db.close()


@bp.route('/data', methods=['GET'])
def get_report_data():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        tendencia_rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(m.fecha_creacion, '%b') AS mes,
                DATE_FORMAT(m.fecha_creacion, '%Y-%m') AS periodo,
                SUM(
                    CASE
                        WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto
                        WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN -m.monto
                        ELSE 0
                    END
                ) AS balance
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(m.fecha_creacion, '%Y-%m'), DATE_FORMAT(m.fecha_creacion, '%b')
            ORDER BY periodo ASC
            """,
            (user_id,),
        )

        categorias_rows = db.execute_query(
            """
            SELECT
                COALESCE(cat.nombre, 'Sin categoria') AS nombre,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY COALESCE(cat.nombre, 'Sin categoria')
            ORDER BY total DESC
            LIMIT 8
            """,
            (user_id,),
        )

        payload = {
            'months': [row.get('mes') for row in tendencia_rows],
            'balance_trend': [float(row.get('balance') or 0) for row in tendencia_rows],
            'categories': [
                {
                    'nombre': row.get('nombre'),
                    'total': float(row.get('total') or 0),
                }
                for row in categorias_rows
            ],
        }
        return jsonify(payload), 200
    except Exception as e:
        logger.error('Error generando reporte: %s', e)
        return jsonify({'message': 'Error al generar reporte'}), 500
    finally:
        db.close()


@bp.route('/suite', methods=['GET'])
def get_report_suite():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        filters = _normalize_filters()

        current_summary = _summary_totals(db, user_id, filters)
        previous_summary = _summary_totals(db, user_id, filters, 'compare_start_date', 'compare_end_date')
        comparison = _comparison_payload(current_summary, previous_summary, filters['compare_label'])

        monthly_rows = _monthly_series(db, user_id, filters)
        periodos = [r.get('periodo') for r in monthly_rows]
        meses = [r.get('mes') for r in monthly_rows]
        ingresos = [float(r.get('ingresos') or 0) for r in monthly_rows]
        gastos = [float(r.get('gastos') or 0) for r in monthly_rows]
        balance = [round(i - g, 2) for i, g in zip(ingresos, gastos)]

        where_money_goes = _merge_dimension_rows(
            _category_totals(db, user_id, filters, 'gasto'),
            _category_totals(db, user_id, filters, 'gasto', 'compare_start_date', 'compare_end_date'),
            'categoria',
        )
        income_sources = _merge_dimension_rows(
            _category_totals(db, user_id, filters, 'ingreso'),
            _category_totals(db, user_id, filters, 'ingreso', 'compare_start_date', 'compare_end_date'),
            'categoria',
        )

        forecast_rows = _monthly_series(
            db,
            user_id,
            {
                **filters,
                'start_date': (date.today() - timedelta(days=90)).isoformat(),
                'end_date': date.today().isoformat(),
            },
        )
        forecast_in = [float(r.get('ingresos') or 0) for r in forecast_rows]
        forecast_out = [float(r.get('gastos') or 0) for r in forecast_rows]
        forecast = {
            'promedio_ingresos_3m': round(sum(forecast_in) / len(forecast_in), 2) if forecast_in else 0.0,
            'promedio_gastos_3m': round(sum(forecast_out) / len(forecast_out), 2) if forecast_out else 0.0,
        }
        forecast['saldo_estimado_siguiente_mes'] = round(
            forecast['promedio_ingresos_3m'] - forecast['promedio_gastos_3m'],
            2,
        )

        beneficiaries_current = _beneficiary_totals(db, user_id, filters)
        beneficiaries_previous = _beneficiary_totals(db, user_id, filters, 'compare_start_date', 'compare_end_date')
        previous_beneficiaries = {
            str(r.get('beneficiario') or '').strip().lower(): float(r.get('gasto_total') or 0)
            for r in beneficiaries_previous
        }
        beneficiaries = [
            {
                'beneficiario': r.get('beneficiario'),
                'movimientos': int(r.get('movimientos') or 0),
                'gasto_total': float(r.get('gasto_total') or 0),
                'delta_pct': _pct_change(
                    float(r.get('gasto_total') or 0),
                    previous_beneficiaries.get(str(r.get('beneficiario') or '').strip().lower(), 0.0),
                ),
            }
            for r in beneficiaries_current
        ]

        account_period = _account_totals(db, user_id, filters)
        account_year = _account_totals(
            db,
            user_id,
            {
                **filters,
                'start_date': date(filters['year'], 1, 1).isoformat(),
                'end_date': date(filters['year'], 12, 31).isoformat(),
            },
        )

        budget_performance, budget_categories = _budget_summary(db, user_id, filters)

        return jsonify(
            {
                'anio': filters['year'],
                'filtros': {
                    'year': filters['year'],
                    'start_date': filters['start_date'],
                    'end_date': filters['end_date'],
                    'cuenta_id': filters['cuenta_id'],
                    'categoria_id': filters['categoria_id'],
                    'beneficiario_id': filters['beneficiario_id'],
                    'compare_label': filters['compare_label'],
                },
                'flujo_caja': {
                    'periodos': periodos,
                    'meses': meses,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'balance': balance,
                    'resumen': {
                        **current_summary,
                        'comparativo': comparison,
                    },
                    'donde_va_dinero': where_money_goes,
                    'de_donde_viene': income_sources,
                    'prevision': forecast,
                },
                'ingresos_gastos_mensual': {
                    'periodos': periodos,
                    'meses': meses,
                    'ingresos': ingresos,
                    'gastos': gastos,
                },
                'mi_uso': {
                    'beneficiarios': beneficiaries,
                },
                'resumen_cuentas': {
                    'periodo': account_period,
                    'anual': account_year,
                },
                'presupuestos': {
                    'desempeno': budget_performance,
                    'resumen_categoria': budget_categories,
                },
            }
        ), 200
    except Exception as e:
        logger.error('Error generando suite de reportes: %s', e)
        return jsonify({'message': 'Error al generar suite de reportes'}), 500
    finally:
        db.close()
