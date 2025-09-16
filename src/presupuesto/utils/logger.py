import logging
import os

# Crear carpeta de logs si no existe
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,  # Nivel: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),   # Guardar en archivo
        logging.StreamHandler()                # Mostrar en consola
    ]
)

# Obtener el logger
logger = logging.getLogger("app-presupuesto")
