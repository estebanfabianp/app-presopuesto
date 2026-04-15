"""Rutas API para el módulo de Análisis de consumo."""

import calendar
import logging
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector
from src.analisis_thresholds import (
    SCORE_THRESHOLDS,
    SCORE_TARGETS,
    SCORE_PENALTIES,
    PRESUPUESTO_STATES,
    ALERT_THRESHOLDS,
    ANOMALY_DETECTION,
    OPPORTUNITIES,
)

bp = Blueprint('analisis', __name__, url_prefix='/api/analisis')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _safe_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _get_meses(default: int, max_meses: int = 120) -> int:
    """Obtiene y valida el rango en meses desde query params."""
    try:
        meses = int(request.args.get('meses', default))
    except (TypeError, ValueError):
        meses = default
    return max(1, min(meses, max_meses))


# ──────────────────────────────────────────────────────────────
# GET /api/analisis/resumen?meses=6
# KPIs principales: ingresos, gastos, ahorro, % ejecución presupuesto
# ──────────────────────────────────────────────────────────────
@bp.route('/resumen', methods=['GET'])
def get_resumen():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(6)
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
    meses = _get_meses(3)
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
    meses = _get_meses(12)
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
    meses  = _get_meses(1)
    limite = min(int(request.args.get('limite', 10)), 50)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                COALESCE(m.nota, '') AS descripcion,
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
                                        (SELECT SUM(mt.valor)
                     FROM movimiento_tarjeta mt
                     WHERE mt.id_tarjeta = tc.id_tarjeta
                       AND MONTH(mt.fecha) = MONTH(CURDATE())
                       AND YEAR(mt.fecha)  = YEAR(CURDATE())),
                    0
                ) AS gasto_mes
            FROM tarjeta_credito tc
            LEFT JOIN estado_tarjeta et ON et.id_estado = tc.id_estado
            WHERE tc.id_persona = %s
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


@bp.route('/score-salud', methods=['GET'])
def get_score_salud():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(3)
    db = DatabaseConnector()
    try:
        flujo = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END), 0) AS ingresos,
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gastos,
                COALESCE(SUM(CASE
                    WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
                     AND LOWER(CONVERT(COALESCE(cg.nombre, '') USING utf8mb4)) REGEXP 'arriendo|alquiler|servicio|luz|agua|gas|internet|colegio|prestamo|credito|seguro|nomina|hipoteca|suscrip'
                    THEN m.monto ELSE 0 END), 0) AS gastos_fijos
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria cg ON cg.id_categoria = m.id_categoria
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            """,
            (user_id, meses),
        )
        ingresos = _safe_float(flujo[0]['ingresos']) if flujo else 0.0
        gastos = _safe_float(flujo[0]['gastos']) if flujo else 0.0
        gastos_fijos = _safe_float(flujo[0]['gastos_fijos']) if flujo else 0.0
        tasa_ahorro = ((ingresos - gastos) / ingresos * 100) if ingresos > 0 else 0.0
        pct_fijos = (gastos_fijos / gastos * 100) if gastos > 0 else 0.0

        uso_tarjeta = db.execute_query(
            """
            SELECT COALESCE(AVG(CASE WHEN tc.limite_credito > 0 THEN (tc.saldo_actual / tc.limite_credito) * 100 ELSE 0 END), 0) AS uso_promedio
            FROM tarjeta_credito tc
            WHERE tc.id_persona = %s
            """,
            (user_id,),
        )
        pct_uso_tarjetas = _safe_float(uso_tarjeta[0]['uso_promedio']) if uso_tarjeta else 0.0

        variacion = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion)=MONTH(CURDATE()) AND YEAR(m.fecha_creacion)=YEAR(CURDATE())
                    THEN m.monto ELSE 0 END), 0) AS gasto_actual,
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion)=MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                     AND YEAR(m.fecha_creacion)=YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                    THEN m.monto ELSE 0 END), 0) AS gasto_anterior
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            """,
            (user_id,),
        )
        gasto_actual = _safe_float(variacion[0]['gasto_actual']) if variacion else 0.0
        gasto_anterior = _safe_float(variacion[0]['gasto_anterior']) if variacion else 0.0
        var_gasto = ((gasto_actual - gasto_anterior) / gasto_anterior * 100) if gasto_anterior > 0 else 0.0

        score = 100.0
        score -= max(0.0, (SCORE_TARGETS['tasa_ahorro_min'] - tasa_ahorro)) * SCORE_PENALTIES['ahorro_diferencia']
        score -= max(0.0, (pct_fijos - SCORE_TARGETS['pct_gasto_fijo_ideal'])) * SCORE_PENALTIES['fijo_exceso']
        score -= max(0.0, (pct_uso_tarjetas - SCORE_TARGETS['pct_uso_tarjetas_ideal'])) * SCORE_PENALTIES['tarjeta_exceso']
        score -= max(0.0, var_gasto - SCORE_TARGETS['variacion_gasto_max']) * SCORE_PENALTIES['variacion_exceso']
        score = max(0.0, min(100.0, round(score, 1)))

        if score >= SCORE_THRESHOLDS['excelente']:
            nivel = 'Excelente'
        elif score >= SCORE_THRESHOLDS['estable']:
            nivel = 'Estable'
        elif score >= SCORE_THRESHOLDS['en_riesgo']:
            nivel = 'En riesgo'
        else:
            nivel = 'Critico'

        return jsonify({
            'score': score,
            'nivel': nivel,
            'componentes': {
                'tasa_ahorro': round(tasa_ahorro, 1),
                'pct_gasto_fijo': round(pct_fijos, 1),
                'uso_tarjetas': round(pct_uso_tarjetas, 1),
                'variacion_gasto': round(var_gasto, 1),
            },
        })
    except Exception as e:
        logger.error('Error score-salud: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/presupuesto-categorias', methods=['GET'])
