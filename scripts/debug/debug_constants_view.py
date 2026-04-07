"""
Script de debug para verificar por qué no carga la grilla
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

from src.database.db_connector import DatabaseConnector
from src.views.constante import SystemConstantsView, Constant, ConstantType

# Simulación de página Flet
class MockPage:
    def __init__(self):
        self.controls = []
        self.update_called = False
    
    def update(self):
        self.update_called = True
        print("[OK] page.update() fue llamado")
    
    def go(self, route):
        print(f"[NAV] Navegando a: {route}")

# Test 1: Verificar BD directamente
print("=" * 60)
print("TEST 1: Verificar conexion y datos en BD")
print("=" * 60)

db = DatabaseConnector()
if not db.conn:
    print("[ERROR] No se pudo conectar a BD")
    sys.exit(1)

try:
    rows = db.execute_query(
        "SELECT id_constante, categoria, nombre, valor FROM constantes WHERE estado = 1 LIMIT 3"
    )
    print("[OK] Conexion exitosa")
    print(f"[OK] Se encontraron filas: {len(rows) if rows else 0}")
    
    if rows:
        for row in rows:
            print(f"     - {row}")
except Exception as e:
    print(f"[ERROR] Error en BD: {e}")
    sys.exit(1)

# Test 2: Instanciar la clase y llamar _load_constants
print("\n" + "=" * 60)
print("TEST 2: Instanciar SystemConstantsView y cargar constantes")
print("=" * 60)

mock_page = MockPage()

try:
    view = SystemConstantsView(mock_page)
    print("[OK] Clase instanciada")
    print(f"[OK] Constantes cargadas: {len(view.constants)}")
    print(f"[OK] Constantes filtradas: {len(view.filtered_constants)}")
    
    if view.constants:
        print("\n[INFO] Primeras 3 constantes cargadas:")
        for const in view.constants[:3]:
            print(f"       - {const.categoria}: {const.nombre} = {const.valor} ({const.tipo_dato})")
    else:
        print("\n[WARN] No se cargaron constantes!")
        
except Exception as e:
    print(f"[ERROR] Error instanciando clase: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verificar que table_container tiene contenido
print("\n" + "=" * 60)
print("TEST 3: Verificar contenido de table_container")
print("=" * 60)

print(f"[OK] table_container.content tipo: {type(view.table_container.content).__name__}")
print(f"[OK] page.update() fue llamado: {mock_page.update_called}")

# Test 4: Llamar _refresh_table manualmente
print("\n" + "=" * 60)
print("TEST 4: Llamar _refresh_table manualmente")
print("=" * 60)

try:
    view._refresh_table()
    print("[OK] _refresh_table() ejecutado")
    print(f"[OK] table_container.content ahora contiene: {type(view.table_container.content).__name__}")
except Exception as e:
    print(f"[ERROR] Error en _refresh_table: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Llamar build() que es lo que hace la app realmente
print("\n" + "=" * 60)
print("TEST 5: Llamar view.build() como lo hace la app")
print("=" * 60)

try:
    built_container = view.build()
    print("[OK] view.build() ejecutado")
    print(f"[OK] Retorna tipo: {type(built_container).__name__}")
    print(f"[OK] table_container.content ahora es: {type(view.table_container.content).__name__}")
    
    if hasattr(view.table_container.content, 'controls'):
        print(f"[OK] Column contiene {len(view.table_container.content.controls)} elemento(s)")
except Exception as e:
    print(f"[ERROR] Error en build(): {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("[OK] Todos los tests completados")
print("=" * 60)
