from flask import Blueprint, jsonify, request

bp = Blueprint('generic', __name__)

@bp.route('/', methods=['GET'])
def listar():
    return jsonify([])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    return jsonify({})

@bp.route('/', methods=['POST'])
def crear():
    data = request.get_json()
    return jsonify(data), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    data = request.get_json()
    return jsonify(data)

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    return jsonify({'message': 'Eliminado correctamente'})
