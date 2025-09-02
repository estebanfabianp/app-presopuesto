"""
Vistas Flask para operaciones sobre préstamos.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar préstamos.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todos los préstamos.
    Returns:
        JSON: Lista de préstamos.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener un préstamo por su ID.
    Args:
        id (int): Identificador del préstamo.
    Returns:
        JSON: Datos del préstamo.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear un nuevo préstamo.
    Returns:
        JSON: Datos del préstamo creado.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar un préstamo existente.
    Args:
        id (int): Identificador del préstamo.
    Returns:
        JSON: Datos del préstamo actualizado.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar un préstamo por su ID.
    Args:
        id (int): Identificador del préstamo.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
