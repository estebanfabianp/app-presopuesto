"""
Vistas Flask para operaciones sobre tarjetas.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar tarjetas.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todas las tarjetas.
    Returns:
        JSON: Lista de tarjetas.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener una tarjeta por su ID.
    Args:
        id (int): Identificador de la tarjeta.
    Returns:
        JSON: Datos de la tarjeta.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear una nueva tarjeta.
    Returns:
        JSON: Datos de la tarjeta creada.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar una tarjeta existente.
    Args:
        id (int): Identificador de la tarjeta.
    Returns:
        JSON: Datos de la tarjeta actualizada.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar una tarjeta por su ID.
    Args:
        id (int): Identificador de la tarjeta.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
