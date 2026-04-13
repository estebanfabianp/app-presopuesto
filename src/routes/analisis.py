"""Rutas API para el módulo de Análisis de consumo."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('analisis', __name__, url_prefix='/api/analisis')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/resumen?meses=6
# KPIs principales: ingresos, gastos, ahorro, % ejecución presupuesto
# ──────────────────────────────────────────────────────────────
@bp.route('/resumen', methods=['GET'])
def get_resumen():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = min(int(request.args.get('meses', 6)), 24)
    db = DatabaseConnector()
    try:
        # Ingresos y gastos del periodo
        flujo = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso'
                                  THEN m.monto ELSE 0 END), 0) AS ingresos,
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
                                  THEN m.monto ELSE 0 END), 0) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            """,
            (user_id, meses),
        )
        ingresos = float(flujo[0]['ingresos']) if flujo else 0.0
        gastos   = float(flujo[0]['gastos'])   if flujo else 0.0
        ahorro   = ingresos - gastos
        tasa_ahorro = round(ahorro / ingresos * 100, 1) if ingresos > 0 else 0.0

        # Presupuesto ejecutado (mes actual)
        pres = db.execute_query(
            """
            SELECT COALESCE(SUM(monto_total), 0) AS presupuesto_total
            FROM presupuesto
            WHERE id_persona = %s
              AND (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
              AND (fecha_fin IS NULL OR fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuesto_total = float(pres[0]['presupuesto_total']) if pres else 0.0
        gasto_mes = db.execute_query(
            """
            SELECT COALESCE(SUM(m.monto), 0) AS gasto_mes
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion)  = YEAR(CURDATE())
            """,
            (user_id,),
        )
        gasto_mes_val = float(gasto_mes[0]['gasto_mes']) if gasto_mes else 0.0
        pct_presupuesto = round(gasto_mes_val / presupuesto_total * 100, 1) if presupuesto_total > 0 else None

        return jsonify({
            'ingresos':         ingresos,
            'gastos':           gastos,
            'ahorro':           ahorro,
            'tasa_ahorro':      tasa_ahorro,
            'gasto_mes':        gasto_mes_val,
            'presupuesto_total': presupuesto_total,
            'pct_presupuesto':  pct_presupuesto,
        })
    except Exception as e:
        logger.error('Error resumen análisis: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/por-categoria?meses=3
# Gasto desglosado por categoría
# ──────────────────────────────────────────────────────────────
@bp.route('/por-categoria', methods=['GET'])
def get_por_categoria():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = min(int(request.args.get('meses', 3)), 24)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                COALESCE(c.nombre, 'Sin categoría') AS categoria,
                COALESCE(SUM(m.monto), 0) AS total,
                COUNT(*) AS transacciones
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY m.id_categoria, c.nombre
            ORDER BY total DESC
            LIMIT 15
            """,
            (user_id, meses),
        )
        return jsonify([
            {
                'categoria':      r['categoria'],
                'total':          float(r['total']),
                'transacciones':  r['transacciones'],
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error por-categoria: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/tendencia?meses=12
# Ingresos y gastos mes a mes
# ──────────────────────────────────────────────────────────────
@bp.route('/tendencia', methods=['GET'])
def get_tendencia():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = min(int(request.args.get('meses', 12)), 24)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(m.fecha_creacion, '%%Y-%%m') AS mes,
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso'
                                  THEN m.monto ELSE 0 END), 0) AS ingresos,
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
                                  THEN m.monto ELSE 0 END), 0) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY DATE_FORMAT(m.fecha_creacion, '%%Y-%%m')
            ORDER BY mes ASC
            """,
            (user_id, meses),
        )
        return jsonify([
            {
                'mes':      r['mes'],
                'ingresos': float(r['ingresos']),
                'gastos':   float(r['gastos']),
                'ahorro':   float(r['ingresos']) - float(r['gastos']),
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error tendencia: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/top-gastos?meses=1&limite=10
# Transacciones de mayor monto en el periodo
# ──────────────────────────────────────────────────────────────
@bp.route('/top-gastos', methods=['GET'])
def get_top_gastos():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses  = min(int(request.args.get('meses', 1)), 24)
    limite = min(int(request.args.get('limite', 10)), 50)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                m.descripcion,
                m.monto,
                m.fecha_creacion,
                COALESCE(c.nombre, 'Sin categoría') AS categoria
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            ORDER BY m.monto DESC
            LIMIT %s
            """,
            (user_id, meses, limite),
        )
        return jsonify([
            {
                'id':            r['id_movimiento'],
                'descripcion':   r['descripcion'],
                'monto':         float(r['monto']),
                'fecha':         str(r['fecha_creacion'])[:10],
                'categoria':     r['categoria'],
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error top-gastos: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/tarjetas
# Resumen de uso de tarjetas de crédito
# ──────────────────────────────────────────────────────────────
@bp.route('/tarjetas', methods=['GET'])
def get_analisis_tarjetas():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                tc.id_tarjeta,
                tc.numero_tarjeta,
                tc.limite_credito,
                tc.saldo_actual,
                COALESCE(et.nombre, 'Activa') AS estado,
                COALESCE(
                    (SELECT COUNT(*) FROM tarjeta_diferido td WHERE td.id_tarjeta = tc.id_tarjeta),
                    0
                ) AS diferidos_activos,
                COALESCE(
                    (SELECT SUM(mt.monto)
                     FROM movimiento_tarjeta mt
                     WHERE mt.id_tarjeta = tc.id_tarjeta
                       AND MONTH(mt.fecha_movimiento) = MONTH(CURDATE())
                       AND YEAR(mt.fecha_movimiento)  = YEAR(CURDATE())),
                    0
                ) AS gasto_mes
            FROM tarjeta_credito tc
            INNER JOIN producto p ON p.id_producto = tc.id_producto
            LEFT JOIN estado_tarjeta et ON et.id_estado = tc.id_estado
            WHERE p.id_persona = %s
            ORDER BY tc.saldo_actual DESC
            """,
            (user_id,),
        )
        return jsonify([
            {
                'id':               r['id_tarjeta'],
                'numero':           r['numero_tarjeta'],
                'limite':           float(r['limite_credito'] or 0),
                'saldo':            float(r['saldo_actual'] or 0),
                'disponible':       float(r['limite_credito'] or 0) - float(r['saldo_actual'] or 0),
                'pct_uso':          round(float(r['saldo_actual'] or 0) / float(r['limite_credito']) * 100, 1) if r['limite_credito'] else 0,
                'estado':           r['estado'],
                'diferidos':        r['diferidos_activos'],
                'gasto_mes':        float(r['gasto_mes'] or 0),
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error analisis tarjetas: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/comparativa-meses
# Comparativa gasto actual vs mes anterior por categoría
# ──────────────────────────────────────────────────────────────
@bp.route('/comparativa-meses', methods=['GET'])
def get_comparativa():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                COALESCE(c.nombre, 'Sin categoría') AS categoria,
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion) = MONTH(CURDATE())
                     AND YEAR(m.fecha_creacion)  = YEAR(CURDATE())
                    THEN m.monto ELSE 0 END), 0) AS mes_actual,
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                     AND YEAR(m.fecha_creacion)  = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                    THEN m.monto ELSE 0 END), 0) AS mes_anterior
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            GROUP BY m.id_categoria, c.nombre
            HAVING mes_actual > 0 OR mes_anterior > 0
            ORDER BY mes_actual DESC
            LIMIT 12
            """,
            (user_id,),
        )
        return jsonify([
            {
                'categoria':    r['categoria'],
                'mes_actual':   float(r['mes_actual']),
                'mes_anterior': float(r['mes_anterior']),
                'variacion':    round((float(r['mes_actual']) - float(r['mes_anterior'])) / float(r['mes_anterior']) * 100, 1)
                                if float(r['mes_anterior']) > 0 else None,
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error comparativa meses: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
