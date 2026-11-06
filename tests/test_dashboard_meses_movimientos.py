from datetime import date
from unittest.mock import MagicMock

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from src.routes import dashboard


class FechaFija(date):
    @classmethod
    def today(cls):
        return cls(2026, 1, 15)


def crear_cliente():
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-dashboard-tests')
    JWTManager(app)
    app.register_blueprint(dashboard.bp)
    with app.app_context():
        token = create_access_token(identity='42')
    return app.test_client(), {'Authorization': f'Bearer {token}'}


def test_meses_incluyen_vacios_cambio_de_anio_y_ultimo_fuera_del_periodo(monkeypatch):
    db = MagicMock()
    db.is_connected.return_value = True
    cursor = db.conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        {'tipo': 'cuentas', 'anio': 2026, 'mes': 1, 'cantidad': 3},
        {'tipo': 'cuentas', 'anio': 2025, 'mes': 11, 'cantidad': 2},
        {'tipo': 'tarjetas', 'anio': 2024, 'mes': 2, 'cantidad': 4},
    ]
    monkeypatch.setattr(dashboard, 'DatabaseConnector', lambda: db)
    monkeypatch.setattr(dashboard, 'date', FechaFija)
    client, headers = crear_cliente()

    response = client.get('/api/dashboard/meses-con-movimientos', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['meses']) == 12
    assert data['meses'][0] == {'mes': '2026-01', 'cuentas': 3, 'tarjetas': 0}
    assert data['meses'][1] == {'mes': '2025-12', 'cuentas': 0, 'tarjetas': 0}
    assert data['meses'][2]['cuentas'] == 2
    assert data['meses'][-1]['mes'] == '2025-02'
    assert data['ultimo_mes'] == {'cuentas': '2026-01', 'tarjetas': '2024-02'}
    query, params = cursor.execute.call_args.args
    assert 'c.id_persona = %s' in query
    assert 'mt.id_persona = %s' in query
    assert params == (42, date(2026, 1, 16), 42, date(2026, 1, 16))
    db.close.assert_called_once()


def test_sin_movimientos(monkeypatch):
    db = MagicMock()
    db.is_connected.return_value = True
    db.conn.cursor.return_value.__enter__.return_value.fetchall.return_value = []
    monkeypatch.setattr(dashboard, 'DatabaseConnector', lambda: db)
    monkeypatch.setattr(dashboard, 'date', FechaFija)
    client, headers = crear_cliente()

    response = client.get('/api/dashboard/meses-con-movimientos', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['ultimo_mes'] == {'cuentas': None, 'tarjetas': None}
    assert len(data['meses']) == 12
    assert all(row['cuentas'] == row['tarjetas'] == 0 for row in data['meses'])


def test_error_de_consulta_no_se_muestra_como_sin_datos(monkeypatch):
    db = MagicMock()
    db.is_connected.return_value = True
    db.conn.cursor.return_value.__enter__.return_value.execute.side_effect = RuntimeError('fallo SQL')
    monkeypatch.setattr(dashboard, 'DatabaseConnector', lambda: db)
    client, headers = crear_cliente()

    response = client.get('/api/dashboard/meses-con-movimientos', headers=headers)

    assert response.status_code == 500
    assert 'message' in response.get_json()
    db.close.assert_called_once()


def test_requiere_autenticacion():
    client, _ = crear_cliente()
    assert client.get('/api/dashboard/meses-con-movimientos').status_code == 401
