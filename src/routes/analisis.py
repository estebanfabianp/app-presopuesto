"""Rutas API para el módulo de Análisis de consumo."""

import calendar
import logging
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

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


def _has_column(db: DatabaseConnector, table_name: str, column_name: str) -> bool:
        rows = db.execute_query(
                """
                SELECT 1
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = %s
                LIMIT 1
                """,
                (table_name, column_name),
        ) or []
        return bool(rows)


def _table_exists(db: DatabaseConnector, table_name: str) -> bool:
        rows = db.execute_query(
                """
                SELECT 1
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                LIMIT 1
                """,
                (table_name,),
        ) or []
        return bool(rows)


def _datos_consumo(db, user_id, inicio, fin):
    """Movimientos reales compatibles con el criterio de la hoja de presupuesto."""
    if not db.conn:
        raise RuntimeError('No hay conexión para consultar movimientos')
    with db.conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT DATE(m.fecha_creacion) AS fecha, m.monto, LOWER(tm.nombre) AS tipo,
                   m.id_categoria, COALESCE(c.nombre,'Sin categoría') AS categoria,
                   c.parent_id, cp.nombre AS nombre_padre, COALESCE(m.nota,'') AS descripcion, 'cuenta' AS origen
            FROM movimiento m JOIN cuenta cu ON cu.id_cuenta=m.id_cuenta
            JOIN tipo_movimiento tm ON tm.id_tipo=m.id_tipo
            LEFT JOIN categoria c ON c.id_categoria=m.id_categoria
            LEFT JOIN categoria cp ON cp.id_categoria=c.parent_id
            WHERE cu.id_persona=%s AND m.fecha_creacion >= %s AND m.fecha_creacion < %s
              AND LOWER(tm.nombre) IN ('ingreso','gasto')
              AND (LOWER(tm.nombre) <> 'gasto'
                   OR LOWER(COALESCE(c.nombre,'')) <> 'pagos de tarjeta de crédito')
            UNION ALL
            SELECT mt.fecha, mt.valor, 'gasto', mt.id_categoria,
                   COALESCE(c.nombre,'Sin categoría'), c.parent_id, cp.nombre, COALESCE(mt.nota,''), 'tarjeta'
            FROM movimiento_tarjeta mt LEFT JOIN categoria c ON c.id_categoria=mt.id_categoria
            LEFT JOIN categoria cp ON cp.id_categoria=c.parent_id
            WHERE mt.id_persona=%s AND mt.fecha >= %s AND mt.fecha < %s
              AND LOWER(COALESCE(mt.estado,''))='compra' AND mt.valor > 0
            """,
            (user_id, inicio, fin, user_id, inicio, fin),
        )
        return cursor.fetchall()


def _detalle_presupuesto(db, user_id, inicio, fin):
    if not db.conn:
        raise RuntimeError('No hay conexión para consultar presupuesto')
    with db.conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT pd.id_categoria, COALESCE(c.nombre,pd.categoria_nombre,'Sin categoría') AS categoria,
                   c.parent_id, cp.nombre AS nombre_padre, SUM(pd.monto_estimado) AS presupuesto
            FROM presupuesto_detalle pd
            JOIN presupuesto p ON p.id_presupuesto=pd.id_presupuesto
            LEFT JOIN categoria c ON c.id_categoria=pd.id_categoria
            LEFT JOIN categoria cp ON cp.id_categoria=c.parent_id
            WHERE p.id_presupuesto=(
                SELECT MAX(p2.id_presupuesto) FROM presupuesto p2
                WHERE p2.id_persona=%s AND p2.fecha_inicio=%s AND p2.fecha_fin=%s
            ) AND (pd.tipo='egreso' OR pd.tipo IS NULL)
            GROUP BY pd.id_categoria,c.nombre,pd.categoria_nombre,c.parent_id,cp.nombre
            """, (user_id, inicio, fin),
        )
        return cursor.fetchall()


