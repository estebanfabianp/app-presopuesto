"""Rutas API de Beneficiarios - CRUD completo sobre la tabla beneficiario."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('beneficiarios', __name__, url_prefix='/api/beneficiarios')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


@bp.route('', methods=['GET'])
def list_beneficiarios():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        busqueda = request.args.get('q', '').strip()
        solo_activos = request.args.get('solo_activos', 'false').lower() == 'true'

        conditions = ['b.id_persona = %s']
        params = [user_id]
        if busqueda:
            conditions.append('b.nombre LIKE %s')
            params.append(f'%{busqueda}%')
        if solo_activos:
            conditions.append('b.estado = 1')

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        query = (
            "SELECT b.id_beneficiario, b.nombre, b.estado, b.tipo, "
            "(SELECT COUNT(*) FROM movimiento m WHERE m.id_beneficiario = b.id_beneficiario) AS uso "
            "FROM beneficiario b " + where + " ORDER BY b.nombre"
        )
        rows = db.execute_query(
            query,
            tuple(params) if params else None,
        )

        beneficiarios = [
            {
                'id': r['id_beneficiario'],
                'nombre': r['nombre'],
                'estado': bool(r['estado']),
                'tipo': r.get('tipo') or 'Otro',
                'uso': int(r.get('uso') or 0),
            }
            for r in (rows or [])
        ]
        return jsonify({'beneficiarios': beneficiarios, 'total': len(beneficiarios)}), 200
    except Exception as e:
        logger.error('Error listando beneficiarios: %s', e)
        return jsonify({'message': 'Error al listar beneficiarios'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_beneficiario():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        tipo = (data.get('tipo') or 'Otro').strip()
        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        existe = db.execute_query(
            "SELECT id_beneficiario FROM beneficiario WHERE id_persona = %s AND LOWER(nombre) = LOWER(%s) LIMIT 1",
            (user_id, nombre),
        )
        if existe:
            return jsonify({'message': f'Ya existe un beneficiario con el nombre "{nombre}"'}), 409

        db.execute_non_query(
            "INSERT INTO beneficiario (id_persona, nombre, tipo, estado) VALUES (%s, %s, %s, 1)", (user_id, nombre, tipo)
        )
        rows = db.execute_query(
            "SELECT id_beneficiario FROM beneficiario WHERE id_persona = %s AND nombre = %s ORDER BY id_beneficiario DESC LIMIT 1",
            (user_id, nombre),
        )
        new_id = rows[0]['id_beneficiario'] if rows else None
        return jsonify({'message': 'Beneficiario creado', 'id': new_id, 'nombre': nombre, 'tipo': tipo, 'estado': True}), 201
    except Exception as e:
        logger.error('Error creando beneficiario: %s', e)
        return jsonify({'message': 'Error al crear beneficiario'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiario_id>', methods=['PUT'])
def update_beneficiario(beneficiario_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            "SELECT id_beneficiario, nombre, estado, tipo FROM beneficiario WHERE id_beneficiario = %s AND id_persona = %s LIMIT 1",
            (beneficiario_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Beneficiario no encontrado'}), 404

        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        tipo = (data.get('tipo') or rows[0].get('tipo') or 'Otro').strip()
        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        existe = db.execute_query(
            "SELECT id_beneficiario FROM beneficiario WHERE id_persona = %s AND LOWER(nombre) = LOWER(%s) AND id_beneficiario != %s LIMIT 1",
            (user_id, nombre, beneficiario_id),
        )
        if existe:
            return jsonify({'message': f'Ya existe otro beneficiario con el nombre "{nombre}"'}), 409

        db.execute_non_query(
            "UPDATE beneficiario SET nombre = %s, tipo = %s WHERE id_beneficiario = %s AND id_persona = %s",
            (nombre, tipo, beneficiario_id, user_id),
        )
        return jsonify({'message': 'Beneficiario actualizado'}), 200
    except Exception as e:
        logger.error('Error actualizando beneficiario %s: %s', beneficiario_id, e)
        return jsonify({'message': 'Error al actualizar beneficiario'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiario_id>/estado', methods=['PATCH'])
def toggle_estado_beneficiario(beneficiario_id):
    """Activa o inactiva un beneficiario sin eliminarlo."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            "SELECT id_beneficiario, estado FROM beneficiario WHERE id_beneficiario = %s AND id_persona = %s LIMIT 1",
            (beneficiario_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Beneficiario no encontrado'}), 404

        nuevo_estado = 0 if rows[0]['estado'] else 1
        db.execute_non_query(
            "UPDATE beneficiario SET estado = %s WHERE id_beneficiario = %s AND id_persona = %s",
            (nuevo_estado, beneficiario_id, user_id),
        )
        return jsonify({'message': 'Estado actualizado', 'estado': bool(nuevo_estado)}), 200
    except Exception as e:
        logger.error('Error cambiando estado beneficiario %s: %s', beneficiario_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


@bp.route('/<int:beneficiario_id>', methods=['DELETE'])
def delete_beneficiario(beneficiario_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            "SELECT id_beneficiario FROM beneficiario WHERE id_beneficiario = %s AND id_persona = %s LIMIT 1",
            (beneficiario_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Beneficiario no encontrado'}), 404

        db.execute_non_query(
            "DELETE FROM beneficiario WHERE id_beneficiario = %s AND id_persona = %s", (beneficiario_id, user_id)
        )
        return jsonify({'message': 'Beneficiario eliminado'}), 200
    except Exception as e:
        msg = str(e)
        if '1451' in msg or 'foreign key' in msg.lower():
            return jsonify({
                'message': 'No se puede eliminar: este beneficiario está referenciado en movimientos.'
            }), 409
        logger.error('Error eliminando beneficiario %s: %s', beneficiario_id, e)
        return jsonify({'message': 'Error al eliminar beneficiario'}), 500
    finally:
        db.close()
