import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.services.optimizacion_categorias import OptimizacionCategoriasService


class DummyDB:
    def __init__(self, rows):
        self.rows = rows
        self.conn = object()

    def execute_query(self, query, params=None):
        if 'SELECT * FROM (' in query and 'FROM movimiento m' in query:
            return self.rows
        return []


def test_get_sin_categoria_prefiere_nota_sobre_codigo():
    service = OptimizacionCategoriasService(DummyDB([
        {
            'origen': 'cuenta',
            'id_movimiento': 1,
            'concepto': 'Pago de servicio',
            'fecha': '2026-08-03',
            'valor': 1000,
        }
    ]))

    rows = service.get_sin_categoria(1, limit=5)

    assert rows[0]['concepto'] == 'Pago de servicio'


class DummyDBDescriptionPriority(DummyDB):
    def execute_query(self, query, params=None):
        lower_query = query.lower()
        if 'select * from (' in lower_query and 'from movimiento m' in lower_query:
            assert 'nullif(trim(m.nota)' in lower_query
            assert 'nullif(trim(m.codigo)' in lower_query
            assert lower_query.index('nullif(trim(m.nota)') < lower_query.index('nullif(trim(m.codigo)')
            return [{
                'origen': 'cuenta',
                'id_movimiento': 1,
                'concepto': 'TRANSFERENCIAS A NEQUI',
                'fecha': '2026-08-03',
                'valor': 1000,
            }]
        return []


def test_get_sin_categoria_uses_real_description_before_generated_code():
    service = OptimizacionCategoriasService(DummyDBDescriptionPriority([
        {
            'origen': 'cuenta',
            'id_movimiento': 1,
            'concepto': 'TRANSFERENCIAS A NEQUI',
            'fecha': '2026-08-03',
            'valor': 1000,
        }
    ]))

    rows = service.get_sin_categoria(1, limit=5)

    assert rows[0]['concepto'] == 'TRANSFERENCIAS A NEQUI'
