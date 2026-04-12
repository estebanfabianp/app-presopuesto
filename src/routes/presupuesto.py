"""Rutas API de Presupuesto conectadas a base de datos MySQL."""

from datetime import date, timedelta
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.database.db_connector import DatabaseConnector

bp = Blueprint('presupuesto', __name__, url_prefix='/api/presupuesto')

logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


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


def _resolve_categoria_id(db: DatabaseConnector, categoria_nombre: str):
    if not categoria_nombre:
        return None
    rows = db.execute_query(
        "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
        (categoria_nombre,),
    )
    if rows:
        return rows[0]['id_categoria']
    created = db.execute_non_query(
        "INSERT INTO categoria (nombre) VALUES (%s)",
        (categoria_nombre,),
    )
    return created


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

        response = []
        for row in rows:
            response.append({
                'id': row['id_presupuesto'],
                'nombre': row.get('nombre') or f"Presupuesto {row['id_presupuesto']}",
                'descripcion': row.get('descripcion'),
                'categoria': row.get('categorias') or 'General',
                'monto': float(row.get('monto_total') or 0),
                'periodo': _infer_periodo(row.get('fecha_inicio'), row.get('fecha_fin')),
                'fecha_inicio': row.get('fecha_inicio').isoformat() if row.get('fecha_inicio') else None,
                'fecha_fin': row.get('fecha_fin').isoformat() if row.get('fecha_fin') else None,
                'activo': True,
            })
        return jsonify(response), 200
    except Exception as e:
        logger.error("Error listando presupuestos: %s", e)
        return jsonify({'message': 'Error al listar presupuestos'}), 500
    finally:
        db.close()


@bp.route('/<int:presupuesto_id>', methods=['GET'])
def get_presupuesto(presupuesto_id):
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
            WHERE p.id_presupuesto = %s AND p.id_persona = %s
            GROUP BY p.id_presupuesto, p.nombre, p.descripcion, p.monto_total, p.fecha_inicio, p.fecha_fin
            LIMIT 1
            """,
            (presupuesto_id, user_id),
        )
        if not rows:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

        row = rows[0]
        return jsonify({
            'id': row['id_presupuesto'],
            'nombre': row.get('nombre') or f"Presupuesto {row['id_presupuesto']}",
            'descripcion': row.get('descripcion'),
            'categoria': row.get('categorias') or 'General',
            'monto': float(row.get('monto_total') or 0),
            'periodo': _infer_periodo(row.get('fecha_inicio'), row.get('fecha_fin')),
            'fecha_inicio': row.get('fecha_inicio').isoformat() if row.get('fecha_inicio') else None,
            'fecha_fin': row.get('fecha_fin').isoformat() if row.get('fecha_fin') else None,
            'activo': True,
        }), 200
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
        periodo = (payload.get('periodo') or 'mensual').lower()

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

        categoria_nombre = payload.get('categoria')
        categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
        if categoria_id:
            db.execute_non_query(
                "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                (presupuesto_id, categoria_id),
            )

        return get_presupuesto(presupuesto_id)
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
        existing = db.execute_query(
            "SELECT id_presupuesto FROM presupuesto WHERE id_presupuesto = %s AND id_persona = %s LIMIT 1",
            (presupuesto_id, user_id),
        )
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

        categoria_nombre = payload.get('categoria')
        categoria_id = payload.get('id_categoria') or _resolve_categoria_id(db, categoria_nombre)
        if categoria_id:
            db.execute_non_query("DELETE FROM presupuesto_categoria WHERE id_presupuesto = %s", (presupuesto_id,))
            db.execute_non_query(
                "INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (%s, %s)",
                (presupuesto_id, categoria_id),
            )

        return get_presupuesto(presupuesto_id)
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
        exists = db.execute_query(
            "SELECT id_presupuesto FROM presupuesto WHERE id_presupuesto = %s AND id_persona = %s LIMIT 1",
            (presupuesto_id, user_id),
        )
        if not exists:
            return jsonify({'message': 'Presupuesto no encontrado'}), 404

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
