"""Integración aislada con bases temporales cuando PRESTAMOS_TEST_MYSQL=1."""
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import mysql.connector
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from src.database.db_connector import DatabaseConnector
from src.routes import metas

pytestmark = pytest.mark.skipif(os.getenv('PRESTAMOS_TEST_MYSQL') != '1', reason='Requiere MySQL local')


@pytest.fixture
def entorno(monkeypatch):
    database = 'test_metas_' + uuid4().hex
    servidor = mysql.connector.connect(host='127.0.0.1', user='root', password='')
    with servidor.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE `{database}`')
        cursor.execute(f'USE `{database}`')
        cursor.execute('CREATE TABLE persona (id_persona INT PRIMARY KEY) ENGINE=InnoDB')
        cursor.execute('INSERT INTO persona VALUES (1),(2)')
        sql = (Path(__file__).resolve().parents[1] / 'base_de_datos' / 'db' /
               '02_maintenance' / '2026-11-06_metas_ahorro.sql').read_text(encoding='utf-8')
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
    servidor.commit()
    monkeypatch.setattr(metas, '_conexion', lambda: DatabaseConnector(host='127.0.0.1', database=database))
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-savings-goals')
    JWTManager(app)
    app.register_blueprint(metas.bp)
    with app.app_context():
        headers = [{'Authorization': f'Bearer {create_access_token(identity=str(i))}'} for i in (1, 2)]
    try:
        yield app.test_client(), headers, database
    finally:
        with servidor.cursor() as cursor:
            cursor.execute(f'DROP DATABASE `{database}`')
        servidor.close()


def test_metas_aportes_retiros_y_aislamiento(entorno):
    client, (h1, h2), database = entorno
    payload = {'nombre': 'Viaje', 'objetivo': '1000.00', 'fecha_objetivo': '2027-01-31', 'referencia': str(uuid4())}
    response = client.post('/api/metas', headers=h1, json=payload)
    assert response.status_code == 201
    meta_id = response.get_json()['id']
    assert client.post('/api/metas', headers=h1, json=payload).get_json()['id'] == meta_id
    assert client.post('/api/metas', headers=h2, json=payload).status_code == 400
    assert client.get('/api/metas', headers=h2).get_json()['metas'] == []
    url = f'/api/metas/{meta_id}'
    assert client.get(url, headers=h2).status_code == 404
    assert client.put(url, headers=h2, json=payload).status_code == 404
    aporte = {'tipo': 'aporte', 'monto': '600.50', 'nota': 'Inicial', 'referencia': str(uuid4())}
    assert client.post(url + '/movimientos', headers=h2, json=aporte).status_code == 404
    assert client.post(url + '/movimientos', headers=h1, json=aporte).status_code == 201
    assert client.post(url + '/movimientos', headers=h1, json=aporte).status_code == 200
    retiro = {'tipo': 'retiro', 'monto': '601', 'referencia': str(uuid4())}
    assert client.post(url + '/movimientos', headers=h1, json=retiro).status_code == 400
    retiro['monto'] = '100.50'
    assert client.post(url + '/movimientos', headers=h1, json=retiro).status_code == 201
    detalle = client.get(url, headers=h1).get_json()
    assert detalle['meta']['ahorrado'] == '500.00'
    assert detalle['meta']['faltante'] == '500.00'
    assert float(detalle['meta']['progreso']) == 50
    assert len(detalle['movimientos']) == 2
    assert client.put(url, headers=h1, json={'nombre': 'Casa', 'objetivo': '400', 'fecha_objetivo': None}).status_code == 200
    detalle = client.get(url, headers=h1).get_json()
    assert detalle['meta']['nombre'] == 'Casa'
    assert detalle['meta']['faltante'] == '0'
    assert float(detalle['meta']['progreso']) == 125
    summary = client.get('/api/metas/summary', headers=h1).get_json()
    assert summary['total_metas'] == 1 and summary['avance_estimado_pct'] == 125
    assert summary['gasto_mes'] is None


def test_validacion_y_error_de_bd(entorno):
    client, (headers, _), database = entorno
    base = {'nombre': 'Prueba', 'objetivo': '100', 'referencia': str(uuid4())}
    for data in ({**base, 'nombre': ''}, {**base, 'objetivo': '0'}, {**base, 'objetivo': 'NaN'},
                 {**base, 'objetivo': '1.001'}, {**base, 'fecha_objetivo': '2026-02-31'},
                 {**base, 'referencia': 'incorrecta'}):
        assert client.post('/api/metas', headers=headers, json=data).status_code == 400
    meta_id = client.post('/api/metas', headers=headers, json=base).get_json()['id']
    url = f'/api/metas/{meta_id}/movimientos'
    for data in ({'tipo': 'aporte', 'monto': '0', 'referencia': str(uuid4())},
                 {'tipo': 'otro', 'monto': '1', 'referencia': str(uuid4())},
                 {'tipo': 'aporte', 'monto': '1', 'referencia': 'incorrecta'}):
        assert client.post(url, headers=headers, json=data).status_code == 400
    conexion = mysql.connector.connect(host='127.0.0.1', user='root', password='', database=database)
    with conexion.cursor() as cursor:
        cursor.execute('DROP TABLE meta_ahorro_movimiento')
    conexion.close()
    assert client.get('/api/metas', headers=headers).status_code == 500


def test_retiros_simultaneos_no_superan_saldo(entorno):
    client, (headers, _), _ = entorno
    meta_id = client.post('/api/metas', headers=headers, json={
        'nombre': 'Reserva', 'objetivo': '100', 'referencia': str(uuid4())
    }).get_json()['id']
    url = f'/api/metas/{meta_id}/movimientos'
    assert client.post(url, headers=headers, json={
        'tipo': 'aporte', 'monto': '100', 'referencia': str(uuid4())
    }).status_code == 201

    def retirar(_):
        with client.application.test_client() as concurrent_client:
            return concurrent_client.post(url, headers=headers, json={
                'tipo': 'retiro', 'monto': '80', 'referencia': str(uuid4())
            }).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(retirar, range(2)))
    assert sorted(resultados) == [201, 400]
    assert client.get(f'/api/metas/{meta_id}', headers=headers).get_json()['meta']['ahorrado'] == '20.00'
