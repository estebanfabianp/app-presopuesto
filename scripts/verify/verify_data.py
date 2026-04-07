"""
Script de prueba para verificar que la BD tiene datos y que la vista los puede cargar
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_connector import DatabaseConnector

# Probar conexión y datos
db = DatabaseConnector()
conn = db.conn

if not conn:
    print("❌ No se pudo conectar a la BD")
    sys.exit(1)

try:
    cursor = conn.cursor(dictionary=True)
    
    # Contar constantes
    cursor.execute("SELECT COUNT(*) as total FROM constantes WHERE estado = 1")
    result = cursor.fetchone()
    total = result['total'] if result else 0
    
    print(f"✅ Total de constantes activas: {total}")
    
    if total == 0:
        print("⚠️ No hay constantes. Usa insert_test_data.py para agregar datos de prueba")
    else:
        # Mostrar primeras 3 constantes
        cursor.execute("""
            SELECT id_constante, categoria, nombre, valor, tipo_dato, descripcion 
            FROM constantes 
            WHERE estado = 1 
            LIMIT 3
        """)
        
        rows = cursor.fetchall()
        print(f"\n📋 Primeras 3 constantes:")
        for row in rows:
            print(f"   - {row['categoria']}: {row['nombre']} = {row['valor']} ({row['tipo_dato']})")
    
    cursor.close()
    conn.close()
    print("\n✅ Verificación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
