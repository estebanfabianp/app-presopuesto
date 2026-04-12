"""
Rutas de autenticación para la aplicación Flask
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity, get_jwt
import logging

from src.models.persona_model import PersonaModel

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _serialize_user(user_data):
    return {
        'id': user_data.get('id_persona'),
        'email': user_data.get('correo_electronico'),
        'nombre': user_data.get('nombre') or user_data.get('nombres') or 'Usuario',
        'username': user_data.get('usuario'),
    }


@bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login
    
    POST /api/auth/login
    JSON: {"email": "user@example.com", "password": "password"}
    """
    try:
        data = request.get_json()
        
        # Validar entrada
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email y contraseña requeridos'}), 400

        persona_model = PersonaModel()
        user = persona_model.login(data['email'], data['password'])
        if not user:
            return jsonify({'message': 'Credenciales inválidas'}), 401

        user_id = user.get('id_persona')
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={
                'email': user.get('correo_electronico'),
                'nombre': user.get('nombre'),
            },
        )

        return jsonify({
            'token': access_token,
            'user': _serialize_user(user)
        }), 200
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if 'persona_model' in locals():
            persona_model.close_connection()


@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Obtener usuario actual autenticado
    
    GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity) if str(identity).isdigit() else 1

        persona_model = PersonaModel()
        user = persona_model.get_persona_by_id(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'id': user_id,
            'email': user.get('correo_electronico') or claims.get('email'),
            'nombre': user.get('nombre') or claims.get('nombre') or 'Usuario',
            'username': user.get('usuario'),
            'authenticated': True
        }), 200
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'message': 'Unauthorized'}), 401
    finally:
        if 'persona_model' in locals():
            persona_model.close_connection()


@bp.route('/logout', methods=['POST'])
def logout():
    """
    Cerrar sesión del usuario
    
    POST /api/auth/logout
    """
    try:
        return jsonify({'message': 'Logout exitoso'}), 200
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Error en logout'}), 500
