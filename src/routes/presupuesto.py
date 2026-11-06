"""Rutas API de presupuesto con soporte de hoja detallada anual y mensual."""

import calendar
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Union

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.business.services.libre_mes import calcular_dinero_libre_mes
from src.database.db_connector import DatabaseConnector

bp = Blueprint('presupuesto', __name__, url_prefix='/api/presupuesto')
logger = logging.getLogger(__name__)

FRECUENCIAS_VALIDAS = {
    'ninguno', 'diario', 'semanal', 'quincenal', 'mensualmente',
    'bimensual', 'trimestral', 'semestral', 'anual'
}

MONTH_NAMES_ES = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _table_exists(db: DatabaseConnector, table_name: str) -> bool:
    rows = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        """,
        (table_name,),
    )
    return bool(rows and int(rows[0].get('total') or 0) > 0)


def _column_exists(db: DatabaseConnector, table_name: str, column_name: str) -> bool:
    rows = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table_name, column_name),
    )
    return bool(rows and int(rows[0].get('total') or 0) > 0)


def _infer_tipo_categoria(cat_nombre: Optional[str], parent_id: Optional[int] = None) -> str:
    """Infiere si una categoría corresponde a Ingreso o Egreso basándose en su jerarquía o nombre."""
    if parent_id == 75:  # Categoría principal Ingresos
        return 'ingreso'
    nombre_lower = (cat_nombre or '').strip().lower()
    incomes_keywords = (
        'salario', 'sueldo', 'bonificación', 'bonificacion', 'bonificaciones',
        'freelance', 'independiente', 'inversiones', 'dividendos', 'intereses bancarios',
        'alquiler de propiedades', 'ventas', 'subsidios', 'pensión', 'pension',
        'otros ingresos', 'honorarios'
    )
    if nombre_lower == 'ingresos' or any(k in nombre_lower for k in incomes_keywords):
        return 'ingreso'
    return 'egreso'


def _fetch_monthly_income(db: DatabaseConnector, user_id: int) -> float:
    rows = db.execute_query(
        """
        SELECT COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        WHERE c.id_persona = %s
          AND LOWER(COALESCE(tm.nombre, '')) = 'ingreso'
          AND MONTH(m.fecha_creacion) = MONTH(CURDATE())
          AND YEAR(m.fecha_creacion) = YEAR(CURDATE())
        """,
        (user_id,),
    )
    return float(rows[0]['total']) if rows else 0.0


def _fetch_monthly_budget_expenses(db: DatabaseConnector, user_id: int) -> Tuple[float, float, List[dict], bool]:
    """Obtiene los gastos fijos y variables de la hoja mensual guardada."""
    _ensure_presupuesto_detalle_schema(db)
    hoy = date.today()
    start_date, end_date = _period_bounds(hoy.year, 'mensual', hoy.month)

    pres = _find_presupuesto_by_period(db, user_id, start_date, end_date)
    if not pres:
        return 0.0, 0.0, [], False

    rows = db.execute_query(
        """
        SELECT 
            COALESCE(c.nombre, pd.categoria_nombre, 'Gasto fijo') AS categoria,
            pd.monto_estimado,
            pd.monto_importe,
            pd.frecuencia,
            pd.tipo,
            pd.es_fijo
        FROM presupuesto_detalle pd
        LEFT JOIN categoria c ON c.id_categoria = pd.id_categoria
        WHERE pd.id_presupuesto = %s
          AND (pd.tipo = 'egreso' OR pd.tipo IS NULL)
        ORDER BY pd.es_fijo DESC, pd.orden ASC
        """,
        (pres['id_presupuesto'],),
    )

    detalle = []
    fijos = 0.0
    variables = 0.0
    for r in rows or []:
        val = float(r.get('monto_estimado') or 0.0)
        if val > 0:
            if r.get('es_fijo'):
                fijos += val
            else:
                variables += val
            detalle.append({
                'categoria': r['categoria'],
                'monto': round(val, 2),
                'frecuencia': r.get('frecuencia', 'Mensualmente'),
                'tipo': r.get('tipo', 'egreso'),
                'es_fijo': bool(r.get('es_fijo', False)),
            })

    return round(fijos, 2), round(variables, 2), detalle, True


def _fetch_monthly_budget_income(db: DatabaseConnector, user_id: int) -> float:
    """Obtiene los ingresos estimados de la hoja mensual guardada."""
    hoy = date.today()
    start_date, end_date = _period_bounds(hoy.year, 'mensual', hoy.month)
    if not db.conn:
        raise RuntimeError('No hay conexión para consultar ingresos presupuestados')
    with db.conn.cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT COALESCE(SUM(pd.monto_estimado), 0) AS total
            FROM presupuesto_detalle pd
            JOIN presupuesto p ON p.id_presupuesto = pd.id_presupuesto
            WHERE p.id_persona = %s AND p.fecha_inicio = %s AND p.fecha_fin = %s
              AND p.id_presupuesto = (
                  SELECT MAX(p2.id_presupuesto) FROM presupuesto p2
                  WHERE p2.id_persona = %s AND p2.fecha_inicio = %s AND p2.fecha_fin = %s
              )
              AND pd.tipo = 'ingreso'
            """,
            (user_id, start_date, end_date, user_id, start_date, end_date),
        )
        return float(cursor.fetchone()['total'])


def _fetch_monthly_fixed_budget(db: DatabaseConnector, user_id: int) -> Tuple[float, List[dict]]:
    fijos, _, detalle, _ = _fetch_monthly_budget_expenses(db, user_id)
    return fijos, [line for line in detalle if line['es_fijo']]


def _fetch_monthly_budget_lines_total(db: DatabaseConnector, user_id: int) -> float:
    total_fijos, _ = _fetch_monthly_fixed_budget(db, user_id)
    if total_fijos > 0:
        return total_fijos

    if _table_exists(db, 'presupuesto_detalle'):
        rows = db.execute_query(
            """
            SELECT COALESCE(SUM(pd.monto_estimado), 0) AS total
            FROM presupuesto_detalle pd
            INNER JOIN presupuesto p ON p.id_presupuesto = pd.id_presupuesto
            WHERE p.id_persona = %s
              AND (pd.tipo = 'egreso' OR pd.tipo IS NULL)
            """,
            (user_id,),
        )
        if rows and float(rows[0].get('total') or 0) > 0:
            return float(rows[0].get('total') or 0)
    if _table_exists(db, 'presupuesto'):
        rows = db.execute_query(
            """
            SELECT COALESCE(SUM(p.monto_total), 0) AS total
            FROM presupuesto p
            WHERE p.id_persona = %s
            """,
            (user_id,),
        )
        if rows:
            return float(rows[0].get('total') or 0)
    return 0.0
    if _table_exists(db, 'presupuesto'):
        rows = db.execute_query(
            """
            SELECT COALESCE(SUM(p.monto_total), 0) AS total
            FROM presupuesto p
            WHERE p.id_persona = %s
            """,
            (user_id,),
        )
        if rows:
            return float(rows[0].get('total') or 0)
    return 0.0


