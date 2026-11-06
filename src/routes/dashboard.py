"""
Rutas del Dashboard — datos reales desde MySQL.
"""

from datetime import date, datetime, timedelta

import pandas as pd
from flask import Blueprint, jsonify, request
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


def _safe_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_date_arg(value: str | None, fallback: date) -> date:
    if not value:
        return fallback
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return fallback


def _color_for_index(idx: int) -> str:
    return _CHART_COLORS[idx % len(_CHART_COLORS)]


@bp.route('/meses-con-movimientos', methods=['GET'])
def get_meses_con_movimientos():
    """Presencia de movimientos por mes, hasta la fecha actual."""
    verify_jwt_in_request()
    identity = get_jwt_identity()
    if not str(identity).isdigit() or int(identity) <= 0:
        return jsonify({'message': 'Identidad de usuario inválida'}), 401

    db = DatabaseConnector()
    try:
        if not db.is_connected():
            raise RuntimeError('No hay conexión con la base de datos')

        hoy = date.today()
        limite = hoy + timedelta(days=1)
        with db.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT 'cuentas' AS tipo, YEAR(m.fecha_creacion) AS anio,
                       MONTH(m.fecha_creacion) AS mes, COUNT(*) AS cantidad
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s AND m.fecha_creacion < %s
                GROUP BY YEAR(m.fecha_creacion), MONTH(m.fecha_creacion)
                UNION ALL
                SELECT 'tarjetas' AS tipo, YEAR(mt.fecha) AS anio,
                       MONTH(mt.fecha) AS mes, COUNT(*) AS cantidad
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s AND mt.fecha < %s
                GROUP BY YEAR(mt.fecha), MONTH(mt.fecha)
                """,
                (int(identity), limite, int(identity), limite),
            )
            rows = cursor.fetchall()

        counts = {'cuentas': {}, 'tarjetas': {}}
        for row in rows:
            key = f"{int(row['anio']):04d}-{int(row['mes']):02d}"
            counts[row['tipo']][key] = int(row['cantidad'])

        current = hoy.year * 12 + hoy.month - 1
        months = []
        for offset in range(12):
            year, month = divmod(current - offset, 12)
            key = f'{year:04d}-{month + 1:02d}'
            months.append({
                'mes': key,
                'cuentas': counts['cuentas'].get(key, 0),
                'tarjetas': counts['tarjetas'].get(key, 0),
            })

        return jsonify({
            'meses': months,
            'ultimo_mes': {
                tipo: max(valores, default=None)
                for tipo, valores in counts.items()
            },
        }), 200
    except Exception:
        logger.exception('Error al consultar meses con movimientos')
        return jsonify({'message': 'No fue posible consultar los meses con movimientos'}), 500
    finally:
        db.close()


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


@bp.route('/gastos-categoria-tendencia', methods=['GET'])
def get_gastos_categoria_tendencia():
    """
    GET /api/dashboard/gastos-categoria-tendencia
    Serie temporal de gastos por categoría con filtros de fecha y categoría.
    Registros sin categoría se reasignan a "Sin categoría" usando Pandas.
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        today = date.today()
        default_start = today - timedelta(days=180)
        start_date = _parse_date_arg(request.args.get('fecha_inicio'), default_start)
        end_date = _parse_date_arg(request.args.get('fecha_fin'), today)
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        selected_categories = {
            c.strip()
            for c in (request.args.get('categorias') or '').split(',')
            if c.strip()
        }
        selected_products = {
            p.strip()
            for p in (request.args.get('productos') or '').split(',')
            if p.strip()
        }

        catalog_rows = db.execute_query(
            """
            SELECT id_producto, nombre
            FROM v_producto_unificado
            WHERE id_persona = %s
            ORDER BY nombre ASC
            """,
            (user_id,),
        ) or []

        available_products_catalog = [
            {'id': str(int(r['id_producto'])), 'nombre': str(r['nombre'])}
            for r in catalog_rows
            if r.get('id_producto') is not None
        ]

        rows = db.execute_query(
            """
            SELECT
                DATE(m.fecha_creacion) AS fecha,
                COALESCE(m.monto, 0) AS monto,
                cat.id_categoria AS id_categoria,
                cat.nombre AS categoria,
                m.id_producto AS id_producto,
                COALESCE(vpu.nombre, CONCAT('Producto ', m.id_producto)) AS producto
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
            LEFT JOIN v_producto_unificado vpu
              ON vpu.id_persona = c.id_persona
             AND vpu.id_producto = m.id_producto
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND DATE(m.fecha_creacion) BETWEEN %s AND %s
            ORDER BY m.fecha_creacion ASC
            """,
            (user_id, start_date, end_date),
        )

        if not rows:
            return jsonify({
                'filters': {
                    'fecha_inicio': str(start_date),
                    'fecha_fin': str(end_date),
                    'categories_selected': [],
                    'products_selected': sorted(selected_products),
                },
                'available_categories': [],
                'available_products': available_products_catalog,
                'labels': [],
                'datasets': [],
                'granularidad': 'mensual',
            }), 200

        df = pd.DataFrame(rows)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0.0)

        # Regla de limpieza: categorías nulas o vacías se renombran a "Sin categoría".
        df['categoria'] = df['categoria'].fillna('').astype(str).str.strip()
        df.loc[df['categoria'] == '', 'categoria'] = 'Sin categoría'
        df['categoria_key'] = df['id_categoria'].apply(
            lambda x: 'sin_categoria' if pd.isna(x) else str(int(x))
        )
        df['producto'] = df['producto'].fillna('').astype(str).str.strip()
        df.loc[df['producto'] == '', 'producto'] = 'Sin producto'
        df['producto_key'] = df['id_producto'].apply(
            lambda x: 'sin_producto' if pd.isna(x) else str(int(x))
        )

        categories_df = (
            df[['categoria_key', 'categoria']]
            .drop_duplicates()
            .sort_values('categoria')
        )
        available_categories = [
            {'id': row['categoria_key'], 'nombre': row['categoria']}
            for _, row in categories_df.iterrows()
        ]
        products_df = (
            df[['producto_key', 'producto']]
            .drop_duplicates()
            .sort_values('producto')
        )
        movement_products = [
            {'id': row['producto_key'], 'nombre': row['producto']}
            for _, row in products_df.iterrows()
        ]

        available_products_by_id = {
            p['id']: p for p in available_products_catalog
        }
        for prod in movement_products:
            available_products_by_id[prod['id']] = prod
        available_products = list(available_products_by_id.values())
        available_products.sort(key=lambda x: (x['nombre'] or '').lower())

        if selected_categories:
            df = df[df['categoria_key'].isin(selected_categories)]
        if selected_products:
            df = df[df['producto_key'].isin(selected_products)]

        if df.empty:
            return jsonify({
                'filters': {
                    'fecha_inicio': str(start_date),
                    'fecha_fin': str(end_date),
                    'categories_selected': sorted(selected_categories),
                    'products_selected': sorted(selected_products),
                },
                'available_categories': available_categories,
                'available_products': available_products,
                'labels': [],
                'datasets': [],
                'granularidad': 'mensual',
            }), 200

        total_days = (end_date - start_date).days
        use_daily = total_days <= 62
        granularidad = 'diaria' if use_daily else 'mensual'

        if use_daily:
            df['periodo'] = df['fecha'].dt.strftime('%Y-%m-%d')
        else:
            df['periodo'] = df['fecha'].dt.to_period('M').dt.to_timestamp().dt.strftime('%Y-%m')

        grouped = (
            df.groupby(['periodo', 'categoria'], as_index=False)['monto']
            .sum()
        )

        pivot = grouped.pivot(index='periodo', columns='categoria', values='monto').fillna(0.0)
        period_index = pd.to_datetime(pivot.index)
        pivot = pivot.reindex(pivot.index[period_index.argsort()])

        if use_daily:
            labels = [pd.to_datetime(p).strftime('%d %b %Y') for p in pivot.index]
        else:
            labels = [pd.to_datetime(f'{p}-01').strftime('%b %Y') for p in pivot.index]

        datasets = []
        for idx, category_name in enumerate(pivot.columns.tolist()):
            datasets.append({
                'label': category_name,
                'data': [float(v) for v in pivot[category_name].tolist()],
                'borderColor': _color_for_index(idx),
                'backgroundColor': _color_for_index(idx),
                'tension': 0.25,
            })

        return jsonify({
            'filters': {
                'fecha_inicio': str(start_date),
                'fecha_fin': str(end_date),
                'categories_selected': sorted(selected_categories),
                'products_selected': sorted(selected_products),
            },
            'available_categories': available_categories,
            'available_products': available_products,
            'labels': labels,
            'datasets': datasets,
            'granularidad': granularidad,
        }), 200

    except Exception as e:
        logger.error('Gastos categoria tendencia error: %s', e)
        return jsonify({'message': 'Error al obtener tendencia de gastos por categoría'}), 500
    finally:
        db.close()


