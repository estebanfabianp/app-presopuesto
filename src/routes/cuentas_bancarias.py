"""Rutas API para movimientos de cuentas bancarias."""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('cuentas_bancarias', __name__, url_prefix='/api/cuentas-bancarias')
logger = logging.getLogger(__name__)

ESTADOS_CONCILIACION = [
    'sin conciliar',
    'conciliado',
    'duplicado',
    'seguimiento',
    'anulado',
]


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _resolve_tipo_id(db: DatabaseConnector, nombre_tipo: str):
    nombre_tipo = (nombre_tipo or 'gasto').strip().lower()
    rows = db.execute_query(
        "SELECT id_tipo FROM tipo_movimiento WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (nombre_tipo,),
    )
    if rows:
        return rows[0]['id_tipo']
    return db.execute_non_query("INSERT INTO tipo_movimiento (nombre) VALUES (%s)", (nombre_tipo,))


def _ensure_estados_conciliacion(db: DatabaseConnector):
    for nombre in ESTADOS_CONCILIACION:
        found = db.execute_query(
            "SELECT id_estado FROM estado_movimiento WHERE LOWER(nombre)=LOWER(%s) LIMIT 1",
            (nombre,),
        )
        if not found:
            db.execute_non_query("INSERT INTO estado_movimiento (nombre) VALUES (%s)", (nombre,))


def _resolve_estado_id(db: DatabaseConnector, estado_nombre: str = None, id_estado=None):
    if id_estado:
        return int(id_estado)
    if not estado_nombre:
        estado_nombre = 'sin conciliar'
    rows = db.execute_query(
        "SELECT id_estado FROM estado_movimiento WHERE LOWER(nombre)=LOWER(%s) LIMIT 1",
        (estado_nombre,),
    )
    if rows:
        return rows[0]['id_estado']
    return db.execute_non_query("INSERT INTO estado_movimiento (nombre) VALUES (%s)", (estado_nombre,))


_detalle_table_ensured = False


def _ensure_detalle_table(db: DatabaseConnector):
    """Crea la tabla movimiento_detalle si no existe (se ejecuta una sola vez por proceso)."""
    global _detalle_table_ensured
    if _detalle_table_ensured:
        return
    try:
        db.execute_non_query(
            """
            CREATE TABLE IF NOT EXISTS movimiento_detalle (
              id_detalle    INT AUTO_INCREMENT PRIMARY KEY,
              id_movimiento INT NOT NULL,
              id_categoria  INT DEFAULT NULL,
              monto         DECIMAL(15,2) NOT NULL DEFAULT 0.00,
              descripcion   VARCHAR(200) DEFAULT NULL,
              CONSTRAINT fk_det_mov
                FOREIGN KEY (id_movimiento) REFERENCES movimiento (id_movimiento)
                ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
            """
        )
        _detalle_table_ensured = True
    except Exception as exc:
        logger.warning("No se pudo crear movimiento_detalle: %s", exc)


def _save_detalles(db: DatabaseConnector, mov_id: int, detalles_raw: list) -> float:
    """Reemplaza los detalles de un movimiento. Retorna la suma total de montos."""
    db.execute_non_query(
        "DELETE FROM movimiento_detalle WHERE id_movimiento = %s",
        (mov_id,),
    )
    total = 0.0
    for d in detalles_raw:
        m = abs(float(d.get('monto') or 0))
        if m <= 0:
            continue
        total += m
        cat_id = int(d['id_categoria']) if d.get('id_categoria') else None
        desc = (d.get('descripcion') or '').strip() or None
        db.execute_non_query(
            """
            INSERT INTO movimiento_detalle (id_movimiento, id_categoria, monto, descripcion)
            VALUES (%s, %s, %s, %s)
            """,
            (mov_id, cat_id, m, desc),
        )
    return total


