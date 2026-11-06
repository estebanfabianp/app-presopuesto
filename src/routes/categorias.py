"""Rutas API de Categorías - CRUD con soporte de subcategorías (parent_id)."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')
logger = logging.getLogger(__name__)


def _normalizar_nombre_categoria(nombre: str) -> str:
    """Normaliza nombres de categoría: corrige mojibake y deja una redacción consistente."""
    if nombre is None:
        return ''

    valor = str(nombre).strip()
    if not valor:
        return ''

    reemplazos = {
        '├│': 'ó',
        '├║': 'ú',
        '├¡': 'í',
        '├®': 'é',
        '├│n': 'ón',
        '├║blico': 'úblico',
        '├¡a': 'ía',
        '├®s': 'és',
        '├│s': 'ós',
        '├▒': 'a',
        '├⌐': 'á',
        '├¼': 'ü',
        '├¢': 'á',
        '├£': 'í',
        '├ñ': 'ñ',
        '├¤': 'é',
        '├': 'ó',
        '¿': '',
        '¡': '',
        '  ': ' ',
    }

    for origen, destino in reemplazos.items():
        valor = valor.replace(origen, destino)

    valor = valor.replace('  ', ' ').strip()
    valor = ' '.join(valor.split())
    valor = valor.replace(' / ', ' / ')

    words = valor.split()
    normalized_words = []
    connectors = {'y', 'de', 'del', 'la', 'las', 'los', 'el', 'al', 'a', 'por', 'con'}

    for idx, word in enumerate(words):
        lower_word = word.lower()
        if idx > 0 and lower_word in connectors:
            normalized_words.append(lower_word)
        else:
            normalized_words.append(lower_word.capitalize())

    return ' '.join(normalized_words)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _build_tree(rows):
    """Construye árbol padre → hijos y ordena por estado y jerarquía para la UI."""
    by_id = {}
    for r in rows:
        by_id[r['id']] = {**r, 'subcategorias': [], 'ruta': None, 'nivel': 1 if not r.get('parent_id') else 2}

    raices = []
    for node in by_id.values():
        pid = node.get('parent_id')
        if pid and pid in by_id:
            padre = by_id[pid]
            node['nombre_padre'] = padre['nombre']
            padre['subcategorias'].append(node)
        else:
            raices.append(node)

    def _sort_key(node):
        estado = 0 if node.get('estado') is False else 1
        return (-estado, str(node.get('nombre') or '').lower())

    def _walk(nodes, prefix=''):
        ordered = sorted(nodes, key=_sort_key)
        for node in ordered:
            node['ruta'] = f"{prefix} / {node['nombre']}" if prefix else node['nombre']
            node['nivel'] = 2 if node.get('parent_id') else 1
            node['subcategorias'].sort(key=_sort_key)
            _walk(node['subcategorias'], node['ruta'])
            node['hijos'] = len(node['subcategorias'])
        return ordered

    _walk(raices)
    raices.sort(key=_sort_key)
    return raices


def _flatten_tree(nodes):
    """Aplana el árbol para devolver una lista con metadatos listos para la UI."""
    flat = []
    for node in nodes:
        flat.append({
            'id': node['id'],
            'nombre': node['nombre'],
            'parent_id': node.get('parent_id'),
            'nombre_padre': node.get('nombre_padre'),
            'estado': bool(node.get('estado', True)),
            'icono': node.get('icono') or 'fa-tag',
            'color': node.get('color') or '#6c757d',
            'uso': int(node.get('uso', 0) or 0),
            'ruta': node.get('ruta'),
            'nivel': node.get('nivel', 1),
            'hijos': len(node.get('subcategorias', [])),
        })
        flat.extend(_flatten_tree(node.get('subcategorias', [])))
    return flat


def _get_categoria_columns(db) -> set:
    """Devuelve las columnas reales de la tabla categoria para soportar esquemas antiguos."""
    try:
        rows = db.execute_query(
            """
            SELECT COLUMN_NAME
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'categoria'
            ORDER BY ORDINAL_POSITION
            """
        )
        return {str(r.get('COLUMN_NAME', '')).lower() for r in (rows or [])}
    except Exception:
        return set()


def _filter_categoria_conditions(columns: set, user_id: int, busqueda: str, solo_activas: bool):
    conditions = []
    params = []
    if 'id_persona' in columns:
        conditions.append('c.id_persona = %s')
        params.append(user_id)
    if busqueda:
        conditions.append('c.nombre LIKE %s')
        params.append(f'%{busqueda}%')
    if solo_activas and 'estado' in columns:
        conditions.append('c.estado = 1')
    return conditions, params


def _build_categoria_select(columns: set) -> str:
    select_parts = ['id_categoria', 'nombre']
    if 'parent_id' in columns:
        select_parts.append('parent_id')
    if 'estado' in columns:
        select_parts.append('estado')
    if 'icono' in columns:
        select_parts.append('icono')
    if 'color' in columns:
        select_parts.append('color')

    return f"SELECT {', '.join(select_parts)} FROM categoria"


def _build_categoria_insert_sql(columns: set, user_id: int, nombre: str, parent_id, icono: str, color: str):
    fields = ['nombre']
    values = [nombre]
    if 'id_persona' in columns:
        fields.append('id_persona')
        values.append(user_id)
    if 'parent_id' in columns:
        fields.append('parent_id')
        values.append(parent_id)
    if 'icono' in columns:
        fields.append('icono')
        values.append(icono)
    if 'color' in columns:
        fields.append('color')
        values.append(color)
    if 'estado' in columns:
        fields.append('estado')
        values.append(1)
    placeholders = ', '.join(['%s'] * len(values))
    return f"INSERT INTO categoria ({', '.join(fields)}) VALUES ({placeholders})", tuple(values)


def _build_categoria_exists_query(columns: set, user_id: int, nombre: str, parent_id, categoria_id=None):
    query = 'SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s)'
    params = [nombre]
    if 'id_persona' in columns:
        query += ' AND id_persona = %s'
        params.append(user_id)
    if 'parent_id' in columns:
        query += ' AND (parent_id <=> %s)'
        params.append(parent_id)
    if categoria_id is not None:
        query += ' AND id_categoria != %s'
        params.append(categoria_id)
    query += ' LIMIT 1'
    return query, tuple(params)


def _build_categoria_fetch_query(columns: set, categoria_id: int, user_id: int):
    query = 'SELECT id_categoria'
    params = [categoria_id]
    if 'parent_id' in columns:
        query += ', parent_id'
    if 'icono' in columns:
        query += ', icono'
    if 'color' in columns:
        query += ', color'
    query += ' FROM categoria WHERE id_categoria = %s'
    if 'id_persona' in columns:
        query += ' AND id_persona = %s'
        params.append(user_id)
    query += ' LIMIT 1'
    return query, tuple(params)


@bp.route('', methods=['GET'])
def list_categorias():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        busqueda = request.args.get('q', '').strip()
        plana = request.args.get('plana', 'false').lower() == 'true'
        solo_activas = request.args.get('solo_activas', 'false').lower() == 'true'

        columns = _get_categoria_columns(db)
        query = _build_categoria_select(columns)
        params = []

        if busqueda:
            query += " WHERE nombre LIKE %s"
            params.append(f'%{busqueda}%')
        elif solo_activas and 'estado' in columns:
            query += " WHERE estado = 1"

        query += " ORDER BY nombre"

        rows = db.execute_query(query, tuple(params))

        flat = [
            {
                'id': r['id_categoria'],
                'nombre': _normalizar_nombre_categoria(r['nombre']),
                'parent_id': r.get('parent_id') if 'parent_id' in columns else None,
                'nombre_padre': None,
                'estado': bool(r.get('estado', 1)) if 'estado' in columns else True,
                'icono': r.get('icono') or 'fa-tag' if 'icono' in columns else 'fa-tag',
                'color': r.get('color') or '#6c757d' if 'color' in columns else '#6c757d',
                'uso': 0,
            }
            for r in (rows or [])
        ]

        arbol = _build_tree(flat)
        flat = _flatten_tree(arbol)
        flat.sort(key=lambda item: (
            0 if item.get('estado') is not False else 1,
            0 if item.get('parent_id') is None else 1,
            str(item.get('nombre') or '').lower(),
        ))

        if plana:
            return jsonify({'categorias': flat, 'total': len(flat)}), 200

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
        columns = _get_categoria_columns(db)
        data = request.get_json() or {}
        nombre = _normalizar_nombre_categoria(data.get('nombre') or '')
        parent_id = data.get('parent_id') or None
        icono = (data.get('icono') or 'fa-tag').strip()
        color = (data.get('color') or '#6c757d').strip()

        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        # Validar que el padre exista y no sea él mismo una subcategoría
        if parent_id and 'parent_id' in columns:
            padre = db.execute_query(
                "SELECT id_categoria, parent_id FROM categoria WHERE id_categoria = %s" + (
                    " AND id_persona = %s" if 'id_persona' in columns else ''
                ) + " LIMIT 1",
                (parent_id, user_id) if 'id_persona' in columns else (parent_id,),
            )
            if not padre:
                return jsonify({'message': 'La categoría padre no existe'}), 400
            if padre[0]['parent_id'] is not None:
                return jsonify({'message': 'No se pueden crear subcategorías de subcategorías'}), 400

        existe_query, existe_params = _build_categoria_exists_query(columns, user_id, nombre, parent_id)
        existe = db.execute_query(existe_query, existe_params)
        if existe:
            return jsonify({'message': f'Ya existe una categoría con el nombre "{nombre}" en ese nivel'}), 409

        insert_query, insert_params = _build_categoria_insert_sql(columns, user_id, nombre, parent_id, icono, color)
        db.execute_non_query(insert_query, insert_params)
        fetch_query = 'SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s)'
        fetch_params = [nombre]
        if 'id_persona' in columns:
            fetch_query += ' AND id_persona = %s'
            fetch_params.append(user_id)
        if 'parent_id' in columns:
            fetch_query += ' AND (parent_id <=> %s)'
            fetch_params.append(parent_id)
        fetch_query += ' ORDER BY id_categoria DESC LIMIT 1'
        rows = db.execute_query(fetch_query, tuple(fetch_params))
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
        columns = _get_categoria_columns(db)
        actual = db.execute_query(
            _build_categoria_fetch_query(columns, categoria_id, user_id)[0],
            _build_categoria_fetch_query(columns, categoria_id, user_id)[1],
        )
        if not actual:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        data = request.get_json() or {}
        nombre = _normalizar_nombre_categoria(data.get('nombre') or '')
        # 'parent_id' ausente del payload = no cambiar; null explícito = quitar padre
        parent_id = data.get('parent_id', actual[0].get('parent_id') if 'parent_id' in columns else None)
        icono = (data.get('icono') or actual[0].get('icono') or 'fa-tag').strip() if 'icono' in columns or 'icono' in actual[0] else 'fa-tag'
        color = (data.get('color') or actual[0].get('color') or '#6c757d').strip() if 'color' in columns or 'color' in actual[0] else '#6c757d'

        if not nombre:
            return jsonify({'message': 'El nombre es obligatorio'}), 400

        # Evitar que se asigne como propio padre
        if parent_id == categoria_id:
            return jsonify({'message': 'Una categoría no puede ser su propio padre'}), 400

        # Validar que el nuevo padre no sea una subcategoría de éste
        if parent_id and 'parent_id' in columns:
            padre = db.execute_query(
                "SELECT id_categoria, parent_id FROM categoria WHERE id_categoria = %s" + (
                    " AND id_persona = %s" if 'id_persona' in columns else ''
                ) + " LIMIT 1",
                (parent_id, user_id) if 'id_persona' in columns else (parent_id,),
            )
            if not padre:
                return jsonify({'message': 'La categoría padre no existe'}), 400
            if padre[0]['parent_id'] is not None:
                return jsonify({'message': 'No se pueden crear subcategorías de subcategorías'}), 400

        # Evitar duplicado de nombre al mismo nivel
        existe_query, existe_params = _build_categoria_exists_query(columns, user_id, nombre, parent_id, categoria_id)
        existe = db.execute_query(existe_query, existe_params)
        if existe:
            return jsonify({'message': f'Ya existe otra categoría con el nombre "{nombre}" en ese nivel'}), 409

        update_fields = ['nombre = %s']
        update_values = [nombre]
        if 'parent_id' in columns:
            update_fields.append('parent_id = %s')
            update_values.append(parent_id)
        if 'icono' in columns:
            update_fields.append('icono = %s')
            update_values.append(icono)
        if 'color' in columns:
            update_fields.append('color = %s')
            update_values.append(color)
        update_query = f"UPDATE categoria SET {', '.join(update_fields)} WHERE id_categoria = %s"
        update_values.append(categoria_id)
        if 'id_persona' in columns:
            update_query += ' AND id_persona = %s'
            update_values.append(user_id)
        db.execute_non_query(update_query, tuple(update_values))
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
        columns = _get_categoria_columns(db)
        rows = db.execute_query(
            "SELECT id_categoria" + (', estado' if 'estado' in columns else '') + " FROM categoria WHERE id_categoria = %s" + (
                " AND id_persona = %s" if 'id_persona' in columns else ''
            ) + " LIMIT 1",
            (categoria_id, user_id) if 'id_persona' in columns else (categoria_id,),
        )
        if not rows:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        if 'estado' not in columns:
            return jsonify({'message': 'Estado actualizado', 'estado': True}), 200

        nuevo_estado = 0 if rows[0]['estado'] else 1
        db.execute_non_query(
            "UPDATE categoria SET estado = %s WHERE id_categoria = %s" + (
                " AND id_persona = %s" if 'id_persona' in columns else ''
            ),
            (nuevo_estado, categoria_id, user_id) if 'id_persona' in columns else (nuevo_estado, categoria_id),
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
        columns = _get_categoria_columns(db)
        rows = db.execute_query(
            "SELECT id_categoria FROM categoria WHERE id_categoria = %s" + (
                " AND id_persona = %s" if 'id_persona' in columns else ''
            ) + " LIMIT 1",
            (categoria_id, user_id) if 'id_persona' in columns else (categoria_id,),
        )
        if not rows:
            return jsonify({'message': 'Categoría no encontrada'}), 404

        # Verificar que no tenga subcategorías
        if 'parent_id' in columns:
            hijos = db.execute_query(
                "SELECT COUNT(*) AS total FROM categoria WHERE parent_id = %s" + (
                    " AND id_persona = %s" if 'id_persona' in columns else ''
                ),
                (categoria_id, user_id) if 'id_persona' in columns else (categoria_id,),
            )
            if hijos and hijos[0]['total'] > 0:
                return jsonify({
                    'message': 'No se puede eliminar: esta categoría tiene subcategorías. Inactívala o elimina las subcategorías primero.'
                }), 409

        db.execute_non_query(
            "DELETE FROM categoria WHERE id_categoria = %s" + (
                " AND id_persona = %s" if 'id_persona' in columns else ''
            ),
            (categoria_id, user_id) if 'id_persona' in columns else (categoria_id,),
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