def _fetch_monthly_diferidos_total(db: DatabaseConnector, user_id: int) -> float:
    if _table_exists(db, 'tarjeta_diferido') and _column_exists(db, 'tarjeta_diferido', 'cuota_mensual'):
        rows = db.execute_query(
            """
            SELECT COALESCE(SUM(tcuota.cuota_mensual), 0) AS total
            FROM (
                SELECT cuota_mensual
                FROM tarjeta_diferido
                WHERE id_persona = %s
                  AND LOWER(COALESCE(estado, '')) IN ('activo', 'pendiente', 'vigente')
            ) AS tcuota
            """,
            (user_id,),
        )
        if rows:
            return float(rows[0].get('total') or 0)
    return 0.0


def _fetch_monthly_prestamos_total(db: DatabaseConnector, user_id: int) -> float:
    if _table_exists(db, 'prestamo_cuota') and _table_exists(db, 'prestamo_cargo'):
        today = date.today()
        start, end = _period_bounds(today.year, 'mensual', today.month)
        if not db.conn:
            raise RuntimeError('No hay conexión para consultar préstamos')
        with db.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(q.capital - q.capital_pagado +
                    q.interes - q.interes_pagado +
                    COALESCE(c.cargos_pendientes, 0)), 0) AS total
                FROM prestamo_cuota q
                JOIN prestamo p ON p.id = q.id_prestamo
                LEFT JOIN (
                    SELECT id_cuota, SUM(monto - pagado) AS cargos_pendientes
                    FROM prestamo_cargo GROUP BY id_cuota
                ) c ON c.id_cuota = q.id
                WHERE p.id_persona = %s AND q.cancelada = 0
                  AND q.fecha BETWEEN %s AND %s
                """,
                (user_id, start, end),
            )
            return float(cursor.fetchone()['total'])
    if _table_exists(db, 'prestamo') and _column_exists(db, 'prestamo', 'cuota_mensual'):
        rows = db.execute_query(
            """
            SELECT COALESCE(SUM(cuota_mensual), 0) AS total
            FROM prestamo
            WHERE id_persona = %s
              AND LOWER(COALESCE(estado, '')) IN ('activo', 'vigente', 'pendiente')
            """,
            (user_id,),
        )
        if rows:
            return float(rows[0].get('total') or 0)
    return 0.0


def _normalize_periodo(periodo: Optional[str]) -> str:
    periodo_normalizado = (periodo or 'mensual').strip().lower()
    if periodo_normalizado not in {'anual', 'mensual', 'trimestral', 'personalizado'}:
        return 'mensual'
    return periodo_normalizado


def _infer_periodo(fecha_inicio, fecha_fin) -> str:
    if not fecha_inicio or not fecha_fin:
        return 'mensual'
    dias = (fecha_fin - fecha_inicio).days
    if dias <= 35:
        return 'mensual'
    if dias <= 100:
        return 'trimestral'
    if dias <= 370:
        return 'anual'
    return 'personalizado'


def _period_bounds(year: int, periodo: str, month: Optional[int] = None) -> Tuple[date, date]:
    if periodo == 'anual':
        return date(year, 1, 1), date(year, 12, 31)
    if periodo == 'mensual':
        month = int(month or 1)
        month = max(1, min(12, month))
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)
    if periodo == 'trimestral':
        quarter = max(1, min(4, int(month or 1)))
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        last_day = calendar.monthrange(year, end_month)[1]
        return date(year, start_month, 1), date(year, end_month, last_day)
    return date(year, 1, 1), date(year, 12, 31)


def _default_budget_name(periodo: str, year: int, month: Optional[int] = None) -> str:
    if periodo == 'anual':
        return f"Presupuesto {year}"
    if periodo == 'mensual':
        month_idx = max(1, min(12, int(month or 1)))
        month_name = MONTH_NAMES_ES.get(month_idx, 'Mes')
        return f"{month_name} {year}"
    return f"Presupuesto {periodo} {year}"


def _ensure_presupuesto_detalle_schema(db: DatabaseConnector) -> None:
    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS presupuesto (
            id_presupuesto INT AUTO_INCREMENT PRIMARY KEY,
            id_persona INT NOT NULL,
            nombre VARCHAR(150) NOT NULL,
            descripcion TEXT NULL,
            monto_total DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_presupuesto_persona (id_persona),
            CONSTRAINT fk_presupuesto_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
    )
    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS presupuesto_categoria (
            id_presupuesto INT NOT NULL,
            id_categoria INT NOT NULL,
            PRIMARY KEY (id_presupuesto, id_categoria),
            CONSTRAINT fk_pc_presupuesto FOREIGN KEY (id_presupuesto) REFERENCES presupuesto(id_presupuesto) ON DELETE CASCADE,
            CONSTRAINT fk_pc_categoria FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
    )
    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS presupuesto_detalle (
            id_detalle INT NOT NULL AUTO_INCREMENT,
            id_presupuesto INT NOT NULL,
            id_categoria INT NULL,
            categoria_nombre VARCHAR(150) NULL,
            frecuencia VARCHAR(30) NOT NULL DEFAULT 'Ninguno',
            tipo VARCHAR(20) NOT NULL DEFAULT 'egreso',
            es_fijo TINYINT(1) NOT NULL DEFAULT 0,
            tolerancia_pct DECIMAL(6,2) NOT NULL DEFAULT 10.00,
            monto_importe DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            monto_estimado DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            notas TEXT NULL,
            orden INT NOT NULL DEFAULT 0,
            fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id_detalle),
            KEY idx_presupuesto_detalle_presupuesto (id_presupuesto),
            KEY idx_presupuesto_detalle_categoria (id_categoria),
            CONSTRAINT fk_presupuesto_detalle_presupuesto
                FOREIGN KEY (id_presupuesto) REFERENCES presupuesto(id_presupuesto)
                ON DELETE CASCADE,
            CONSTRAINT fk_presupuesto_detalle_categoria
                FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
                ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
    )
    cols = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'presupuesto_detalle'
          AND COLUMN_NAME = 'tolerancia_pct'
        """
    )
    if not cols or int(cols[0].get('total') or 0) == 0:
        db.execute_non_query(
            "ALTER TABLE presupuesto_detalle ADD COLUMN tolerancia_pct DECIMAL(6,2) NOT NULL DEFAULT 10.00 AFTER frecuencia"
        )
    cols_tipo = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'presupuesto_detalle'
          AND COLUMN_NAME = 'tipo'
        """
    )
    if not cols_tipo or int(cols_tipo[0].get('total') or 0) == 0:
        db.execute_non_query(
            "ALTER TABLE presupuesto_detalle ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT 'egreso' AFTER frecuencia"
        )
    cols_fijo = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'presupuesto_detalle'
          AND COLUMN_NAME = 'es_fijo'
        """
    )
    if not cols_fijo or int(cols_fijo[0].get('total') or 0) == 0:
        db.execute_non_query(
            "ALTER TABLE presupuesto_detalle ADD COLUMN es_fijo TINYINT(1) NOT NULL DEFAULT 0 AFTER tipo"
        )


def _resolve_categoria_id(db: DatabaseConnector, categoria_nombre: Optional[str]):
    if not categoria_nombre:
        return None
    rows = db.execute_query(
        "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (categoria_nombre.strip(),),
    )
    if rows:
        return rows[0]['id_categoria']
    return db.execute_non_query(
        "INSERT INTO categoria (nombre) VALUES (%s)",
        (categoria_nombre.strip(),),
    )


