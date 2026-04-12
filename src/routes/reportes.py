"""Rutas API de Reportes con datos reales desde MySQL."""

import logging

from flask import Blueprint, jsonify
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
