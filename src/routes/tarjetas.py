"""Rutas API para módulo de tarjetas (resumen y movimientos recientes)."""

import logging

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

bp = Blueprint('tarjetas', __name__, url_prefix='/api/tarjetas')


def _get_user_id() -> int:
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


@bp.route('/summary', methods=['GET'])
def get_tarjetas_summary():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        totals = db.execute_query(
            """
            SELECT
                COUNT(*) AS total_tarjetas,
                COALESCE(SUM(limite_credito), 0) AS limite_total,
                COALESCE(SUM(saldo_actual), 0) AS saldo_actual_total,
                COALESCE(SUM(saldo_disponible), 0) AS disponible_total
            FROM v_producto_unificado
            WHERE id_persona = %s
              AND tipo_producto = 'tarjeta_credito'
            """,
            (user_id,),
        )
        t = totals[0] if totals else {}

        month = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN LOWER(COALESCE(estado, '')) = 'compra' THEN valor ELSE 0 END), 0) AS compras_mes,
                COALESCE(SUM(CASE WHEN LOWER(COALESCE(estado, '')) = 'abono'  THEN valor ELSE 0 END), 0) AS abonos_mes,
                COUNT(*) AS movimientos_mes
            FROM movimiento_tarjeta
            WHERE id_persona = %s
              AND MONTH(fecha) = MONTH(CURDATE())
              AND YEAR(fecha) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        m = month[0] if month else {}

        recent_rows = db.execute_query(
            """
            SELECT
                id_movimiento_tarjeta,
                fecha,
                valor,
                estado,
                nota
            FROM movimiento_tarjeta
            WHERE id_persona = %s
            ORDER BY fecha DESC, id_movimiento_tarjeta DESC
            LIMIT 5
            """,
            (user_id,),
        )

        return jsonify({
            'total_tarjetas': int(t.get('total_tarjetas') or 0),
            'limite_total': float(t.get('limite_total') or 0),
            'saldo_actual_total': float(t.get('saldo_actual_total') or 0),
            'disponible_total': float(t.get('disponible_total') or 0),
            'compras_mes': float(m.get('compras_mes') or 0),
            'abonos_mes': float(m.get('abonos_mes') or 0),
            'movimientos_mes': int(m.get('movimientos_mes') or 0),
            'movimientos_recientes': [
                {
                    'id': r['id_movimiento_tarjeta'],
                    'fecha': r['fecha'].isoformat() if r.get('fecha') else None,
                    'valor': float(r.get('valor') or 0),
                    'estado': r.get('estado') or 'N/A',
                    'nota': r.get('nota') or '',
                }
                for r in recent_rows
            ],
        }), 200
    except Exception as e:
        logger.error('Error obteniendo resumen de tarjetas: %s', e)
        return jsonify({'message': 'Error al obtener datos de tarjetas'}), 500
    finally:
        db.close()