@bp.route('/catalogos', methods=['GET'])
def get_catalogos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        _ensure_estados_conciliacion(db)

        cuentas = db.execute_query(
            """SELECT 
                c.id_cuenta, 
                c.nombre, 
                c.tipo, 
                c.moneda,
                CAST(
                    COALESCE(c.saldo_inicial, 0) + 
                    COALESCE(SUM(
                        CASE
                            WHEN LOWER(TRIM(tm.nombre)) = 'ingreso' THEN COALESCE(m.monto, 0)
                            ELSE 0
                        END
                    ), 0) - 
                    COALESCE(SUM(
                        CASE
                            WHEN LOWER(TRIM(tm.nombre)) = 'gasto' THEN COALESCE(m.monto, 0)
                            ELSE 0
                        END
                    ), 0)
                AS DECIMAL(15,2)) AS saldo_actual
               FROM cuenta c
               LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
               LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
               WHERE c.id_persona = %s
                                 AND COALESCE(LOWER(c.estado), 'activo') IN ('activo', 'activa')
               GROUP BY c.id_cuenta, c.nombre, c.tipo, c.moneda, c.saldo_inicial
               ORDER BY c.nombre""",
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
        estados = db.execute_query(
            "SELECT id_estado, nombre FROM estado_movimiento ORDER BY nombre"
        )
        productos = db.execute_query(
            """SELECT id_producto, tipo_producto, nombre
               FROM v_producto_unificado
               WHERE id_persona = %s
               ORDER BY tipo_producto, nombre""",
            (user_id,),
        )

        return jsonify({
            'cuentas': cuentas,
            'categorias': categorias,
            'beneficiarios': beneficiarios,
            'estados': estados,
            'productos': productos,
        }), 200
    except Exception as e:
        logger.error("Error cargando catálogos de cuentas bancarias: %s", e)
        return jsonify({'message': 'Error al cargar catálogos'}), 500
    finally:
        db.close()


@bp.route('/movimientos', methods=['GET'])
def list_movimientos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        limit = min(int(request.args.get('limit', 300)), 1000)
        cuenta_id = request.args.get('cuenta_id', type=int)

        if cuenta_id:
            rows = db.execute_query(
                """
                SELECT
                    m.id_movimiento,
                    m.id_cuenta,
                    c.nombre AS cuenta_nombre,
                    DATE(m.fecha_creacion) AS fecha,
                    COALESCE(NULLIF(m.nota,''), COALESCE(NULLIF(m.codigo,''), 'Sin descripción')) AS descripcion,
                    COALESCE(m.nota, '') AS observacion,
                    COALESCE(cat.nombre, 'General') AS categoria,
                    m.id_categoria,
                    COALESCE(b.nombre, '—') AS beneficiario,
                    m.id_beneficiario,
                    COALESCE(tm.nombre, 'gasto') AS tipo,
                    COALESCE(em.nombre, 'sin conciliar') AS estado,
                    m.id_estado,
                    m.id_producto,
                    m.numero_transaccion,
                    m.monto
                FROM movimiento m
                INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
                LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
                LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
                LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
                LEFT JOIN estado_movimiento em ON m.id_estado = em.id_estado
                WHERE c.id_persona = %s AND m.id_cuenta = %s
                ORDER BY m.fecha_creacion DESC, m.id_movimiento DESC
                LIMIT %s
                """,
                (user_id, cuenta_id, limit),
            )
        else:
            rows = db.execute_query(
                """
                SELECT
                    m.id_movimiento,
                    m.id_cuenta,
                    c.nombre AS cuenta_nombre,
                    DATE(m.fecha_creacion) AS fecha,
                    COALESCE(NULLIF(m.nota,''), COALESCE(NULLIF(m.codigo,''), 'Sin descripción')) AS descripcion,
                    COALESCE(m.nota, '') AS observacion,
                    COALESCE(cat.nombre, 'General') AS categoria,
                    m.id_categoria,
                    COALESCE(b.nombre, '—') AS beneficiario,
                    m.id_beneficiario,
                    COALESCE(tm.nombre, 'gasto') AS tipo,
                    COALESCE(em.nombre, 'sin conciliar') AS estado,
                    m.id_estado,
                    m.id_producto,
                    m.numero_transaccion,
                    m.monto
                FROM movimiento m
                INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
                LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
                LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
                LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
                LEFT JOIN estado_movimiento em ON m.id_estado = em.id_estado
                WHERE c.id_persona = %s
                ORDER BY m.fecha_creacion DESC, m.id_movimiento DESC
                LIMIT %s
                """,
                (user_id, limit),
            )

        result = []
        for r in rows:
            monto = float(r.get('monto') or 0)
            tipo = (r.get('tipo') or 'gasto').lower()
            signed = monto if tipo == 'ingreso' else -abs(monto)
            result.append({
                'id': r['id_movimiento'],
                'id_cuenta': r['id_cuenta'],
                'cuenta_nombre': r.get('cuenta_nombre'),
                'fecha': r['fecha'].isoformat() if r.get('fecha') else None,
                'descripcion': r.get('descripcion') or 'Sin descripción',
                'observacion': r.get('observacion') or '',
                'categoria': r.get('categoria') or 'General',
                'id_categoria': r.get('id_categoria'),
                'beneficiario': r.get('beneficiario') or '—',
                'id_beneficiario': r.get('id_beneficiario'),
                'tipo': tipo,
                'estado': r.get('estado') or 'sin conciliar',
                'id_estado': r.get('id_estado'),
                'id_producto': r.get('id_producto'),
                'numero_transaccion': r.get('numero_transaccion'),
                'monto': signed,
                'detalles': [],
            })

        # Adjuntar detalles de categorías múltiples en una sola consulta
        if result:
            _ensure_detalle_table(db)
            ids = tuple(row_d['id'] for row_d in result)
            ph = ','.join(['%s'] * len(ids))
            det_query = (
                "SELECT md.id_movimiento, md.id_detalle, md.id_categoria,"
                " COALESCE(cat.nombre, 'General') AS categoria_nombre,"
                " md.monto, COALESCE(md.descripcion, '') AS descripcion"
                " FROM movimiento_detalle md"
                " LEFT JOIN categoria cat ON md.id_categoria = cat.id_categoria"
                " WHERE md.id_movimiento IN (" + ph + ")"  # nosec B608 — ph son sólo marcadores %s
                " ORDER BY md.id_movimiento, md.id_detalle"
            )
            det_rows = db.execute_query(det_query, ids) or []
            det_map: dict = {}
            for det in det_rows:
                mid = det['id_movimiento']
                det_map.setdefault(mid, []).append({
                    'id_detalle': det['id_detalle'],
                    'id_categoria': det['id_categoria'],
                    'categoria': det['categoria_nombre'],
                    'monto': float(det['monto']),
                    'descripcion': det.get('descripcion') or '',
                })
            for row_d in result:
                row_d['detalles'] = det_map.get(row_d['id'], [])

        return jsonify(result), 200
    except Exception as e:
        logger.error("Error listando movimientos de cuentas bancarias: %s", e)
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
        id_cuenta = int(payload.get('id_cuenta') or 0)

        owner = db.execute_query(
            "SELECT id_cuenta FROM cuenta WHERE id_cuenta = %s AND id_persona = %s LIMIT 1",
            (id_cuenta, user_id),
        )
        if not owner:
            return jsonify({'message': 'Cuenta no válida para este usuario'}), 400

        descripcion = (payload.get('descripcion') or '').strip() or 'Sin descripción'
        observacion = (payload.get('observacion') or '').strip() or None
        tipo = (payload.get('tipo') or 'gasto').strip().lower()
        detalles_raw = payload.get('detalles') or []

        if detalles_raw:
            monto = sum(abs(float(d.get('monto') or 0)) for d in detalles_raw)
            id_categoria = None
            payload['monto'] = monto  # para _create_transferencia
        else:
            monto = abs(float(payload.get('monto') or 0))
            id_categoria = payload.get('id_categoria')

        if monto <= 0:
            return jsonify({'message': 'El monto (o la suma de los detalles) debe ser mayor a 0'}), 400

        id_tipo = _resolve_tipo_id(db, tipo)
        id_estado = _resolve_estado_id(db, payload.get('estado'), payload.get('id_estado'))
        id_beneficiario = payload.get('id_beneficiario')
        fecha = payload.get('fecha')
        es_transferencia = bool(payload.get('es_transferencia'))

        if es_transferencia:
            return _create_transferencia(db, user_id, payload, id_estado)

        _ensure_detalle_table(db)
        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento (
                codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario,
                numero_transaccion, nota, fecha_creacion, id_cuenta
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, COALESCE(%s, NOW()), %s
            )
            """,
            (
                (payload.get('codigo') or descripcion)[:45],
                monto,
                id_tipo,
                id_estado,
                payload.get('id_producto'),
                id_categoria,
                id_beneficiario,
                payload.get('numero_transaccion') or f"CB-{user_id}-{int(datetime.now().timestamp())}",
                observacion,
                fecha,
                id_cuenta,
            ),
        )

        if not mov_id:
            return jsonify({'message': 'No se pudo crear el movimiento'}), 500

        if detalles_raw:
            _save_detalles(db, mov_id, detalles_raw)

        return jsonify({'message': 'Movimiento creado', 'id': mov_id}), 201
    except Exception as e:
        logger.error("Error creando movimiento de cuenta bancaria: %s", e)
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
            """
            SELECT m.id_movimiento, m.id_cuenta, COALESCE(em.nombre, '') AS estado_actual
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            LEFT JOIN estado_movimiento em ON m.id_estado = em.id_estado
            WHERE m.id_movimiento = %s AND c.id_persona = %s
            LIMIT 1
            """,
            (movimiento_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        estado_actual = (exists[0].get('estado_actual') or '').strip().lower()
        if estado_actual == 'conciliado':
            campos_bloqueados = [
                'id_cuenta',
                'descripcion',
                'monto',
                'fecha',
                'id_categoria',
                'id_beneficiario',
                'tipo',
                'id_producto',
            ]
            if any(payload.get(campo) is not None for campo in campos_bloqueados) or payload.get('detalles') is not None:
                return jsonify({
                    'message': 'El movimiento está conciliado. Solo puede cambiar estado u observación.'
                }), 400

        id_cuenta = payload.get('id_cuenta')
        if id_cuenta:
            owner = db.execute_query(
                "SELECT id_cuenta FROM cuenta WHERE id_cuenta = %s AND id_persona = %s LIMIT 1",
                (id_cuenta, user_id),
            )
            if not owner:
                return jsonify({'message': 'Cuenta no válida para este usuario'}), 400

        tipo_id = None
        if payload.get('tipo'):
            tipo_id = _resolve_tipo_id(db, payload.get('tipo'))

        estado_id = None
        if payload.get('estado') or payload.get('id_estado'):
            estado_id = _resolve_estado_id(db, payload.get('estado'), payload.get('id_estado'))

        monto = payload.get('monto')
        monto = abs(float(monto)) if monto is not None else None

        db.execute_non_query(
            """
            UPDATE movimiento
            SET id_cuenta = COALESCE(%s, id_cuenta),
                codigo = COALESCE(%s, codigo),
                nota = COALESCE(%s, nota),
                monto = COALESCE(%s, monto),
                fecha_creacion = COALESCE(%s, fecha_creacion),
                id_categoria = COALESCE(%s, id_categoria),
                id_beneficiario = COALESCE(%s, id_beneficiario),
                id_tipo = COALESCE(%s, id_tipo),
                id_estado = COALESCE(%s, id_estado),
                id_producto = COALESCE(%s, id_producto)
            WHERE id_movimiento = %s
            """,
            (
                id_cuenta,
                payload.get('descripcion'),
                payload.get('observacion'),
                monto,
                payload.get('fecha'),
                payload.get('id_categoria'),
                payload.get('id_beneficiario'),
                tipo_id,
                estado_id,
                payload.get('id_producto'),
                movimiento_id,
            ),
        )

        detalles_raw = payload.get('detalles')
        if detalles_raw is not None:
            _ensure_detalle_table(db)
            total_monto = _save_detalles(db, movimiento_id, detalles_raw)
            if total_monto > 0:
                db.execute_non_query(
                    "UPDATE movimiento SET monto = %s, id_categoria = NULL WHERE id_movimiento = %s",
                    (total_monto, movimiento_id),
                )

        return jsonify({'message': 'Movimiento actualizado'}), 200
    except Exception as e:
        logger.error("Error actualizando movimiento %s: %s", movimiento_id, e)
        return jsonify({'message': 'Error al actualizar movimiento'}), 500
    finally:
        db.close()


@bp.route('/movimientos/<int:movimiento_id>/duplicar', methods=['POST'])
def duplicate_movimiento(movimiento_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            """
            SELECT m.*
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            WHERE m.id_movimiento = %s AND c.id_persona = %s
            LIMIT 1
            """,
            (movimiento_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        src = rows[0]
        estado_dup = _resolve_estado_id(db, 'duplicado', None)
        new_id = db.execute_non_query(
            """
            INSERT INTO movimiento (
                codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario,
                numero_transaccion, nota, fecha_creacion, id_cuenta
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, NOW(), %s
            )
            """,
            (
                f"DUP-{src.get('codigo') or src.get('id_movimiento')}",
                src.get('monto'),
                src.get('id_tipo'),
                estado_dup,
                src.get('id_producto'),
                src.get('id_categoria'),
                src.get('id_beneficiario'),
                src.get('numero_transaccion'),
                f"(Duplicado) {src.get('nota') or 'Sin descripción'}",
                src.get('id_cuenta'),
            ),
        )
        if not new_id:
            return jsonify({'message': 'No se pudo duplicar el movimiento'}), 500

        # Copiar detalles de categorías múltiples si existen
        _ensure_detalle_table(db)
        dets = db.execute_query(
            "SELECT id_categoria, monto, descripcion FROM movimiento_detalle WHERE id_movimiento = %s ORDER BY id_detalle",
            (movimiento_id,),
        ) or []
        for d in dets:
            db.execute_non_query(
                "INSERT INTO movimiento_detalle (id_movimiento, id_categoria, monto, descripcion) VALUES (%s, %s, %s, %s)",
                (new_id, d.get('id_categoria'), d.get('monto'), d.get('descripcion')),
            )

        return jsonify({'message': 'Movimiento duplicado', 'id': new_id}), 201
    except Exception as e:
        logger.error("Error duplicando movimiento %s: %s", movimiento_id, e)
        return jsonify({'message': 'Error al duplicar movimiento'}), 500
    finally:
        db.close()


def _create_transferencia(db: DatabaseConnector, user_id: int, payload: dict, id_estado: int):
    id_origen = int(payload.get('id_cuenta') or 0)
    id_destino_cuenta = payload.get('id_cuenta_destino')
    destino_tipo = (payload.get('destino_tipo') or 'cuenta').strip().lower()
    destino_producto = payload.get('id_producto_destino')
    monto = abs(float(payload.get('monto') or 0))
    fecha = payload.get('fecha')
    observacion = (payload.get('observacion') or '').strip() or 'Transferencia'
    descripcion = (payload.get('descripcion') or 'Transferencia')[:45]
    tx_ref = payload.get('numero_transaccion') or f"TRF-{user_id}-{int(datetime.now().timestamp())}"

    if monto <= 0:
        return jsonify({'message': 'El monto de transferencia debe ser mayor a 0'}), 400

    tipo_gasto = _resolve_tipo_id(db, 'gasto')
    tipo_ingreso = _resolve_tipo_id(db, 'ingreso')

    if destino_tipo == 'cuenta':
        if not id_destino_cuenta:
            return jsonify({'message': 'Cuenta destino obligatoria para transferencia entre cuentas'}), 400
        if int(id_destino_cuenta) == id_origen:
            return jsonify({'message': 'La cuenta destino debe ser diferente a la cuenta origen'}), 400

        own_dest = db.execute_query(
            "SELECT id_cuenta FROM cuenta WHERE id_cuenta = %s AND id_persona = %s LIMIT 1",
            (id_destino_cuenta, user_id),
        )
        if not own_dest:
            return jsonify({'message': 'La cuenta destino no pertenece al usuario'}), 400

        id_out = db.execute_non_query(
            """
            INSERT INTO movimiento (codigo, monto, id_tipo, id_estado, id_producto, id_categoria,
                                    id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,COALESCE(%s, NOW()),%s)
            """,
            (f"{descripcion} (Salida)", monto, tipo_gasto, id_estado, None,
             payload.get('id_categoria'), payload.get('id_beneficiario'), tx_ref,
             observacion, fecha, id_origen),
        )
        id_in = db.execute_non_query(
            """
            INSERT INTO movimiento (codigo, monto, id_tipo, id_estado, id_producto, id_categoria,
                                    id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,COALESCE(%s, NOW()),%s)
            """,
            (f"{descripcion} (Entrada)", monto, tipo_ingreso, id_estado, None,
             payload.get('id_categoria'), payload.get('id_beneficiario'), tx_ref,
             observacion, fecha, id_destino_cuenta),
        )
        return jsonify({'message': 'Transferencia entre cuentas registrada', 'ids': [id_out, id_in]}), 201

    if destino_tipo == 'producto':
        if not destino_producto:
            return jsonify({'message': 'Producto destino obligatorio'}), 400

        id_mov = db.execute_non_query(
            """
            INSERT INTO movimiento (codigo, monto, id_tipo, id_estado, id_producto, id_categoria,
                                    id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,COALESCE(%s, NOW()),%s)
            """,
            (f"{descripcion} (Producto)", monto, tipo_gasto, id_estado, destino_producto,
             payload.get('id_categoria'), payload.get('id_beneficiario'), tx_ref,
             observacion, fecha, id_origen),
        )
        return jsonify({'message': 'Transferencia a producto registrada', 'id': id_mov}), 201

    return jsonify({'message': 'destino_tipo no válido. Use cuenta o producto'}), 400


@bp.route('/movimientos/<int:movimiento_id>', methods=['DELETE'])
def delete_movimiento(movimiento_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        exists = db.execute_query(
            """
            SELECT m.id_movimiento
            FROM movimiento m
            INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
            WHERE m.id_movimiento = %s AND c.id_persona = %s
            LIMIT 1
            """,
            (movimiento_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Movimiento no encontrado'}), 404

        db.execute_non_query("DELETE FROM movimiento WHERE id_movimiento = %s", (movimiento_id,))
        return jsonify({'message': 'Movimiento eliminado'}), 200
    except Exception as e:
        logger.error("Error eliminando movimiento %s: %s", movimiento_id, e)
        return jsonify({'message': 'Error al eliminar movimiento'}), 500
    finally:
        db.close()
