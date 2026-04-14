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


@bp.route('/register', methods=['POST'])
def register():
    """
    Registro de usuario nuevo.

    POST /api/auth/register
    JSON: {"nombre": "...", "email": "...", "password": "...", "telefono": "..."}
    """
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = (data.get('password') or '').strip() or '123456'
        telefono = (data.get('telefono') or '').strip() or None

        if not nombre or not email:
            return jsonify({'message': 'Debes enviar nombre y email'}), 400

        if len(password) < 6:
            return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400

        persona_model = PersonaModel()

        existing = persona_model.db.execute_query(
            "SELECT id_persona FROM persona WHERE correo_electronico = %s LIMIT 1",
            (email,),
        )
        if existing:
            return jsonify({'message': 'Ya existe un usuario con ese correo'}), 409

        user = persona_model.add_persona(
            nombre=nombre,
            email=email,
            telefono=telefono,
            clave=password,
            estado_id=1,
        )
        if not user:
            return jsonify({'message': 'No fue posible crear el usuario'}), 500

        user_id = user.get('id_persona')
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={
                'email': user.get('correo_electronico'),
                'nombre': user.get('nombre'),
            },
        )

        return jsonify({
            'message': 'Usuario creado correctamente',
            'token': access_token,
            'user': _serialize_user(user),
        }), 201

    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if 'persona_model' in locals():
            persona_model.close_connection()


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
            'fecha_creacion': user.get('fecha_creacion').isoformat() if user.get('fecha_creacion') else None,
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


@bp.route('/change-password', methods=['PUT'])
def change_password():
    """
    Cambiar contraseña del usuario autenticado

    PUT /api/auth/change-password
    Headers: Authorization: Bearer <token>
    JSON: {"current_password": "...", "new_password": "..."}
    """
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        user_id = int(identity) if str(identity).isdigit() else None
        if not user_id:
            return jsonify({'message': 'Token inválido'}), 401

        data = request.get_json()
        current_password = (data or {}).get('current_password', '').strip()
        new_password = (data or {}).get('new_password', '').strip()

        if not current_password or not new_password:
            return jsonify({'message': 'Debes proporcionar la contraseña actual y la nueva'}), 400

        if len(new_password) < 6:
            return jsonify({'message': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400

        persona_model = PersonaModel()
        success, reason = persona_model.change_password(user_id, current_password, new_password)

        if not success:
            if reason == 'wrong_password':
                return jsonify({'message': 'La contraseña actual es incorrecta'}), 400
            return jsonify({'message': 'Usuario no encontrado'}), 404

        return jsonify({'message': 'Contraseña actualizada correctamente'}), 200

    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if 'persona_model' in locals():
            persona_model.close_connection()


@bp.route('/update-profile', methods=['PUT'])
def update_profile():
    """
    Actualizar nombre del usuario autenticado

    PUT /api/auth/update-profile
    Headers: Authorization: Bearer <token>
    JSON: {"nombre": "Nuevo Nombre"}
    """
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        user_id = int(identity) if str(identity).isdigit() else None
        if not user_id:
            return jsonify({'message': 'Token inválido'}), 401

        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return jsonify({'message': 'El nombre no puede estar vacío'}), 400
        if len(nombre) > 100:
            return jsonify({'message': 'El nombre no puede superar 100 caracteres'}), 400

        from src.database.db_connector import DatabaseConnector
        db = DatabaseConnector()
        try:
            db.execute_non_query(
                "UPDATE persona SET nombre = %s WHERE id_persona = %s",
                (nombre, user_id),
            )
        finally:
            db.close()

        return jsonify({'message': 'Perfil actualizado', 'nombre': nombre}), 200

    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Recuperar contraseña por correo electrónico.

    POST /api/auth/reset-password
    JSON: {"email": "user@example.com", "new_password": "..."}
    """
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        new_password = (data.get('new_password') or '').strip()

        if not email or not new_password:
            return jsonify({'message': 'Debes enviar email y nueva contraseña'}), 400

        if len(new_password) < 6:
            return jsonify({'message': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400

        persona_model = PersonaModel()
        success, reason = persona_model.reset_password_by_email(email, new_password)
        if not success:
            if reason == 'not_found':
                return jsonify({'message': 'No existe un usuario con ese correo'}), 404
            return jsonify({'message': 'No fue posible actualizar la contraseña'}), 400

        return jsonify({'message': 'Contraseña actualizada correctamente. Ya puedes iniciar sesión.'}), 200

    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if 'persona_model' in locals():
            persona_model.close_connection()
