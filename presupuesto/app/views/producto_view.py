"""
Vistas Flask para operaciones sobre productos.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar productos.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todos los productos.
    Returns:
        JSON: Lista de productos.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener un producto por su ID.
    Args:
        id (int): Identificador del producto.
    Returns:
        JSON: Datos del producto.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear un nuevo producto.
    Returns:
        JSON: Datos del producto creado.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar un producto existente.
    Args:
        id (int): Identificador del producto.
    Returns:
        JSON: Datos del producto actualizado.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar un producto por su ID.
    Args:
        id (int): Identificador del producto.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