def get_presupuesto_categorias():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        ptotal = db.execute_query(
            """
            SELECT COALESCE(SUM(p.monto_total), 0) AS total
            FROM presupuesto p
            WHERE p.id_persona = %s
              AND (p.fecha_inicio IS NULL OR p.fecha_inicio <= CURDATE())
              AND (p.fecha_fin IS NULL OR p.fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuesto_total = _safe_float(ptotal[0]['total']) if ptotal else 0.0

        categorias_presupuesto = db.execute_query(
            """
            SELECT DISTINCT c.id_categoria, c.nombre
            FROM presupuesto p
            INNER JOIN presupuesto_categoria pc ON pc.id_presupuesto = p.id_presupuesto
            INNER JOIN categoria c ON c.id_categoria = pc.id_categoria
            WHERE p.id_persona = %s
              AND (p.fecha_inicio IS NULL OR p.fecha_inicio <= CURDATE())
              AND (p.fecha_fin IS NULL OR p.fecha_fin >= CURDATE())
            ORDER BY c.nombre
            """,
            (user_id,),
        )
        gasto_mes = db.execute_query(
            """
            SELECT m.id_categoria, COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(m.monto), 0) AS ejecutado
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            GROUP BY m.id_categoria, c.nombre
            ORDER BY ejecutado DESC
            """,
            (user_id,),
        )

        count_cat = len(categorias_presupuesto) if categorias_presupuesto else 0
        presupuesto_por_cat = (presupuesto_total / count_cat) if count_cat > 0 else 0.0
        pres_map = {int(r['id_categoria']): r['nombre'] for r in categorias_presupuesto if r.get('id_categoria') is not None}

        salida = []
        seen = set()
        for row in gasto_mes:
            cid = row.get('id_categoria')
            cid_key = int(cid) if cid is not None else -1
            seen.add(cid_key)
            presupuesto_cat = presupuesto_por_cat if cid is not None and int(cid) in pres_map else 0.0
            ejecutado = _safe_float(row.get('ejecutado'))
            pct = (ejecutado / presupuesto_cat * 100) if presupuesto_cat > 0 else None
            if pct is None:
                estado = 'sin-presupuesto'
            elif pct < PRESUPUESTO_STATES['verde']:
                estado = 'verde'
            elif pct <= PRESUPUESTO_STATES['amarillo']:
                estado = 'amarillo'
            else:
                estado = 'rojo'
            salida.append({
                'categoria': row.get('categoria') or 'Sin categoría',
                'presupuesto': round(presupuesto_cat, 2),
                'ejecutado': round(ejecutado, 2),
                'desviacion': round(ejecutado - presupuesto_cat, 2),
                'pct': round(pct, 1) if pct is not None else None,
                'estado': estado,
            })

        for cid, nombre in pres_map.items():
            if cid in seen:
                continue
            salida.append({
                'categoria': nombre,
                'presupuesto': round(presupuesto_por_cat, 2),
                'ejecutado': 0.0,
                'desviacion': round(-presupuesto_por_cat, 2),
                'pct': 0.0,
                'estado': 'verde',
            })

        salida.sort(key=lambda x: x['ejecutado'], reverse=True)
        return jsonify({
            'presupuesto_total': round(presupuesto_total, 2),
            'categorias': salida[:20],
        })
    except Exception as e:
        logger.error('Error presupuesto-categorias: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/anomalias', methods=['GET'])
def get_anomalias():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(6)
    limite = min(int(request.args.get('limite', 10)), 50)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                x.id_movimiento,
                x.fecha_creacion,
                x.monto,
                x.descripcion,
                x.categoria,
                x.promedio_categoria,
                x.desviacion_categoria
            FROM (
                SELECT
                    m.id_movimiento,
                    m.fecha_creacion,
                    m.monto,
                    COALESCE(m.nota, '') AS descripcion,
                    COALESCE(c.nombre, 'Sin categoría') AS categoria,
                    AVG(m.monto) OVER(PARTITION BY m.id_categoria) AS promedio_categoria,
                    STDDEV_POP(m.monto) OVER(PARTITION BY m.id_categoria) AS desviacion_categoria
                FROM movimiento m
                INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
                INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
                LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
                WHERE cta.id_persona = %s
                  AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
                  AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            ) x
            WHERE x.monto > (x.promedio_categoria + (2 * COALESCE(x.desviacion_categoria, 0)))
              AND x.monto > (x.promedio_categoria * 1.5)
            ORDER BY x.monto DESC
            LIMIT %s
            """,
            (user_id, meses, limite),
        )
        return jsonify([
            {
                'id': r['id_movimiento'],
                'fecha': str(r['fecha_creacion'])[:10],
                'monto': _safe_float(r['monto']),
                'descripcion': r['descripcion'],
                'categoria': r['categoria'],
                'promedio': round(_safe_float(r['promedio_categoria']), 2),
                'desviacion': round(_safe_float(r['desviacion_categoria']), 2),
            }
            for r in rows
        ])
    except Exception as e:
        logger.error('Error anomalias: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/proyeccion-mes', methods=['GET'])
