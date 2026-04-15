#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector

db = DatabaseConnector()
cursor = db.conn.cursor()

# Listar vistas
cursor.execute("SHOW FULL TABLES WHERE Table_Type = 'VIEW'")
views = cursor.fetchall()

print("VISTAS EN LA BASE DE DATOS:")
for view in views:
    print(f"  {view[0]}")

# Ver definición de v_cuenta_saldos
print("\nDEFINICION DE v_cuenta_saldos:")
cursor.execute("SHOW CREATE VIEW v_cuenta_saldos")
result = cursor.fetchone()
if result:
    print(result[1])

cursor.close()
db.conn.close()
