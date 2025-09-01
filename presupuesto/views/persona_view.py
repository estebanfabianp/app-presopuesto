class PersonaView:
    @staticmethod
    def mostrar_personas(personas):
        print("📋 Lista de Personas:")
        for persona in personas:
            print(f"- {persona['idpersona']}: {persona['nombre']}")

    @staticmethod
    def mostrar_mensaje(mensaje):
        print(mensaje)
