"""Cálculo de planes de amortización para préstamos personales."""

import calendar
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


CENTAVO = Decimal('0.01')
PERIODOS_ANUALES = {
    'semanal': 52,
    'quincenal': 24,
    'mensual': 12,
    'trimestral': 4,
    'anual': 1,
}


def dinero(valor):
    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError('El importe no es válido') from None
    if not resultado.is_finite() or not Decimal('0') <= resultado <= Decimal('9999999999999.99'):
        raise ValueError('El importe debe ser un número no negativo dentro del límite permitido')
    if resultado != resultado.quantize(CENTAVO, rounding=ROUND_HALF_UP):
        raise ValueError('Los importes admiten hasta dos decimales')
    return resultado.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def fecha_cuota(primera_fecha, frecuencia, indice):
    if frecuencia not in PERIODOS_ANUALES or indice < 0:
        raise ValueError('Frecuencia o número de cuota inválido')
    if frecuencia == 'semanal':
        return primera_fecha + timedelta(days=7 * indice)
    if frecuencia == 'quincenal':
        ultimo = calendar.monthrange(primera_fecha.year, primera_fecha.month)[1]
        if primera_fecha.day not in (15, ultimo):
            raise ValueError('La primera cuota quincenal debe vencer el día 15 o el último día del mes')
        pos = primera_fecha.year * 12 + primera_fecha.month - 1
        pos_cuota = (0 if primera_fecha.day == 15 else 1) + indice
        year, month = divmod(pos + pos_cuota // 2, 12)
        mes = month + 1
        dia = 15 if pos_cuota % 2 == 0 else calendar.monthrange(year, mes)[1]
        return date(year, mes, dia)
    meses = {'mensual': 1, 'trimestral': 3, 'anual': 12}[frecuencia]
    year, month = divmod(primera_fecha.year * 12 + primera_fecha.month - 1 + meses * indice, 12)
    mes = month + 1
    return date(year, mes, min(primera_fecha.day, calendar.monthrange(year, mes)[1]))


def calcular_plan(capital, tasa_efectiva_anual, numero_cuotas, frecuencia, metodo, primera_fecha):
    capital = dinero(capital)
    if capital <= 0 or capital > Decimal('9999999999999.99'):
        raise ValueError('El capital debe ser mayor que cero y no superar el límite permitido')
    try:
        tasa = Decimal(str(tasa_efectiva_anual))
    except (InvalidOperation, ValueError):
        raise ValueError('La tasa efectiva anual no es válida') from None
    if not tasa.is_finite() or not Decimal('0') <= tasa <= Decimal('1000'):
        raise ValueError('La tasa efectiva anual debe estar entre 0 y 1000 por ciento')
    if isinstance(numero_cuotas, bool) or not isinstance(numero_cuotas, int) or not 1 <= numero_cuotas <= 360:
        raise ValueError('El número de cuotas debe estar entre 1 y 360')
    if frecuencia not in PERIODOS_ANUALES or metodo not in ('frances', 'capital_fijo'):
        raise ValueError('Frecuencia o método de amortización inválido')
    if not isinstance(primera_fecha, date):
        raise ValueError('La primera fecha de vencimiento no es válida')

    with localcontext() as ctx:
        ctx.prec = 40
        interes_periodico = (Decimal(1) + tasa / 100) ** (
            Decimal(1) / PERIODOS_ANUALES[frecuencia]
        ) - Decimal(1)
        if interes_periodico:
            cuota_fija = capital * interes_periodico / (
                Decimal(1) - (Decimal(1) + interes_periodico) ** -numero_cuotas
            )
        else:
            cuota_fija = capital / numero_cuotas
        abono_fijo = capital / numero_cuotas
        saldo = capital
        cuotas = []
        for indice in range(numero_cuotas):
            interes = (saldo * interes_periodico).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            if indice == numero_cuotas - 1:
                abono = saldo
            elif metodo == 'capital_fijo':
                abono = abono_fijo.quantize(CENTAVO, rounding=ROUND_HALF_UP)
            else:
                abono = (cuota_fija - interes).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            abono = min(saldo, max(Decimal('0'), abono))
            saldo -= abono
            cuotas.append({
                'numero': indice + 1,
                'fecha': fecha_cuota(primera_fecha, frecuencia, indice),
                'capital': abono,
                'interes': interes,
                'saldo': saldo,
            })
        return cuotas