@bp.route('/overview', methods=['GET'])
def get_overview():
    """
    GET /api/dashboard/overview
    Dashboard extendido con comparativos, alertas, flujo semanal,
    top categorías/beneficiarios y próximos compromisos.
    """
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        month_rows = db.execute_query(
            """
            SELECT
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'   THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
              AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
            """,
            (user_id,),
        )
        current_ingresos = _safe_float(month_rows[0]['ingresos']) if month_rows else 0.0
        current_gastos = _safe_float(month_rows[0]['gastos']) if month_rows else 0.0

        prev_rows = db.execute_query(
            """
            SELECT
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'   THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND MONTH(m.fecha_creacion) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
              AND YEAR(m.fecha_creacion) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
            """,
            (user_id,),
        )
        prev_ingresos = _safe_float(prev_rows[0]['ingresos']) if prev_rows else 0.0
        prev_gastos = _safe_float(prev_rows[0]['gastos']) if prev_rows else 0.0

        budget_rows = db.execute_query(
            """
            SELECT
                COALESCE(SUM(p.monto_total), 0) AS presupuesto_total,
                COUNT(*) AS presupuestos_activos
            FROM presupuesto p
            WHERE p.id_persona = %s
              AND (p.fecha_inicio IS NULL OR p.fecha_inicio <= CURDATE())
              AND (p.fecha_fin IS NULL OR p.fecha_fin >= CURDATE())
            """,
            (user_id,),
        )
        presupuesto_total = _safe_float(budget_rows[0]['presupuesto_total']) if budget_rows else 0.0
        presupuestos_activos = int(budget_rows[0]['presupuestos_activos']) if budget_rows else 0

        saldo_rows = db.execute_query(
            """
            SELECT COALESCE(SUM(saldo_actual), 0) AS saldo_total
            FROM v_cuenta_saldos
            WHERE id_persona = %s
            """,
            (user_id,),
        )
        saldo_total_cuentas = _safe_float(saldo_rows[0]['saldo_total']) if saldo_rows else 0.0

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

        # Flujo semanal de las últimas 8 semanas.
        weekly_rows = db.execute_query(
            """
            SELECT
                DATE_FORMAT(DATE_SUB(DATE(m.fecha_creacion), INTERVAL WEEKDAY(m.fecha_creacion) DAY), '%d/%m') AS semana,
                YEARWEEK(m.fecha_creacion, 3) AS week_key,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'ingreso' THEN m.monto ELSE 0 END) AS ingresos,
                SUM(CASE WHEN LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'   THEN m.monto ELSE 0 END) AS gastos
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE c.id_persona = %s
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 8 WEEK)
            GROUP BY week_key, semana
            ORDER BY week_key ASC
            """,
            (user_id,),
        )

        top_categories_rows = db.execute_query(
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
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY COALESCE(cat.nombre, 'Sin categoría')
            ORDER BY total DESC
            LIMIT 5
            """,
            (user_id,),
        )

        top_beneficiarios_rows = db.execute_query(
            """
            SELECT
                COALESCE(b.nombre, 'Sin beneficiario') AS nombre,
                SUM(m.monto) AS total
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
            WHERE c.id_persona = %s
              AND LOWER(CONVERT(tm.nombre USING utf8mb4)) = 'gasto'
              AND m.fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY COALESCE(b.nombre, 'Sin beneficiario')
            ORDER BY total DESC
            LIMIT 5
            """,
            (user_id,),
        )

        compromisos_rows = db.execute_query(
            """
            SELECT
                tp.id_transaccion,
                tp.fecha,
                COALESCE(b.nombre, 'Sin beneficiario') AS beneficiario,
                COALESCE(ca.nombre, 'Sin categoría') AS categoria,
                tm.nombre AS tipo,
                tp.monto,
                tp.repeticion
            FROM transaccion_programada tp
            LEFT JOIN beneficiario b ON tp.id_beneficiario = b.id_beneficiario
            LEFT JOIN categoria ca ON tp.id_categoria = ca.id_categoria
            LEFT JOIN tipo_movimiento tm ON tp.id_tipo = tm.id_tipo
                        WHERE tp.id_persona = %s
                            AND tp.fecha >= CURDATE()
            ORDER BY tp.fecha ASC
            LIMIT 5
            """,
                        (user_id,),
        )

        saldo_mes = current_ingresos - current_gastos
        ahorro_rate = (saldo_mes / current_ingresos * 100) if current_ingresos > 0 else 0

        delta_ingresos = current_ingresos - prev_ingresos
        delta_gastos = current_gastos - prev_gastos

        alertas = []
        if presupuesto_total > 0:
            consumo = (current_gastos / presupuesto_total) * 100
            if consumo >= 100:
                alertas.append({
                    'nivel': 'danger',
                    'titulo': 'Presupuesto excedido',
                    'detalle': f'Gastaste {consumo:.1f}% del presupuesto activo.'
                })
            elif consumo >= 80:
                alertas.append({
                    'nivel': 'warning',
                    'titulo': 'Presupuesto al límite',
                    'detalle': f'Ya consumiste {consumo:.1f}% del presupuesto activo.'
                })

        if saldo_mes < 0:
            alertas.append({
                'nivel': 'danger',
                'titulo': 'Flujo mensual negativo',
                'detalle': 'Tus gastos del mes superan tus ingresos.'
            })

        if not alertas:
            alertas.append({
                'nivel': 'success',
                'titulo': 'Buen ritmo financiero',
                'detalle': 'No se detectan alertas críticas en este momento.'
            })

        return jsonify({
            'kpis': {
                'ingresos_mes': current_ingresos,
                'gastos_mes': current_gastos,
                'saldo_mes': saldo_mes,
                'saldo_total_cuentas': saldo_total_cuentas,
                'tasa_ahorro_pct': round(ahorro_rate, 2),
                'delta_ingresos': delta_ingresos,
                'delta_gastos': delta_gastos,
                'presupuesto_total': presupuesto_total,
                'presupuestos_activos': presupuestos_activos,
                'transacciones_recientes': transacciones_recientes,
            },
            'alertas': alertas,
            'flujo_semanal': {
                'labels': [r['semana'] for r in weekly_rows],
                'ingresos': [_safe_float(r['ingresos']) for r in weekly_rows],
                'gastos': [_safe_float(r['gastos']) for r in weekly_rows],
            },
            'top_categorias': [
                {'nombre': r['nombre'], 'total': _safe_float(r['total'])}
                for r in top_categories_rows
            ],
            'top_beneficiarios': [
                {'nombre': r['nombre'], 'total': _safe_float(r['total'])}
                for r in top_beneficiarios_rows
            ],
            'proximos_compromisos': [
                {
                    'id_transaccion': r['id_transaccion'],
                    'fecha': str(r['fecha']) if r.get('fecha') else None,
                    'beneficiario': r['beneficiario'],
                    'categoria': r['categoria'],
                    'tipo': r.get('tipo'),
                    'monto': _safe_float(r['monto']),
                    'repeticion': r.get('repeticion'),
                }
                for r in compromisos_rows
            ],
        }), 200

    except Exception as e:
        logger.error('Dashboard overview error: %s', e)
        return jsonify({'message': 'Error al obtener dashboard extendido'}), 500
    finally:
        db.close()
