from flask import Flask

from src.routes import categorias as categorias_module


class FakeDB:
    def __init__(self):
        self.queries = []

    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'information_schema.columns' in lower_query:
            return [
                {'COLUMN_NAME': 'id_categoria'},
                {'COLUMN_NAME': 'nombre'},
            ]
        return [
            {
                'id_categoria': 1,
                'nombre': 'Alimentación',
                'uso': 2,
            }
        ]

    def execute_non_query(self, query, params=None):
        return 1

    def close(self):
        return None


class FakeDBExtendedSchema(FakeDB):
    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'information_schema.columns' in lower_query:
            return [
                {'COLUMN_NAME': 'id_categoria'},
                {'COLUMN_NAME': 'nombre'},
                {'COLUMN_NAME': 'parent_id'},
                {'COLUMN_NAME': 'estado'},
                {'COLUMN_NAME': 'icono'},
                {'COLUMN_NAME': 'color'},
            ]
        return [
            {
                'id_categoria': 1,
                'nombre': 'Alimentación',
                'parent_id': None,
                'estado': 1,
                'icono': 'fa-tag',
                'color': '#6c757d',
                'uso': 2,
            }
        ]


class FakeDBOrderedSchema(FakeDBExtendedSchema):
    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        lower_query = query.lower()
        if 'information_schema.columns' in lower_query:
            return [
                {'COLUMN_NAME': 'id_categoria'},
                {'COLUMN_NAME': 'nombre'},
                {'COLUMN_NAME': 'parent_id'},
                {'COLUMN_NAME': 'estado'},
                {'COLUMN_NAME': 'icono'},
                {'COLUMN_NAME': 'color'},
            ]
        return [
            {
                'id_categoria': 10,
                'nombre': 'Inactiva',
                'parent_id': None,
                'estado': 0,
                'icono': 'fa-tag',
                'color': '#6c757d',
                'uso': 0,
            },
            {
                'id_categoria': 11,
                'nombre': 'Activa',
                'parent_id': None,
                'estado': 1,
                'icono': 'fa-tag',
                'color': '#6c757d',
                'uso': 1,
            },
            {
                'id_categoria': 12,
                'nombre': 'Subcategoría',
                'parent_id': 11,
                'estado': 1,
                'icono': 'fa-tag',
                'color': '#6c757d',
                'uso': 0,
            },
        ]

    def execute_non_query(self, query, params=None):
        return 1

    def close(self):
        return None


def test_list_categorias_with_legacy_schema(monkeypatch):
    app = Flask(__name__)
    fake_db = FakeDB()

    monkeypatch.setattr(categorias_module, 'verify_jwt_in_request', lambda: None)
    monkeypatch.setattr(categorias_module, '_get_user_id', lambda: 1)
    monkeypatch.setattr(categorias_module, 'DatabaseConnector', lambda: fake_db)

    with app.test_request_context('/api/categorias?plana=true'):
        response, status_code = categorias_module.list_categorias()

    assert status_code == 200
    payload = response.get_json()
    assert payload['total'] == 1
    assert payload['categorias'][0]['nombre'] == 'Alimentación'
    assert payload['categorias'][0]['estado'] is True


def test_list_categorias_builds_safe_select_for_extended_schema(monkeypatch):
    app = Flask(__name__)
    fake_db = FakeDBExtendedSchema()

    monkeypatch.setattr(categorias_module, 'verify_jwt_in_request', lambda: None)
    monkeypatch.setattr(categorias_module, '_get_user_id', lambda: 1)
    monkeypatch.setattr(categorias_module, 'DatabaseConnector', lambda: fake_db)

    with app.test_request_context('/api/categorias?plana=true'):
        response, status_code = categorias_module.list_categorias()

    assert status_code == 200
    payload = response.get_json()
    assert payload['total'] == 1

    query = fake_db.queries[1][0]
    assert query.startswith('SELECT id_categoria, nombre')
    assert 'FROM categoria' in query
    assert 'FROM categoria, ' not in query


def test_list_categorias_sorts_active_roots_before_inactive(monkeypatch):
    app = Flask(__name__)
    fake_db = FakeDBOrderedSchema()

    monkeypatch.setattr(categorias_module, 'verify_jwt_in_request', lambda: None)
    monkeypatch.setattr(categorias_module, '_get_user_id', lambda: 1)
    monkeypatch.setattr(categorias_module, 'DatabaseConnector', lambda: fake_db)

    with app.test_request_context('/api/categorias?plana=true'):
        response, status_code = categorias_module.list_categorias()

    assert status_code == 200
    payload = response.get_json()
    names = [item['nombre'] for item in payload['categorias']]
    assert names == ['Activa', 'Subcategoría', 'Inactiva']
