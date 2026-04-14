"""API HTML/Flask para Optimización de Categorías."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.business.services.optimizacion_categorias import OptimizacionCategoriasService
from src.database.db_connector import DatabaseConnector

bp = Blueprint('optimizacion_categorias', __name__, url_prefix='/api/optimizacion-categorias')
logger = logging.getLogger(__name__)


def _get_user_id() -> int:
    identity = get_jwt_identity() or {}
    if isinstance(identity, dict):
        return int(identity.get('user_id', 1))
    if str(identity).isdigit():
        return int(identity)
    return 1


def _service():
    db = DatabaseConnector()
    return db, OptimizacionCategoriasService(db)


@bp.route('/resumen', methods=['GET'])
def resumen():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        return jsonify(svc.get_stats(user_id)), 200
    except Exception as exc:
        logger.error('Error cargando resumen de optimización: %s', exc)
        return jsonify({'message': 'Error al cargar resumen'}), 500
    finally:
        db.close()


@bp.route('/reglas', methods=['GET'])
def reglas():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        return jsonify({'reglas': svc.get_reglas(user_id)}), 200
    except Exception as exc:
        logger.error('Error cargando reglas: %s', exc)
        return jsonify({'message': 'Error al cargar reglas'}), 500
    finally:
        db.close()


@bp.route('/conflictos', methods=['GET'])
def conflictos():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        return jsonify({'conflictos': svc.get_conflictos(user_id)}), 200
    except Exception as exc:
        logger.error('Error cargando conflictos: %s', exc)
        return jsonify({'message': 'Error al cargar conflictos'}), 500
    finally:
        db.close()


@bp.route('/pendientes', methods=['GET'])
def pendientes():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        limit = min(int(request.args.get('limit', 200)), 1000)
        return jsonify({'movimientos': svc.get_sin_categoria(user_id, limit=limit)}), 200
    except Exception as exc:
        logger.error('Error cargando pendientes sin categoría: %s', exc)
        return jsonify({'message': 'Error al cargar pendientes'}), 500
    finally:
        db.close()


@bp.route('/catalogos', methods=['GET'])
def catalogos():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        return jsonify({'categorias': svc.get_categorias(user_id)}), 200
    except Exception as exc:
        logger.error('Error cargando catálogos de optimización: %s', exc)
        return jsonify({'message': 'Error al cargar catálogos'}), 500
    finally:
        db.close()


@bp.route('/aplicar', methods=['POST'])
def aplicar():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        actualizados = svc.aplicar_reglas(user_id)
        return jsonify({'message': 'Reglas aplicadas', 'actualizados': actualizados}), 200
    except Exception as exc:
        logger.error('Error aplicando reglas: %s', exc)
        return jsonify({'message': 'Error al aplicar reglas'}), 500
    finally:
        db.close()


@bp.route('/reglas/confirmar', methods=['POST'])
def confirmar_regla():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        concepto = (data.get('concepto') or '').strip()
        id_categoria = data.get('id_categoria')
        if not concepto or not id_categoria:
            return jsonify({'message': 'concepto e id_categoria son obligatorios'}), 400
        ok = svc.confirmar_regla(concepto, int(id_categoria), user_id)
        if not ok:
            return jsonify({'message': 'No se pudo guardar la regla'}), 500
        return jsonify({'message': 'Regla confirmada'}), 200
    except Exception as exc:
        logger.error('Error confirmando regla: %s', exc)
        return jsonify({'message': 'Error al confirmar regla'}), 500
    finally:
        db.close()


@bp.route('/reglas/ignorar', methods=['POST'])
def ignorar_regla():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        concepto = (data.get('concepto') or '').strip()
        if not concepto:
            return jsonify({'message': 'concepto es obligatorio'}), 400
        ok = svc.ignorar_concepto(concepto, user_id)
        if not ok:
            return jsonify({'message': 'No se pudo guardar la regla de ignorar'}), 500
        return jsonify({'message': 'Concepto ignorado'}), 200
    except Exception as exc:
        logger.error('Error ignorando concepto: %s', exc)
        return jsonify({'message': 'Error al ignorar concepto'}), 500
    finally:
        db.close()


@bp.route('/reglas', methods=['DELETE'])
def limpiar_regla():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        concepto = (request.args.get('concepto') or '').strip()
        if not concepto:
            return jsonify({'message': 'concepto es obligatorio'}), 400
        ok = svc.limpiar_regla(concepto, user_id)
        if not ok:
            return jsonify({'message': 'No se encontró regla para limpiar'}), 404
        return jsonify({'message': 'Regla eliminada'}), 200
    except Exception as exc:
        logger.error('Error limpiando regla: %s', exc)
        return jsonify({'message': 'Error al limpiar regla'}), 500
    finally:
        db.close()


@bp.route('/movimientos/asignar', methods=['POST'])
def asignar_movimiento():
    verify_jwt_in_request()
    db, svc = _service()
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}
        id_movimiento_tarjeta = data.get('id_movimiento_tarjeta')
        id_categoria = data.get('id_categoria')
        if not id_movimiento_tarjeta or not id_categoria:
            return jsonify({'message': 'id_movimiento_tarjeta e id_categoria son obligatorios'}), 400
        ok = svc.asignar_categoria_movimiento(int(id_movimiento_tarjeta), int(id_categoria), user_id)
        if not ok:
            return jsonify({'message': 'No se pudo asignar la categoría'}), 500
        return jsonify({'message': 'Categoría asignada'}), 200
    except Exception as exc:
        logger.error('Error asignando categoría a movimiento: %s', exc)
        return jsonify({'message': 'Error al asignar categoría'}), 500
    finally:
        db.close()
