import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.services.optimizacion_categorias import OptimizacionCategoriasService


class FakeCursor:
    def __init__(self):
        self.executed_queries = []
        self.rowcount = 0

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        self.executed_queries.append((query, params))

    def close(self):
        return None


class FakeConn:
    def __init__(self):
        self.cursor_obj = FakeCursor()

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        return None


class FakeDB:
    def __init__(self):
        self.conn = FakeConn()
        self.queries = []

    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'information_schema.columns' in lower_query:
            return [
                {'COLUMN_NAME': 'id_categoria'},
                {'COLUMN_NAME': 'nombre'},
                {'COLUMN_NAME': 'estado'},
                {'COLUMN_NAME': 'icono'},
                {'COLUMN_NAME': 'color'},
            ]
        if 'from categoria' in lower_query:
            return [
                {'id_categoria': 1, 'nombre': 'Alimentación', 'icono': 'fa-tag', 'color': '#6c757d'},
            ]
        if 'select id_cuenta from cuenta' in lower_query:
            return [{'id_cuenta': 1}]
        if 'from movimiento_tarjeta' in lower_query:
            return [{'concepto': 'Supermercado'}]
        if 'from movimiento' in lower_query:
            return [{'concepto': 'Supermercado'}]
        return []

    def execute_non_query(self, query, params=None):
        self.queries.append((query, params))
        return 1


class FakeDBWithAppliedRules(FakeDB):
    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'information_schema.columns' in lower_query:
            return [
                {'COLUMN_NAME': 'id_categoria'},
                {'COLUMN_NAME': 'nombre'},
                {'COLUMN_NAME': 'estado'},
                {'COLUMN_NAME': 'icono'},
                {'COLUMN_NAME': 'color'},
            ]
        if 'from categoria_regla cr' in lower_query:
            return [
                {
                    'concepto': 'Supermercado',
                    'id_categoria': 1,
                    'nombre_categoria': 'Alimentación',
                    'total_movimientos': 5,
                    'pendientes': 0,
                    'fuente': 'confirmada',
                }
            ]
        if 'select concepto from categoria_regla' in lower_query:
            return [{'concepto': 'Supermercado'}]
        if 'from categoria where id_categoria = %s' in lower_query:
            return [{'nombre': 'Alimentación'}]
        if 'from (\n                select nullif(trim(mt.nota), \'\') as concepto, mt.id_categoria' in lower_query:
            return []
        return []


class FakeDBNoCollation(FakeDBWithAppliedRules):
    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'collate' in lower_query or 'binary trim' in lower_query:
            raise RuntimeError('illegal mix of collations')
        return super().execute_query(query, params)


def test_get_categorias_uses_schema_safe_query_without_id_persona():
    db = FakeDB()
    service = OptimizacionCategoriasService(db)

    rows = service.get_categorias(7)

    assert rows[0]['nombre'] == 'Alimentación'
    assert any('from categoria' in query.lower() for query, _ in db.queries)


def test_asignar_categoria_movimiento_creates_rule_for_concept():
    db = FakeDB()
    service = OptimizacionCategoriasService(db)

    ok = service.asignar_categoria_movimiento('tarjeta', 12, 3, 7)

    assert ok is True
    assert any('insert into categoria_regla' in (query.lower()) for query, _ in db.conn.cursor_obj.executed_queries)


def test_get_reglas_keeps_applied_rules_visible():
    db = FakeDBWithAppliedRules()
    service = OptimizacionCategoriasService(db)

    reglas = service.get_reglas(7)

    assert len(reglas) == 1
    assert reglas[0]['concepto'] == 'Supermercado'
    assert reglas[0]['fuente'] == 'confirmada'
    assert reglas[0]['pendientes'] == 0


def test_get_reglas_avoids_collation_sensitive_comparisons():
    db = FakeDBNoCollation()
    service = OptimizacionCategoriasService(db)

    reglas = service.get_reglas(7)

    assert reglas[0]['concepto'] == 'Supermercado'


def test_aplicar_una_regla_prefers_bank_note_over_generated_code():
    db = FakeDB()
    service = OptimizacionCategoriasService(db)

    total = service._aplicar_una_regla(7, 'PAGO SUC VIRT TC VISA', 9)

    assert total == 0
    all_queries = [query for query, _ in db.queries + db.conn.cursor_obj.executed_queries]
    assert any('nullif(trim(nota)' in query.lower() for query in all_queries)
    assert any('nullif(trim(codigo)' in query.lower() for query in all_queries)
    assert any(
        'update movimiento' in query.lower()
        and 'nullif(trim(nota)' in query.lower()
        and 'nullif(trim(codigo)' in query.lower()
        and query.lower().index('nullif(trim(nota)') < query.lower().index('nullif(trim(codigo)')
        for query in all_queries
    )
