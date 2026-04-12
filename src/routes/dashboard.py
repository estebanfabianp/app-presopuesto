"""
Rutas del Dashboard — datos reales desde MySQL.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging

from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# Paleta de colores para el gráfico de dona
_CHART_COLORS = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#C9CBCF', '#E7E9ED', '#71B37C', '#A8DADC',
]


def _get_user_id() -> int:
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


@bp.route('/summary', methods=['GET'])
def get_summary():
    """
    GET /api/dashboard/summary
    Devuelve ingresos, gastos, saldo, presupuestos activos,
    transacciones recientes y datos del gráfico de dona.
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        # --- Ingresos del mes actual ---
        ing_rows = db.execute_query(
            """
            SELECT COALESCE(SUM(m.monto), 0) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        total_ingresos = float(ing_rows[0]['total']) if ing_rows else 0.0

        # --- Gastos del mes actual ---
        gas_rows = db.execute_query(
            """
            SELECT COALESCE(SUM(m.monto), 0) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        total_gastos = float(gas_rows[0]['total']) if gas_rows else 0.0

        # --- Presupuestos activos ---
        pres_rows = db.execute_query(
            """
            SELECT COUNT(*) AS total
            FROM presupuesto
            WHERE id_persona = %s
              AND (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
              AND (fecha_fin IS NULL OR fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuestos_activos = int(pres_rows[0]['total']) if pres_rows else 0

        # --- Transacciones de los últimos 30 días ---
        tx_rows = db.execute_query(
            """
            SELECT COUNT(*) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """,
            (user_id,),
        )
        transacciones_recientes = int(tx_rows[0]['total']) if tx_rows else 0

        # --- Gastos por categoría (mes actual) para el gráfico ---
        cat_rows = db.execute_query(
            """
            SELECT
                COALESCE(cat.nombre, 'Sin categoría') AS nombre,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            GROUP BY COALESCE(cat.nombre, 'Sin categoría')
            ORDER BY total DESC
            LIMIT 8
            """,
            (user_id,),
        )

        labels = [r['nombre'] for r in cat_rows]
        values = [float(r['total']) for r in cat_rows]
        colors = _CHART_COLORS[:len(labels)]

        chart_data = {
            'labels': labels,
            'datasets': [{'data': values, 'backgroundColor': colors}],
        }

        return jsonify({
            'total_ingresos': total_ingresos,
            'total_gastos': total_gastos,
            'saldo': total_ingresos - total_gastos,
            'presupuestos_activos': presupuestos_activos,
            'transacciones_recientes': transacciones_recientes,
            'chart_data': chart_data,
        }), 200

    except Exception as e:
        logger.error("Dashboard summary error: %s", e)
        return jsonify({'message': 'Error al obtener resumen'}), 500
    finally:
        db.close()


@bp.route('/gastos-por-categoria', methods=['GET'])
def get_gastos_por_categoria():
    """
    GET /api/dashboard/gastos-por-categoria
    Gastos agrupados por categoría (últimos 6 meses).
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        rows = db.execute_query(
            """
            SELECT
                COALESCE(cat.nombre, 'Sin categoría') AS nombre,
                cat.id_categoria AS id,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY cat.id_categoria, COALESCE(cat.nombre, 'Sin categoría')
            ORDER BY total DESC
            LIMIT 10
            """,
            (user_id,),
        )

        return jsonify({
            'categories': [
                {'id': r.get('id'), 'nombre': r['nombre'], 'total': float(r['total'])}
                for r in rows
            ]
        }), 200

    except Exception as e:
        logger.error("Gastos por categoria error: %s", e)
        return jsonify({'message': 'Error al obtener categorías'}), 500
    finally:
        db.close()


@bp.route('/tendencia', methods=['GET'])
def get_tendencia():
    """
    GET /api/dashboard/tendencia
    Balance mensual de los últimos 6 meses para el gráfico de tendencia.
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(m.fecha_creacion, '%b %Y') AS mes,
                DATE_FORMAT(m.fecha_creacion, '%Y-%m') AS periodo,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'   THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(m.fecha_creacion, '%Y-%m'), DATE_FORMAT(m.fecha_creacion, '%b %Y')
            ORDER BY periodo ASC
            """,
            (user_id,),
        )

        return jsonify({
            'months': [r['mes'] for r in rows],
            'ingresos': [float(r['ingresos']) for r in rows],
            'gastos': [float(r['gastos']) for r in rows],
        }), 200

    except Exception as e:
        logger.error("Tendencia error: %s", e)
        return jsonify({'message': 'Error al obtener tendencia'}), 500
    finally:
        db.close()
