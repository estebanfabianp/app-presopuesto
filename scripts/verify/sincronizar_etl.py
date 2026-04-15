#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar movimientos con el archivo ETL Excel
"""

import sys
from pathlib import Path
import openpyxl
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

# Leer el Excel
excel_path = ROOT_DIR / "cuenta_bancaria.xlsx"

print("\n" + "=" * 100)
print("SINCRONIZACION DE MOVIMIENTOS - CUENTA BANCARIA")
print("=" * 100)

wb = openpyxl.load_workbook(excel_path)
ws = wb['Hoja1']

# Extraer todos los movimientos del Excel
excel_movimientos = []
for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    fecha, descripcion, sucursal, dcto, valor, saldo = row[:6]
    
    if fecha is None:
        break
    
    # Convertir valor de formato texto a número
    if isinstance(valor, str):
        # El formato es: -10,900.00 o 1.234.567,89
        # Primero eliminar puntos (separadores de miles), luego reemplazar coma por punto
        valor_limpio = valor.replace('.', '').replace(',', '.')
        try:
            valor_num = float(valor_limpio)
        except:
            print(f"ERROR parsing valor en row {row_idx}: '{valor}' -> '{valor_limpio}'")
            valor_num = 0.0
    else:
        valor_num = float(valor) if valor else 0.0
    
    excel_movimientos.append({
        'fecha': fecha,
        'descripcion': descripcion,
        'valor': valor_num,
        'saldo': float(saldo) if saldo else None,
        'row': row_idx
    })

print(f"\nTotal de movimientos en Excel: {len(excel_movimientos)}")

# Conectar a BD
db = DatabaseConnector()
cursor = db.conn.cursor()

# Obtener movimientos de la BD
cursor.execute("SELECT id_cuenta FROM cuenta WHERE nombre LIKE %s", ("%cuanto%",))
id_cuenta = cursor.fetchone()[0]

cursor.execute('''
    SELECT id_movimiento, fecha_creacion, monto 
    FROM movimiento 
    WHERE id_cuenta = %s
    ORDER BY fecha_creacion
''', (id_cuenta,))

bd_movimientos = cursor.fetchall()
print(f"Total de movimientos en BD: {len(bd_movimientos)}")

# Mostrar comparación
print(f"\n" + "=" * 100)
print("COMPARACION PRIMEROS 10 Y ULTIMOS 10:")
print("=" * 100)

print("\nPRIMEROS 10 DEL EXCEL:")
for i, mov in enumerate(excel_movimientos[:10]):
    print(f"  {i+1}. {mov['fecha'].date()} | {mov['descripcion']:30s} | {mov['valor']:12.2f} | Saldo: {mov['saldo']}")

print("\nPRIMEROS 10 DE LA BD:")
for i, (id_mov, fecha, monto) in enumerate(bd_movimientos[:10]):
    print(f"  {i+1}. {fecha} | {monto:12.2f} | ID: {id_mov}")

print("\n\nULTIMOS 10 DEL EXCEL:")
for i, mov in enumerate(excel_movimientos[-10:], start=len(excel_movimientos)-9):
    print(f"  {i}. {mov['fecha'].date()} | {mov['descripcion']:30s} | {mov['valor']:12.2f} | Saldo: {mov['saldo']}")

print("\nULTIMOS 10 DE LA BD:")
for i, (id_mov, fecha, monto) in enumerate(bd_movimientos[-10:], start=len(bd_movimientos)-9):
    print(f"  {i}. {fecha} | {monto:12.2f} | ID: {id_mov}")

# Calcular saldo correcto
print(f"\n" + "=" * 100)
print("CALCULO DE SALDOS:")
print("=" * 100)

saldo_inicial_excel = 466003.46  # Indicado por el usuario
suma_valores_excel = sum(mov['valor'] for mov in excel_movimientos)
saldo_final_esperado = saldo_inicial_excel + suma_valores_excel

print(f"\nSegun EXCEL:")
print(f"  Saldo Inicial: {saldo_inicial_excel}")
print(f"  Suma de todos los valores: {suma_valores_excel:.2f}")
print(f"  Saldo Final (calculado): {saldo_final_esperado:.2f}")
print(f"  Saldo Final (en Excel): {excel_movimientos[-1]['saldo']:.2f}")
print(f"  Coincidence: {'SI' if abs(saldo_final_esperado - excel_movimientos[-1]['saldo']) < 0.01 else 'NO'}")

# Verificar suma en BD
cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM movimiento WHERE id_cuenta = %s', (id_cuenta,))
suma_bd = cursor.fetchone()[0]

print(f"\nSegun BASE DE DATOS:")
print(f"  Suma de movimientos: {suma_bd:.2f}")
print(f"  DIFERENCIA: {suma_bd - suma_valores_excel:.2f}")

cursor.close()
db.conn.close()
wb.close()

print("\n" + "=" * 100)
