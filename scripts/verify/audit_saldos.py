#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para auditar y corregir saldos de cuentas
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

def audit_account_balances():
    """Verifica y audita los saldos de las cuentas."""
    db = DatabaseConnector()
    cursor = db.conn.cursor()
    
    try:
        # Obtener todas las cuentas
        cursor.execute('''
            SELECT id_cuenta, id_persona, nombre, saldo_inicial, tipo, moneda 
            FROM cuenta 
            ORDER BY id_cuenta
        ''')
        cuentas = cursor.fetchall()
        
        print("\n" + "=" * 100)
        print("AUDITORIA DE SALDOS - TODAS LAS CUENTAS")
        print("=" * 100)
        
        discrepancies = []
        
        for cuenta in cuentas:
            id_cuenta, id_persona, nombre, saldo_inicial, tipo, moneda = cuenta
            
            # Saldo registrado
            cursor.execute('SELECT saldo FROM cuenta WHERE id_cuenta = %s', (id_cuenta,))
            saldo_actual = cursor.fetchone()[0]
            
            # Calcular saldo correcto sumando movimientos
            cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) FROM movimiento 
                WHERE id_cuenta = %s
            ''', (id_cuenta,))
            total_movimientos = cursor.fetchone()[0]
            
            saldo_correcto = float(saldo_inicial) + float(total_movimientos)
            diferencia = float(saldo_actual) - saldo_correcto
            
            estado = "OK" if abs(diferencia) < 0.01 else "ERROR"
            
            print(f"\n[{estado}] Cuenta: {nombre} (ID: {id_cuenta}, Tipo: {tipo})")
            print(f"    Saldo Inicial:        {saldo_inicial}")
            print(f"    Total Movimientos:    {total_movimientos}")
            print(f"    Saldo Calculado:      {saldo_correcto}")
            print(f"    Saldo en BD:          {saldo_actual}")
            print(f"    Diferencia:           {diferencia}")
            
            if abs(diferencia) >= 0.01:
                discrepancies.append({
                    'id_cuenta': id_cuenta,
                    'nombre': nombre,
                    'saldo_actual': saldo_actual,
                    'saldo_correcto': saldo_correcto,
                    'diferencia': diferencia
                })
        
        print("\n" + "=" * 100)
        print("RESUMEN")
        print("=" * 100)
        print(f"Total de cuentas: {len(cuentas)}")
        print(f"Cuentas con discrepancias: {len(discrepancies)}")
        
        if discrepancies:
            print("\nCUENTAS CON ERRORES:")
            for disc in discrepancies:
                print(f"  - {disc['nombre']} (ID: {disc['id_cuenta']}): Diferencia de {disc['diferencia']}")
                print(f"    Actual: {disc['saldo_actual']}, Correcto: {disc['saldo_correcto']}")
        
        cursor.close()
        db.conn.close()
        
        return discrepancies
        
    except Exception as e:
        print(f"Error: {e}")
        db.conn.close()
        return []

if __name__ == "__main__":
    audit_account_balances()
