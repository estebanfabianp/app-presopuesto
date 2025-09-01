from controllers.persona_controller import PersonaController

def main():
    while True:
        print("\n--- Menú ---")
        print("1. Listar personas")
        print("2. Agregar persona")
        print("3. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            PersonaController.listar_personas()
        elif opcion == "2":
            nombre = input("Ingrese el nombre de la persona: ")
            PersonaController.agregar_persona(nombre)
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()
