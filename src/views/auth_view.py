from flask import Blueprint, request, jsonify
from src.controllers.auth_controller import registrar_usuario, autenticar_usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    Recibe nombre, correo y contraseña en formato JSON.
    Returns:
        JSON: Mensaje de éxito o error.
    """
    data = request.json
    usuario, error = registrar_usuario(data["nombre"], data["correo"], data["password"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"mensaje": "Usuario registrado con éxito", "id": usuario.id})

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Endpoint para autenticar un usuario.
    Recibe correo y contraseña en formato JSON.
    Returns:
        JSON: Mensaje de bienvenida o error de autenticación.
    """
    data = request.json
    usuario = autenticar_usuario(data["correo"], data["password"])
    if usuario:
        return jsonify({"mensaje": f"Bienvenido {usuario.nombre}"})
    return jsonify({"error": "Credenciales inválidas"}), 401
