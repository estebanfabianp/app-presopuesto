from presupuesto.models.models import PersonaModel
from views.persona_view import PersonaView

class PersonaController:
    @staticmethod
    def listar_personas():
        personas = PersonaModel.obtener_todos()
        PersonaView.mostrar_personas(personas)

    @staticmethod
    def agregar_persona(nombre):
        PersonaModel.crear(nombre)
        PersonaView.mostrar_mensaje("Persona agregada correctamente ✅")
