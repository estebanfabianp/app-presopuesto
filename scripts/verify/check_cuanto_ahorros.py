#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
cursor = db.conn.cursor()

# Buscar la cuenta
cursor.execute("SELECT id_cuenta, nombre, saldo_inicial FROM cuenta WHERE nombre LIKE %s", ("%cuanto%",))
result = cursor.fetchone()

if result:
    id_cuenta, nombre, saldo_inicial = result
    print(f'Cuenta encontrada: {nombre} (ID: {id_cuenta})')
    print(f'Saldo inicial: {saldo_inicial}')
    
    # Calcular saldo correcto
    cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM movimiento WHERE id_cuenta = %s', (id_cuenta,))
    total_mov = cursor.fetchone()[0]
    
    saldo_correcto = float(saldo_inicial) + float(total_mov)
    
    print(f'Total movimientos: {total_mov}')
    print(f'Saldo correcto debe ser: {saldo_correcto}')
    
    # Ver últimos movimientos
    cursor.execute('SELECT fecha_creacion, monto FROM movimiento WHERE id_cuenta = %s ORDER BY fecha_creacion DESC LIMIT 10', (id_cuenta,))
    movs = cursor.fetchall()
    print(f'\nUltimos 10 movimientos:')
    for mov in movs:
        print(f'  {mov[0]} | {mov[1]:>12.2f}')
else:
    print('Cuenta no encontrada')

cursor.close()
db.conn.close()
