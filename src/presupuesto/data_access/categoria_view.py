"""
Vistas Flask para operaciones sobre categorías.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar categorías.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todas las categorías.
    Returns:
        JSON: Lista de categorías.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener una categoría por su ID.
    Args:
        id (int): Identificador de la categoría.
    Returns:
        JSON: Datos de la categoría.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear una nueva categoría.
    Returns:
        JSON: Datos de la categoría creada.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar una categoría existente.
    Args:
        id (int): Identificador de la categoría.
    Returns:
        JSON: Datos de la categoría actualizada.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar una categoría por su ID.
    Args:
        id (int): Identificador de la categoría.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
