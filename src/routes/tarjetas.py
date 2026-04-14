"""Rutas API para modulo de tarjetas (movimientos y compras diferidas)."""

import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

bp = Blueprint('tarjetas', __name__, url_prefix='/api/tarjetas')

ESTADOS_MOV = ['compra', 'abono', 'diferido', 'pendiente', 'aprobado']


def _q2(v: Decimal) -> Decimal:
    return Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _to_decimal(v) -> Decimal:
    return Decimal(str(v or 0))


def _get_user_id() -> int:
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _add_months(d: date, months: int = 1) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, last_day))


def _calcular_diferido(valor_total: Decimal, numero_cuotas: int, tasa_mensual: Decimal, sin_interes: bool):
    if numero_cuotas <= 0:
        raise ValueError('numero_cuotas debe ser mayor que 0')
    if valor_total <= 0:
        raise ValueError('valor_total debe ser mayor que 0')

    p = _to_decimal(valor_total)
    i = Decimal('0') if sin_interes else _to_decimal(tasa_mensual)

    if i == 0:
        cuota = _q2(p / Decimal(numero_cuotas))
        total_pagado = _q2(cuota * Decimal(numero_cuotas))
        total_intereses = _q2(total_pagado - p)
    else:
        one = Decimal('1')
        factor = (one + i) ** numero_cuotas
        cuota = _q2(p * (i * factor) / (factor - one))
        total_pagado = _q2(cuota * Decimal(numero_cuotas))
        total_intereses = _q2(total_pagado - p)

    return {
        'cuota_mensual': cuota,
        'total_pagado': total_pagado,
        'total_intereses': total_intereses,
    }


