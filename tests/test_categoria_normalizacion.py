import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.routes.categorias import _normalizar_nombre_categoria


class TestCategoriaNormalizacion(unittest.TestCase):
    def test_repara_categorias_con_mojibake(self):
        self.assertEqual(_normalizar_nombre_categoria('Pensi├│n'), 'Pensión')
        self.assertEqual(_normalizar_nombre_categoria('Servicios P├║blicos'), 'Servicios Públicos')
        self.assertEqual(_normalizar_nombre_categoria('Internet y Telefon├¡a'), 'Internet y Telefonía')
        self.assertEqual(_normalizar_nombre_categoria('  comida  y  bebida  '), 'Comida y Bebida')


if __name__ == '__main__':
    unittest.main()
