"""Rutas API de Transacciones conectadas a base de datos MySQL."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('transacciones', __name__, url_prefix='/api/transacciones')

logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _resolve_tipo_id(db: DatabaseConnector, nombre_tipo: str):
    if not nombre_tipo:
        nombre_tipo = 'gasto'
    rows = db.execute_query(
        "SELECT id_tipo FROM tipo_movimiento WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (nombre_tipo,),
    )
    if rows:
        return rows[0]['id_tipo']
    return db.execute_non_query("INSERT INTO tipo_movimiento (nombre) VALUES (%s)", (nombre_tipo,))


def _resolve_categoria_id(db: DatabaseConnector, nombre_categoria: str):
    if not nombre_categoria:
        return None
    rows = db.execute_query(
        "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (nombre_categoria,),
    )
    if rows:
        return rows[0]['id_categoria']
    return db.execute_non_query("INSERT INTO categoria (nombre) VALUES (%s)", (nombre_categoria,))


def _default_cuenta_id(db: DatabaseConnector, user_id: int):
    rows = db.execute_query(
        "SELECT id_cuenta FROM cuenta WHERE id_persona = %s ORDER BY id_cuenta ASC LIMIT 1",
        (user_id,),
    )
    if rows:
        return rows[0]['id_cuenta']
    return None


@bp.route('', methods=['GET'])
def list_transacciones():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        limit = min(int(request.args.get('limit', 100)), 500)
        rows = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                DATE(m.fecha_creacion) AS fecha,
                COALESCE(m.nota, m.codigo, 'Sin descripción') AS descripcion,
                COALESCE(ca.nombre, 'General') AS categoria,
                COALESCE(tm.nombre, 'gasto') AS tipo,
                m.monto
            FROM movimiento m
            INNER JOIN cuenta cu ON m.id_cuenta = cu.id_cuenta
            LEFT JOIN categoria ca ON m.id_categoria = ca.id_categoria
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE cu.id_persona = %s
            ORDER BY m.fecha_creacion DESC, m.id_movimiento DESC
            LIMIT %s
            """,
            (user_id, limit),
        )

        result = []
        for row in rows:
            monto = float(row.get('monto') or 0)
            tipo = (row.get('tipo') or '').lower()
            signed_monto = monto if tipo == 'ingreso' else -abs(monto)
            result.append({
                'id': row['id_movimiento'],
                'fecha': row['fecha'].isoformat() if row.get('fecha') else None,
                'descripcion': row.get('descripcion') or 'Sin descripción',
                'categoria': row.get('categoria') or 'General',
                'monto': signed_monto,
                'tipo': tipo,
            })

        return jsonify(result), 200
    except Exception as e:
        logger.error("Error listando transacciones: %s", e)
        return jsonify({'message': 'Error al listar transacciones'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_transaccion():
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        descripcion = payload.get('descripcion') or payload.get('nota') or 'Sin descripción'
        categoria = payload.get('categoria')
        tipo = (payload.get('tipo') or ('ingreso' if float(payload.get('monto', 0) or 0) >= 0 else 'gasto')).lower()
        monto = abs(float(payload.get('monto', 0) or 0))
        fecha = payload.get('fecha')
        id_estado = int(payload.get('id_estado', 2))

        id_tipo = payload.get('id_tipo') or _resolve_tipo_id(db, tipo)
        id_categoria = payload.get('id_categoria') or _resolve_categoria_id(db, categoria)
        id_cuenta = payload.get('id_cuenta') or _default_cuenta_id(db, user_id)
        if not id_cuenta:
            return jsonify({'message': 'No existe una cuenta para registrar la transacción'}), 400

        mov_id = db.execute_non_query(
            """
            INSERT INTO movimiento (
                codigo, monto, id_tipo, id_estado, id_categoria, id_beneficiario,
                fecha_creacion, id_cuenta, nota, numero_transaccion
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                COALESCE(%s, NOW()), %s, %s, %s
            )
            """,
            (
                payload.get('codigo') or f"MOV-{user_id}-{id_cuenta}",
                monto,
                id_tipo,
                id_estado,
                id_categoria,
                payload.get('id_beneficiario'),
                fecha,
                id_cuenta,
                descripcion,
                payload.get('numero_transaccion'),
            ),
        )

        if not mov_id:
            return jsonify({'message': 'No se pudo crear la transacción'}), 500

        created = db.execute_query(
            """
            SELECT
                m.id_movimiento,
                DATE(m.fecha_creacion) AS fecha,
                COALESCE(m.nota, m.codigo, 'Sin descripción') AS descripcion,
                COALESCE(ca.nombre, 'General') AS categoria,
                COALESCE(tm.nombre, 'gasto') AS tipo,
                m.monto
            FROM movimiento m
            LEFT JOIN categoria ca ON m.id_categoria = ca.id_categoria
            LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
            WHERE m.id_movimiento = %s
            LIMIT 1
            """,
            (mov_id,),
        )

        if not created:
            return jsonify({'message': 'Transacción creada'}), 201

        row = created[0]
        valor = float(row.get('monto') or 0)
        tipo_row = (row.get('tipo') or '').lower()
        return jsonify({
            'id': row['id_movimiento'],
            'fecha': row['fecha'].isoformat() if row.get('fecha') else None,
            'descripcion': row.get('descripcion') or 'Sin descripción',
            'categoria': row.get('categoria') or 'General',
            'monto': valor if tipo_row == 'ingreso' else -abs(valor),
            'tipo': tipo_row,
        }), 201
    except Exception as e:
        logger.error("Error creando transacción: %s", e)
        return jsonify({'message': 'Error al crear transacción'}), 500
    finally:
        db.close()


@bp.route('/<int:transaccion_id>', methods=['PUT'])
def update_transaccion(transaccion_id):
    verify_jwt_in_request()
    payload = request.get_json(silent=True) or {}
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
            (transaccion_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Transacción no encontrada'}), 404

        categoria_id = payload.get('id_categoria')
        if payload.get('categoria'):
            categoria_id = _resolve_categoria_id(db, payload.get('categoria'))

        tipo_id = payload.get('id_tipo')
        if payload.get('tipo'):
            tipo_id = _resolve_tipo_id(db, payload.get('tipo'))

        monto = payload.get('monto')
        monto = abs(float(monto)) if monto is not None else None

        db.execute_non_query(
            """
            UPDATE movimiento
            SET nota = COALESCE(%s, nota),
                monto = COALESCE(%s, monto),
                fecha_creacion = COALESCE(%s, fecha_creacion),
                id_categoria = COALESCE(%s, id_categoria),
                id_tipo = COALESCE(%s, id_tipo),
                id_estado = COALESCE(%s, id_estado)
            WHERE id_movimiento = %s
            """,
            (
                payload.get('descripcion'),
                monto,
                payload.get('fecha'),
                categoria_id,
                tipo_id,
                payload.get('id_estado'),
                transaccion_id,
            ),
        )

        return jsonify({'message': 'Transacción actualizada'}), 200
    except Exception as e:
        logger.error("Error actualizando transacción %s: %s", transaccion_id, e)
        return jsonify({'message': 'Error al actualizar transacción'}), 500
    finally:
        db.close()


@bp.route('/<int:transaccion_id>', methods=['DELETE'])
def delete_transaccion(transaccion_id):
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
            (transaccion_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Transacción no encontrada'}), 404

        db.execute_non_query("DELETE FROM movimiento WHERE id_movimiento = %s", (transaccion_id,))
        return jsonify({'message': 'Transacción eliminada'}), 200
    except Exception as e:
        logger.error("Error eliminando transacción %s: %s", transaccion_id, e)
        return jsonify({'message': 'Error al eliminar transacción'}), 500
    finally:
        db.close()