def _ensure_diferidos_tables(db: DatabaseConnector):
    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS tarjeta_diferido (
            id_diferido INT AUTO_INCREMENT PRIMARY KEY,
            id_tarjeta INT NOT NULL,
            id_persona INT NOT NULL,
            id_movimiento_tarjeta INT NULL,
            descripcion VARCHAR(255) NOT NULL,
            valor_total DECIMAL(15,2) NOT NULL,
            numero_cuotas INT NOT NULL,
            tasa_mensual DECIMAL(10,6) NOT NULL DEFAULT 0,
            sin_interes TINYINT(1) NOT NULL DEFAULT 0,
            cuota_mensual DECIMAL(15,2) NOT NULL,
            total_intereses DECIMAL(15,2) NOT NULL DEFAULT 0,
            total_pagado_estimado DECIMAL(15,2) NOT NULL,
            cuotas_pagadas INT NOT NULL DEFAULT 0,
            saldo_pendiente DECIMAL(15,2) NOT NULL,
            fecha_compra DATE NOT NULL,
            fecha_proximo_pago DATE NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            numero_transaccion VARCHAR(60) NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_td_persona (id_persona),
            INDEX idx_td_tarjeta (id_tarjeta),
            INDEX idx_td_estado (estado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    db.execute_non_query(
        """
        CREATE TABLE IF NOT EXISTS tarjeta_diferido_pago (
            id_pago INT AUTO_INCREMENT PRIMARY KEY,
            id_diferido INT NOT NULL,
            numero_cuota INT NOT NULL,
            fecha_pago DATE NOT NULL,
            valor_pagado DECIMAL(15,2) NOT NULL,
            interes_pagado DECIMAL(15,2) NOT NULL DEFAULT 0,
            capital_pagado DECIMAL(15,2) NOT NULL,
            saldo_restante DECIMAL(15,2) NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_tdp_diferido (id_diferido),
            UNIQUE KEY uq_tdp_cuota (id_diferido, numero_cuota),
            CONSTRAINT fk_tdp_diferido FOREIGN KEY (id_diferido)
                REFERENCES tarjeta_diferido(id_diferido)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


@bp.route('/catalogos', methods=['GET'])
def get_catalogos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        tarjetas = db.execute_query(
            """
            SELECT tc.id_tarjeta,
                   CONCAT('****', RIGHT(tc.numero_tarjeta, 4)) AS nombre,
                   tc.numero_tarjeta,
                   tc.limite_credito,
                   tc.saldo_actual,
                   tc.fecha_corte,
                   tc.fecha_pago,
                   COALESCE(et.nombre, 'activa') AS estado
            FROM tarjeta_credito tc
            LEFT JOIN estado_tarjeta et ON tc.id_estado = et.id_estado
            WHERE tc.id_tarjeta IN (
                SELECT DISTINCT id_tarjeta FROM movimiento_tarjeta WHERE id_persona = %s
            )
            ORDER BY tc.id_tarjeta
            """,
            (user_id,),
        )

        categorias = db.execute_query(
            "SELECT id_categoria, nombre FROM categoria WHERE id_persona = %s AND estado = 1 ORDER BY nombre",
            (user_id,),
        )
        beneficiarios = db.execute_query(
            "SELECT id_beneficiario, nombre FROM beneficiario WHERE id_persona = %s AND estado = 1 ORDER BY nombre",
            (user_id,),
        )

        for t in tarjetas:
            for k in ('fecha_corte', 'fecha_pago'):
                if t.get(k):
                    t[k] = t[k].isoformat()
            for k in ('limite_credito', 'saldo_actual'):
                t[k] = float(t.get(k) or 0)

        return jsonify({
            'tarjetas': tarjetas,
            'estados': ESTADOS_MOV,
            'categorias': categorias,
            'beneficiarios': beneficiarios,
        }), 200
    except Exception as e:
        logger.error('Error cargando catalogos de tarjetas: %s', e)
        return jsonify({'message': 'Error al cargar catalogos'}), 500
    finally:
        db.close()


@bp.route('/movimientos', methods=['GET'])
def list_movimientos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()
        limit = min(int(request.args.get('limit', 500)), 1000)
        tarjeta_id = request.args.get('tarjeta_id', type=int)

        base_sql = """
            SELECT
                mt.id_movimiento_tarjeta,
                mt.id_tarjeta,
                CONCAT('****', RIGHT(tc.numero_tarjeta, 4)) AS tarjeta_nombre,
                mt.fecha,
                mt.valor,
                mt.estado,
                COALESCE(mt.nota, '') AS nota,
                mt.numero_transaccion,
                mt.id_categoria,
                COALESCE(cat.nombre, 'General') AS categoria,
                mt.id_beneficiario,
                COALESCE(b.nombre, '—') AS beneficiario,
                mt.saldo,
                mt.cuotas,
                td.id_diferido,
                td.numero_cuotas AS dif_numero_cuotas,
                td.cuotas_pagadas AS dif_cuotas_pagadas,
                td.saldo_pendiente AS dif_saldo_pendiente,
                td.estado AS dif_estado
            FROM movimiento_tarjeta mt
            INNER JOIN tarjeta_credito tc ON mt.id_tarjeta = tc.id_tarjeta
            LEFT JOIN categoria cat ON mt.id_categoria = cat.id_categoria
            LEFT JOIN beneficiario b ON mt.id_beneficiario = b.id_beneficiario
            LEFT JOIN tarjeta_diferido td ON td.id_movimiento_tarjeta = mt.id_movimiento_tarjeta AND td.id_persona = mt.id_persona
            WHERE mt.id_persona = %s
        """
        if tarjeta_id:
            rows = db.execute_query(
                base_sql + " AND mt.id_tarjeta = %s ORDER BY mt.fecha DESC, mt.id_movimiento_tarjeta DESC LIMIT %s",
                (user_id, tarjeta_id, limit),
            )
        else:
            rows = db.execute_query(
                base_sql + " ORDER BY mt.fecha DESC, mt.id_movimiento_tarjeta DESC LIMIT %s",
                (user_id, limit),
            )

        result = []
        for r in rows:
            estado = (r.get('estado') or 'compra').lower()
            val = float(r.get('valor') or 0)
            signed = -abs(val) if estado not in ('abono', 'aprobado') else abs(val)

            diferido = None
            if r.get('id_diferido'):
                cuotas_pagadas = int(r.get('dif_cuotas_pagadas') or 0)
                numero_cuotas = int(r.get('dif_numero_cuotas') or 0)
                cuota_actual = min(cuotas_pagadas + 1, numero_cuotas) if numero_cuotas else 0
                diferido = {
                    'id_diferido': int(r['id_diferido']),
                    'cuotas_pagadas': cuotas_pagadas,
                    'numero_cuotas': numero_cuotas,
                    'cuota_actual': cuota_actual,
                    'progreso_texto': f'Cuota {cuota_actual} de {numero_cuotas}' if numero_cuotas else 'Diferido',
                    'saldo_pendiente': float(r.get('dif_saldo_pendiente') or 0),
                    'estado': r.get('dif_estado') or 'activo',
                }

            result.append({
                'id': r['id_movimiento_tarjeta'],
                'id_tarjeta': r['id_tarjeta'],
                'tarjeta_nombre': r.get('tarjeta_nombre') or '****',
                'fecha': r['fecha'].isoformat() if r.get('fecha') else None,
                'valor': signed,
                'estado': estado,
                'nota': r.get('nota') or '',
                'numero_transaccion': r.get('numero_transaccion'),
                'id_categoria': r.get('id_categoria'),
                'categoria': r.get('categoria') or 'General',
                'id_beneficiario': r.get('id_beneficiario'),
                'beneficiario': r.get('beneficiario') or '—',
                'saldo': float(r.get('saldo') or 0),
                'cuotas': int(r.get('cuotas') or 1),
                'diferido': diferido,
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error('Error listando movimientos de tarjeta: %s', e)
        return jsonify({'message': 'Error al listar movimientos'}), 500
    finally:
        db.close()


@bp.route('/movimientos', methods=['POST'])
def create_movimiento():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        id_tarjeta = int(payload.get('id_tarjeta') or 0)
        if not id_tarjeta:
            return jsonify({'message': 'Tarjeta obligatoria'}), 400

        owner = db.execute_query(
            "SELECT id_tarjeta FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s LIMIT 1",
            (id_tarjeta, user_id),
        )
        if not owner:
            return jsonify({'message': 'Tarjeta no valida para este usuario'}), 400

        estado = (payload.get('estado') or 'compra').strip().lower()
        if estado not in ESTADOS_MOV:
            return jsonify({'message': f'Estado no valido. Use: {", ".join(ESTADOS_MOV)}'}), 400

        items = payload.get('items') or []
        if items:
            valor = sum(abs(float(it.get('monto', 0))) for it in items)
            if valor <= 0:
                return jsonify({'message': 'El total de ítems debe ser mayor a 0'}), 400
            nota = ' \u2022 '.join(
                f"{it.get('descripcion', 'Ítem')} (${int(abs(float(it.get('monto', 0)))):,})".replace(',', '.')
                for it in items
            )
            id_categoria = (items[0].get('id_categoria') or None)
        else:
            valor = abs(float(payload.get('valor') or 0))
            if valor <= 0:
                return jsonify({'message': 'El valor debe ser mayor a 0'}), 400
            nota = (payload.get('nota') or '').strip() or None
            id_categoria = payload.get('id_categoria') or None
        fecha = payload.get('fecha') or datetime.now().strftime('%Y-%m-%d')
        id_beneficiario = payload.get('id_beneficiario') or None
        cuotas = max(1, int(payload.get('cuotas') or 1))
        tx_ref = payload.get('numero_transaccion') or f"TC-{user_id}-{int(datetime.now().timestamp())}"

        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento_tarjeta
                (id_tarjeta, id_persona, fecha, valor, estado, nota,
                 numero_transaccion, id_categoria, id_beneficiario, cuotas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (id_tarjeta, user_id, fecha, valor, estado, nota,
             tx_ref, id_categoria, id_beneficiario, cuotas),
        )
        if not mov_id:
            return jsonify({'message': 'No se pudo crear el movimiento'}), 500

        # Guardar items desglosados si aplica
        if items:
            for idx, item in enumerate(items, start=1):
                db.execute_non_query(
                    """
                    INSERT INTO movimiento_tarjeta_item
                        (id_movimiento_tarjeta, numero_item, descripcion, id_categoria, monto)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (mov_id, idx, item.get('descripcion', 'Ítem'), 
                     item.get('id_categoria') or None, 
                     float(item.get('monto', 0))),
                )

        return jsonify({'message': 'Movimiento creado', 'id': mov_id}), 201
    except Exception as e:
        logger.error('Error creando movimiento de tarjeta: %s', e)
        return jsonify({'message': 'Error al crear movimiento'}), 500
    finally:
        db.close()


@bp.route('/movimientos/<int:movimiento_id>', methods=['PUT'])
def update_movimiento(movimiento_id):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        exists = db.execute_query(
            "SELECT id_movimiento_tarjeta FROM movimiento_tarjeta WHERE id_movimiento_tarjeta = %s AND id_persona = %s LIMIT 1",
            (movimiento_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        estado = (payload.get('estado') or '').strip().lower() or None
        if estado and estado not in ESTADOS_MOV:
            return jsonify({'message': f'Estado no valido. Use: {", ".join(ESTADOS_MOV)}'}), 400

        valor = payload.get('valor')
        valor = abs(float(valor)) if valor is not None else None
        cuotas = payload.get('cuotas')
        cuotas = max(1, int(cuotas)) if cuotas is not None else None

        db.execute_non_query(
            """
            UPDATE movimiento_tarjeta
            SET id_tarjeta      = COALESCE(%s, id_tarjeta),
                fecha           = COALESCE(%s, fecha),
                valor           = COALESCE(%s, valor),
                estado          = COALESCE(%s, estado),
                nota            = COALESCE(%s, nota),
                id_categoria    = COALESCE(%s, id_categoria),
                id_beneficiario = COALESCE(%s, id_beneficiario),
                cuotas          = COALESCE(%s, cuotas)
            WHERE id_movimiento_tarjeta = %s
            """,
            (
                payload.get('id_tarjeta') or None,
                payload.get('fecha') or None,
                valor,
                estado,
                payload.get('nota'),
                payload.get('id_categoria') or None,
                payload.get('id_beneficiario') or None,
                cuotas,
                movimiento_id,
            ),
        )
        return jsonify({'message': 'Movimiento actualizado'}), 200
    except Exception as e:
        logger.error('Error actualizando movimiento de tarjeta %s: %s', movimiento_id, e)
        return jsonify({'message': 'Error al actualizar movimiento'}), 500
    finally:
        db.close()


@bp.route('/movimientos/<int:movimiento_id>', methods=['DELETE'])
def delete_movimiento(movimiento_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = db.execute_query(
            "SELECT id_movimiento_tarjeta FROM movimiento_tarjeta WHERE id_movimiento_tarjeta = %s AND id_persona = %s LIMIT 1",
            (movimiento_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        db.execute_non_query(
            "DELETE FROM movimiento_tarjeta WHERE id_movimiento_tarjeta = %s",
            (movimiento_id,),
        )
        return jsonify({'message': 'Movimiento eliminado'}), 200
    except Exception as e:
        logger.error('Error eliminando movimiento de tarjeta %s: %s', movimiento_id, e)
        return jsonify({'message': 'Error al eliminar movimiento'}), 500
    finally:
        db.close()


@bp.route('/diferidos', methods=['GET'])
def list_diferidos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()
        id_tarjeta = request.args.get('id_tarjeta', type=int)

        base_sql = """
            SELECT
                td.id_diferido,
                td.id_tarjeta,
                td.descripcion,
                td.valor_total,
                td.numero_cuotas,
                td.tasa_mensual,
                td.sin_interes,
                td.cuota_mensual,
                td.total_intereses,
                td.total_pagado_estimado,
                td.cuotas_pagadas,
                td.saldo_pendiente,
                td.fecha_compra,
                td.fecha_proximo_pago,
                td.estado,
                td.numero_transaccion,
                CONCAT('****', RIGHT(tc.numero_tarjeta, 4)) AS tarjeta_nombre
            FROM tarjeta_diferido td
            INNER JOIN tarjeta_credito tc ON tc.id_tarjeta = td.id_tarjeta
            WHERE td.id_persona = %s
        """
        if id_tarjeta:
            rows = db.execute_query(
                base_sql + " AND td.id_tarjeta = %s ORDER BY td.fecha_compra DESC, td.id_diferido DESC",
                (user_id, id_tarjeta),
            )
        else:
            rows = db.execute_query(
                base_sql + " ORDER BY td.fecha_compra DESC, td.id_diferido DESC",
                (user_id,),
            )

        result = []
        for r in rows:
            cuotas_pagadas = int(r.get('cuotas_pagadas') or 0)
            numero_cuotas = int(r.get('numero_cuotas') or 0)
            cuota_actual = min(cuotas_pagadas + 1, numero_cuotas) if numero_cuotas else 0
            result.append({
                'id_diferido': int(r['id_diferido']),
                'id_tarjeta': int(r['id_tarjeta']),
                'tarjeta_nombre': r.get('tarjeta_nombre') or '****',
                'descripcion': r.get('descripcion') or '',
                'valor_total': float(r.get('valor_total') or 0),
                'numero_cuotas': numero_cuotas,
                'tasa_mensual': float(r.get('tasa_mensual') or 0),
                'sin_interes': bool(r.get('sin_interes') or 0),
                'cuota_mensual': float(r.get('cuota_mensual') or 0),
                'total_intereses': float(r.get('total_intereses') or 0),
                'total_pagado_estimado': float(r.get('total_pagado_estimado') or 0),
                'cuotas_pagadas': cuotas_pagadas,
                'saldo_pendiente': float(r.get('saldo_pendiente') or 0),
                'fecha_compra': r['fecha_compra'].isoformat() if r.get('fecha_compra') else None,
                'fecha_proximo_pago': r['fecha_proximo_pago'].isoformat() if r.get('fecha_proximo_pago') else None,
                'estado': r.get('estado') or 'activo',
                'numero_transaccion': r.get('numero_transaccion'),
                'cuota_actual': cuota_actual,
                'progreso_texto': f'Cuota {cuota_actual} de {numero_cuotas}' if numero_cuotas else 'Diferido',
                'progreso': (cuotas_pagadas / numero_cuotas) if numero_cuotas else 0,
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error('Error listando diferidos: %s', e)
        return jsonify({'message': 'Error al listar diferidos'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:id_diferido>/detalle', methods=['GET'])
def detalle_diferido(id_diferido):
    """Obtiene el detalle completo de un diferido incluyendo amortización y pagos realizados."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        # Obtener diferido
        rows = db.execute_query(
            """
            SELECT
                td.id_diferido,
                td.id_tarjeta,
                td.descripcion,
                td.valor_total,
                td.numero_cuotas,
                td.tasa_mensual,
                td.sin_interes,
                td.cuota_mensual,
                td.total_intereses,
                td.total_pagado_estimado,
                td.cuotas_pagadas,
                td.saldo_pendiente,
                td.fecha_compra,
                td.fecha_proximo_pago,
                td.estado,
                tc.numero_tarjeta,
                CONCAT('****', RIGHT(tc.numero_tarjeta, 4)) AS tarjeta_nombre
            FROM tarjeta_diferido td
            INNER JOIN tarjeta_credito tc ON tc.id_tarjeta = td.id_tarjeta
            WHERE td.id_diferido = %s AND td.id_persona = %s
            """,
            (id_diferido, user_id),
        )
        if not rows:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        td = rows[0]
        valor_total = _to_decimal(td['valor_total'])
        numero_cuotas = int(td['numero_cuotas'] or 0)
        tasa_mensual = _to_decimal(td['tasa_mensual'] or 0)
        sin_interes = bool(td.get('sin_interes') or 0)
        cuotas_pagadas = int(td.get('cuotas_pagadas') or 0)

        # Construir tabla de amortización
        amortizacion = []
        saldo_actual = valor_total
        tasa = Decimal('0') if sin_interes else (tasa_mensual / Decimal('100'))

        for num_cuota in range(1, numero_cuotas + 1):
            if sin_interes:
                capital = _q2(valor_total / Decimal(numero_cuotas))
                interes = Decimal('0')
            else:
                one = Decimal('1')
                factor = (one + tasa) ** numero_cuotas
                cuota_calc = _q2(valor_total * (tasa * factor) / (factor - one))
                interes = _q2(saldo_actual * tasa)
                capital = _q2(cuota_calc - interes)

            saldo_anterior = saldo_actual
            saldo_actual = _q2(saldo_actual - capital)
            if saldo_actual < 0:
                saldo_actual = Decimal('0')

            # Determinar si fue pagada
            pagada = num_cuota <= cuotas_pagadas
            fecha_pago = None
            if pagada:
                pagos = db.execute_query(
                    """
                    SELECT fecha_pago FROM tarjeta_diferido_pago
                    WHERE id_diferido = %s AND numero_cuota = %s LIMIT 1
                    """,
                    (id_diferido, num_cuota),
                )
                if pagos:
                    fecha_pago = pagos[0].get('fecha_pago')

            amortizacion.append({
                'numero_cuota': num_cuota,
                'capital': float(capital),
                'interes': float(interes),
                'cuota_total': float(capital + interes),
                'saldo_anterior': float(saldo_anterior),
                'saldo_restante': float(saldo_actual),
                'pagada': pagada,
                'fecha_pago': fecha_pago.isoformat() if fecha_pago else None,
            })

        # Obtener histórico de pagos realizados
        pagos = db.execute_query(
            """
            SELECT
                numero_cuota,
                fecha_pago,
                valor_pagado,
                capital_pagado,
                interes_pagado,
                saldo_restante
            FROM tarjeta_diferido_pago
            WHERE id_diferido = %s
            ORDER BY numero_cuota ASC
            """,
            (id_diferido,),
        )
        historico_pagos = [
            {
                'numero_cuota': int(p['numero_cuota']),
                'fecha_pago': p['fecha_pago'].isoformat() if p.get('fecha_pago') else None,
                'valor_pagado': float(p.get('valor_pagado') or 0),
                'capital_pagado': float(p.get('capital_pagado') or 0),
                'interes_pagado': float(p.get('interes_pagado') or 0),
                'saldo_restante': float(p.get('saldo_restante') or 0),
            }
            for p in pagos
        ]

        return jsonify({
            'id_diferido': int(td['id_diferido']),
            'descripcion': td.get('descripcion') or '',
            'tarjeta_nombre': td.get('tarjeta_nombre') or '****',
            'valor_total': float(valor_total),
            'numero_cuotas': numero_cuotas,
            'cuotas_pagadas': cuotas_pagadas,
            'tasa_mensual': float(tasa_mensual),
            'sin_interes': sin_interes,
            'cuota_mensual': float(td.get('cuota_mensual') or 0),
            'total_intereses': float(td.get('total_intereses') or 0),
            'total_pagado_estimado': float(td.get('total_pagado_estimado') or 0),
            'saldo_pendiente': float(td.get('saldo_pendiente') or 0),
            'fecha_compra': td['fecha_compra'].isoformat() if td.get('fecha_compra') else None,
            'fecha_proximo_pago': td['fecha_proximo_pago'].isoformat() if td.get('fecha_proximo_pago') else None,
            'estado': td.get('estado') or 'activo',
            'amortizacion': amortizacion,
            'historico_pagos': historico_pagos,
        }), 200
    except Exception as e:
        logger.error('Error obteniendo detalle diferido: %s', e)
        return jsonify({'message': 'Error al obtener detalle del diferido'}), 500
    finally:
        db.close()


@bp.route('/diferidos/summary', methods=['GET'])
def summary_diferidos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        rows = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN estado='activo' THEN saldo_pendiente ELSE 0 END), 0) AS saldo_pendiente_total,
                COALESCE(SUM(CASE
                    WHEN estado='activo'
                     AND MONTH(COALESCE(fecha_proximo_pago, CURDATE())) = MONTH(CURDATE())
                     AND YEAR(COALESCE(fecha_proximo_pago, CURDATE())) = YEAR(CURDATE())
                    THEN cuota_mensual ELSE 0 END), 0) AS cuotas_mes_actual,
                COALESCE(SUM(CASE WHEN estado='activo' THEN 1 ELSE 0 END), 0) AS diferidos_activos
            FROM tarjeta_diferido
            WHERE id_persona = %s
            """,
            (user_id,),
        )
        d = rows[0] if rows else {}

        return jsonify({
            'saldo_pendiente_total': float(d.get('saldo_pendiente_total') or 0),
            'cuotas_mes_actual': float(d.get('cuotas_mes_actual') or 0),
            'diferidos_activos': int(d.get('diferidos_activos') or 0),
        }), 200
    except Exception as e:
        logger.error('Error resumen diferidos: %s', e)
        return jsonify({'message': 'Error al obtener resumen de diferidos'}), 500
    finally:
        db.close()


@bp.route('/diferidos', methods=['POST'])
def create_diferido():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        id_tarjeta = int(payload.get('id_tarjeta') or 0)
        descripcion = (payload.get('descripcion') or '').strip()
        if not id_tarjeta:
            return jsonify({'message': 'Tarjeta obligatoria'}), 400
        if not descripcion:
            return jsonify({'message': 'Descripcion obligatoria'}), 400

        owner = db.execute_query(
            "SELECT id_tarjeta FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s LIMIT 1",
            (id_tarjeta, user_id),
        )
        if not owner:
            return jsonify({'message': 'Tarjeta no valida para este usuario'}), 400

        items = payload.get('items') or []
        if items:
            valor_total = _to_decimal(sum(float(it.get('monto', 0)) for it in items))
            if valor_total <= 0:
                return jsonify({'message': 'El total de ítems debe ser mayor a 0'}), 400
            descripcion = ' • '.join(
                f"{it.get('descripcion', 'Ítem')} (${int(abs(float(it.get('monto', 0)))):,})".replace(',', '.')
                for it in items
            )
            id_categoria = items[0].get('id_categoria') or None
        else:
            valor_total = _to_decimal(payload.get('valor_total'))
            if valor_total <= 0:
                return jsonify({'message': 'Valor total debe ser mayor a 0'}), 400
            id_categoria = payload.get('id_categoria') or None
        
        numero_cuotas = int(payload.get('numero_cuotas') or 0)
        sin_interes = bool(payload.get('sin_interes') or False)
        tasa_mensual = _to_decimal(payload.get('tasa_mensual') or 0)
        fecha_compra = payload.get('fecha_compra') or datetime.now().strftime('%Y-%m-%d')
        id_beneficiario = payload.get('id_beneficiario') or None
        if numero_cuotas <= 0:
            return jsonify({'message': 'Numero de cuotas debe ser mayor a 0'}), 400
        if not sin_interes and tasa_mensual < 0:
            return jsonify({'message': 'Tasa mensual no valida'}), 400

        calc = _calcular_diferido(valor_total, numero_cuotas, tasa_mensual, sin_interes)
        cuota_mensual = calc['cuota_mensual']
        total_intereses = calc['total_intereses']
        total_pagado = calc['total_pagado']
        fecha_proximo_pago = _add_months(datetime.strptime(fecha_compra, '%Y-%m-%d').date(), 1)

        id_diferido = db.execute_non_query(
            """
            INSERT INTO tarjeta_diferido
                (id_tarjeta, id_persona, descripcion, valor_total, numero_cuotas,
                 tasa_mensual, sin_interes, cuota_mensual, total_intereses, total_pagado_estimado,
                 cuotas_pagadas, saldo_pendiente, fecha_compra, fecha_proximo_pago, id_categoria, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, 'activo')
            """,
            (
                id_tarjeta,
                user_id,
                descripcion,
                float(_q2(valor_total)),
                numero_cuotas,
                float(_to_decimal(tasa_mensual)),
                1 if sin_interes else 0,
                float(cuota_mensual),
                float(total_intereses),
                float(total_pagado),
                float(_q2(valor_total)),
                fecha_compra,
                fecha_proximo_pago.strftime('%Y-%m-%d'),
                id_categoria,
            ),
        )
        if not id_diferido:
            return jsonify({'message': 'No se pudo crear el diferido'}), 500

        numero_tx = f"DIF-{id_diferido}-{int(datetime.now().timestamp())}"
        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento_tarjeta
                (id_tarjeta, id_persona, fecha, valor, estado, nota,
                 numero_transaccion, id_categoria, id_beneficiario, cuotas)
            VALUES (%s, %s, %s, %s, 'diferido', %s, %s, %s, %s, %s)
            """,
            (
                id_tarjeta,
                user_id,
                fecha_compra,
                float(_q2(valor_total)),
                f"{descripcion} (Diferido)",
                numero_tx,
                id_categoria,
                id_beneficiario,
                numero_cuotas,
            ),
        )

        # Guardar items desglosados si aplica
        if items:
            for idx, item in enumerate(items, start=1):
                db.execute_non_query(
                    """
                    INSERT INTO movimiento_tarjeta_item
                        (id_movimiento_tarjeta, numero_item, descripcion, id_categoria, monto)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (mov_id, idx, item.get('descripcion', 'Ítem'), 
                     item.get('id_categoria') or None, 
                     float(item.get('monto', 0))),
                )

        db.execute_non_query(
            """
            UPDATE tarjeta_diferido
            SET id_movimiento_tarjeta = %s,
                numero_transaccion = %s
            WHERE id_diferido = %s
            """,
            (mov_id, numero_tx, id_diferido),
        )

        # Registrar relación en detalle_diferido_movimiento (cuota 1 de N)
        db.execute_non_query(
            """
            INSERT INTO detalle_diferido_movimiento
                (id_diferido, id_movimiento_tarjeta, numero_cuota, tipo_cuota, estado)
            VALUES (%s, %s, 1, 'TOTAL', 'PENDIENTE')
            """,
            (id_diferido, mov_id),
        )

        return jsonify({
            'message': 'Compra diferida creada',
            'id_diferido': int(id_diferido),
            'id_movimiento': int(mov_id or 0),
            'cuota_mensual': float(cuota_mensual),
            'total_intereses': float(total_intereses),
            'total_pagado_estimado': float(total_pagado),
        }), 201
    except Exception as e:
        logger.error('Error creando diferido: %s', e)
        return jsonify({'message': 'Error al crear diferido'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:id_diferido>/pagar-cuota', methods=['POST'])
def pagar_cuota_diferido(id_diferido):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        row = db.execute_query(
            """
            SELECT *
            FROM tarjeta_diferido
            WHERE id_diferido = %s AND id_persona = %s
            LIMIT 1
            """,
            (id_diferido, user_id),
        )
        if not row:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        d = row[0]
        if (d.get('estado') or '').lower() != 'activo':
            return jsonify({'message': 'Este diferido no esta activo'}), 400

        numero_cuotas = int(d.get('numero_cuotas') or 0)
        cuotas_pagadas = int(d.get('cuotas_pagadas') or 0)
        if cuotas_pagadas >= numero_cuotas:
            return jsonify({'message': 'Todas las cuotas ya fueron pagadas'}), 400

        numero_cuota = cuotas_pagadas + 1
        pago_existente = db.execute_query(
            "SELECT id_pago FROM tarjeta_diferido_pago WHERE id_diferido = %s AND numero_cuota = %s LIMIT 1",
            (id_diferido, numero_cuota),
        )
        if pago_existente:
            return jsonify({'message': f'La cuota {numero_cuota} ya fue pagada'}), 400

        saldo = _to_decimal(d.get('saldo_pendiente'))
        tasa = _to_decimal(d.get('tasa_mensual'))
        cuota = _to_decimal(d.get('cuota_mensual'))
        sin_interes = bool(d.get('sin_interes') or 0)

        if sin_interes or tasa == 0:
            interes = Decimal('0')
            capital = min(cuota, saldo)
            valor_pagado = capital
        else:
            interes = _q2(saldo * tasa)
            capital = _q2(cuota - interes)
            if capital < Decimal('0.01'):
                capital = min(cuota, saldo)
                interes = _q2(cuota - capital)
            capital = min(capital, saldo)
            valor_pagado = _q2(capital + interes)

        nuevo_saldo = _q2(saldo - capital)
        pagado_completo = numero_cuota >= numero_cuotas or nuevo_saldo <= Decimal('0.01')
        if pagado_completo:
            nuevo_saldo = Decimal('0.00')

        fecha_pago = payload.get('fecha_pago') or datetime.now().strftime('%Y-%m-%d')
        fecha_compra_base = d.get('fecha_compra')
        if not fecha_compra_base:
            fecha_compra_base = datetime.now().date()
        if isinstance(fecha_compra_base, str):
            fecha_compra_base = datetime.strptime(fecha_compra_base, '%Y-%m-%d').date()
        fecha_movimiento_cuota = _add_months(fecha_compra_base, numero_cuota)
        if pagado_completo:
            fecha_proximo = None
        else:
            fecha_proximo = _add_months(fecha_compra_base, numero_cuota + 1).strftime('%Y-%m-%d')

        db.execute_non_query(
            """
            INSERT INTO tarjeta_diferido_pago
                (id_diferido, numero_cuota, fecha_pago, valor_pagado, interes_pagado, capital_pagado, saldo_restante)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                id_diferido,
                numero_cuota,
                fecha_pago,
                float(_q2(valor_pagado)),
                float(_q2(interes)),
                float(_q2(capital)),
                float(_q2(nuevo_saldo)),
            ),
        )

        db.execute_non_query(
            """
            UPDATE tarjeta_diferido
            SET cuotas_pagadas = %s,
                saldo_pendiente = %s,
                fecha_proximo_pago = %s,
                estado = %s
            WHERE id_diferido = %s
            """,
            (
                numero_cuota,
                float(_q2(nuevo_saldo)),
                fecha_proximo,
                'pagado' if pagado_completo else 'activo',
                id_diferido,
            ),
        )

        categoria_pago = d.get('id_categoria') or None
        numero_tx = f"DIFPAY-{id_diferido}-{numero_cuota}-{int(datetime.now().timestamp())}"

        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento_tarjeta
                (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, cuotas)
            VALUES (%s, %s, %s, %s, 'abono', %s, %s, %s, 1)
            """,
            (
                int(d['id_tarjeta']),
                user_id,
                fecha_movimiento_cuota.strftime('%Y-%m-%d'),
                float(_q2(valor_pagado)),
                f"Pago cuota {numero_cuota}/{numero_cuotas} - {d.get('descripcion') or 'Diferido'}",
                numero_tx,
                categoria_pago,
            ),
        )

        # Desglose del pago: replica proporcionalmente los ítems de la compra diferida.
        items_insertados = 0
        mov_origen = d.get('id_movimiento_tarjeta')
        if mov_origen:
            items_origen = db.execute_query(
                """
                SELECT descripcion, id_categoria, monto
                FROM movimiento_tarjeta_item
                WHERE id_movimiento_tarjeta = %s
                ORDER BY numero_item
                """,
                (int(mov_origen),),
            ) or []

            total_origen = _to_decimal(sum(float(it.get('monto') or 0) for it in items_origen))
            if items_origen and total_origen > 0:
                acumulado = Decimal('0.00')
                for idx, it in enumerate(items_origen, start=1):
                    if idx < len(items_origen):
                        monto_item = _q2(_to_decimal(valor_pagado) * (_to_decimal(it.get('monto')) / total_origen))
                        acumulado = _q2(acumulado + monto_item)
                    else:
                        # Último ítem absorbe diferencia de redondeo.
                        monto_item = _q2(_to_decimal(valor_pagado) - acumulado)

                    db.execute_non_query(
                        """
                        INSERT INTO movimiento_tarjeta_item
                            (id_movimiento_tarjeta, numero_item, descripcion, id_categoria, monto)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            int(mov_id),
                            idx,
                            it.get('descripcion') or f"Cuota {numero_cuota}/{numero_cuotas}",
                            it.get('id_categoria') or categoria_pago,
                            float(monto_item),
                        ),
                    )
                    items_insertados += 1

        if items_insertados == 0:
            db.execute_non_query(
                """
                INSERT INTO movimiento_tarjeta_item
                    (id_movimiento_tarjeta, numero_item, descripcion, id_categoria, monto)
                VALUES (%s, 1, %s, %s, %s)
                """,
                (
                    int(mov_id),
                    f"Cuota {numero_cuota}/{numero_cuotas}",
                    categoria_pago,
                    float(_q2(valor_pagado)),
                ),
            )
            items_insertados = 1

        return jsonify({
            'message': 'Pago registrado',
            'id_diferido': id_diferido,
            'id_movimiento': int(mov_id or 0),
            'numero_cuota': numero_cuota,
            'numero_cuotas': numero_cuotas,
            'valor_pagado': float(_q2(valor_pagado)),
            'interes_pagado': float(_q2(interes)),
            'capital_pagado': float(_q2(capital)),
            'saldo_restante': float(_q2(nuevo_saldo)),
            'items_desglose': items_insertados,
            'id_categoria': categoria_pago,
            'fecha_movimiento': fecha_movimiento_cuota.strftime('%Y-%m-%d'),
            'fecha_registro_pago': fecha_pago,
            'estado': 'pagado' if pagado_completo else 'activo',
        }), 200
    except Exception as e:
        logger.error('Error pagando cuota de diferido %s: %s', id_diferido, e)
        return jsonify({'message': 'Error al registrar pago'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:id_diferido>/actualizar', methods=['PUT'])
def actualizar_diferido(id_diferido):
    """Actualiza número de cuotas, saldo pendiente y/o tasa de un diferido activo."""
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        row = db.execute_query(
            "SELECT * FROM tarjeta_diferido WHERE id_diferido = %s AND id_persona = %s LIMIT 1",
            (id_diferido, user_id),
        )
        if not row:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        d = row[0]
        if (d.get('estado') or '').lower() != 'activo':
            return jsonify({'message': 'Solo se pueden modificar diferidos activos'}), 400

        numero_cuotas_actual = int(d.get('numero_cuotas') or 0)
        cuotas_pagadas = int(d.get('cuotas_pagadas') or 0)
        saldo_actual = _to_decimal(d.get('saldo_pendiente'))
        valor_total = _to_decimal(d.get('valor_total'))
        tasa_actual = _to_decimal(d.get('tasa_mensual') or 0)
        sin_interes = bool(d.get('sin_interes') or 0)

        nuevo_numero_cuotas = payload.get('numero_cuotas')
        nuevo_saldo = payload.get('saldo_pendiente')
        nueva_tasa = payload.get('tasa_mensual')

        if nuevo_numero_cuotas is not None:
            nuevo_numero_cuotas = int(nuevo_numero_cuotas)
            if nuevo_numero_cuotas <= cuotas_pagadas:
                return jsonify({'message': f'Número de cuotas debe ser mayor a {cuotas_pagadas} (cuotas pagadas)'}), 400
            if nuevo_numero_cuotas <= 0:
                return jsonify({'message': 'Número de cuotas debe ser positivo'}), 400
        else:
            nuevo_numero_cuotas = numero_cuotas_actual

        if nuevo_saldo is not None:
            nuevo_saldo = _to_decimal(nuevo_saldo)
            if nuevo_saldo < Decimal('0.01'):
                return jsonify({'message': 'Saldo debe ser mayor a 0'}), 400
        else:
            nuevo_saldo = saldo_actual

        if nueva_tasa is not None:
            nueva_tasa = _to_decimal(nueva_tasa)
            if nueva_tasa < 0:
                return jsonify({'message': 'Tasa no puede ser negativa'}), 400
            sin_interes_nuevo = nueva_tasa == 0
        else:
            nueva_tasa = tasa_actual
            sin_interes_nuevo = sin_interes

        cuota_calc = _calcular_diferido(valor_total, nuevo_numero_cuotas, nueva_tasa, sin_interes_nuevo)
        nueva_cuota_mensual = cuota_calc['cuota_mensual']

        cuotas_restantes = nuevo_numero_cuotas - cuotas_pagadas
        total_pagado_estimado = _q2(nueva_cuota_mensual * Decimal(cuotas_restantes))

        db.execute_non_query(
            """UPDATE tarjeta_diferido
               SET numero_cuotas = %s, cuota_mensual = %s, saldo_pendiente = %s, tasa_mensual = %s, 
                   sin_interes = %s, total_pagado_estimado = %s
               WHERE id_diferido = %s""",
            (
                nuevo_numero_cuotas,
                float(nueva_cuota_mensual),
                float(nuevo_saldo),
                float(nueva_tasa),
                1 if sin_interes_nuevo else 0,
                float(total_pagado_estimado),
                id_diferido,
            ),
        )

        return jsonify({
            'message': 'Diferido actualizado',
            'id_diferido': id_diferido,
            'numero_cuotas': nuevo_numero_cuotas,
            'tasa_mensual': float(nueva_tasa),
            'sin_interes': sin_interes_nuevo,
            'cuota_mensual': float(nueva_cuota_mensual),
            'saldo_pendiente': float(nuevo_saldo),
            'total_pagado_estimado': float(total_pagado_estimado),
        }), 200
    except Exception as e:
        logger.error('Error actualizando diferido %s: %s', id_diferido, e)
        return jsonify({'message': 'Error al actualizar diferido'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:id_diferido>/liquidar', methods=['POST'])
def liquidar_diferido(id_diferido):
    """Liquida anticipadamente todas las cuotas restantes de un diferido."""
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        row = db.execute_query(
            "SELECT * FROM tarjeta_diferido WHERE id_diferido = %s AND id_persona = %s LIMIT 1",
            (id_diferido, user_id),
        )
        if not row:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        d = row[0]
        if (d.get('estado') or '').lower() != 'activo':
            return jsonify({'message': 'Este diferido no esta activo'}), 400

        numero_cuotas = int(d.get('numero_cuotas') or 0)
        cuotas_pagadas = int(d.get('cuotas_pagadas') or 0)
        if cuotas_pagadas >= numero_cuotas:
            return jsonify({'message': 'Todas las cuotas ya fueron pagadas'}), 400

        saldo_pendiente = _to_decimal(d.get('saldo_pendiente'))
        if saldo_pendiente <= Decimal('0.01'):
            return jsonify({'message': 'No hay saldo pendiente'}), 400

        cuotas_restantes = numero_cuotas - cuotas_pagadas
        fecha_pago = payload.get('fecha_pago') or datetime.now().strftime('%Y-%m-%d')

        tasa = _to_decimal(d.get('tasa_mensual') or 0)
        sin_interes = bool(d.get('sin_interes') or 0)

        if sin_interes or tasa == 0:
            total_pagado = _q2(saldo_pendiente)
            interes_total = Decimal('0')
        else:
            interes_total = Decimal('0')
            saldo_temp = saldo_pendiente
            cuota_base = _to_decimal(d.get('cuota_mensual'))
            for i in range(cuotas_restantes):
                interes = _q2(saldo_temp * tasa)
                interes_total = _q2(interes_total + interes)
                capital = _q2(min(cuota_base - interes, saldo_temp))
                saldo_temp = _q2(saldo_temp - capital)
            total_pagado = _q2(saldo_pendiente + interes_total)

        for num_cuota in range(cuotas_pagadas + 1, numero_cuotas + 1):
            pago_existente = db.execute_query(
                "SELECT id_pago FROM tarjeta_diferido_pago WHERE id_diferido = %s AND numero_cuota = %s LIMIT 1",
                (id_diferido, num_cuota),
            )
            if not pago_existente:
                db.execute_non_query(
                    "INSERT INTO tarjeta_diferido_pago (id_diferido, numero_cuota, fecha_pago, valor_pagado, interes_pagado, capital_pagado, saldo_restante) VALUES (%s, %s, %s, 0, 0, 0, 0)",
                    (id_diferido, num_cuota, fecha_pago),
                )

        db.execute_non_query(
            "UPDATE tarjeta_diferido SET cuotas_pagadas = %s, saldo_pendiente = 0, fecha_proximo_pago = NULL, estado = 'pagado' WHERE id_diferido = %s",
            (numero_cuotas, id_diferido),
        )

        db.execute_non_query(
            "INSERT INTO movimiento_tarjeta (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion) VALUES (%s, %s, %s, %s, 'abono', %s, %s)",
            (
                int(d['id_tarjeta']),
                user_id,
                fecha_pago,
                float(total_pagado),
                f"Liquidacion anticipada - {d.get('descripcion') or 'Diferido'} ({cuotas_restantes} cuotas)",
                f"DIFLIQ-{id_diferido}-{int(datetime.now().timestamp())}",
            ),
        )

        return jsonify({
            'message': 'Diferido liquidado anticipadamente',
            'id_diferido': id_diferido,
            'cuotas_liquidadas': cuotas_restantes,
            'valor_pagado': float(total_pagado),
            'interes_cancelado': float(interes_total),
            'saldo_anterior': float(saldo_pendiente),
        }), 200
    except Exception as e:
        logger.error('Error liquidando diferido %s: %s', id_diferido, e)
        return jsonify({'message': 'Error al liquidar diferido'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:id_diferido>/estado', methods=['PUT'])
def update_estado_diferido(id_diferido):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()
        estado = (payload.get('estado') or '').strip().lower()
        if estado not in ('activo', 'pagado', 'cancelado'):
            return jsonify({'message': 'Estado invalido'}), 400

        row = db.execute_query(
            "SELECT id_diferido FROM tarjeta_diferido WHERE id_diferido = %s AND id_persona = %s LIMIT 1",
            (id_diferido, user_id),
        )
        if not row:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        db.execute_non_query(
            "UPDATE tarjeta_diferido SET estado = %s WHERE id_diferido = %s",
            (estado, id_diferido),
        )
        return jsonify({'message': 'Estado de diferido actualizado'}), 200
    except Exception as e:
        logger.error('Error actualizando estado diferido %s: %s', id_diferido, e)
        return jsonify({'message': 'Error al actualizar estado'}), 500
    finally:
        db.close()


@bp.route('/summary', methods=['GET'])
def get_tarjetas_summary():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        totals = db.execute_query(
            """
            SELECT
                COUNT(DISTINCT tc.id_tarjeta) AS total_tarjetas,
                COALESCE(SUM(tc.limite_credito), 0) AS limite_total,
                COALESCE(SUM(tc.saldo_actual), 0) AS saldo_actual_total,
                COALESCE(SUM(tc.limite_credito - tc.saldo_actual), 0) AS disponible_total
            FROM tarjeta_credito tc
            WHERE tc.id_tarjeta IN (
                SELECT DISTINCT id_tarjeta FROM movimiento_tarjeta WHERE id_persona = %s
            )
            """,
            (user_id,),
        )
        t = totals[0] if totals else {}

        month = db.execute_query(
            """
            SELECT
                COALESCE(SUM(CASE WHEN LOWER(COALESCE(estado,''))='compra'  THEN valor ELSE 0 END),0) AS compras_mes,
                COALESCE(SUM(CASE WHEN LOWER(COALESCE(estado,''))='abono'   THEN valor ELSE 0 END),0) AS abonos_mes,
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
            SELECT id_movimiento_tarjeta, fecha, valor, estado, nota
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


@bp.route('/movimientos/<int:movimiento_id>/items', methods=['GET'])
def get_movimiento_items(movimiento_id):
    """Obtiene los items desglosados de un movimiento."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        # Verificar que el movimiento pertenece al usuario
        mov = db.execute_query(
            "SELECT id_movimiento_tarjeta FROM movimiento_tarjeta WHERE id_movimiento_tarjeta = %s AND id_persona = %s LIMIT 1",
            (movimiento_id, user_id),
        )
        if not mov:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        items = db.execute_query(
            """
            SELECT i.id_item, i.numero_item, i.descripcion, i.id_categoria, i.monto,
                   c.nombre as categoria_nombre
            FROM movimiento_tarjeta_item i
            LEFT JOIN categoria c ON i.id_categoria = c.id_categoria
            WHERE i.id_movimiento_tarjeta = %s
            ORDER BY i.numero_item
            """,
            (movimiento_id,),
        )

        return jsonify({
            'movimiento_id': movimiento_id,
            'items': [
                {
                    'id': row['id_item'],
                    'numero': row['numero_item'],
                    'descripcion': row['descripcion'],
                    'id_categoria': row['id_categoria'],
                    'categoria': row.get('categoria_nombre') or 'Sin categoría',
                    'monto': float(row['monto']),
                }
                for row in items
            ],
            'total_items': len(items),
        }), 200
    except Exception as e:
        logger.error('Error obteniendo items del movimiento %s: %s', movimiento_id, e)
        return jsonify({'message': 'Error al obtener items'}), 500
    finally:
        db.close()


@bp.route('/diferidos/<int:diferido_id>/movimientos', methods=['GET'])
def get_diferido_movimientos(diferido_id):
    """Obtiene los movimientos/cuotas asociados a un diferido."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        _ensure_diferidos_tables(db)
        user_id = _get_user_id()

        # Verificar que el diferido pertenece al usuario
        dif = db.execute_query(
            "SELECT id_diferido FROM tarjeta_diferido WHERE id_diferido = %s AND id_persona = %s LIMIT 1",
            (diferido_id, user_id),
        )
        if not dif:
            return jsonify({'message': 'Diferido no encontrado'}), 404

        movimientos = db.execute_query(
            """
            SELECT dm.id_detalle, dm.numero_cuota, dm.tipo_cuota, dm.estado,
                   m.id_movimiento_tarjeta, m.valor, m.fecha, m.estado as mov_estado
            FROM detalle_diferido_movimiento dm
            LEFT JOIN movimiento_tarjeta m ON dm.id_movimiento_tarjeta = m.id_movimiento_tarjeta
            WHERE dm.id_diferido = %s
            ORDER BY dm.numero_cuota
            """,
            (diferido_id,),
        )

        return jsonify({
            'diferido_id': diferido_id,
            'cuotas': [
                {
                    'numero_cuota': row['numero_cuota'],
                    'tipo': row['tipo_cuota'],
                    'estado': row['estado'],
                    'movimiento_id': row.get('id_movimiento_tarjeta'),
                    'valor': float(row['valor']) if row.get('valor') else None,
                    'fecha': row['fecha'].isoformat() if row.get('fecha') else None,
                }
                for row in movimientos
            ],
            'total_cuotas': len(movimientos),
        }), 200
    except Exception as e:
        logger.error('Error obteniendo movimientos del diferido %s: %s', diferido_id, e)
        return jsonify({'message': 'Error al obtener movimientos'}), 500
    finally:
        db.close()


@bp.route('/rechazos', methods=['GET'])
def get_rechazos():
    """Obtiene el historial de movimientos rechazados del usuario."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        limit = int(request.args.get('limit', 50))

        rechazos = db.execute_query(
            """
            SELECT id_rechazo, id_tarjeta, motivo, descripcion, intento_valor,
                   intento_fecha, fecha_rechazo, intentos_consecutivos,
                   fecha_resolucion, resolucion_nota
            FROM movimiento_rechazo
            WHERE id_persona = %s
            ORDER BY fecha_rechazo DESC
            LIMIT %s
            """,
            (user_id, limit),
        )

        return jsonify({
            'rechazos': [
                {
                    'id': row['id_rechazo'],
                    'id_tarjeta': row['id_tarjeta'],
                    'motivo': row['motivo'],
                    'descripcion': row['descripcion'],
                    'valor_intento': float(row['intento_valor']),
                    'fecha_rechazo': row['fecha_rechazo'].isoformat() if row.get('fecha_rechazo') else None,
                    'intentos_consecutivos': row['intentos_consecutivos'],
                    'resuelto': row.get('fecha_resolucion') is not None,
                    'nota_resolucion': row.get('resolucion_nota'),
                }
                for row in rechazos
            ],
            'total': len(rechazos),
        }), 200
    except Exception as e:
        logger.error('Error obteniendo rechazos del usuario %s: %s', user_id, e)
        return jsonify({'message': 'Error al obtener rechazos'}), 500
    finally:
        db.close()


@bp.route('/rechazos/estadisticas', methods=['GET'])
def get_rechazos_estadisticas():
    """Analiza patrones de rechazos."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()

        # Rechazos por motivo
        por_motivo = db.execute_query(
            """
            SELECT motivo, COUNT(*) as cantidad, SUM(intento_valor) as valor_total
            FROM movimiento_rechazo
            WHERE id_persona = %s AND fecha_rechazo > DATE_SUB(NOW(), INTERVAL 90 DAY)
            GROUP BY motivo
            ORDER BY cantidad DESC
            """,
            (user_id,),
        )

        # Rechazos por tarjeta
        por_tarjeta = db.execute_query(
            """
            SELECT id_tarjeta, COUNT(*) as cantidad, MAX(fecha_rechazo) as ultimo_rechazo
            FROM movimiento_rechazo
            WHERE id_persona = %s AND fecha_rechazo > DATE_SUB(NOW(), INTERVAL 90 DAY)
            GROUP BY id_tarjeta
            ORDER BY cantidad DESC
            """,
            (user_id,),
        )

        # Rechazos sin resolver
        sin_resolver = db.execute_query(
            """
            SELECT COUNT(*) as cantidad, SUM(intento_valor) as valor_total
            FROM movimiento_rechazo
            WHERE id_persona = %s AND fecha_resolucion IS NULL
            """,
            (user_id,),
        )
        sr = sin_resolver[0] if sin_resolver else {}

        return jsonify({
            'periodo': '90 días',
            'por_motivo': [
                {
                    'motivo': row['motivo'],
                    'cantidad': row['cantidad'],
                    'valor_total': float(row['valor_total']),
                }
                for row in por_motivo
            ],
            'por_tarjeta': [
                {
                    'id_tarjeta': row['id_tarjeta'],
                    'cantidad': row['cantidad'],
                    'ultimo_rechazo': row['ultimo_rechazo'].isoformat() if row.get('ultimo_rechazo') else None,
                }
                for row in por_tarjeta
            ],
            'sin_resolver': {
                'cantidad': int(sr.get('cantidad') or 0),
                'valor_total': float(sr.get('valor_total') or 0),
            },
        }), 200
    except Exception as e:
        logger.error('Error obteniendo estadísticas de rechazos del usuario %s: %s', user_id, e)
        return jsonify({'message': 'Error al obtener estadísticas'}), 500
    finally:
        db.close()