def get_proyeccion_mes():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        q = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END), 0) AS ingresos_mes,
                COALESCE(SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto' THEN m.monto ELSE 0 END), 0) AS gastos_mes
            FROM movimiento m
            INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE c.id_persona = %s
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        ingresos = _safe_float(q[0]['ingresos_mes']) if q else 0.0
        gastos = _safe_float(q[0]['gastos_mes']) if q else 0.0

        ptotal = db.execute_query(
            """
            SELECT COALESCE(SUM(monto_total), 0) AS presupuesto_total
            FROM presupuesto
            WHERE id_persona = %s
              AND (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
              AND (fecha_fin IS NULL OR fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuesto_total = _safe_float(ptotal[0]['presupuesto_total']) if ptotal else 0.0

        today = date.today()
        dias_mes = calendar.monthrange(today.year, today.month)[1]
        dias_transcurridos = today.day
        factor = (dias_mes / dias_transcurridos) if dias_transcurridos > 0 else 1

        proy_ingresos = ingresos * factor
        proy_gastos = gastos * factor
        proy_ahorro = proy_ingresos - proy_gastos
        exceso = (proy_gastos - presupuesto_total) if presupuesto_total > 0 else 0.0

        return jsonify({
            'ingresos_actual': round(ingresos, 2),
            'gastos_actual': round(gastos, 2),
            'proy_ingresos': round(proy_ingresos, 2),
            'proy_gastos': round(proy_gastos, 2),
            'proy_ahorro': round(proy_ahorro, 2),
            'presupuesto_total': round(presupuesto_total, 2),
            'exceso_estimado': round(exceso, 2),
            'dias_transcurridos': dias_transcurridos,
            'dias_mes': dias_mes,
        })
    except Exception as e:
        logger.error('Error proyeccion-mes: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/oportunidades', methods=['GET'])
def get_oportunidades():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        oportunidades = []
        var_rows = db.execute_query(
            """
            SELECT
                COALESCE(c.nombre, 'Sin categoría') AS categoria,
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion)=MONTH(CURDATE()) AND YEAR(m.fecha_creacion)=YEAR(CURDATE())
                    THEN m.monto ELSE 0 END), 0) AS actual,
                COALESCE(SUM(CASE
                    WHEN MONTH(m.fecha_creacion)=MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                     AND YEAR(m.fecha_creacion)=YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
                    THEN m.monto ELSE 0 END), 0) AS anterior
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
            GROUP BY m.id_categoria, c.nombre
            LIMIT 8
            """,
            (user_id,),
        )

        var_rows = sorted(var_rows, key=lambda x: (_safe_float(x.get('actual')) - _safe_float(x.get('anterior'))), reverse=True)
        for r in var_rows:
            actual = _safe_float(r['actual'])
            anterior = _safe_float(r['anterior'])
            if anterior > 0 and actual > anterior * 1.15:
                oportunidades.append({
                    'tipo': 'reduccion_categoria',
                    'titulo': f"{r['categoria']} subio {round(((actual-anterior)/anterior)*100, 1)}%",
                    'impacto_mensual': round(actual - anterior, 2),
                    'accion': 'Revisar tope de categoria y gastos recurrentes',
                    'action_type': 'ajustar_presupuesto',
                    'categoria': r['categoria'],
                })

        sus = db.execute_query(
            """
            SELECT COALESCE(SUM(m.monto), 0) AS total_sus
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
              AND LOWER(CONVERT(COALESCE(c.nombre, '') USING utf8mb4)) REGEXP 'suscrip|stream|membresia|apps'
            """,
            (user_id,),
        )
        total_sus = _safe_float(sus[0]['total_sus']) if sus else 0.0
        if total_sus > 0:
            oportunidades.append({
                'tipo': 'suscripciones',
                'titulo': 'Suscripciones detectadas',
                'impacto_mensual': round(total_sus, 2),
                'accion': 'Cancelar o renegociar suscripciones poco usadas',
                'action_type': 'revisar_suscripciones',
            })

        return jsonify(oportunidades[:10])
    except Exception as e:
        logger.error('Error oportunidades: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/cohortes', methods=['GET'])
def get_cohortes():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(6)
    db = DatabaseConnector()
    try:
        por_dia = db.execute_query(
            """
            SELECT
                WEEKDAY(m.fecha_creacion) AS wd,
                COALESCE(SUM(m.monto), 0) AS total
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY WEEKDAY(m.fecha_creacion)
            ORDER BY wd
            """,
            (user_id, meses),
        )
        nombres = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        by_day = [0.0] * 7
        for r in por_dia:
            idx = int(r['wd']) if r['wd'] is not None else 0
            if 0 <= idx <= 6:
                by_day[idx] = round(_safe_float(r['total']), 2)

        por_quincena = db.execute_query(
            """
            SELECT
                CASE WHEN DAY(m.fecha_creacion) <= 15 THEN 'q1' ELSE 'q2' END AS quincena,
                COALESCE(SUM(m.monto), 0) AS total
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY CASE WHEN DAY(m.fecha_creacion) <= 15 THEN 'q1' ELSE 'q2' END
            """,
            (user_id, meses),
        )
        quincena = {'q1': 0.0, 'q2': 0.0}
        for r in por_quincena:
            quincena[r['quincena']] = round(_safe_float(r['total']), 2)

        return jsonify({
            'dias_semana': [{'dia': nombres[i], 'total': by_day[i]} for i in range(7)],
            'quincena': quincena,
        })
    except Exception as e:
        logger.error('Error cohortes: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/fijo-variable', methods=['GET'])
def get_fijo_variable():
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(3)
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE
                    WHEN LOWER(CONVERT(COALESCE(c.nombre, '') USING utf8mb4)) REGEXP 'arriendo|alquiler|servicio|luz|agua|gas|internet|colegio|prestamo|credito|seguro|nomina|hipoteca|suscrip'
                    THEN m.monto ELSE 0 END), 0) AS fijo,
                COALESCE(SUM(CASE
                    WHEN LOWER(CONVERT(COALESCE(c.nombre, '') USING utf8mb4)) REGEXP 'arriendo|alquiler|servicio|luz|agua|gas|internet|colegio|prestamo|credito|seguro|nomina|hipoteca|suscrip'
                    THEN 0 ELSE m.monto END), 0) AS variable,
                COALESCE(SUM(m.monto), 0) AS total_gasto
            FROM movimiento m
            INNER JOIN cuenta cta ON cta.id_cuenta = m.id_cuenta
            INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
            WHERE cta.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            """,
            (user_id, meses),
        )
        fijo = _safe_float(rows[0]['fijo']) if rows else 0.0
        variable = _safe_float(rows[0]['variable']) if rows else 0.0
        total = _safe_float(rows[0]['total_gasto']) if rows else 0.0
        return jsonify({
            'fijo': round(fijo, 2),
            'variable': round(variable, 2),
            'total': round(total, 2),
            'pct_fijo': round((fijo / total * 100), 1) if total > 0 else 0,
            'pct_variable': round((variable / total * 100), 1) if total > 0 else 0,
        })
    except Exception as e:
        logger.error('Error fijo-variable: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/alertas-inteligentes', methods=['GET'])
