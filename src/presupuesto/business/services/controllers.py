from flask import Blueprint, request, jsonify
from presupuesto.models.models import PersonaModel
from views.persona_view import PersonaView

services_bp = Blueprint('services', __name__)

@services_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "Servicio activo"})

@services_bp.route('/procesar', methods=['POST'])
def procesar():
    data = request.get_json()
    # Aquí iría la lógica de negocio principal
    resultado = {"procesado": True, "input": data}
    return jsonify(resultado)

class PersonaController:
    @staticmethod
    def listar_personas():
        personas = PersonaModel.obtener_todos()
        PersonaView.mostrar_personas(personas)

    @staticmethod
    def agregar_persona(nombre):
        PersonaModel.crear(nombre)
        PersonaView.mostrar_mensaje("Persona agregada correctamente ✅")
