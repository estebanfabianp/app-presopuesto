from decimal import Decimal, InvalidOperation


def _to_decimal(value, default=0.0):
    try:
        if value is None or value == '':
            return Decimal(str(default))
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(str(default))


def calcular_dinero_libre_mes(
    ingresos_mensuales=0,
    gastos_fijos_mensuales=0,
    diferidos_mensuales=0,
    prestamos_mensuales=0,
    otros_compromisos=0,
):
    """Calcula el dinero libre del mes.

    Formula:
        dinero_libre = ingresos - gastos_fijos - diferidos - prestamos - otros_compromisos
    """
    ingresos = _to_decimal(ingresos_mensuales)
    gastos_fijos = _to_decimal(gastos_fijos_mensuales)
    diferidos = _to_decimal(diferidos_mensuales)
    prestamos = _to_decimal(prestamos_mensuales)
    otros = _to_decimal(otros_compromisos)

    total_compromisos = gastos_fijos + diferidos + prestamos + otros
    dinero_libre = ingresos - total_compromisos

    return {
        'ingresos_mensuales': float(ingresos),
        'gastos_fijos_mensuales': float(gastos_fijos),
        'diferidos_mensuales': float(diferidos),
        'prestamos_mensuales': float(prestamos),
        'otros_compromisos': float(otros),
        'compromiso_total': float(total_compromisos),
        'dinero_libre_mes': float(dinero_libre),
        'estado': 'positivo' if dinero_libre >= 0 else 'negativo',
        'formula': (
            f'{ingresos} - {gastos_fijos} - {diferidos} - {prestamos} - {otros} '
            f'= {dinero_libre}'
        ),
    }
