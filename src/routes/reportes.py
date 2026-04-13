"""Rutas API de Reportes con datos reales desde MySQL."""

import logging
from datetime import date

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


def _real_totals_by_category(db: DatabaseConnector, user_id: int, start_date: str, end_date: str):
    totals = {}

    mov_rows = db.execute_query(
        """
        SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
        WHERE cu.id_persona = %s
          AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
          AND DATE(m.fecha_creacion) BETWEEN %s AND %s
        GROUP BY COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date, end_date),
    )
    for row in mov_rows or []:
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
        (user_id, start_date, end_date),
    )
    for row in tarjeta_rows or []:
        key = (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    return totals


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
                COALESCE(cat.nombre, 'Sin categoría') AS nombre,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY COALESCE(cat.nombre, 'Sin categoría')
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
        logger.error("Error generando reporte: %s", e)
        return jsonify({'message': 'Error al generar reporte'}), 500
    finally:
        db.close()


@bp.route('/suite', methods=['GET'])
def get_report_suite():
    """
    GET /api/reportes/suite
    Entrega una suite consolidada para la nueva interfaz de reportes:
    flujo de caja, categorías, previsión, ingresos/gastos, mi uso,
    resumen de cuentas y desempeño de presupuesto.
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        year = int(request.args.get('year', date.today().year))

        # 1) Flujo de caja mensual del año
        cashflow_rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(m.fecha_creacion, '%Y-%m') AS periodo,
                DATE_FORMAT(m.fecha_creacion, '%b') AS mes,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND YEAR(m.fecha_creacion) = %s
            GROUP BY DATE_FORMAT(m.fecha_creacion, '%Y-%m'), DATE_FORMAT(m.fecha_creacion, '%b')
            ORDER BY periodo ASC
            """,
            (user_id, year),
        )

        meses = [r.get('mes') for r in cashflow_rows]
        ingresos = [float(r.get('ingresos') or 0) for r in cashflow_rows]
        gastos = [float(r.get('gastos') or 0) for r in cashflow_rows]
        balance = [round(i - g, 2) for i, g in zip(ingresos, gastos)]

        resumen = {
            'ingresos_total': round(sum(ingresos), 2),
            'gastos_total': round(sum(gastos), 2),
        }
        resumen['saldo_total'] = round(resumen['ingresos_total'] - resumen['gastos_total'], 2)

        # 2) Dónde va el dinero (gastos por categoría)
        where_money_goes_rows = db.execute_query(
            """
            SELECT
                COALESCE(cat.nombre, 'Sin categoría') AS categoria,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria cat ON cat.id_categoria = m.id_categoria
            WHERE c.id_persona = %s
              AND YEAR(m.fecha_creacion) = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
            GROUP BY COALESCE(cat.nombre, 'Sin categoría')
            ORDER BY total DESC
            LIMIT 12
            """,
            (user_id, year),
        )
        total_gasto_categorias = sum(float(r.get('total') or 0) for r in where_money_goes_rows)
        where_money_goes = [
            {
                'categoria': r.get('categoria'),
                'total': float(r.get('total') or 0),
                'pct': round((float(r.get('total') or 0) / total_gasto_categorias * 100), 2) if total_gasto_categorias > 0 else 0,
            }
            for r in where_money_goes_rows
        ]

        # 3) De dónde viene el dinero (ingresos por categoría)
        income_sources_rows = db.execute_query(
            """
            SELECT
                COALESCE(cat.nombre, 'Sin categoría') AS categoria,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria cat ON cat.id_categoria = m.id_categoria
            WHERE c.id_persona = %s
              AND YEAR(m.fecha_creacion) = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso'
            GROUP BY COALESCE(cat.nombre, 'Sin categoría')
            ORDER BY total DESC
            LIMIT 12
            """,
            (user_id, year),
        )
        total_income_sources = sum(float(r.get('total') or 0) for r in income_sources_rows)
        income_sources = [
            {
                'categoria': r.get('categoria'),
                'total': float(r.get('total') or 0),
                'pct': round((float(r.get('total') or 0) / total_income_sources * 100), 2) if total_income_sources > 0 else 0,
            }
            for r in income_sources_rows
        ]

        # 4) Informe de previsión simple (promedio últimos 3 meses)
        forecast_rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(m.fecha_creacion, '%Y-%m') AS periodo,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            GROUP BY DATE_FORMAT(m.fecha_creacion, '%Y-%m')
            ORDER BY periodo ASC
            """,
            (user_id,),
        )
        f_ing = [float(r.get('ingresos') or 0) for r in forecast_rows]
        f_gas = [float(r.get('gastos') or 0) for r in forecast_rows]
        promedio_ingresos = round(sum(f_ing) / len(f_ing), 2) if f_ing else 0.0
        promedio_gastos = round(sum(f_gas) / len(f_gas), 2) if f_gas else 0.0
        forecast = {
            'promedio_ingresos_3m': promedio_ingresos,
            'promedio_gastos_3m': promedio_gastos,
            'saldo_estimado_siguiente_mes': round(promedio_ingresos - promedio_gastos, 2),
        }

        # 5) Mi uso (beneficiarios)
        beneficiaries_rows = db.execute_query(
            """
            SELECT
                COALESCE(b.nombre, 'Sin beneficiario') AS beneficiario,
                COUNT(*) AS movimientos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END) AS gasto_total
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            LEFT JOIN beneficiario b ON b.id_beneficiario = m.id_beneficiario
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND YEAR(m.fecha_creacion) = %s
            GROUP BY COALESCE(b.nombre, 'Sin beneficiario')
            ORDER BY movimientos DESC
            LIMIT 10
            """,
            (user_id, year),
        )
        beneficiaries = [
            {
                'beneficiario': r.get('beneficiario'),
                'movimientos': int(r.get('movimientos') or 0),
                'gasto_total': float(r.get('gasto_total') or 0),
            }
            for r in beneficiaries_rows
        ]

        # 6) Resumen de cuentas mensual y anual
        accounts_month_rows = db.execute_query(
            """
            SELECT
                c.nombre AS cuenta,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END) AS gastos
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
            GROUP BY c.id_cuenta, c.nombre
            ORDER BY c.nombre
            """,
            (user_id,),
        )
        accounts_year_rows = db.execute_query(
            """
            SELECT
                c.nombre AS cuenta,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END) AS gastos
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
              AND YEAR(m.fecha_creacion) = %s
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
            GROUP BY c.id_cuenta, c.nombre
            ORDER BY c.nombre
            """,
            (year, user_id),
        )
        accounts_summary = {
            'mensual': [
                {
                    'cuenta': r.get('cuenta'),
                    'ingresos': float(r.get('ingresos') or 0),
                    'gastos': float(r.get('gastos') or 0),
                    'saldo': round(float(r.get('ingresos') or 0) - float(r.get('gastos') or 0), 2),
                }
                for r in accounts_month_rows
            ],
            'anual': [
                {
                    'cuenta': r.get('cuenta'),
                    'ingresos': float(r.get('ingresos') or 0),
                    'gastos': float(r.get('gastos') or 0),
                    'saldo': round(float(r.get('ingresos') or 0) - float(r.get('gastos') or 0), 2),
                }
                for r in accounts_year_rows
            ],
        }

        # 7) Desempeño presupuesto y resumen por categoría
        first_day_month = date.today().replace(day=1).isoformat()
        end_day_month = date.today().isoformat()

        presupuesto_rows = db.execute_query(
            """
            SELECT id_presupuesto, nombre, monto_total, fecha_inicio, fecha_fin
            FROM presupuesto
            WHERE id_persona = %s
              AND fecha_inicio <= %s
              AND fecha_fin >= %s
            ORDER BY fecha_inicio DESC, id_presupuesto DESC
            LIMIT 1
            """,
            (user_id, end_day_month, first_day_month),
        )

        presupuesto_performance = {
            'nombre': None,
            'estimado_total': 0.0,
            'real_total': 0.0,
            'ejecucion_pct': 0.0,
        }
        presupuesto_category_summary = []

        if presupuesto_rows:
            pres = presupuesto_rows[0]
            presupuesto_performance['nombre'] = pres.get('nombre')

            detalle_rows = db.execute_query(
                """
                SELECT
                    COALESCE(c.nombre, pd.categoria_nombre, 'Sin categoría') AS categoria,
                    COALESCE(pd.monto_estimado, 0) AS estimado
                FROM presupuesto_detalle pd
                LEFT JOIN categoria c ON c.id_categoria = pd.id_categoria
                WHERE pd.id_presupuesto = %s
                ORDER BY pd.orden, pd.id_detalle
                """,
                (pres['id_presupuesto'],),
            )

            real_by_category = _real_totals_by_category(db, user_id, first_day_month, end_day_month)
            estimado_total = 0.0
            real_total = 0.0
            for row in detalle_rows or []:
                categoria = row.get('categoria') or 'Sin categoría'
                estimado = float(row.get('estimado') or 0)
                real = float(real_by_category.get(categoria.strip().lower(), 0.0))
                estimado_total += estimado
                real_total += real
                presupuesto_category_summary.append(
                    {
                        'categoria': categoria,
                        'estimado': estimado,
                        'real': real,
                        'diferencia': round(estimado - real, 2),
                        'ejecucion_pct': round((real / estimado) * 100, 2) if estimado > 0 else 0,
                    }
                )

            presupuesto_performance['estimado_total'] = round(estimado_total, 2)
            presupuesto_performance['real_total'] = round(real_total, 2)
            presupuesto_performance['ejecucion_pct'] = round((real_total / estimado_total) * 100, 2) if estimado_total > 0 else 0

        return jsonify(
            {
                'anio': year,
                'flujo_caja': {
                    'meses': meses,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'balance': balance,
                    'resumen': resumen,
                    'donde_va_dinero': where_money_goes,
                    'de_donde_viene': income_sources,
                    'prevision': forecast,
                },
                'ingresos_gastos_mensual': {
                    'meses': meses,
                    'ingresos': ingresos,
                    'gastos': gastos,
                },
                'mi_uso': {
                    'beneficiarios': beneficiaries,
                },
                'resumen_cuentas': accounts_summary,
                'presupuestos': {
                    'desempeno': presupuesto_performance,
                    'resumen_categoria': presupuesto_category_summary,
                },
            }
        ), 200
    except Exception as e:
        logger.error("Error generando suite de reportes: %s", e)
        return jsonify({'message': 'Error al generar suite de reportes'}), 500
    finally:
        db.close()
