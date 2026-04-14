"""Rutas API para Transacciones Programadas (recurrentes)."""

import logging
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('programadas', __name__, url_prefix='/api/programadas')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


# ──────────────────────────────────────────────────────────────
# GET /api/programadas
# ──────────────────────────────────────────────────────────────
@bp.route('', methods=['GET'])
def list_programadas():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            """
            SELECT
                tp.id_transaccion,
                tp.fecha,
                tp.numero_transaccion,
                tp.monto,
                tp.repeticion,
                tp.fecha_creacion,
                tm.nombre  AS tipo,
                c.nombre   AS categoria,
                b.nombre   AS beneficiario
            FROM transaccion_programada tp
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo   = tp.id_tipo
            LEFT JOIN categoria       c  ON c.id_categoria = tp.id_categoria
            LEFT JOIN beneficiario    b  ON b.id_beneficiario = tp.id_beneficiario
            WHERE tp.id_persona = %s
            ORDER BY tp.fecha ASC
            """,
            (user_id,),
        )
        result = []
        for r in rows:
            result.append({
                'id_transaccion':    r['id_transaccion'],
                'fecha':             str(r['fecha']) if r['fecha'] else None,
                'numero_transaccion': r['numero_transaccion'],
                'monto':             float(r['monto'] or 0),
                'repeticion':        r['repeticion'],
                'fecha_creacion':    str(r['fecha_creacion']) if r['fecha_creacion'] else None,
                'tipo':              r['tipo'],
                'categoria':         r['categoria'],
                'beneficiario':      r['beneficiario'],
            })
        return jsonify(result)
    except Exception as e:
        logger.error('Error listando programadas: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/programadas/<id>
# ──────────────────────────────────────────────────────────────
@bp.route('/<int:id_transaccion>', methods=['GET'])
def get_programada(id_transaccion):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            """
            SELECT
                tp.id_transaccion,
                tp.fecha,
                tp.id_tipo,
                tp.numero_transaccion,
                tp.monto,
                tp.repeticion,
                tp.id_categoria,
                tp.id_beneficiario,
                tp.fecha_creacion,
                tm.nombre  AS tipo,
                c.nombre   AS categoria,
                b.nombre   AS beneficiario
            FROM transaccion_programada tp
            LEFT JOIN tipo_movimiento tm ON tm.id_tipo        = tp.id_tipo
            LEFT JOIN categoria       c  ON c.id_categoria    = tp.id_categoria
            LEFT JOIN beneficiario    b  ON b.id_beneficiario = tp.id_beneficiario
                        WHERE tp.id_transaccion = %s
                            AND tp.id_persona = %s
            LIMIT 1
            """,
                        (id_transaccion, user_id),
        )
        if not rows:
            return jsonify({'error': 'No encontrada'}), 404
        r = rows[0]
        return jsonify({
            'id_transaccion':    r['id_transaccion'],
            'fecha':             str(r['fecha']) if r['fecha'] else None,
            'id_tipo':           r['id_tipo'],
            'numero_transaccion': r['numero_transaccion'],
            'monto':             float(r['monto'] or 0),
            'repeticion':        r['repeticion'],
            'id_categoria':      r['id_categoria'],
            'id_beneficiario':   r['id_beneficiario'],
            'fecha_creacion':    str(r['fecha_creacion']) if r['fecha_creacion'] else None,
            'tipo':              r['tipo'],
            'categoria':         r['categoria'],
            'beneficiario':      r['beneficiario'],
        })
    except Exception as e:
        logger.error('Error obteniendo programada %s: %s', id_transaccion, e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# POST /api/programadas
# ──────────────────────────────────────────────────────────────
@bp.route('', methods=['POST'])
def create_programada():
    verify_jwt_in_request()
    data = request.get_json(silent=True) or {}
    user_id = _get_user_id()

    fecha            = data.get('fecha')
    id_tipo          = data.get('id_tipo')
    numero_transaccion = data.get('numero_transaccion', '')
    monto            = data.get('monto')
    repeticion       = data.get('repeticion', 0)
    id_categoria     = data.get('id_categoria') or None
    id_beneficiario  = data.get('id_beneficiario') or None

    if not fecha or not monto or not id_tipo:
        return jsonify({'error': 'Campos obligatorios: fecha, monto, id_tipo'}), 400

    db = DatabaseConnector()
    try:
        new_id = db.execute_non_query(
            """
            INSERT INTO transaccion_programada
                (id_persona, fecha, id_tipo, numero_transaccion, monto, repeticion, id_categoria, id_beneficiario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, fecha, id_tipo, numero_transaccion, monto, repeticion, id_categoria, id_beneficiario),
        )
        return jsonify({'id_transaccion': new_id, 'message': 'Creada correctamente'}), 201
    except Exception as e:
        logger.error('Error creando programada: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# PUT /api/programadas/<id>
# ──────────────────────────────────────────────────────────────
@bp.route('/<int:id_transaccion>', methods=['PUT'])
def update_programada(id_transaccion):
    verify_jwt_in_request()
    data = request.get_json(silent=True) or {}
    user_id = _get_user_id()

    db = DatabaseConnector()
    try:
        # Verify exists
        existing = db.execute_query(
            'SELECT id_transaccion FROM transaccion_programada WHERE id_transaccion = %s AND id_persona = %s',
            (id_transaccion, user_id),
        )
        if not existing:
            return jsonify({'error': 'No encontrada'}), 404

        fecha            = data.get('fecha')
        id_tipo          = data.get('id_tipo')
        numero_transaccion = data.get('numero_transaccion', '')
        monto            = data.get('monto')
        repeticion       = data.get('repeticion', 0)
        id_categoria     = data.get('id_categoria') or None
        id_beneficiario  = data.get('id_beneficiario') or None

        db.execute_non_query(
            """
            UPDATE transaccion_programada
               SET fecha = %s,
                   id_tipo = %s,
                   numero_transaccion = %s,
                   monto = %s,
                   repeticion = %s,
                   id_categoria = %s,
                   id_beneficiario = %s
             WHERE id_transaccion = %s
                             AND id_persona = %s
            """,
            (fecha, id_tipo, numero_transaccion, monto, repeticion,
                         id_categoria, id_beneficiario, id_transaccion, user_id),
        )
        return jsonify({'message': 'Actualizada correctamente'})
    except Exception as e:
        logger.error('Error actualizando programada %s: %s', id_transaccion, e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# DELETE /api/programadas/<id>
# ──────────────────────────────────────────────────────────────
@bp.route('/<int:id_transaccion>', methods=['DELETE'])
def delete_programada(id_transaccion):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        existing = db.execute_query(
            'SELECT id_transaccion FROM transaccion_programada WHERE id_transaccion = %s AND id_persona = %s',
            (id_transaccion, user_id),
        )
        if not existing:
            return jsonify({'error': 'No encontrada'}), 404

        db.execute_non_query(
            'DELETE FROM transaccion_programada WHERE id_transaccion = %s AND id_persona = %s',
            (id_transaccion, user_id),
        )
        return jsonify({'message': 'Eliminada correctamente'})
    except Exception as e:
        logger.error('Error eliminando programada %s: %s', id_transaccion, e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────
# GET /api/programadas/catalogos  (tipos, categorías, beneficiarios)
# ──────────────────────────────────────────────────────────────
@bp.route('/catalogos', methods=['GET'])
def get_catalogos():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        tipos = db.execute_query('SELECT id_tipo, nombre FROM tipo_movimiento ORDER BY nombre')
        cats  = db.execute_query('SELECT id_categoria, nombre FROM categoria WHERE id_persona = %s ORDER BY nombre', (user_id,))
        benes = db.execute_query('SELECT id_beneficiario, nombre FROM beneficiario WHERE id_persona = %s ORDER BY nombre', (user_id,))
        return jsonify({
            'tipos':         [{'id': r['id_tipo'],          'nombre': r['nombre']} for r in tipos],
            'categorias':    [{'id': r['id_categoria'],     'nombre': r['nombre']} for r in cats],
            'beneficiarios': [{'id': r['id_beneficiario'],  'nombre': r['nombre']} for r in benes],
        })
    except Exception as e:
        logger.error('Error obteniendo catálogos: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
