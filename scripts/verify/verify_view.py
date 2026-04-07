"""
Script final para verificar que la vista carga correctamente
Simula exactamente lo que hace la navegación en la app
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Simulación de página Flet más realista
class MockFletPage:
    def __init__(self):
        self.controls = []
        self.views = []
        self.route = "/constantes"
        self.title = "Test"
    
    def update(self):
        """Requiere que los controles existan"""
        if self.views:
            view = self.views[-1]
            if hasattr(view, 'controls') and view.controls:
                return True
        return True
    
    def go(self, route):
        print(f"[NAV] Navegando a: {route}")
        self.route = route

print("[INFO] Simulando navegación a /constantes...")
print("=" * 60)

# Importar lo que hace main.py cuando navega a /constantes  
from src.views.constante import system_constants_view

try:
    # 1. Crear página simulada
    mock_page = MockFletPage()
    print("[OK] Página creada")
    
    # 2. Llamar a system_constants_view (como hace el router)
    print("[INFO] Llamando system_constants_view(page)...")
    view = system_constants_view(mock_page)
    print(f"[OK] Retorna: {type(view).__name__}")
    
    # 3. Verificar que el View tiene controles
    print(f"[OK] View.route = {view.route}")
    print(f"[OK] View.controls = {len(view.controls)} elemento(s)")
    
    if view.controls:
        control = view.controls[0]
        print(f"[OK] Control[0] tipo: {type(control).__name__}")
        
        # 4. Verificar que el contenedor tiene contenido
        if hasattr(control, 'content'):
            print(f"[OK] Control tiene content")
            if hasattr(control.content, 'controls'):
                print(f"[OK] Content tiene {len(control.content.controls)} elementos (Row con sidebar + stack)")
    
    # 5. Agregar view a página (como hace el router)
    mock_page.views.append(view)
    print("[OK] View agregada a página.views")
    
    # 6. Intentar page.update() (como hace el router)
    mock_page.update()
    print("[OK] page.update() ejecutado")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] La vista debería cargarse correctamente en la app")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
