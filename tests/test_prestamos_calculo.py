from datetime import date
from decimal import Decimal

import pytest

from src.business.services.prestamos import calcular_plan, fecha_cuota


@pytest.mark.parametrize('metodo', ['frances', 'capital_fijo'])
def test_plan_sin_interes_amortiza_capital_con_redondeo(metodo):
    plan = calcular_plan('1000', '0', 3, 'mensual', metodo, date(2026, 1, 31))
    assert [cuota['fecha'] for cuota in plan] == [
        date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31),
    ]
    assert sum(cuota['capital'] for cuota in plan) == Decimal('1000.00')
    assert all(cuota['interes'] == 0 for cuota in plan)
    assert plan[-1]['saldo'] == 0


def test_frances_interes_anual_equivalente_y_redondeo():
    plan = calcular_plan('1000', '12', 12, 'mensual', 'frances', date(2026, 1, 1))
    assert plan[0]['interes'] == Decimal('9.49')
    assert plan[0]['capital'] == Decimal('79.07')
    assert plan[-1]['saldo'] == 0
    assert sum(cuota['capital'] for cuota in plan) == Decimal('1000.00')


def test_capital_fijo_cuotas_decrecientes():
    plan = calcular_plan('1200', '12', 12, 'mensual', 'capital_fijo', date(2026, 1, 1))
    assert all(cuota['capital'] == Decimal('100.00') for cuota in plan)
    assert plan[0]['interes'] > plan[-1]['interes']
    assert plan[-1]['saldo'] == 0


def test_vencimientos_quincenales_y_febrero_bisiesto():
    primera = date(2028, 1, 31)
    assert [fecha_cuota(primera, 'quincenal', i) for i in range(4)] == [
        date(2028, 1, 31), date(2028, 2, 15),
        date(2028, 2, 29), date(2028, 3, 15),
    ]


@pytest.mark.parametrize(('frecuencia', 'ultima'), [
    ('semanal', date(2026, 1, 15)),
    ('mensual', date(2026, 3, 1)),
    ('trimestral', date(2026, 7, 1)),
    ('anual', date(2028, 1, 1)),
])
def test_frecuencias(frecuencia, ultima):
    assert fecha_cuota(date(2026, 1, 1), frecuencia, 2) == ultima


@pytest.mark.parametrize(('capital', 'tasa', 'cuotas', 'frecuencia', 'metodo', 'fecha'), [
    ('0', '1', 12, 'mensual', 'frances', date(2026, 1, 1)),
    ('1000', '-1', 12, 'mensual', 'frances', date(2026, 1, 1)),
    ('1000', 'NaN', 12, 'mensual', 'frances', date(2026, 1, 1)),
    ('1000', '1', 0, 'mensual', 'frances', date(2026, 1, 1)),
    ('1000', '1', 12, 'diario', 'frances', date(2026, 1, 1)),
    ('1000', '1', 12, 'mensual', 'otro', date(2026, 1, 1)),
    ('1000', '1', 12, 'quincenal', 'frances', date(2026, 1, 1)),
])
def test_rechaza_datos_invalidos(capital, tasa, cuotas, frecuencia, metodo, fecha):
    with pytest.raises(ValueError):
        calcular_plan(capital, tasa, cuotas, frecuencia, metodo, fecha)
