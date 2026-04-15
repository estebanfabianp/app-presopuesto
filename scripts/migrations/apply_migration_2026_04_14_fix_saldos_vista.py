#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la vista v_cuenta_saldos
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
cursor = db.conn.cursor()

try:
    # Eliminar la vista anterior
    print("Eliminando vista v_cuenta_saldos anterior...")
    cursor.execute("DROP VIEW IF EXISTS v_cuenta_saldos")
    db.conn.commit()
    
    # Crear la nueva vista con cálculo correcto de saldos
    print("Creando nueva vista v_cuenta_saldos...")
    sql_new_view = """
    CREATE VIEW v_cuenta_saldos AS
    SELECT 
        c.id_cuenta,
        c.nombre AS nombre_cuenta,
        c.tipo AS tipo_cuenta,
        c.moneda,
        c.saldo_inicial,
        COALESCE(SUM(m.monto), 0) AS total_movimientos,
        (c.saldo_inicial + COALESCE(SUM(m.monto), 0)) AS saldo_actual,
        p.nombre AS titular
    FROM cuenta c
    LEFT JOIN movimiento m ON c.id_cuenta = m.id_cuenta
    JOIN persona p ON c.id_persona = p.id_persona
    GROUP BY c.id_cuenta, c.nombre, c.tipo, c.moneda, c.saldo_inicial, p.nombre
    ORDER BY c.id_cuenta
    """
    
    cursor.execute(sql_new_view)
    db.conn.commit()
    print("✓ Vista v_cuenta_saldos creada correctamente")
    
    # Verificar los saldos de la vista
    print("\nVERIFICACION DE SALDOS EN LA VISTA:")
    print("=" * 100)
    cursor.execute("""
        SELECT id_cuenta, nombre_cuenta, saldo_inicial, total_movimientos, saldo_actual
        FROM v_cuenta_saldos
        ORDER BY id_cuenta
    """)
    
    results = cursor.fetchall()
    for row in results:
        id_cuenta, nombre, saldo_inicial, total_mov, saldo_actual = row
        print(f"{nombre:30s} | Inicial: {saldo_inicial:15.2f} | Movs: {total_mov:15.2f} | Actual: {saldo_actual:15.2f}")
    
    # Específicamente la cuenta "cuanto de ahorros"
    print("\n" + "=" * 100)
    print("VERIFICACION ESPECIFICA - 'cuanto de ahorros':")
    cursor.execute("""
        SELECT id_cuenta, nombre_cuenta, saldo_inicial, total_movimientos, saldo_actual
        FROM v_cuenta_saldos
        WHERE nombre_cuenta LIKE '%cuanto%'
    """)
    
    row = cursor.fetchone()
    if row:
        id_cuenta, nombre, saldo_inicial, total_mov, saldo_actual = row
        print(f"Cuenta: {nombre} (ID: {id_cuenta})")
        print(f"  Saldo Inicial:       {saldo_inicial:15.2f}")
        print(f"  Total Movimientos:   {total_mov:15.2f}")
        print(f"  Saldo Actual:        {saldo_actual:15.2f}")
    
    cursor.close()
    db.conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    db.conn.rollback()
    db.conn.close()
