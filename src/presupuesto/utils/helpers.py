from datetime import datetime
import locale

# Formatear monto en formato moneda
def formato_moneda(valor: float, moneda: str = "COP") -> str:
    return f"{moneda} {valor:,.2f}"

# Convertir string a fecha segura
def str_a_fecha(fecha_str: str, formato: str = "%Y-%m-%d") -> datetime:
    try:
        return datetime.strptime(fecha_str, formato)
    except ValueError:
        raise ValueError(f"Formato de fecha inválido: {fecha_str}. Esperado: {formato}")

# Calcular porcentaje con validación
def calcular_porcentaje(parte: float, total: float) -> float:
    if total == 0:
        return 0.0
    return (parte / total) * 100

# Normalizar descripción de movimientos (ej: quitar espacios, minúsculas)
def normalizar_texto(texto: str) -> str:
    return texto.strip().lower()

# Generar timestamp actual en string
def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