def get_alertas_inteligentes():
    verify_jwt_in_request()
    user_id = _get_user_id()
    db = DatabaseConnector()
    try:
        alertas = []

        presupuesto = db.execute_query(
            """
            SELECT
                COALESCE(SUM(p.monto_total), 0) AS presupuesto_total,
                COALESCE(SUM(CASE
                    WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
                     AND MONTH(m.fecha_creacion)=MONTH(CURDATE())
                     AND YEAR(m.fecha_creacion)=YEAR(CURDATE())
                    THEN m.monto ELSE 0 END), 0) AS gasto_mes
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
            LEFT JOIN presupuesto p ON p.id_persona = c.id_persona
            WHERE c.id_persona = %s
            """,
            (user_id,),
        )
        if presupuesto:
            ptotal = _safe_float(presupuesto[0]['presupuesto_total'])
            gmes = _safe_float(presupuesto[0]['gasto_mes'])
            pct = (gmes / ptotal * 100) if ptotal > 0 else 0
            if pct >= ALERT_THRESHOLDS['presupuesto_warning']:
                nivel_alerta = 'alta' if pct >= ALERT_THRESHOLDS['presupuesto_critical'] else 'media'
                alertas.append({
                    'tipo': 'presupuesto',
                    'nivel': nivel_alerta,
                    'mensaje': f'Consumo mensual en {round(pct, 1)}% del presupuesto.',
                })

        tarjetas = db.execute_query(
            """
            SELECT COUNT(*) AS criticas
            FROM tarjeta_credito
            WHERE id_persona = %s
              AND limite_credito > 0
              AND (saldo_actual / limite_credito) >= %s
            """,
            (user_id, ALERT_THRESHOLDS['tarjeta_warning']),
        )
        crit = int(tarjetas[0]['criticas']) if tarjetas else 0
        if crit > 0:
            pct_aviso = int(ALERT_THRESHOLDS['tarjeta_warning'] * 100)
            alertas.append({
                'tipo': 'tarjetas',
                'nivel': 'media',
                'mensaje': f'{crit} tarjeta(s) con uso mayor o igual a {pct_aviso}% del cupo.',
            })

        if not alertas:
            alertas.append({
                'tipo': 'estado',
                'nivel': 'ok',
                'mensaje': 'Sin alertas criticas por ahora. Buen control financiero.',
            })

        return jsonify(alertas)
    except Exception as e:
        logger.error('Error alertas-inteligentes: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
