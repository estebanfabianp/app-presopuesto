#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el saldo inicial de "cuanto de ahorros"
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
cursor = db.conn.cursor()

try:
    print("\n" + "=" * 100)
    print("CORRECCION DE SALDO INICIAL - CUANTO DE AHORROS")
    print("=" * 100)
    
    # Obtener la cuenta
    cursor.execute("SELECT id_cuenta, nombre, saldo_inicial FROM cuenta WHERE nombre LIKE %s", ("%cuanto%",))
    result = cursor.fetchone()
    
    if result:
        id_cuenta, nombre, saldo_actual_bd = result
        
        # Valores correctos según el usuario
        nuevo_saldo_inicial = 466003.46
        saldo_actual_correcto = 1971099.04
        
        # Calcular total de movimientos necesario
        total_movimientos_esperado = saldo_actual_correcto - nuevo_saldo_inicial
        
        print(f"\nCuenta: {nombre} (ID: {id_cuenta})")
        print(f"\nDATA ANTERIOR:")
        print(f"  Saldo Inicial (incorrecto): {saldo_actual_bd}")
        
        # Verificar movimientos actuales
        cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM movimiento WHERE id_cuenta = %s', (id_cuenta,))
        total_mov_actual = cursor.fetchone()[0]
        print(f"  Total Movimientos: {total_mov_actual}")
        
        print(f"\nDATA NUEVA (CORRECTA):")
        print(f"  Saldo Inicial: {nuevo_saldo_inicial}")
        print(f"  Saldo Actual Esperado: {saldo_actual_correcto}")
        print(f"  Total Movimientos Esperado: {total_movimientos_esperado}")
        
        # Actualizar el saldo inicial
        print(f"\nActualizando saldo inicial en la BD...")
        cursor.execute(
            'UPDATE cuenta SET saldo_inicial = %s WHERE id_cuenta = %s',
            (nuevo_saldo_inicial, id_cuenta)
        )
        db.conn.commit()
        print(f"✓ Saldo inicial actualizado a: {nuevo_saldo_inicial}")
        
        # Verificar que la vista calcula correctamente
        print(f"\nVERIFICANDO VISTA v_cuenta_saldos:")
        cursor.execute(
            """SELECT saldo_inicial, total_movimientos, saldo_actual 
               FROM v_cuenta_saldos WHERE nombre_cuenta LIKE %s""",
            ("%cuanto%",)
        )
        result = cursor.fetchone()
        if result:
            saldo_ini, total_mov, saldo_act = result
            print(f"  Saldo Inicial: {saldo_ini}")
            print(f"  Total Movimientos: {total_mov}")
            print(f"  Saldo Actual: {saldo_act}")
            
            if abs(float(saldo_act) - saldo_actual_correcto) < 0.01:
                print(f"  ✓ CORRECTO: Saldo actual = {saldo_actual_correcto}")
            else:
                print(f"  ✗ ERROR: Esperaba {saldo_actual_correcto}, pero obtuvo {saldo_act}")
        
        print("\n" + "=" * 100)
        print("CORRECCION COMPLETADA")
        print("=" * 100)
    else:
        print("✗ Cuenta no encontrada")
    
    cursor.close()
    db.conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    db.conn.rollback()
    db.conn.close()
