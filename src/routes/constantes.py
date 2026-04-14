"""Rutas API de Constantes - CRUD completo sobre la tabla constantes."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('constantes', __name__, url_prefix='/api/constantes')
logger = logging.getLogger(__name__)

TIPOS_DATO = ('STRING', 'INTEGER', 'DECIMAL', 'BOOLEAN', 'JSON', 'DATE')


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


# ---------------------------------------------------------------------------
# GET /api/constantes  — listar (con filtro opcional por categoria y estado)
# ---------------------------------------------------------------------------
@bp.route('', methods=['GET'])
def list_constantes():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        categoria = request.args.get('categoria', '').strip()
        solo_activas = request.args.get('activas', 'true').lower() == 'true'

        conditions = ['id_persona = %s']
        params = [user_id]

        if categoria:
            conditions.append('categoria = %s')
            params.append(categoria)
        if solo_activas:
            conditions.append('estado = 1')

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        query = (
            "SELECT id_constante, categoria, nombre, valor, tipo_dato, "
            "descripcion, es_editable, estado, fecha_actualizacion "
            "FROM constantes " + where + " ORDER BY categoria, nombre"
        )
        rows = db.execute_query(
            query,
            tuple(params) if params else None,
        )

        result = []
        for r in (rows or []):
            result.append({
                'id': r['id_constante'],
                'categoria': r['categoria'],
                'nombre': r['nombre'],
                'valor': r['valor'],
                'tipo_dato': r['tipo_dato'],
                'descripcion': r.get('descripcion') or '',
                'es_editable': bool(r['es_editable']),
                'estado': bool(r['estado']),
                'fecha_actualizacion': (
                    r['fecha_actualizacion'].isoformat()
                    if r.get('fecha_actualizacion') else None
                ),
            })

        # Categorías disponibles para filtros
        cats = db.execute_query(
            "SELECT DISTINCT categoria FROM constantes WHERE id_persona = %s AND estado = 1 ORDER BY categoria",
            (user_id,),
        )
        categorias = [c['categoria'] for c in (cats or [])]

        return jsonify({'constantes': result, 'categorias': categorias}), 200
    except Exception as e:
        logger.error('Error listando constantes: %s', e)
        return jsonify({'message': 'Error al listar constantes'}), 500
    finally:
        db.close()


# ---------------------------------------------------------------------------
# POST /api/constantes  — crear
# ---------------------------------------------------------------------------
@bp.route('', methods=['POST'])
def create_constante():
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        categoria = (data.get('categoria') or '').strip().upper()
        nombre = (data.get('nombre') or '').strip().upper()
        valor = str(data.get('valor') or '').strip()
        tipo_dato = (data.get('tipo_dato') or 'STRING').strip().upper()
        descripcion = (data.get('descripcion') or '').strip()
        es_editable = int(bool(data.get('es_editable', True)))

        if not categoria or not nombre or not valor:
            return jsonify({'message': 'categoria, nombre y valor son obligatorios'}), 400
        if tipo_dato not in TIPOS_DATO:
            return jsonify({'message': f'tipo_dato debe ser uno de: {", ".join(TIPOS_DATO)}'}), 400

        db.execute_non_query(
            """
            INSERT INTO constantes (id_persona, categoria, nombre, valor, tipo_dato, descripcion, es_editable, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (user_id, categoria, nombre, valor, tipo_dato, descripcion, es_editable),
        )
        rows = db.execute_query(
            'SELECT id_constante FROM constantes WHERE id_persona = %s AND categoria = %s AND nombre = %s LIMIT 1',
            (user_id, categoria, nombre),
        )
        new_id = rows[0]['id_constante'] if rows else None
        return jsonify({'message': 'Constante creada', 'id': new_id}), 201
    except Exception as e:
        msg = str(e)
        if 'Duplicate entry' in msg:
            return jsonify({'message': f'Ya existe una constante con el nombre "{nombre}"'}), 409
        logger.error('Error creando constante: %s', e)
        return jsonify({'message': 'Error al crear constante'}), 500
    finally:
        db.close()


# ---------------------------------------------------------------------------
# PUT /api/constantes/<id>  — actualizar
# ---------------------------------------------------------------------------
@bp.route('/<int:constante_id>', methods=['PUT'])
def update_constante(constante_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        # Verificar que existe y es editable
        rows = db.execute_query(
            'SELECT es_editable FROM constantes WHERE id_constante = %s AND id_persona = %s AND estado = 1 LIMIT 1',
            (constante_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Constante no encontrada'}), 404
        if not rows[0]['es_editable']:
            return jsonify({'message': 'Esta constante no es editable'}), 403

        data = request.get_json() or {}
        valor = str(data.get('valor') or '').strip()
        descripcion = (data.get('descripcion') or '').strip()
        categoria = (data.get('categoria') or '').strip().upper()
        tipo_dato = (data.get('tipo_dato') or 'STRING').strip().upper()

        if not valor:
            return jsonify({'message': 'El valor no puede estar vacío'}), 400
        if tipo_dato not in TIPOS_DATO:
            return jsonify({'message': f'tipo_dato debe ser uno de: {", ".join(TIPOS_DATO)}'}), 400

        db.execute_non_query(
            """
            UPDATE constantes
            SET valor = %s, descripcion = %s, categoria = %s, tipo_dato = %s
            WHERE id_constante = %s AND id_persona = %s
            """,
            (valor, descripcion, categoria, tipo_dato, constante_id, user_id),
        )
        return jsonify({'message': 'Constante actualizada'}), 200
    except Exception as e:
        logger.error('Error actualizando constante %s: %s', constante_id, e)
        return jsonify({'message': 'Error al actualizar constante'}), 500
    finally:
        db.close()


# ---------------------------------------------------------------------------
# DELETE /api/constantes/<id>  — baja lógica (estado = 0)
# ---------------------------------------------------------------------------
@bp.route('/<int:constante_id>', methods=['DELETE'])
def delete_constante(constante_id):
    verify_jwt_in_request()
    db = DatabaseConnector()
    try:
        user_id = _get_user_id()
        rows = db.execute_query(
            'SELECT es_editable FROM constantes WHERE id_constante = %s AND id_persona = %s AND estado = 1 LIMIT 1',
            (constante_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Constante no encontrada'}), 404
        if not rows[0]['es_editable']:
            return jsonify({'message': 'Esta constante del sistema no se puede eliminar'}), 403

        db.execute_non_query(
            'UPDATE constantes SET estado = 0 WHERE id_constante = %s AND id_persona = %s',
            (constante_id, user_id),
        )
        return jsonify({'message': 'Constante eliminada'}), 200
    except Exception as e:
        logger.error('Error eliminando constante %s: %s', constante_id, e)
        return jsonify({'message': 'Error al eliminar constante'}), 500
    finally:
        db.close()