def _fetch_presupuesto_row(db: DatabaseConnector, user_id: int, presupuesto_id: int):
    rows = db.execute_query(
        """
        SELECT
            p.id_presupuesto,
            p.nombre,
            p.descripcion,
            p.monto_total,
            p.fecha_inicio,
            p.fecha_fin,
            GROUP_CONCAT(c.nombre ORDER BY c.nombre SEPARATOR ', ') AS categorias
        FROM presupuesto p
        LEFT JOIN presupuesto_categoria pc ON p.id_presupuesto = pc.id_presupuesto
        LEFT JOIN categoria c ON pc.id_categoria = c.id_categoria
        WHERE p.id_presupuesto = %s AND p.id_persona = %s
        GROUP BY p.id_presupuesto, p.nombre, p.descripcion, p.monto_total, p.fecha_inicio, p.fecha_fin
        LIMIT 1
        """,
        (presupuesto_id, user_id),
    )
    return rows[0] if rows else None


def _find_presupuesto_by_period(
    db: DatabaseConnector,
    user_id: int,
    start_date: date,
    end_date: date,
):
    rows = db.execute_query(
        """
        SELECT id_presupuesto
        FROM presupuesto
        WHERE id_persona = %s AND fecha_inicio = %s AND fecha_fin = %s
        ORDER BY id_presupuesto DESC
        LIMIT 1
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    if not rows:
        return None
    return _fetch_presupuesto_row(db, user_id, rows[0]['id_presupuesto'])


def _serialize_presupuesto_row(row: Optional[dict]) -> Optional[dict]:
    if not row:
        return None
    return {
        'id': row['id_presupuesto'],
        'nombre': row.get('nombre') or f"Presupuesto {row['id_presupuesto']}",
        'descripcion': row.get('descripcion'),
        'categoria': row.get('categorias') or 'General',
        'monto': float(row.get('monto_total') or 0),
        'periodo': _infer_periodo(row.get('fecha_inicio'), row.get('fecha_fin')),
        'fecha_inicio': row.get('fecha_inicio').isoformat() if row.get('fecha_inicio') else None,
        'fecha_fin': row.get('fecha_fin').isoformat() if row.get('fecha_fin') else None,
        'activo': True,
    }


def _normalize_lines(lines: Optional[List[dict]]) -> List[dict]:
    normalized = []
    for idx, line in enumerate(lines or []):
        categoria = (line.get('categoria') or line.get('categoria_nombre') or '').strip()
        frecuencia = (line.get('frecuencia') or 'Ninguno').strip()
        if frecuencia.lower() not in FRECUENCIAS_VALIDAS:
            frecuencia = 'Ninguno'

        tipo = (line.get('tipo') or '').strip().lower()
        if tipo not in ('ingreso', 'egreso'):
            tipo = _infer_tipo_categoria(categoria, line.get('parent_id'))

        importe = float(line.get('importe', line.get('monto_importe', 0)) or 0)
        estimado = float(line.get('estimado', line.get('monto_estimado', importe)) or 0)
        notas = (line.get('notas') or '').strip() or None

        if tipo == 'ingreso':
            es_fijo = False
        else:
            es_fijo_val = line.get('es_fijo')
            if es_fijo_val is not None:
                es_fijo = bool(es_fijo_val) if not isinstance(es_fijo_val, str) else es_fijo_val.lower() in ('true', '1', 'si', 'sí')
            else:
                cat_lower = categoria.lower()
                es_fijo = any(k in cat_lower for k in ('luz', 'agua', 'gas', 'triple', 'servicio', 'arriendo', 'hipoteca', 'internet', 'seguro', 'pensión', 'pension'))

        if not categoria and not importe and not estimado and not notas:
            continue

        normalized.append(
            {
                'categoria': categoria or 'Sin categoría',
                'id_categoria': line.get('id_categoria'),
                'frecuencia': frecuencia.capitalize() if frecuencia.lower() != 'mensualmente' else 'Mensualmente',
                'tipo': tipo,
                'es_fijo': es_fijo,
                'tolerancia': round(float(line.get('tolerancia', line.get('tolerancia_pct', 10)) or 10), 2),
                'importe': round(importe, 2),
                'estimado': round(estimado, 2),
                'notas': notas,
                'orden': int(line.get('orden', idx)),
            }
        )
    return normalized


def _derivar_lineas_desde_anual(lines: List[dict], divisor: int = 12) -> List[dict]:
    """Divide el presupuesto anual entre 12 para generar la vista mensual."""
    if divisor <= 0:
        raise ValueError('El divisor debe ser mayor que cero')

    derivadas = []
    for idx, line in enumerate(lines or []):
        categoria = (line.get('categoria') or line.get('categoria_nombre') or 'Sin categoría').strip() or 'Sin categoría'
        importe_anual = float(line.get('importe', line.get('monto_importe', 0)) or 0)
        estimado_anual = float(line.get('estimado', line.get('monto_estimado', importe_anual)) or 0)
        tipo = line.get('tipo') or _infer_tipo_categoria(categoria, line.get('parent_id'))
        derivadas.append(
            {
                'categoria': categoria,
                'id_categoria': line.get('id_categoria'),
                'parent_id': line.get('parent_id'),
                'frecuencia': (line.get('frecuencia') or 'Mensualmente').strip() or 'Mensualmente',
                'tipo': tipo,
                'es_fijo': bool(line.get('es_fijo', False)) if tipo != 'ingreso' else False,
                'importe': round(importe_anual / divisor, 2),
                'estimado': round(estimado_anual / divisor, 2),
                'tolerancia': round(float(line.get('tolerancia', line.get('tolerancia_pct', 10)) or 10), 2),
                'notas': line.get('notas') or '',
                'orden': int(line.get('orden', idx)),
            }
        )
    return derivadas


def _sync_budget_categories(db: DatabaseConnector, presupuesto_id: int, lines: List[dict]) -> None:
    db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
    seen = set()
    for line in lines:
        categoria = line.get('categoria')
        if not categoria or categoria.lower() == 'sin categoría':
            continue
        categoria_id = _resolve_categoria_id(db, categoria)
        if categoria_id and categoria_id not in seen:
            db.execute_non_query(
                "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                (presupuesto_id, categoria_id),
            )
            seen.add(categoria_id)


def _save_budget_lines(db: DatabaseConnector, presupuesto_id: int, lines: List[dict]) -> float:
    _ensure_presupuesto_detalle_schema(db)
    db.execute_non_query("DELETE FROM presupuesto_detalle WHERE id_presupuesto = %s", (presupuesto_id,))

    total_estimado_egresos = 0.0
    total_estimado_general = 0.0
    for idx, line in enumerate(lines):
        categoria_id = None
        categoria = line.get('categoria') or 'Sin categoría'
        if categoria.lower() != 'sin categoría':
            categoria_id = _resolve_categoria_id(db, categoria)

        tipo = line.get('tipo') or _infer_tipo_categoria(categoria)
        importe = float(line.get('importe') or 0)
        estimado = float(line.get('estimado', importe) or 0)
        total_estimado_general += estimado
        if tipo != 'ingreso':
            total_estimado_egresos += estimado

        es_fijo_val = 1 if (line.get('es_fijo') and tipo != 'ingreso') else 0

        db.execute_non_query(
            """
            INSERT INTO presupuesto_detalle (
                id_presupuesto, id_categoria, categoria_nombre, frecuencia, tipo, es_fijo,
                tolerancia_pct, monto_importe, monto_estimado, notas, orden
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                presupuesto_id,
                categoria_id,
                categoria,
                line.get('frecuencia') or 'Ninguno',
                tipo,
                es_fijo_val,
                float(line.get('tolerancia', 10) or 10),
                importe,
                estimado,
                line.get('notas'),
                int(line.get('orden', idx)),
            ),
        )

    _sync_budget_categories(db, presupuesto_id, lines)
    return round(total_estimado_egresos if total_estimado_egresos > 0 else total_estimado_general, 2)


