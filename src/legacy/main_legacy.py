try:
    from .views.user_view import user_app
except ImportError:
    # Fallback if relative import fails or module doesn't exist
    try:
        from views.user_view import user_app
    except ImportError:
        print("Error: No se pudo importar user_view. Módulo no encontrado.")
        user_app = None

def main():
    print("Iniciando sistema")
    if user_app:
        user_app()
    else:
        print("Error: user_app no está disponible")

if __name__ == "__main__":
    main()
