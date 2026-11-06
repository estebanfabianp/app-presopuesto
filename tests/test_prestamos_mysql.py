"""Integración aislada: ejecutar con PRESTAMOS_TEST_MYSQL=1 y MySQL local."""

import os
from pathlib import Path
from uuid import uuid4

import mysql.connector
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from src.database.db_connector import DatabaseConnector
from src.routes import prestamos

pytestmark = pytest.mark.skipif(
    os.getenv('PRESTAMOS_TEST_MYSQL') != '1',
    reason='La prueba crea y elimina una base temporal de MySQL',
)


@pytest.fixture
def entorno(monkeypatch):
    nombre = 'test_prestamos_' + uuid4().hex
    servidor = mysql.connector.connect(host='127.0.0.1', user='root', password='')
    cursor = servidor.cursor()
    cursor.execute(f'CREATE DATABASE `{nombre}`')
    try:
        cursor.execute(f'USE `{nombre}`')
        cursor.execute('CREATE TABLE persona (id_persona INT PRIMARY KEY) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE cuenta (id_cuenta INT PRIMARY KEY, id_persona INT, nombre VARCHAR(100), moneda VARCHAR(10)) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE tipo_movimiento (id_tipo INT PRIMARY KEY, nombre VARCHAR(20)) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE movimiento (id_movimiento INT AUTO_INCREMENT PRIMARY KEY, id_cuenta INT, id_tipo INT, monto DECIMAL(15,2), fecha_creacion DATETIME, nota TEXT, numero_transaccion VARCHAR(45)) ENGINE=InnoDB')
        cursor.execute('INSERT INTO persona VALUES (1), (2)')
        cursor.execute("INSERT INTO cuenta VALUES (1,1,'Cuenta prueba','COP'), (2,2,'Cuenta ajena','COP')")
        cursor.execute("INSERT INTO tipo_movimiento VALUES (1,'gasto')")
        sql = (Path(__file__).resolve().parents[1] / 'base_de_datos' / 'db' /
               '02_maintenance' / '2026-11-06_prestamos.sql').read_text(encoding='utf-8')
        for sentencia in sql.split(';'):
            if sentencia.strip():
                cursor.execute(sentencia)
        servidor.commit()
        monkeypatch.setattr(prestamos, '_conexion', lambda: DatabaseConnector(host='127.0.0.1', database=nombre))
        app = Flask(__name__)
        app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-loan-integration')
        JWTManager(app)
        app.register_blueprint(prestamos.bp)
        with app.app_context():
            tokens = [create_access_token(identity=str(i)) for i in (1, 2)]
        yield app.test_client(), [{'Authorization': f'Bearer {token}'} for token in tokens], nombre
    finally:
        cursor.execute(f'DROP DATABASE `{nombre}`')
        cursor.close()
        servidor.close()


def crear(client, headers):
    response = client.post('/api/prestamos', headers=headers, json={
        'nombre': 'Préstamo prueba', 'acreedor': 'Banco',
        'capital': '1000', 'tasa_ea': '0', 'numero_cuotas': 2,
        'frecuencia': 'mensual', 'metodo': 'frances', 'primera_fecha': '2026-01-31',
        'cargos': [{'nombre': 'Seguro', 'monto': '20'}, {'nombre': 'Administración', 'monto': '10'}],
    })
    assert response.status_code == 201, response.get_json()
    return response.get_json()['id']


def pago(client, headers, prestamo_id, monto, **extras):
    payload = {'tipo': 'cuota', 'numero_cuota': 1, 'monto': monto, 'fecha': '2026-01-15',
               'referencia': str(uuid4()), 'id_cuenta': None}
    payload.update(extras)
    return client.post(f'/api/prestamos/{prestamo_id}/pagos', headers=headers, json=payload)