def _save_sheet_transaction(db, user_id, existing_id, nombre, descripcion, start_date, end_date, lines):
    """Guarda cabecera, líneas y asociaciones en una sola transacción."""
    _ensure_presupuesto_detalle_schema(db)
    if not db.conn:
        raise RuntimeError('No hay conexión para guardar el presupuesto')
    has_persona = _column_exists(db, 'categoria', 'id_persona')
    db.conn.commit()
    try:
        with db.conn.cursor(dictionary=True) as cursor:
            if existing_id:
                cursor.execute(
                    "SELECT id_presupuesto FROM presupuesto WHERE id_presupuesto=%s AND id_persona=%s FOR UPDATE",
                    (existing_id, user_id),
                )
                if not cursor.fetchone():
                    raise ValueError('El presupuesto no pertenece al usuario')
                cursor.execute(
                    "UPDATE presupuesto SET nombre=%s, descripcion=%s, fecha_inicio=%s, fecha_fin=%s WHERE id_presupuesto=%s AND id_persona=%s",
                    (nombre, descripcion, start_date, end_date, existing_id, user_id),
                )
                presupuesto_id = existing_id
            else:
                cursor.execute(
                    "INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion) VALUES (%s,%s,0,%s,%s,%s,NOW())",
                    (nombre, descripcion, start_date, end_date, user_id),
                )
                presupuesto_id = cursor.lastrowid
            cursor.execute("DELETE FROM presupuesto_detalle WHERE id_presupuesto=%s", (presupuesto_id,))
            cursor.execute("DELETE FROM presupuesto_categoria WHERE id_presupuesto=%s", (presupuesto_id,))
            seen = set()
            egresos = 0.0
            general = 0.0
            for idx, line in enumerate(lines):
                categoria = line.get('categoria') or 'Sin categoría'
                categoria_id = line.get('id_categoria')
                if categoria_id:
                    sql = "SELECT id_categoria, nombre FROM categoria WHERE id_categoria=%s"
                    params = (categoria_id,)
                    if has_persona:
                        sql += " AND (id_persona=%s OR id_persona IS NULL)"
                        params += (user_id,)
                    cursor.execute(sql, params)
                    cat = cursor.fetchone()
                    if not cat or cat['nombre'].strip().lower() != categoria.strip().lower():
                        raise ValueError('Categoría inválida o no disponible para el usuario')
                    categoria_id = cat['id_categoria']
                elif categoria.lower() != 'sin categoría':
                    sql = "SELECT id_categoria FROM categoria WHERE LOWER(nombre)=LOWER(%s)"
                    params = (categoria,)
                    if has_persona:
                        sql += " AND (id_persona=%s OR id_persona IS NULL)"
                        params += (user_id,)
                    cursor.execute(sql, params)
                    matches = cursor.fetchall()
                    if len(matches) > 1:
                        raise ValueError('Hay varias categorías con ese nombre; selecciona una categoría del catálogo')
                    if matches:
                        categoria_id = matches[0]['id_categoria']
                    else:
                        if has_persona:
                            cursor.execute("INSERT INTO categoria (nombre, id_persona) VALUES (%s,%s)", (categoria, user_id))
                        else:
                            cursor.execute("INSERT INTO categoria (nombre) VALUES (%s)", (categoria,))
                        categoria_id = cursor.lastrowid
                tipo = line.get('tipo') or _infer_tipo_categoria(categoria)
                estimado = float(line.get('estimado') or 0)
                general += estimado
                if tipo != 'ingreso':
                    egresos += estimado
                cursor.execute(
                    """INSERT INTO presupuesto_detalle
                    (id_presupuesto,id_categoria,categoria_nombre,frecuencia,tipo,es_fijo,tolerancia_pct,monto_importe,monto_estimado,notas,orden)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (presupuesto_id, categoria_id, categoria, line.get('frecuencia') or 'Ninguno',
                     tipo, bool(line.get('es_fijo') and tipo != 'ingreso'),
                     line.get('tolerancia', 10), line.get('importe') or 0, estimado,
                     line.get('notas'), line.get('orden', idx)),
                )
                if categoria_id and categoria_id not in seen:
                    cursor.execute("INSERT INTO presupuesto_categoria (id_presupuesto,id_categoria) VALUES (%s,%s)",
                                   (presupuesto_id, categoria_id))
                    seen.add(categoria_id)
            cursor.execute("UPDATE presupuesto SET monto_total=%s WHERE id_presupuesto=%s AND id_persona=%s",
                           (round(egresos if egresos > 0 else general, 2), presupuesto_id, user_id))
        db.conn.commit()
        return presupuesto_id
    except Exception:
        db.conn.rollback()
        raise


def _fetch_real_totals(db: DatabaseConnector, user_id: int, start_date: date, end_date: date) -> Dict[Union[int, str], float]:
    """Obtiene el gasto real ejecutado por categoría (egresos)."""
    totals: Dict[Union[int, str], float] = {}

    movimiento_rows = db.execute_query(
        """
        SELECT c.id_categoria, COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
        WHERE cu.id_persona = %s
          AND LOWER(tm.nombre) = 'gasto'
          AND DATE(m.fecha_creacion) BETWEEN %s AND %s
          AND LOWER(COALESCE(c.nombre, '')) <> 'pagos de tarjeta de crédito'
        GROUP BY c.id_categoria, COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    for row in movimiento_rows or []:
        key = row.get('id_categoria') or (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    tarjeta_rows = db.execute_query(
        """
        SELECT c.id_categoria, COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(mt.valor), 0) AS total
        FROM movimiento_tarjeta mt
        LEFT JOIN categoria c ON c.id_categoria = mt.id_categoria
        WHERE mt.id_persona = %s
          AND DATE(mt.fecha) BETWEEN %s AND %s
          AND LOWER(COALESCE(mt.estado, '')) = 'compra'
          AND mt.valor > 0
        GROUP BY c.id_categoria, COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    for row in tarjeta_rows or []:
        key = row.get('id_categoria') or (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    return totals


def _count_abonos_por_revisar(db: DatabaseConnector, user_id: int, start_date: date, end_date: date) -> int:
    if not db.conn:
        raise RuntimeError('No hay conexión para consultar abonos')
    with db.conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) FROM movimiento_tarjeta mt
            LEFT JOIN categoria c ON c.id_categoria = mt.id_categoria
            WHERE mt.id_persona = %s AND DATE(mt.fecha) BETWEEN %s AND %s
              AND (LOWER(COALESCE(mt.estado, '')) = 'abono' OR mt.valor < 0)
              AND LOWER(COALESCE(c.nombre, '')) <> 'abono al banco'
              AND UPPER(TRIM(COALESCE(mt.nota, ''))) <> 'ABONO SUCURSAL VIRTUAL'
              AND COALESCE(mt.numero_transaccion, '') NOT LIKE 'DIFPAY-%%'
              AND COALESCE(mt.numero_transaccion, '') NOT LIKE 'DIFLIQ-%%'
            """,
            (user_id, start_date, end_date),
        )
        return int(cursor.fetchone()[0])


def _fetch_real_income_totals(db: DatabaseConnector, user_id: int, start_date: date, end_date: date) -> Dict[Union[int, str], float]:
    """Obtiene el ingreso real registrado por categoría."""
    totals: Dict[Union[int, str], float] = {}

    movimiento_rows = db.execute_query(
        """
        SELECT c.id_categoria, COALESCE(c.nombre, 'Sin categoría') AS categoria, COALESCE(SUM(m.monto), 0) AS total
        FROM movimiento m
        INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
        INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
        LEFT JOIN categoria c ON c.id_categoria = m.id_categoria
        WHERE cu.id_persona = %s
          AND LOWER(tm.nombre) = 'ingreso'
          AND DATE(m.fecha_creacion) BETWEEN %s AND %s
        GROUP BY c.id_categoria, COALESCE(c.nombre, 'Sin categoría')
        """,
        (user_id, start_date.isoformat(), end_date.isoformat()),
    )
    for row in movimiento_rows or []:
        key = row.get('id_categoria') or (row.get('categoria') or 'Sin categoría').strip().lower()
        totals[key] = totals.get(key, 0.0) + float(row.get('total') or 0)

    return totals


def _fetch_budget_lines(
    db: DatabaseConnector,
    presupuesto_id: int,
    user_id: int,
    start_date: date,
    end_date: date,
) -> List[dict]:
    _ensure_presupuesto_detalle_schema(db)
    rows = db.execute_query(
        """
        SELECT
            pd.id_detalle,
            pd.id_categoria,
            pd.categoria_nombre,
            pd.frecuencia,
            pd.tipo,
            pd.es_fijo,
            pd.tolerancia_pct,
            pd.monto_importe,
            pd.monto_estimado,
            pd.notas,
            pd.orden,
            c.nombre AS categoria_catalogo,
            c.parent_id
        FROM presupuesto_detalle pd
        LEFT JOIN categoria c ON c.id_categoria = pd.id_categoria
        WHERE pd.id_presupuesto = %s
        ORDER BY pd.orden, pd.id_detalle
        """,
        (presupuesto_id,),
    )
    reales_gastos = _fetch_real_totals(db, user_id, start_date, end_date)
    reales_ingresos = _fetch_real_income_totals(db, user_id, start_date, end_date)

    lines = []
    for row in rows or []:
        categoria = row.get('categoria_catalogo') or row.get('categoria_nombre') or 'Sin categoría'
        tipo = (row.get('tipo') or '').strip().lower()
        if tipo not in ('ingreso', 'egreso'):
            tipo = _infer_tipo_categoria(categoria, row.get('parent_id'))

        estimado = float(row.get('monto_estimado') or 0)
        if tipo == 'ingreso':
            real = round(reales_ingresos.get(row.get('id_categoria'), reales_ingresos.get(categoria.strip().lower(), 0.0)), 2)
            diferencia = round(real - estimado, 2)
            es_fijo = False
        else:
            real = round(reales_gastos.get(row.get('id_categoria'), reales_gastos.get(categoria.strip().lower(), 0.0)), 2)
            diferencia = round(estimado - real, 2)
            es_fijo = bool(row.get('es_fijo', 0))

        lines.append(
            {
                'id_detalle': row['id_detalle'],
                'id_categoria': row.get('id_categoria'),
                'categoria': categoria,
                'parent_id': row.get('parent_id'),
                'frecuencia': row.get('frecuencia') or 'Ninguno',
                'tipo': tipo,
                'es_fijo': es_fijo,
                'tolerancia': float(row.get('tolerancia_pct') or 10),
                'importe': float(row.get('monto_importe') or 0),
                'estimado': estimado,
                'real': real,
                'diferencia': diferencia,
                'notas': row.get('notas') or '',
                'orden': int(row.get('orden') or 0),
            }
        )
    return lines


def _fetch_all_catalog_categories(db: DatabaseConnector, user_id: int) -> List[dict]:
    """Obtiene todas las categorías activas del catálogo disponibles para el usuario."""
    try:
        cols = db.execute_query(
            """
            SELECT COLUMN_NAME
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'categoria'
            """
        )
        col_set = {str(c.get('COLUMN_NAME', '')).lower() for c in (cols or [])}
        has_parent = 'parent_id' in col_set
        has_persona = 'id_persona' in col_set
        has_estado = 'estado' in col_set

        if has_parent:
            if has_persona and has_estado:
                sql = "SELECT id_categoria, nombre, parent_id FROM categoria WHERE (id_persona = %s OR id_persona IS NULL) AND estado = 1 ORDER BY nombre ASC"
                return db.execute_query(sql, (user_id,)) or []
            if has_persona:
                sql = "SELECT id_categoria, nombre, parent_id FROM categoria WHERE (id_persona = %s OR id_persona IS NULL) ORDER BY nombre ASC"
                return db.execute_query(sql, (user_id,)) or []
            if has_estado:
                sql = "SELECT id_categoria, nombre, parent_id FROM categoria WHERE estado = 1 ORDER BY nombre ASC"
                return db.execute_query(sql) or []
            sql = "SELECT id_categoria, nombre, parent_id FROM categoria ORDER BY nombre ASC"
            return db.execute_query(sql) or []

        if has_persona and has_estado:
            sql = "SELECT id_categoria, nombre FROM categoria WHERE (id_persona = %s OR id_persona IS NULL) AND estado = 1 ORDER BY nombre ASC"
            return db.execute_query(sql, (user_id,)) or []
        if has_persona:
            sql = "SELECT id_categoria, nombre FROM categoria WHERE (id_persona = %s OR id_persona IS NULL) ORDER BY nombre ASC"
            return db.execute_query(sql, (user_id,)) or []
        if has_estado:
            sql = "SELECT id_categoria, nombre FROM categoria WHERE estado = 1 ORDER BY nombre ASC"
            return db.execute_query(sql) or []
        sql = "SELECT id_categoria, nombre FROM categoria ORDER BY nombre ASC"
        return db.execute_query(sql) or []
    except Exception as exc:
        logger.warning("No se pudieron cargar categorías del catálogo: %s", exc)
        return []


def _merge_catalog_categories_into_lines(
    lines: List[dict],
    catalog_categories: List[dict],
    reales_gastos: Dict[Union[int, str], float],
    reales_ingresos: Dict[Union[int, str], float],
    periodo: str,
) -> Tuple[List[dict], int, int]:
    """Combina las líneas del presupuesto con todas las categorías activas del catálogo."""
    frecuencia_defecto = 'Mensualmente' if periodo == 'mensual' else 'Anual'
    existing_by_norm = {}
    existing_by_id = {}
    for line in lines:
        cat_name = (line.get('categoria') or '').strip().lower()
        if cat_name:
            if line.get('id_categoria'):
                existing_by_id[line['id_categoria']] = line
            else:
                existing_by_norm[cat_name] = line
            line['en_catalogo'] = False
            line['presupuestada'] = float(line.get('estimado') or 0) > 0 or float(line.get('importe') or 0) > 0

    merged = list(lines)
    for cat in catalog_categories:
        cat_nombre = (cat.get('nombre') or '').strip()
        if not cat_nombre:
            continue
        norm_key = cat_nombre.lower()
        ex_line = existing_by_id.get(cat.get('id_categoria')) or existing_by_norm.pop(norm_key, None)
        if ex_line:
            ex_line['en_catalogo'] = True
            if not ex_line.get('id_categoria'):
                ex_line['id_categoria'] = cat.get('id_categoria')
            if cat.get('parent_id') and not ex_line.get('parent_id'):
                ex_line['parent_id'] = cat.get('parent_id')
            if not ex_line.get('tipo'):
                ex_line['tipo'] = _infer_tipo_categoria(cat_nombre, cat.get('parent_id'))
            if cat.get('icono') and not ex_line.get('icono'):
                ex_line['icono'] = cat.get('icono')
            if cat.get('color') and not ex_line.get('color'):
                ex_line['color'] = cat.get('color')
        else:
            tipo = _infer_tipo_categoria(cat_nombre, cat.get('parent_id'))
            if tipo == 'ingreso':
                real_val = round(reales_ingresos.get(cat.get('id_categoria'), reales_ingresos.get(norm_key, 0.0)), 2)
                sug_fijo = False
                diferencia = round(real_val - 0.0, 2)
            else:
                real_val = round(reales_gastos.get(cat.get('id_categoria'), reales_gastos.get(norm_key, 0.0)), 2)
                sug_fijo = any(k in norm_key for k in ('luz', 'agua', 'gas', 'triple', 'servicio', 'arriendo', 'hipoteca', 'internet', 'seguro', 'pensión', 'pension'))
                diferencia = round(0.0 - real_val, 2)

            nueva = {
                'id_detalle': None,
                'id_categoria': cat.get('id_categoria'),
                'categoria': cat_nombre,
                'parent_id': cat.get('parent_id'),
                'icono': cat.get('icono') or ('fa-arrow-trend-up' if tipo == 'ingreso' else 'fa-tag'),
                'color': cat.get('color') or ('#10b981' if tipo == 'ingreso' else '#6c757d'),
                'frecuencia': frecuencia_defecto,
                'tipo': tipo,
                'es_fijo': sug_fijo,
                'tolerancia': 10.0,
                'importe': 0.0,
                'estimado': 0.0,
                'real': real_val,
                'diferencia': diferencia,
                'notas': '',
                'orden': 1000 + len(merged),
                'en_catalogo': True,
                'presupuestada': False,
            }
            merged.append(nueva)
            existing_by_id[cat.get('id_categoria')] = nueva

    # Ordenar: primero los que tienen presupuesto o gasto real, luego por tipo (ingresos agrupados), luego alfabéticamente
    merged.sort(key=lambda item: (
        0 if float(item.get('estimado') or 0) > 0 or float(item.get('importe') or 0) > 0 or float(item.get('real') or 0) > 0 else 1,
        0 if item.get('tipo') == 'ingreso' else 1,
        (item.get('categoria') or '').lower()
    ))

    catalog_count = len(catalog_categories)
    presupuestadas_count = sum(1 for l in merged if float(l.get('estimado') or 0) > 0 or float(l.get('importe') or 0) > 0)
    return merged, catalog_count, presupuestadas_count


def _sheet_response(
    db: DatabaseConnector,
    user_id: int,
    row: Optional[dict],
    year: int,
    periodo: str,
    month: Optional[int] = None,
    derived_from: Optional[dict] = None,
    incluir_todas_categorias: bool = True,
) -> dict:
    start_date, end_date = _period_bounds(year, periodo, month)
    serialized = _serialize_presupuesto_row(row)
    reales_gastos = _fetch_real_totals(db, user_id, start_date, end_date)
    reales_ingresos = _fetch_real_income_totals(db, user_id, start_date, end_date)

    if row:
        lines = _fetch_budget_lines(db, row['id_presupuesto'], user_id, start_date, end_date)
    elif derived_from:
        annual_lines = _fetch_budget_lines(db, derived_from['id_presupuesto'], user_id, date(year, 1, 1), date(year, 12, 31))
        lines = []
        for idx, line in enumerate(_derivar_lineas_desde_anual(annual_lines, divisor=12)):
            categoria = line['categoria']
            tipo = line.get('tipo', 'egreso')
            estimado = float(line['estimado'] or 0)
            importe = float(line['importe'] or 0)
            if tipo == 'ingreso':
                real = round(reales_ingresos.get(line.get('id_categoria'), reales_ingresos.get(categoria.strip().lower(), 0.0)), 2)
                diferencia = round(real - estimado, 2)
            else:
                real = round(reales_gastos.get(line.get('id_categoria'), reales_gastos.get(categoria.strip().lower(), 0.0)), 2)
                diferencia = round(estimado - real, 2)
            lines.append(
                {
                    'id_detalle': None,
                    'id_categoria': line.get('id_categoria'),
                    'categoria': categoria,
                    'parent_id': line.get('parent_id'),
                    'frecuencia': line.get('frecuencia') or 'Mensualmente',
                    'tipo': tipo,
                    'es_fijo': bool(line.get('es_fijo', False)),
                    'importe': importe,
                    'estimado': estimado,
                    'real': real,
                    'diferencia': diferencia,
                    'notas': line.get('notas') or '',
                    'orden': idx,
                }
            )
    else:
        lines = []

    catalog_count = 0
    presupuestadas_count = 0

    if incluir_todas_categorias:
        catalog_cats = _fetch_all_catalog_categories(db, user_id)
        lines, catalog_count, presupuestadas_count = _merge_catalog_categories_into_lines(
            lines, catalog_cats, reales_gastos, reales_ingresos, periodo
        )
    else:
        presupuestadas_count = len([l for l in lines if float(l.get('estimado') or 0) > 0 or float(l.get('importe') or 0) > 0])
        catalog_count = presupuestadas_count

    ingresos_lineas = [l for l in lines if l.get('tipo') == 'ingreso']
    egresos_lineas = [l for l in lines if l.get('tipo') != 'ingreso']

    ingresos_estimado = round(sum(float(line.get('estimado') or 0) for line in ingresos_lineas), 2)
    ingresos_real = round(sum(float(line.get('real') or 0) for line in ingresos_lineas), 2)
    ingresos_diferencia = round(sum(float(line.get('diferencia') or 0) for line in ingresos_lineas), 2)

    egresos_estimado = round(sum(float(line.get('estimado') or 0) for line in egresos_lineas), 2)
    fijos_total = round(sum(float(line.get('estimado') or 0) for line in egresos_lineas if line.get('es_fijo')), 2)
    variables_total = round(sum(float(line.get('estimado') or 0) for line in egresos_lineas if not line.get('es_fijo')), 2)
    egresos_real = round(sum(float(line.get('real') or 0) for line in egresos_lineas), 2)
    egresos_diferencia = round(sum(float(line.get('diferencia') or 0) for line in egresos_lineas), 2)

    flujo_neto_estimado = round(ingresos_estimado - egresos_estimado, 2)
    flujo_neto_real = round(ingresos_real - egresos_real, 2)

    resumen = {
        'ingresos_estimado': ingresos_estimado,
        'ingresos_real': ingresos_real,
        'ingresos_diferencia': ingresos_diferencia,
        'egresos_estimado': egresos_estimado,
        'fijos_total': fijos_total,
        'variables_total': variables_total,
        'egresos_real': egresos_real,
        'egresos_diferencia': egresos_diferencia,
        'flujo_neto_estimado': flujo_neto_estimado,
        'flujo_neto_real': flujo_neto_real,
        'importe_total': round(sum(float(line.get('importe') or 0) for line in egresos_lineas), 2),
        'estimado_total': egresos_estimado,
        'real_total': egresos_real,
        'diferencia_total': egresos_diferencia,
    }

    return {
        'presupuesto': serialized,
        'periodo': periodo,
        'year': year,
        'month': month,
        'fecha_inicio': start_date.isoformat(),
        'fecha_fin': end_date.isoformat(),
        'nombre_sugerido': serialized['nombre'] if serialized else _default_budget_name(periodo, year, month),
        'lineas': lines,
        'resumen': resumen,
        'derivado_desde_anual': _serialize_presupuesto_row(derived_from) if derived_from else None,
        'catalogo_total': catalog_count,
        'categorias_presupuestadas': presupuestadas_count,
        'abonos_por_revisar': _count_abonos_por_revisar(db, user_id, start_date, end_date),
    }


@bp.route('/libre-mes', methods=['GET'])
def libre_mes_disponible():
    """Retorna el dinero libre del mes, basado en ingresos, gastos fijos, diferidos y préstamos."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        diferidos = float(request.args.get('diferidos_mensuales', _fetch_monthly_diferidos_total(db, user_id)) or 0)
        prestamos = float(request.args.get('prestamos_mensuales', _fetch_monthly_prestamos_total(db, user_id)) or 0)
        deudas_mes = round(diferidos + prestamos, 2)

        gastos_fijos_calc, gastos_variables_calc, gastos_detalle, presupuesto_guardado = _fetch_monthly_budget_expenses(db, user_id)
        if request.args.get('ingresos_mensuales') is not None:
            ingresos = float(request.args.get('ingresos_mensuales') or 0)
        else:
            ingresos = _fetch_monthly_budget_income(db, user_id)
        if request.args.get('gastos_fijos_mensuales') is not None:
            gastos_fijos = float(request.args.get('gastos_fijos_mensuales') or 0)
        else:
            gastos_fijos = float(gastos_fijos_calc or 0)
        gastos_variables = float(request.args.get('gastos_variables_mensuales', gastos_variables_calc) or 0)

        otros = float(request.args.get('otros_compromisos', 0) or 0)

        resultado = calcular_dinero_libre_mes(
            ingresos_mensuales=ingresos,
            gastos_fijos_mensuales=gastos_fijos,
            gastos_variables_mensuales=gastos_variables,
            diferidos_mensuales=diferidos,
            prestamos_mensuales=prestamos,
            otros_compromisos=otros,
        )

        resultado['deudas_mensuales'] = deudas_mes
        resultado['gastos_fijos_detalle'] = [line for line in gastos_detalle if line['es_fijo']]
        resultado['gastos_presupuesto_detalle'] = gastos_detalle
        resultado['presupuesto_mensual_guardado'] = presupuesto_guardado
        resultado['formula_detallada'] = f"${ingresos:,.2f} (Ingresos) - ${gastos_fijos:,.2f} (Gastos fijos) - ${gastos_variables:,.2f} (Gastos variables) - ${deudas_mes:,.2f} (Deudas: Diferidos + Préstamos)"
        if otros > 0:
            resultado['formula_detallada'] += f" - ${otros:,.2f} (Otros)"
        resultado['formula_detallada'] += f" = ${resultado['dinero_libre_mes']:,.2f}"

        return jsonify(resultado), 200
    except Exception as e:
        logger.error('Error calculando dinero libre del mes: %s', e)
        return jsonify({'message': 'Error al calcular el dinero libre del mes'}), 500
    finally:
        db.close()


@bp.route('', methods=['GET'])
def list_presupuestos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            """
            SELECT
                p.id_presupuesto,
                p.nombre,
                p.descripcion,
                p.monto_total,
                p.fecha_inicio,
                p.fecha_fin,
                GROUP_CONCAT(c.nombre ORDER BY c.nombre SEPARATOR ', ') AS categorias
            FROM presupuesto p
            LEFT JOIN presupuesto_categoria pc ON p.id_presupuesto = pc.id_presupuesto
            LEFT JOIN categoria c ON pc.id_categoria = c.id_categoria
            WHERE p.id_persona = %s
            GROUP BY p.id_presupuesto, p.nombre, p.descripcion, p.monto_total, p.fecha_inicio, p.fecha_fin
            ORDER BY p.fecha_inicio DESC, p.id_presupuesto DESC
            """,
            (user_id,),
        )
        return jsonify([_serialize_presupuesto_row(row) for row in rows]), 200
    except Exception as e:
        logger.error("Error listando presupuestos: %s", e)
        return jsonify({'message': 'Error al listar presupuestos'}), 500
    finally:
        db.close()


@bp.route('/hoja', methods=['GET'])
def get_presupuesto_sheet():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        year = int(request.args.get('year', date.today().year))
        periodo = _normalize_periodo(request.args.get('periodo', 'anual'))
        month = request.args.get('month', type=int)
        incluir_todas = request.args.get('todas', 'true').lower() in ('true', '1')

        start_date, end_date = _period_bounds(year, periodo, month)
        row = _find_presupuesto_by_period(db, user_id, start_date, end_date)
        derived_from = None
        if not row and periodo == 'mensual':
            derived_from = _find_presupuesto_by_period(db, user_id, date(year, 1, 1), date(year, 12, 31))
        return jsonify(_sheet_response(db, user_id, row, year, periodo, month, derived_from, incluir_todas_categorias=incluir_todas)), 200
    except Exception as e:
        logger.error("Error obteniendo hoja de presupuesto: %s", e)
        return jsonify({'message': 'Error al obtener hoja de presupuesto'}), 500
    finally:
        db.close()


@bp.route('/hoja', methods=['POST'])
def save_presupuesto_sheet():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        periodo = _normalize_periodo(payload.get('periodo', 'anual'))
        year = int(payload.get('year') or date.today().year)
        month = payload.get('month')
        month = int(month) if month not in (None, '') else None
        start_date, end_date = _period_bounds(year, periodo, month)
        normalized_lines = _normalize_lines(payload.get('lineas'))

        guardar_todas = bool(payload.get('guardar_todas', False))
        if not guardar_todas:
            lineas_a_guardar = [
                line for line in normalized_lines
                if float(line.get('estimado') or 0) > 0
                or float(line.get('importe') or 0) > 0
                or (line.get('notas') and line.get('notas').strip())
            ]
            if not lineas_a_guardar and normalized_lines:
                # Si todas están en cero, conservar al menos las que tengan notas o la primera para no dejarlo huérfano
                lineas_a_guardar = normalized_lines
        else:
            lineas_a_guardar = normalized_lines

        presupuesto_id = payload.get('presupuesto_id')
        existing = None
        if presupuesto_id:
            existing = _fetch_presupuesto_row(db, user_id, int(presupuesto_id))
            if not existing:
                return jsonify({'message': 'Presupuesto no encontrado'}), 404
        if not existing:
            existing = _find_presupuesto_by_period(db, user_id, start_date, end_date)

        nombre = (payload.get('nombre') or '').strip() or _default_budget_name(periodo, year, month)
        descripcion = (payload.get('descripcion') or '').strip() or None
        presupuesto_id = _save_sheet_transaction(
            db, user_id, existing['id_presupuesto'] if existing else None,
            nombre, descripcion, start_date, end_date, lineas_a_guardar,
        )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_sheet_response(db, user_id, row, year, periodo, month)), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error("Error guardando hoja de presupuesto: %s", e)
        return jsonify({'message': 'Error al guardar hoja de presupuesto'}), 500
    finally:
        db.close()


@bp.route('/hoja/derivar', methods=['POST'])
def derive_monthly_sheet():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        year = int(payload.get('year') or date.today().year)
        month = int(payload.get('month') or date.today().month)
        overwrite = bool(payload.get('overwrite', False))

        annual_row = _find_presupuesto_by_period(db, user_id, date(year, 1, 1), date(year, 12, 31))
        if not annual_row:
            return jsonify({'message': 'No existe un presupuesto anual para ese año'}), 404

        annual_lines = _fetch_budget_lines(db, annual_row['id_presupuesto'], user_id, date(year, 1, 1), date(year, 12, 31))
        if not annual_lines:
            return jsonify({'message': 'El presupuesto anual no tiene líneas para derivar'}), 400

        start_date, end_date = _period_bounds(year, 'mensual', month)
        monthly_row = _find_presupuesto_by_period(db, user_id, start_date, end_date)
        if monthly_row and not overwrite:
            return jsonify({'message': 'El presupuesto mensual ya existe para ese periodo'}), 409

        derived_lines = _derivar_lineas_desde_anual(annual_lines, divisor=12)

        nombre = payload.get('nombre') or _default_budget_name('mensual', year, month)
        descripcion = payload.get('descripcion') or f"Derivado de {_serialize_presupuesto_row(annual_row)['nombre']}"

        presupuesto_id = _save_sheet_transaction(
            db, user_id, monthly_row['id_presupuesto'] if monthly_row else None,
            nombre, descripcion, start_date, end_date, derived_lines,
        )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_sheet_response(db, user_id, row, year, 'mensual', month)), 200
    except Exception as e:
        logger.error("Error derivando presupuesto mensual: %s", e)
        return jsonify({'message': 'Error al derivar presupuesto mensual'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['GET'])
def get_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        row = _fetch_presupuesto_row(db, _get_user_id(), presupuesto_id)
        if not row:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error obteniendo presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al obtener presupuesto'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_presupuesto():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        nombre = payload.get('nombre') or f"Presupuesto {date.today().isoformat()}"
        descripcion = payload.get('descripcion')
        monto = float(payload.get('monto', payload.get('monto_total', 0)) or 0)
        periodo = _normalize_periodo(payload.get('periodo'))

        fecha_inicio = payload.get('fecha_inicio') or date.today().isoformat()
        if payload.get('fecha_fin'):
            fecha_fin = payload['fecha_fin']
        elif periodo == 'trimestral':
            fecha_fin = (date.today() + timedelta(days=90)).isoformat()
        elif periodo == 'anual':
            fecha_fin = (date.today() + timedelta(days=365)).isoformat()
        else:
            fecha_fin = (date.today() + timedelta(days=30)).isoformat()

        presupuesto_id = db.execute_non_query(
            """
            INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (nombre, descripcion, monto, fecha_inicio, fecha_fin, user_id),
        )
        if not presupuesto_id:
            return jsonify({'message': 'No se pudo crear el presupuesto'}), 500

        lineas = _normalize_lines(payload.get('lineas'))
        if lineas:
            total_guardado = _save_budget_lines(db, presupuesto_id, lineas)
            db.execute_non_query(
                "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
                (total_guardado, presupuesto_id, user_id),
            )
        else:
            categoria_nombre = payload.get('categoria')
            categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
            if categoria_id:
                db.execute_non_query(
                    "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                    (presupuesto_id, categoria_id),
                )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error creando presupuesto: %s", e)
        return jsonify({'message': 'Error al crear presupuesto'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['PUT'])
def update_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        existing = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        if not existing:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

        db.execute_non_query(
            """
            UPDATE presupuesto
            SET nombre = COALESCE(%s, nombre),
                descripcion = COALESCE(%s, descripcion),
                monto_total = COALESCE(%s, monto_total),
                fecha_inicio = COALESCE(%s, fecha_inicio),
                fecha_fin = COALESCE(%s, fecha_fin)
            WHERE id_presupuesto = %s AND id_persona = %s
            """,
            (
                payload.get('nombre'),
                payload.get('descripcion'),
                payload.get('monto'),
                payload.get('fecha_inicio'),
                payload.get('fecha_fin'),
                presupuesto_id,
                user_id,
            ),
        )

        lineas = _normalize_lines(payload.get('lineas'))
        if lineas:
            total_guardado = _save_budget_lines(db, presupuesto_id, lineas)
            db.execute_non_query(
                "UPDATE presupuesto SET monto_total = %s WHERE id_presupuesto = %s AND id_persona = %s",
                (total_guardado, presupuesto_id, user_id),
            )
        else:
            categoria_nombre = payload.get('categoria')
            categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
            if categoria_id:
                db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
                db.execute_non_query(
                    "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                    (presupuesto_id, categoria_id),
                )

        row = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        return jsonify(_serialize_presupuesto_row(row)), 200
    except Exception as e:
        logger.error("Error actualizando presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al actualizar presupuesto'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['DELETE'])
def delete_presupuesto(presupuesto_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = _fetch_presupuesto_row(db, user_id, presupuesto_id)
        if not exists:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

        _ensure_presupuesto_detalle_schema(db)
        db.execute_non_query("DELETE FROM presupuesto_detalle WHERE id_presupuesto = %s", (presupuesto_id,))
        db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
        db.execute_non_query(
            "DELETE FROM presupuesto WHERE id_presupuesto = %s AND id_persona = %s",
            (presupuesto_id, user_id),
        )
        return jsonify({'message': 'Presupuesto eliminado'}), 200
    except Exception as e:
        logger.error("Error eliminando presupuesto %s: %s", presupuesto_id, e)
        return jsonify({'message': 'Error al eliminar presupuesto'}), 500
    finally:
        db.close()
