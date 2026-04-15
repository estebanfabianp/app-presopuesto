#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar movimientos de "cuanto de ahorros"
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
cursor = db.conn.cursor()

try:
    # Obtener la cuenta
    cursor.execute("SELECT id_cuenta FROM cuenta WHERE nombre LIKE %s", ("%cuanto%",))
    id_cuenta = cursor.fetchone()[0]
    
    print("\n" + "=" * 100)
    print(f"MOVIMIENTOS DE 'cuanto de ahorros' (ID: {id_cuenta})")
    print("=" * 100)
    
    # Obtener todos los movimientos
    cursor.execute('''
        SELECT id_movimiento, fecha_creacion, monto, id_categoria, id_beneficiario 
        FROM movimiento 
        WHERE id_cuenta = %s 
        ORDER BY fecha_creacion DESC
    ''', (id_cuenta,))
    
    movimientos = cursor.fetchall()
    
    print(f"\nTotal de movimientos: {len(movimientos)}\n")
    
    # Mostrar primeros 20
    print("ULTIMOS 20 MOVIMIENTOS:")
    print("-" * 100)
    total_suma = 0
    for i, (id_mov, fecha, monto, id_cat, id_ben) in enumerate(movimientos[:20]):
        total_suma += float(monto)
        print(f"{i+1:3d}. {fecha} | Monto: {float(monto):15.2f} | ID Mov: {id_mov} | Cat: {id_cat} | Ben: {id_ben}")
    
    print(f"\nTotal suma (primeros 20): {total_suma:.2f}")
    
    # Estadísticas
    cursor.execute('SELECT COUNT(*), SUM(monto), MIN(monto), MAX(monto) FROM movimiento WHERE id_cuenta = %s', (id_cuenta,))
    count, total, minimo, maximo = cursor.fetchone()
    
    print(f"\nESTADISTICAS:")
    print(f"  Total movimientos: {count}")
    print(f"  Suma total: {float(total):.2f}")
    print(f"  Monto mínimo: {float(minimo):.2f}")
    print(f"  Monto máximo: {float(maximo):.2f}")
    
    # Ver si hay movimientos muy grandes
    print(f"\nMOVIMIENTOS MAYORES A 100,000,000:")
    cursor.execute('''
        SELECT id_movimiento, fecha_creacion, monto 
        FROM movimiento 
        WHERE id_cuenta = %s AND monto > 100000000
        ORDER BY monto DESC
    ''', (id_cuenta,))
    
    grandes = cursor.fetchall()
    if grandes:
        for id_mov, fecha, monto in grandes:
            print(f"  {fecha} | Monto: {float(monto):20.2f} | ID: {id_mov}")
    else:
        print("  Ninguno encontrado")
    
    cursor.close()
    db.conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    db.conn.close()
