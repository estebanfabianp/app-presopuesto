"""
Vistas Flask para operaciones sobre presupuestos.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar presupuestos.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todos los presupuestos.
    Returns:
        JSON: Lista de presupuestos.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener un presupuesto por su ID.
    Args:
        id (int): Identificador del presupuesto.
    Returns:
        JSON: Datos del presupuesto.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear un nuevo presupuesto.
    Returns:
        JSON: Datos del presupuesto creado.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar un presupuesto existente.
    Args:
        id (int): Identificador del presupuesto.
    Returns:
        JSON: Datos del presupuesto actualizado.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar un presupuesto por su ID.
    Args:
        id (int): Identificador del presupuesto.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
