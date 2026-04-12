"""Rutas API para módulo de inversiones."""

import logging

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

bp = Blueprint('inversiones', __name__, url_prefix='/api/inversiones')


def _get_user_id() -> int:
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


@bp.route('/summary', methods=['GET'])
def get_inversiones_summary():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        totals = db.execute_query(
            """
            SELECT
                COUNT(*) AS total_inversiones,
                COALESCE(SUM(valor), 0) AS valor_bruto,
                COALESCE(SUM(depreciacion), 0) AS depreciacion_total
            FROM activo
            WHERE id_persona = %s
            """,
            (user_id,),
        )
        t = totals[0] if totals else {}

        productos = db.execute_query(
            """
            SELECT
                COALESCE(SUM(valor_efectivo), 0) AS valor_portafolio
            FROM v_producto_unificado
            WHERE id_persona = %s
              AND tipo_producto = 'fondo_inversion'
            """,
            (user_id,),
        )
        p = productos[0] if productos else {}

        recent_rows = db.execute_query(
            """
            SELECT id_activo, nombre_activo, valor, depreciacion, fecha_creacion
            FROM activo
            WHERE id_persona = %s
            ORDER BY fecha_creacion DESC, id_activo DESC
            LIMIT 5
            """,
            (user_id,),
        )

        valor_bruto = float(t.get('valor_bruto') or 0)
        depreciacion = float(t.get('depreciacion_total') or 0)

        return jsonify({
            'total_inversiones': int(t.get('total_inversiones') or 0),
            'valor_bruto': valor_bruto,
            'depreciacion_total': depreciacion,
            'valor_neto': valor_bruto - depreciacion,
            'valor_portafolio': float(p.get('valor_portafolio') or 0),
            'activos_recientes': [
                {
                    'id': r['id_activo'],
                    'nombre': r.get('nombre_activo') or f"Activo {r['id_activo']}",
                    'valor': float(r.get('valor') or 0),
                    'depreciacion': float(r.get('depreciacion') or 0),
                    'fecha_creacion': r['fecha_creacion'].isoformat() if r.get('fecha_creacion') else None,
                }
                for r in recent_rows
            ],
        }), 200
    except Exception as e:
        logger.error('Error obteniendo resumen de inversiones: %s', e)
        return jsonify({'message': 'Error al obtener datos de inversiones'}), 500
    finally:
        db.close()
