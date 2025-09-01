"""
Vistas Flask para operaciones sobre personas.
Incluye endpoints para listar, obtener, crear, actualizar y eliminar personas.
"""

from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    """
    Endpoint para listar todas las personas.
    Returns:
        JSON: Lista de personas.
    """
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    """
    Endpoint para obtener una persona por su ID.
    Args:
        id (int): Identificador de la persona.
    Returns:
        JSON: Datos de la persona.
    """
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    """
    Endpoint para crear una nueva persona.
    Returns:
        JSON: Datos de la persona creada.
    """
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    """
    Endpoint para actualizar una persona existente.
    Args:
        id (int): Identificador de la persona.
    Returns:
        JSON: Datos de la persona actualizada.
    """
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    """
    Endpoint para eliminar una persona por su ID.
    Args:
        id (int): Identificador de la persona.
    Returns:
        JSON: Mensaje de confirmación.
    """
    return jsonify({'message': 'Eliminado correctamente'})
