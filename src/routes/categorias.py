"""Rutas API de Categorías - CRUD con soporte de subcategorías (parent_id)."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _build_tree(rows):
    """Construye árbol padre → hijos a partir de una lista plana."""
    by_id = {}
    for r in rows:
        by_id[r['id']] = {**r, 'subcategorias': []}

    raices = []
    for node in by_id.values():
        pid = node['parent_id']
        if pid and pid in by_id:
            by_id[pid]['subcategorias'].append(node)
        else:
            raices.append(node)

    # Ordenar hijos por nombre
    for node in by_id.values():
        node['subcategorias'].sort(key=lambda x: x['nombre'])
    raices.sort(key=lambda x: x['nombre'])
    return raices


@bp.route('', methods=['GET'])
def list_categorias():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        busqueda = request.args.get('q', '').strip()
        plana = request.args.get('plana', 'false').lower() == 'true'
        solo_activas = request.args.get('solo_activas', 'false').lower() == 'true'

        base_select = """
            SELECT c.id_categoria, c.nombre, c.parent_id, c.estado, c.icono, c.color,
                   p.nombre AS nombre_padre,
                   (
                       SELECT COUNT(*)
                       FROM movimiento m
                       INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
                       WHERE m.id_categoria = c.id_categoria
                         AND cu.id_persona = %s
                   ) AS uso
            FROM categoria c
            LEFT JOIN categoria p ON c.parent_id = p.id_categoria
        """

        conditions = ['c.id_persona = %s']
        params = [user_id]
        if busqueda:
            conditions.append('c.nombre LIKE %s')
            params.append(f'%{busqueda}%')
        if solo_activas:
            conditions.append('c.estado = 1')

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        order = 'ORDER BY c.nombre' if busqueda else \
                'ORDER BY COALESCE(c.parent_id, c.id_categoria), c.parent_id IS NOT NULL, c.nombre'

        rows = db.execute_query(
            f"{base_select} {where} {order}",
            (user_id,) + tuple(params),
        )

        flat = [
            {
                'id': r['id_categoria'],
                'nombre': r['nombre'],
                'parent_id': r['parent_id'],
                'nombre_padre': r.get('nombre_padre'),
                'estado': bool(r['estado']),
                'icono': r.get('icono') or 'fa-tag',
                'color': r.get('color') or '#6c757d',
                'uso': int(r.get('uso') or 0),
            }
            for r in (rows or [])
        ]

        if plana:
            return jsonify({'categorias': flat, 'total': len(flat)}), 200

        arbol = _build_tree(flat)
        return jsonify({'arbol': arbol, 'categorias': flat, 'total': len(flat)}), 200
    except Exception as e:
        logger.error('Error listando categorias: %s', e)
        return jsonify({'message': 'Error al listar categorías'}), 500
    finally:
        db.close()


@bp.route('', methods=['POST'])
def create_categoria():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        parent_id = data.get('parent_id') or None
        icono = (data.get('icono') or 'fa-tag').strip()
        color = (data.get('color') or '#6c757d').strip()

        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        # Validar que el padre exista y no sea él mismo una subcategoría
        if parent_id:
            padre = db.execute_query(
                "SELECT id_categoria, parent_id FROM categoria WHERE id_categoria = %s AND id_persona = %s LIMIT 1",
                (parent_id, user_id),
            )
            if not padre:
                return jsonify({'message': 'La categoría padre no existe'}), 400
            if padre[0]['parent_id'] is not None:
                return jsonify({'message': 'No se pueden crear subcategorías de subcategorías'}), 400

        existe = db.execute_query(
            "SELECT id_categoria FROM categoria WHERE id_persona = %s AND LOWER(nombre) = LOWER(%s) AND (parent_id <=> %s) LIMIT 1",
            (user_id, nombre, parent_id),
        )
        if existe:
            return jsonify({'message': f'Ya existe una categoría con el nombre "{nombre}" en ese nivel'}), 409

        db.execute_non_query(
            "INSERT INTO categoria (id_persona, nombre, parent_id, icono, color, estado) VALUES (%s, %s, %s, %s, %s, 1)",
            (user_id, nombre, parent_id, icono, color),
        )
        rows = db.execute_query(
            "SELECT id_categoria FROM categoria WHERE id_persona = %s AND nombre = %s AND (parent_id <=> %s) ORDER BY id_categoria DESC LIMIT 1",
            (user_id, nombre, parent_id),
        )
        new_id = rows[0]['id_categoria'] if rows else None
        return jsonify({'message': 'Categoría creada', 'id': new_id, 'nombre': nombre, 'estado': True}), 201
    except Exception as e:
        logger.error('Error creando categoria: %s', e)
        return jsonify({'message': 'Error al crear categoría'}), 500
    finally:
        db.close()


@bp.route('/<int:categoria_id>', methods=['PUT'])
def update_categoria(categoria_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        actual = db.execute_query(
            "SELECT id_categoria, parent_id, icono, color FROM categoria WHERE id_categoria = %s AND id_persona = %s LIMIT 1",
            (categoria_id, user_id),
        )
        if not actual:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        # 'parent_id' ausente del payload = no cambiar; null explícito = quitar padre
        parent_id = data.get('parent_id', actual[0]['parent_id'])
        icono = (data.get('icono') or actual[0].get('icono') or 'fa-tag').strip()
        color = (data.get('color') or actual[0].get('color') or '#6c757d').strip()

        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        # Evitar que se asigne como propio padre
        if parent_id == categoria_id:
            return jsonify({'message': 'Una categoría no puede ser su propio padre'}), 400

        # Validar que el nuevo padre no sea una subcategoría de éste
        if parent_id:
            padre = db.execute_query(
                "SELECT id_categoria, parent_id FROM categoria WHERE id_categoria = %s AND id_persona = %s LIMIT 1",
                (parent_id, user_id),
            )
            if not padre:
                return jsonify({'message': 'La categoría padre no existe'}), 400
            if padre[0]['parent_id'] is not None:
                return jsonify({'message': 'No se pueden crear subcategorías de subcategorías'}), 400

        # Evitar duplicado de nombre al mismo nivel
        existe = db.execute_query(
            "SELECT id_categoria FROM categoria WHERE id_persona = %s AND LOWER(nombre) = LOWER(%s) AND (parent_id <=> %s) AND id_categoria != %s LIMIT 1",
            (user_id, nombre, parent_id, categoria_id),
        )
        if existe:
            return jsonify({'message': f'Ya existe otra categoría con el nombre "{nombre}" en ese nivel'}), 409

        db.execute_non_query(
            "UPDATE categoria SET nombre = %s, parent_id = %s, icono = %s, color = %s WHERE id_categoria = %s AND id_persona = %s",
            (nombre, parent_id, icono, color, categoria_id, user_id),
        )
        return jsonify({'message': 'Categoría actualizada'}), 200
    except Exception as e:
        logger.error('Error actualizando categoria %s: %s', categoria_id, e)
        return jsonify({'message': 'Error al actualizar categoría'}), 500
    finally:
        db.close()


@bp.route('/<int:categoria_id>/estado', methods=['PATCH'])
def toggle_estado_categoria(categoria_id):
    """Activa o inactiva una categoría sin eliminarla."""
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            "SELECT id_categoria, estado FROM categoria WHERE id_categoria = %s AND id_persona = %s LIMIT 1",
            (categoria_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        nuevo_estado = 0 if rows[0]['estado'] else 1
        db.execute_non_query(
            "UPDATE categoria SET estado = %s WHERE id_categoria = %s AND id_persona = %s",
            (nuevo_estado, categoria_id, user_id),
        )
        return jsonify({'message': 'Estado actualizado', 'estado': bool(nuevo_estado)}), 200
    except Exception as e:
        logger.error('Error cambiando estado categoria %s: %s', categoria_id, e)
        return jsonify({'message': 'Error al cambiar estado'}), 500
    finally:
        db.close()


@bp.route('/<int:categoria_id>', methods=['DELETE'])
def delete_categoria(categoria_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            "SELECT id_categoria FROM categoria WHERE id_categoria = %s AND id_persona = %s LIMIT 1",
            (categoria_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        # Verificar que no tenga subcategorías
        hijos = db.execute_query(
            "SELECT COUNT(*) AS total FROM categoria WHERE parent_id = %s AND id_persona = %s",
            (categoria_id, user_id),
        )
        if hijos and hijos[0]['total'] > 0:
            return jsonify({
                'message': 'No se puede eliminar: esta categoría tiene subcategorías. Inactívala o elimina las subcategorías primero.'
            }), 409

        db.execute_non_query(
            "DELETE FROM categoria WHERE id_categoria = %s AND id_persona = %s", (categoria_id, user_id)
        )
        return jsonify({'message': 'Categoría eliminada'}), 200
    except Exception as e:
        msg = str(e)
        if '1451' in msg or 'foreign key' in msg.lower():
            return jsonify({
                'message': 'No se puede eliminar: esta categoría está siendo usada en movimientos o presupuestos.'
            }), 409
        logger.error('Error eliminando categoria %s: %s', categoria_id, e)
        return jsonify({'message': 'Error al eliminar categoría'}), 500
    finally:
        db.close()