def test_pagos_parciales_desglose_banco_y_aislamiento(entorno):
    client, (h1, h2), database = entorno
    prestamo_id = crear(client, h1)
    url = f'/api/prestamos/{prestamo_id}'
    assert client.get(url, headers=h2).status_code == 404
    assert pago(client, h2, prestamo_id, '10').status_code == 404
    assert pago(client, h1, prestamo_id, '10', id_cuenta=2).status_code == 400
    inicial = client.get(url, headers=h1).get_json()
    assert inicial['cuotas'][0]['cargos'][0]['pagado'] == '0.00'
    assert pago(client, h1, prestamo_id, '25', id_cuenta=1).status_code == 201
    parcial = client.get(url, headers=h1).get_json()
    assert parcial['cuotas'][0]['pendiente'] == '505.00'
    assert [c['pagado'] for c in parcial['cuotas'][0]['cargos']] == ['20.00', '5.00']
    assert parcial['prestamo']['saldo'] == '1000.00'
    assert pago(client, h1, prestamo_id, '2', tipo='abono').status_code == 400
    assert pago(client, h1, prestamo_id, '1', numero_cuota=2).status_code == 400
    assert pago(client, h1, prestamo_id, '506').status_code == 400
    assert pago(client, h1, prestamo_id, '505').status_code == 201
    final = client.get(url, headers=h1).get_json()
    assert final['prestamo']['saldo'] == '500.00'
    assert final['cuotas'][0]['pendiente'] == '0.00'
    conexion = mysql.connector.connect(host='127.0.0.1', user='root', password='', database=database)
    with conexion.cursor() as cursor:
        cursor.execute('SELECT monto, id_cuenta FROM movimiento')
        assert [(str(row[0]), row[1]) for row in cursor.fetchall()] == [('25.00', 1)]
    conexion.close()


def test_ajustes_y_abonos_recalculan_y_conservan_cargos(entorno):
    client, (headers, _), _ = entorno
    prestamo_id = crear(client, headers)
    url = f'/api/prestamos/{prestamo_id}'
    response = client.put(url + '/cuotas/2', headers=headers, json={
        'capital': '500', 'interes': '0', 'cargos': [{'nombre': 'Seguro especial', 'monto': '42'}],
    })
    assert response.status_code == 200
    assert pago(client, headers, prestamo_id, '200', tipo='abono').status_code == 201
    data = client.get(url, headers=headers).get_json()
    assert data['prestamo']['saldo'] == '800.00'
    assert [q['capital'] for q in data['cuotas']] == ['400.00', '400.00']
    assert data['cuotas'][1]['cargos'][0]['monto'] == '42.00'
    assert pago(client, headers, prestamo_id, '800', tipo='abono').status_code == 201
    data = client.get(url, headers=headers).get_json()
    assert data['prestamo']['saldo'] == '0.00'
    assert all(c['cancelada'] for c in data['cuotas'])
    assert len(data['pagos']) == 2


def test_referencia_duplicada_no_duplica_pago(entorno):
    client, (headers, _), _ = entorno
    prestamo_id = crear(client, headers)
    ref = str(uuid4())
    assert pago(client, headers, prestamo_id, '10', referencia=ref).status_code == 201
    assert pago(client, headers, prestamo_id, '10', referencia=ref).status_code == 409
    assert len(client.get(f'/api/prestamos/{prestamo_id}', headers=headers).get_json()['pagos']) == 1


def test_ajuste_capital_e_interes_y_aplicacion_de_pago(entorno):
    client, (headers, _), _ = entorno
    prestamo_id = crear(client, headers)
    url = f'/api/prestamos/{prestamo_id}'
    response = client.put(url + '/cuotas/1', headers=headers, json={
        'capital': '300', 'interes': '40', 'cargos': [{'nombre': 'Seguro', 'monto': '20'}],
    })
    assert response.status_code == 200
    data = client.get(url, headers=headers).get_json()
    assert data['cuotas'][1]['capital'] == '700.00'
    assert pago(client, headers, prestamo_id, '50').status_code == 201
    data = client.get(url, headers=headers).get_json()
    assert data['cuotas'][0]['interes_pagado'] == '30.00'
    assert data['cuotas'][0]['capital_pagado'] == '0.00'
    assert data['prestamo']['saldo'] == '1000.00'
    assert pago(client, headers, prestamo_id, '20').status_code == 201
    data = client.get(url, headers=headers).get_json()
    assert data['cuotas'][0]['capital_pagado'] == '10.00'
    assert data['prestamo']['saldo'] == '990.00'
    assert client.put(url + '/cuotas/1', headers=headers, json={
        'capital': '300', 'interes': '40', 'cargos': [],
    }).status_code == 400


def test_requiere_autenticacion_y_valida_decimales(entorno):
    client, (headers, _), _ = entorno
    assert client.get('/api/prestamos').status_code == 401
    prestamo_id = crear(client, headers)
    assert pago(client, headers, prestamo_id, '1.001').status_code == 400
