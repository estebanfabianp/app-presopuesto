"""
Script para corregir saldo_pendiente de tarjeta_diferido de tarjeta 3495 (id=32)
basado en el extracto Copia de 3495_MAY2024.xlsx
"""
import openpyxl
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

wb = openpyxl.load_workbook('Copia de 3495_MAY2024.xlsx', data_only=True)
ws = wb['PESOS']

# Mayo 2024 -> Abril 2026 = 23 meses transcurridos
MESES_DESDE_EXTRACTO = 23

diferidos = []
for row in list(ws.iter_rows(values_only=True))[1:]:
    if not any(v for v in row):
        continue
    descripcion = str(row[2] or '').strip()
    valor_original_raw = str(row[3] or '0').replace(',', '').strip()
    cargos_raw = str(row[6] or '0').replace(',', '').replace(' ', '')
    saldo_diferir_raw = str(row[7] or '0').replace(',', '').replace(' ', '')
    cuotas_raw = str(row[8] or '').strip()

    negativo = '-' in cargos_raw
    saldo_diferir = float(saldo_diferir_raw.replace('-', ''))

    if negativo or saldo_diferir == 0:
        continue  # solo diferidos

    valor_original = float(valor_original_raw.replace('-', ''))
    cuota_mes = float(cargos_raw.replace('-', ''))

    if '/' not in cuotas_raw:
        continue

    partes = cuotas_raw.split('/')
    cuota_num = int(partes[0])
    total_cuotas = int(partes[1])

    cuotas_pagadas_a_mayo = cuota_num
    cuotas_adicionales = min(MESES_DESDE_EXTRACTO, total_cuotas - cuotas_pagadas_a_mayo)
    cuotas_pagadas_total = cuotas_pagadas_a_mayo + cuotas_adicionales

    if cuotas_pagadas_total >= total_cuotas:
        saldo_actual_calc = 0.0
        estado = 'pagado'
    else:
        cuotas_restantes = total_cuotas - cuotas_pagadas_total
        saldo_actual_calc = round(cuota_mes * cuotas_restantes, 2)
        estado = 'activo'

    diferidos.append({
        'descripcion': descripcion,
        'valor_original': valor_original,
        'cuota_mensual': cuota_mes,
        'total_cuotas': total_cuotas,
        'cuota_extracto': cuota_num,
        'saldo_a_mayo2024': saldo_diferir,
        'cuotas_pagadas_actual': cuotas_pagadas_total,
        'saldo_pendiente_actual': saldo_actual_calc,
        'estado': estado,
    })

print(f"{'Descripcion':<30} {'Cuotas':>8} {'Pagadas':>8} {'CuotaMes':>12} {'SaldoActual':>14} {'Estado':>8}")
print('-' * 90)
total_pendiente = 0.0
for d in diferidos:
    print(
        f"{d['descripcion']:<30} {d['total_cuotas']:>8} {d['cuotas_pagadas_actual']:>8} "
        f"{d['cuota_mensual']:>12,.2f} {d['saldo_pendiente_actual']:>14,.2f} {d['estado']:>8}"
    )
    if d['estado'] == 'activo':
        total_pendiente += d['saldo_pendiente_actual']

print('-' * 90)
print(f"Total diferidos activos pendientes: {total_pendiente:>14,.2f}")
print()

saldo_inicial = 4876430.00
compras = 1977327.63
abonos = 3632490.00
saldo_proyectado = saldo_inicial + compras - abonos + total_pendiente
print(f"Proyeccion saldo_actual tarjeta 3495:")
print(f"  saldo_inicial:  {saldo_inicial:>14,.2f}")
print(f"  + compras:      {compras:>14,.2f}")
print(f"  - abonos:       {abonos:>14,.2f}")
print(f"  + diferidos:    {total_pendiente:>14,.2f}")
print(f"  = saldo_actual: {saldo_proyectado:>14,.2f}")
