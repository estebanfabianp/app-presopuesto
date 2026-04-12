"""Rutas API para módulo de metas de ahorro basado en presupuestos."""

import logging

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

bp = Blueprint('metas', __name__, url_prefix='/api/metas')


def _get_user_id() -> int:
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


@bp.route('/summary', methods=['GET'])
def get_metas_summary():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        totals = db.execute_query(
            """
            SELECT
                COUNT(*) AS total_metas,
                COALESCE(SUM(monto_total), 0) AS monto_total_metas,
                COALESCE(SUM(CASE
                    WHEN (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
                     AND (fecha_fin IS NULL OR fecha_fin >= CURDATE()) THEN 1
                    ELSE 0
                END), 0) AS metas_vigentes,
                COALESCE(SUM(CASE
                    WHEN fecha_fin IS NOT NULL
                     AND fecha_fin >= CURDATE()
                     AND fecha_fin <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 1
                    ELSE 0
                END), 0) AS metas_por_vencer
            FROM presupuesto
            WHERE id_persona = %s
            """,
            (user_id,),
        )
        t = totals[0] if totals else {}

        gasto_mes_rows = db.execute_query(
            """
            SELECT COALESCE(SUM(m.monto), 0) AS gasto_mes
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        gasto_mes = float(gasto_mes_rows[0]['gasto_mes']) if gasto_mes_rows else 0.0

        presupuesto_vigente_rows = db.execute_query(
            """
            SELECT COALESCE(SUM(monto_total), 0) AS presupuesto_vigente
            FROM presupuesto
            WHERE id_persona = %s
              AND (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
              AND (fecha_fin IS NULL OR fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuesto_vigente = (
            float(presupuesto_vigente_rows[0]['presupuesto_vigente'])
            if presupuesto_vigente_rows else 0.0
        )

        avance_estimado = 0.0
        if presupuesto_vigente > 0:
            avance_estimado = min((gasto_mes / presupuesto_vigente) * 100.0, 999.0)

        metas_rows = db.execute_query(
            """
            SELECT
                id_presupuesto,
                COALESCE(nombre, CONCAT('Meta ', id_presupuesto)) AS nombre,
                monto_total,
                fecha_inicio,
                fecha_fin,
                CASE
                    WHEN fecha_fin IS NULL THEN NULL
                    ELSE DATEDIFF(fecha_fin, CURDATE())
                END AS dias_restantes
            FROM presupuesto
            WHERE id_persona = %s
            ORDER BY fecha_fin IS NULL, fecha_fin ASC, id_presupuesto DESC
            LIMIT 5
            """,
            (user_id,),
        )

        return jsonify({
            'total_metas': int(t.get('total_metas') or 0),
            'monto_total_metas': float(t.get('monto_total_metas') or 0),
            'metas_vigentes': int(t.get('metas_vigentes') or 0),
            'metas_por_vencer': int(t.get('metas_por_vencer') or 0),
            'gasto_mes': gasto_mes,
            'presupuesto_vigente': presupuesto_vigente,
            'avance_estimado_pct': round(avance_estimado, 2),
            'metas': [
                {
                    'id': r['id_presupuesto'],
                    'nombre': r.get('nombre') or f"Meta {r['id_presupuesto']}",
                    'monto_total': float(r.get('monto_total') or 0),
                    'fecha_inicio': r['fecha_inicio'].isoformat() if r.get('fecha_inicio') else None,
                    'fecha_fin': r['fecha_fin'].isoformat() if r.get('fecha_fin') else None,
                    'dias_restantes': int(r['dias_restantes']) if r.get('dias_restantes') is not None else None,
                }
                for r in metas_rows
            ],
        }), 200
    except Exception as e:
        logger.error('Error obteniendo resumen de metas: %s', e)
        return jsonify({'message': 'Error al obtener datos de metas'}), 500
    finally:
        db.close()