@bp.route('/vista-consumo', methods=['GET'])
def get_vista_consumo():
    """Datos consistentes de la vista, con rango móvil y comparación mensual."""
    verify_jwt_in_request()
    user_id = _get_user_id()
    meses = _get_meses(3)
    hoy = date.today()
    inicio = hoy - relativedelta(months=meses)
    fin = hoy + timedelta(days=1)
    mes_actual = hoy.replace(day=1)
    mes_anterior = mes_actual - relativedelta(months=1)
    mes_fin = mes_actual + relativedelta(months=1) - timedelta(days=1)
    db = DatabaseConnector()
    try:
        movimientos = _datos_consumo(db, user_id, min(inicio, mes_anterior), fin)
        presupuesto = _detalle_presupuesto(db, user_id, mes_actual, mes_fin)
        periodo = [m for m in movimientos if m['fecha'] >= inicio]
        ingresos = sum(float(m['monto']) for m in periodo if m['tipo'] == 'ingreso')
        gastos = sum(float(m['monto']) for m in periodo if m['tipo'] == 'gasto')
        actuales = [m for m in movimientos if m['fecha'] >= mes_actual and m['tipo'] == 'gasto']
        anteriores = [m for m in movimientos if mes_anterior <= m['fecha'] < mes_actual and m['tipo'] == 'gasto']
        movimientos_mes = sum(1 for m in movimientos if m['fecha'] >= mes_actual)
        por_cat = {}
        tendencias = {}
        for m in periodo:
            key = m['fecha'].strftime('%Y-%m')
            mes = tendencias.setdefault(key, {'mes': key, 'ingresos': 0.0, 'gastos': 0.0})
            mes['ingresos' if m['tipo'] == 'ingreso' else 'gastos'] += float(m['monto'])
            if m['tipo'] == 'gasto':
                key = m['id_categoria'] if m['id_categoria'] is not None else 'sin_categoria'
                cat = por_cat.setdefault(key, {'categoria': m['categoria'], 'total': 0.0, 'transacciones': 0})
                cat['total'] += float(m['monto'])
                cat['transacciones'] += 1
        detalle = {}
        for p in presupuesto:
            key = p['id_categoria'] if p['id_categoria'] is not None else ('manual', p['categoria'])
            cat = detalle.setdefault(key, {'id_categoria': p['id_categoria'], 'categoria': p['categoria'],
                                           'parent_id': p['parent_id'], 'nombre_padre': p['nombre_padre'], 'presupuesto': 0.0, 'ejecutado': 0.0})
            cat['presupuesto'] += float(p['presupuesto'] or 0)
        for m in actuales:
            key = m['id_categoria'] if m['id_categoria'] is not None else ('manual', 'Sin categoría')
            cat = detalle.setdefault(key, {'id_categoria': m['id_categoria'], 'categoria': m['categoria'],
                                           'parent_id': m['parent_id'], 'nombre_padre': m['nombre_padre'], 'presupuesto': 0.0, 'ejecutado': 0.0})
            cat['ejecutado'] += float(m['monto'])
        for cat in detalle.values():
            p, e = cat['presupuesto'], cat['ejecutado']
            cat['desviacion'] = round(e - p, 2)
            cat['estado'] = ('sin-datos' if not movimientos_mes else
                             'sin-presupuesto' if p <= 0 else
                             'verde' if e / p < .8 else 'amarillo' if e / p <= 1 else 'rojo')
        comparativa = {}
        for lista, campo in ((actuales, 'mes_actual'), (anteriores, 'mes_anterior')):
            for m in lista:
                key = m['id_categoria'] if m['id_categoria'] is not None else 'sin_categoria'
                item = comparativa.setdefault(key, {'categoria': m['categoria'], 'mes_actual': 0.0, 'mes_anterior': 0.0})
                item[campo] += float(m['monto'])
        for item in comparativa.values():
            previo = item['mes_anterior']
            item['variacion'] = round((item['mes_actual'] - previo) / previo * 100, 1) if previo else None
        total_presupuesto = sum(float(p['presupuesto'] or 0) for p in presupuesto)
        gasto_mes = sum(float(m['monto']) for m in actuales)
        ingresos_mes = sum(float(m['monto']) for m in movimientos if m['fecha'] >= mes_actual and m['tipo'] == 'ingreso')
        for item in tendencias.values():
            item['ahorro'] = item['ingresos'] - item['gastos']
        return jsonify({
            'inicio': inicio.isoformat(), 'fin': hoy.isoformat(),
            'ingresos_mes': ingresos_mes,
            'resumen': {'ingresos': ingresos, 'gastos': gastos, 'ahorro': ingresos - gastos,
                        'tasa_ahorro': round((ingresos - gastos) / ingresos * 100, 1) if ingresos > 0 else None,
                        'gasto_mes': gasto_mes, 'presupuesto_total': total_presupuesto,
                        'pct_presupuesto': round(gasto_mes / total_presupuesto * 100, 1) if total_presupuesto > 0 else None},
            'por_categoria': sorted(por_cat.values(), key=lambda c: c['total'], reverse=True)[:15],
            'tendencia': sorted(tendencias.values(), key=lambda c: c['mes']),
            'presupuesto_categorias': list(detalle.values()),
            'comparativa': sorted(comparativa.values(), key=lambda c: c['mes_actual'], reverse=True)[:12],
            'top': [{'fecha': m['fecha'].isoformat(), 'monto': float(m['monto']), 'categoria': m['categoria'],
                     'descripcion': m['descripcion'], 'origen': m['origen']}
                    for m in sorted((m for m in periodo if m['tipo'] == 'gasto'), key=lambda m: float(m['monto']), reverse=True)[:10]],
            'movimientos_periodo': len(periodo), 'movimientos_mes': movimientos_mes,
        })
    except Exception:
        logger.exception('Error al calcular análisis de consumo')
        return jsonify({'message': 'No fue posible calcular el análisis de consumo'}), 500
    finally:
        db.close()


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
        has_estado_col = _has_column(db, 'tarjeta_credito', 'estado')
        has_id_estado_col = _has_column(db, 'tarjeta_credito', 'id_estado')
        has_estado_tarjeta_table = _table_exists(db, 'estado_tarjeta')

        if has_estado_col:
            estado_expr = "COALESCE(tc.estado, 'Activa')"
            estado_join = ""
        elif has_id_estado_col and has_estado_tarjeta_table:
            estado_expr = "COALESCE(et.nombre, 'Activa')"
            estado_join = "LEFT JOIN estado_tarjeta et ON et.id_estado = tc.id_estado"
        else:
            estado_expr = "'Activa'"
            estado_join = ""

        rows = db.execute_query(
            """
            SELECT
                tc.id_tarjeta,
                tc.numero_tarjeta,
                tc.limite_credito,
                tc.saldo_actual,
                {estado_expr} AS estado,
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
            {estado_join}
            WHERE tc.id_persona = %s
            ORDER BY tc.saldo_actual DESC
            """.format(estado_expr=estado_expr, estado_join=estado_join),
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
    hoy = date.today()
    inicio = hoy.replace(day=1)
    fin_mes = inicio + relativedelta(months=1) - timedelta(days=1)
    db = DatabaseConnector()
    try:
        movimientos = _datos_consumo(db, user_id, inicio, hoy + timedelta(days=1))
        with db.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT pd.id_categoria, MIN(pd.es_fijo) AS minimo, MAX(pd.es_fijo) AS maximo
                FROM presupuesto_detalle pd
                WHERE pd.id_presupuesto=(
                    SELECT MAX(p.id_presupuesto) FROM presupuesto p
                    WHERE p.id_persona=%s AND p.fecha_inicio=%s AND p.fecha_fin=%s
                ) AND (pd.tipo='egreso' OR pd.tipo IS NULL)
                GROUP BY pd.id_categoria
                """, (user_id, inicio, fin_mes),
            )
            clasificaciones = {r['id_categoria']: r for r in cursor.fetchall() if r['id_categoria'] is not None}
            cursor.execute(
                """
                SELECT COUNT(*) AS cantidad,
                       SUM(CASE WHEN limite_credito IS NULL OR limite_credito <= 0 OR saldo_actual IS NULL
                           THEN 1 ELSE 0 END) AS incompletas,
                       AVG(CASE WHEN limite_credito > 0 AND saldo_actual IS NOT NULL
                           THEN GREATEST(saldo_actual, 0) / limite_credito * 100 END) AS uso
                FROM tarjeta_credito WHERE id_persona=%s
                  AND COALESCE(LOWER(estado), 'activa') IN ('activa', 'activo')
                """, (user_id,),
            )
            tarjetas = cursor.fetchone()
        ingresos = sum(float(m['monto']) for m in movimientos if m['tipo'] == 'ingreso')
        egresos = [m for m in movimientos if m['tipo'] == 'gasto']
        gastos = sum(float(m['monto']) for m in egresos)
        sin_clasificar = sorted({m['categoria'] for m in egresos
            if m['id_categoria'] not in clasificaciones
            or clasificaciones[m['id_categoria']]['minimo'] is None
            or clasificaciones[m['id_categoria']]['minimo'] != clasificaciones[m['id_categoria']]['maximo']})
        razones = []
        if ingresos <= 0:
            razones.append('Registra ingresos reales del mes.')
        if gastos <= 0:
            razones.append('Registra gastos reales del mes.')
        if sin_clasificar:
            razones.append('Clasifica como fija o variable en el presupuesto mensual cada categoría de gasto, sin marcas contradictorias: ' + ', '.join(sin_clasificar) + '.')
        if tarjetas['incompletas']:
            razones.append('Completa el saldo y el límite de las tarjetas activas.')
        tasa_ahorro = (ingresos - gastos) / ingresos * 100 if ingresos > 0 else None
        gastos_fijos = sum(float(m['monto']) for m in egresos
            if m['id_categoria'] in clasificaciones
            and clasificaciones[m['id_categoria']]['minimo'] == 1
            and clasificaciones[m['id_categoria']]['maximo'] == 1)
        pct_fijos = gastos_fijos / gastos * 100 if gastos > 0 and not sin_clasificar else None
        uso = float(tarjetas['uso']) if tarjetas['cantidad'] and not tarjetas['incompletas'] else None
        score = None
        nivel = 'Sin datos suficientes'
        if not razones and tasa_ahorro is not None and pct_fijos is not None:
            score = 100.0
            score -= max(0.0, SCORE_TARGETS['tasa_ahorro_min'] - tasa_ahorro) * SCORE_PENALTIES['ahorro_diferencia']
            score -= max(0.0, pct_fijos - SCORE_TARGETS['pct_gasto_fijo_ideal']) * SCORE_PENALTIES['fijo_exceso']
            if uso is not None:
                score -= max(0.0, uso - SCORE_TARGETS['pct_uso_tarjetas_ideal']) * SCORE_PENALTIES['tarjeta_exceso']
            score = max(0.0, min(100.0, round(score, 1)))
            nivel = ('Excelente' if score >= SCORE_THRESHOLDS['excelente'] else
                     'Estable' if score >= SCORE_THRESHOLDS['estable'] else
                     'En riesgo' if score >= SCORE_THRESHOLDS['en_riesgo'] else 'Crítico')
        return jsonify({'score': score, 'nivel': nivel, 'razones': razones,
                        'inicio': inicio.isoformat(), 'fin': hoy.isoformat(),
                        'componentes': {
                            'tasa_ahorro': round(tasa_ahorro, 1) if tasa_ahorro is not None else None,
                            'pct_gasto_fijo': round(pct_fijos, 1) if pct_fijos is not None else None,
                            'uso_tarjetas': round(uso, 1) if uso is not None else None,
                        }})
    except Exception:
        logger.exception('Error score-salud')
        return jsonify({'error': 'No fue posible calcular la salud financiera'}), 500
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
