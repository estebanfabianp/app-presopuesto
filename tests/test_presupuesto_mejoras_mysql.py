"""Pruebas aisladas: PRESTAMOS_TEST_MYSQL=1 habilita bases temporales."""

import os
from datetime import date, timedelta
from uuid import uuid4

import mysql.connector
import pytest
from dateutil.relativedelta import relativedelta
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from src.database.db_connector import DatabaseConnector
from src.routes import presupuesto
from src.routes import analisis
from src.routes.presupuesto import (
    _count_abonos_por_revisar,
    _fetch_monthly_prestamos_total,
    _fetch_real_totals,
    _fetch_monthly_budget_expenses,
    _save_sheet_transaction,
    _period_bounds,
)

pytestmark = pytest.mark.skipif(os.getenv('PRESTAMOS_TEST_MYSQL') != '1', reason='Requiere MySQL local')


@pytest.fixture
def db():
    name = 'test_presupuesto_' + uuid4().hex
    server = mysql.connector.connect(host='127.0.0.1', user='root', password='')
    with server.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE `{name}`')
        cursor.execute(f'USE `{name}`')
        cursor.execute('CREATE TABLE persona (id_persona INT PRIMARY KEY) ENGINE=InnoDB')
        cursor.execute('INSERT INTO persona VALUES (1),(2)')
        cursor.execute('CREATE TABLE categoria (id_categoria INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150), parent_id INT NULL, id_persona INT NULL) ENGINE=InnoDB')
        cursor.execute("INSERT INTO categoria VALUES (1,'Comida',NULL,NULL),(2,'Pagos de Tarjeta de Crédito',NULL,NULL),(3,'Abono al banco',NULL,NULL),(4,'Privada',NULL,2)")
        cursor.execute('CREATE TABLE cuenta (id_cuenta INT PRIMARY KEY, id_persona INT) ENGINE=InnoDB')
        cursor.execute('INSERT INTO cuenta VALUES (1,1),(2,2)')
        cursor.execute('CREATE TABLE tipo_movimiento (id_tipo INT PRIMARY KEY, nombre VARCHAR(50)) ENGINE=InnoDB')
        cursor.execute("INSERT INTO tipo_movimiento VALUES (1,'gasto')")
        cursor.execute('CREATE TABLE movimiento (id_cuenta INT, id_tipo INT, id_categoria INT, monto DECIMAL(15,2), fecha_creacion DATETIME) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE movimiento_tarjeta (id_persona INT, id_categoria INT, valor DECIMAL(15,2), estado VARCHAR(20), nota TEXT, fecha DATE, numero_transaccion VARCHAR(100)) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE prestamo (id INT PRIMARY KEY, id_persona INT) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE prestamo_cuota (id INT PRIMARY KEY, id_prestamo INT, fecha DATE, capital DECIMAL(15,2), capital_pagado DECIMAL(15,2), interes DECIMAL(15,2), interes_pagado DECIMAL(15,2), cancelada BOOLEAN) ENGINE=InnoDB')
        cursor.execute('CREATE TABLE prestamo_cargo (id_cuota INT, monto DECIMAL(15,2), pagado DECIMAL(15,2)) ENGINE=InnoDB')
    server.commit()
    connector = DatabaseConnector(host='127.0.0.1', database=name)
    try:
        yield connector
    finally:
        connector.close()
        with server.cursor() as cursor:
            cursor.execute(f'DROP DATABASE `{name}`')
        server.close()


def test_compras_y_abonos_no_duplican_gastos(db):
    with db.conn.cursor() as cursor:
        cursor.execute("INSERT INTO movimiento VALUES (1,1,1,25,'2026-03-10'),(1,1,2,100,'2026-03-10'),(2,1,1,999,'2026-03-10')")
        cursor.execute("INSERT INTO movimiento_tarjeta VALUES (1,1,100,'compra','compra','2026-03-10',NULL),(1,3,-80,'abono','ABONO SUCURSAL VIRTUAL','2026-03-10',NULL),(1,1,-20,'abono','posible devolución','2026-03-10',NULL),(1,1,-10,'abono','cuota','2026-03-10','DIFPAY-1'),(2,1,999,'compra','otro usuario','2026-03-10',NULL)")
    db.conn.commit()
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    assert _fetch_real_totals(db, 1, start, end) == {1: 125.0}
    assert _count_abonos_por_revisar(db, 1, start, end) == 1


def test_cuotas_pendientes_suman_cargos_y_no_duplican_capital(db):
    today = date.today()
    with db.conn.cursor() as cursor:
        cursor.execute('INSERT INTO prestamo VALUES (1,1),(2,2)')
        cursor.execute('INSERT INTO prestamo_cuota VALUES (1,1,%s,100,20,10,5,0),(2,2,%s,900,0,0,0,0)', (today, today))
        cursor.execute('INSERT INTO prestamo_cargo VALUES (1,15,5),(1,8,3)')
    db.conn.commit()
    assert _fetch_monthly_prestamos_total(db, 1) == 100


def test_guardado_revertido_y_categorias_aisladas(db):
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    line = {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 100}
    budget_id = _save_sheet_transaction(db, 1, None, 'Original', None, start, end, [line])
    with pytest.raises(ValueError):
        _save_sheet_transaction(db, 1, budget_id, 'Cambio', None, start, end, [
            line, {'id_categoria': 4, 'categoria': 'Privada', 'estimado': 10},
        ])
    with db.conn.cursor(dictionary=True) as cursor:
        cursor.execute('SELECT nombre, monto_total FROM presupuesto WHERE id_presupuesto=%s', (budget_id,))
        row = cursor.fetchone()
        assert row['nombre'] == 'Original'
        assert row['monto_total'] == 100
        cursor.execute('SELECT id_categoria, monto_estimado FROM presupuesto_detalle WHERE id_presupuesto=%s', (budget_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1 and rows[0]['id_categoria'] == 1 and rows[0]['monto_estimado'] == 100


def test_gastos_mes_actual_actualizan_fijos_variables_y_separan_usuarios(db):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    lines = [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 30, 'es_fijo': False},
        {'id_categoria': 2, 'categoria': 'Pagos de Tarjeta de Crédito', 'tipo': 'egreso', 'estimado': 20, 'es_fijo': True},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'ingreso', 'estimado': 500},
    ]
    budget_id = _save_sheet_transaction(db, 1, None, 'Mes actual', None, start, end, lines)
    _save_sheet_transaction(db, 2, None, 'Otro usuario', None, start, end, [
        {'id_categoria': 4, 'categoria': 'Privada', 'tipo': 'egreso', 'estimado': 999},
    ])
    fixed, variable, detail, exists = _fetch_monthly_budget_expenses(db, 1)
    assert (fixed, variable, exists) == (20, 30, True)
    assert len(detail) == 2
    lines[0]['estimado'] = 45
    _save_sheet_transaction(db, 1, budget_id, 'Mes actual', None, start, end, lines)
    assert _fetch_monthly_budget_expenses(db, 1)[:2] == (20, 45)
    assert _fetch_monthly_budget_expenses(db, 2)[:2] == (0, 999)


def test_api_refleja_hoja_guardada_y_ajustes_manuales(db, monkeypatch):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    budget_id = _save_sheet_transaction(db, 1, None, 'Mes actual', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 30, 'es_fijo': False},
        {'id_categoria': 2, 'categoria': 'Pagos de Tarjeta de Crédito', 'tipo': 'egreso', 'estimado': 20, 'es_fijo': True},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'ingreso', 'estimado': 100},
    ])
    with db.conn.cursor() as cursor:
        cursor.execute("INSERT INTO tipo_movimiento VALUES (2,'ingreso')")
        cursor.execute('INSERT INTO movimiento VALUES (1,2,1,900,%s)', (today,))
    db.conn.commit()
    database = db._connection_params['database']
    monkeypatch.setattr(presupuesto, 'DatabaseConnector', lambda: DatabaseConnector(host='127.0.0.1', database=database))
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-budget-integration')
    JWTManager(app)
    app.register_blueprint(presupuesto.bp)
    with app.app_context():
        token = create_access_token(identity='1')
    client = app.test_client()
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/presupuesto/libre-mes', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['presupuesto_mensual_guardado'] is True
    assert (data['ingresos_mensuales'], data['gastos_fijos_mensuales'],
            data['gastos_variables_mensuales'], data['dinero_libre_mes']) == (100, 20, 30, 50)
    _save_sheet_transaction(db, 1, budget_id, 'Mes actual', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 70, 'es_fijo': False},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'ingreso', 'estimado': 100},
    ])
    data = client.get('/api/presupuesto/libre-mes', headers=headers).get_json()
    assert (data['gastos_variables_mensuales'], data['dinero_libre_mes']) == (70, 30)
    data = client.get('/api/presupuesto/libre-mes?gastos_variables_mensuales=120', headers=headers).get_json()
    assert data['dinero_libre_mes'] == -20
    data = client.get('/api/presupuesto/libre-mes?ingresos_mensuales=200', headers=headers).get_json()
    assert (data['ingresos_mensuales'], data['dinero_libre_mes']) == (200, 130)


def test_ingresos_presupuestados_respetan_periodo_y_usuario(db):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    presupuesto._ensure_presupuesto_detalle_schema(db)
    assert presupuesto._fetch_monthly_budget_income(db, 1) == 0
    _save_sheet_transaction(db, 1, None, 'Mes actual', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'ingreso', 'estimado': 100},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'ingreso', 'estimado': 51},
        {'id_categoria': 2, 'categoria': 'Pagos de Tarjeta de Crédito', 'tipo': 'egreso', 'estimado': 25},
    ])
    _save_sheet_transaction(db, 2, None, 'Otro usuario', None, start, end, [
        {'id_categoria': 4, 'categoria': 'Privada', 'tipo': 'ingreso', 'estimado': 999},
    ])
    prev_year = today.year - 1
    old_start, old_end = _period_bounds(prev_year, 'mensual', today.month)
    _save_sheet_transaction(db, 1, None, 'Otro año', None, old_start, old_end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'ingreso', 'estimado': 800},
    ])
    assert presupuesto._fetch_monthly_budget_income(db, 1) == 151
    assert presupuesto._fetch_monthly_budget_income(db, 2) == 999


def test_analisis_usa_gastos_reales_y_presupuesto_por_categoria(db, monkeypatch):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    _save_sheet_transaction(db, 1, None, 'Mes', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 80},
        {'id_categoria': 2, 'categoria': 'Pagos de Tarjeta de Crédito', 'tipo': 'egreso', 'estimado': 20},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'ingreso', 'estimado': 500},
    ])
    with db.conn.cursor() as cursor:
        cursor.execute("INSERT INTO tipo_movimiento VALUES (2,'ingreso')")
        cursor.execute("INSERT INTO movimiento VALUES (1,1,1,10,%s),(1,1,2,100,%s),(1,2,1,200,%s),(2,1,1,999,%s)", (today, today, today, today))
        cursor.execute('ALTER TABLE movimiento ADD COLUMN nota TEXT NULL')
        cursor.execute("INSERT INTO movimiento_tarjeta VALUES (1,1,30,'compra','compra',%s,NULL),(1,1,-5,'abono','devolución',%s,NULL),(2,1,999,'compra','otro',%s,NULL)", (today, today, today))
    db.conn.commit()
    database = db._connection_params['database']
    monkeypatch.setattr(analisis, 'DatabaseConnector', lambda: DatabaseConnector(host='127.0.0.1', database=database))
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-analysis-integration')
    JWTManager(app)
    app.register_blueprint(analisis.bp)
    with app.app_context():
        token = create_access_token(identity='1')
    response = app.test_client().get('/api/analisis/vista-consumo?meses=3', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert (data['resumen']['ingresos'], data['resumen']['gastos'], data['resumen']['presupuesto_total']) == (200, 40, 100)
    cats = {c['categoria']: c for c in data['presupuesto_categorias']}
    assert (cats['Comida']['presupuesto'], cats['Comida']['ejecutado']) == (80, 40)
    assert 'Abono al banco' not in cats
    assert len(data['top']) == 2


def test_analisis_limites_sin_datos_y_errores(db, monkeypatch):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    _save_sheet_transaction(db, 1, None, 'Mes', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 80},
    ])
    with db.conn.cursor() as cursor:
        cursor.execute('ALTER TABLE movimiento ADD COLUMN nota TEXT NULL')
    db.conn.commit()
    database = db._connection_params['database']
    monkeypatch.setattr(analisis, 'DatabaseConnector', lambda: DatabaseConnector(host='127.0.0.1', database=database))
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-analysis-boundaries')
    JWTManager(app)
    app.register_blueprint(analisis.bp)
    with app.app_context():
        token = create_access_token(identity='1')
    client = app.test_client()
    headers = {'Authorization': f'Bearer {token}'}
    url = '/api/analisis/vista-consumo?meses=1'
    data = client.get(url, headers=headers).get_json()
    assert data['movimientos_periodo'] == 0
    assert data['presupuesto_categorias'][0]['estado'] == 'sin-datos'
    beginning = today - relativedelta(months=1)
    with db.conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO movimiento (id_cuenta,id_tipo,id_categoria,monto,fecha_creacion) VALUES '
            '(1,1,1,10,%s),(1,1,1,20,%s),(1,1,1,30,%s),(1,1,1,40,%s)',
            (beginning - timedelta(days=1), beginning, today, today + timedelta(days=1)),
        )
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['inicio'] == beginning.isoformat()
    assert data['fin'] == today.isoformat()
    assert data['resumen']['gastos'] == 50
    assert data['movimientos_periodo'] == 2
    previous_start = today.replace(day=1) - relativedelta(months=1)
    expected_previous = sum(
        amount for day, amount in [(beginning - timedelta(days=1), 10), (beginning, 20)]
        if previous_start <= day < today.replace(day=1)
    )
    assert data['comparativa'][0]['mes_anterior'] == expected_previous

    def fail_query(*args):
        raise RuntimeError('fallo de prueba')

    monkeypatch.setattr(analisis, '_datos_consumo', fail_query)
    assert client.get(url, headers=headers).status_code == 500


def test_score_mensual_usa_clasificacion_y_movimientos_reales(db, monkeypatch):
    today = date.today()
    start, end = _period_bounds(today.year, 'mensual', today.month)
    budget_id = _save_sheet_transaction(db, 1, None, 'Mes', None, start, end, [
        {'id_categoria': 1, 'categoria': 'Comida', 'tipo': 'egreso', 'estimado': 5, 'es_fijo': True},
        {'id_categoria': 3, 'categoria': 'Abono al banco', 'tipo': 'egreso', 'estimado': 900, 'es_fijo': False},
    ])
    with db.conn.cursor() as cursor:
        cursor.execute('ALTER TABLE movimiento ADD COLUMN nota TEXT NULL')
        cursor.execute('CREATE TABLE tarjeta_credito (id_persona INT, estado VARCHAR(20), limite_credito DECIMAL(15,2), saldo_actual DECIMAL(15,2))')
        cursor.execute("INSERT INTO tarjeta_credito VALUES (1,'activa',100,80),(1,'inactiva',100,100),(2,'activa',100,100)")
        cursor.execute("INSERT INTO tipo_movimiento VALUES (2,'ingreso')")
        cursor.execute(
            "INSERT INTO movimiento (id_cuenta,id_tipo,id_categoria,monto,fecha_creacion) VALUES "
            "(1,2,1,100,%s),(1,1,1,30,%s),(1,1,3,10,%s),(1,1,2,90,%s),"
            "(2,1,1,999,%s),(1,1,1,999,%s)",
            (today, today, today, today, today, today + timedelta(days=1)),
        )
        cursor.execute("INSERT INTO movimiento_tarjeta VALUES (1,1,10,'compra','compra',%s,NULL),(1,1,-10,'abono','abono',%s,NULL)", (today, today))
    db.conn.commit()
    database = db._connection_params['database']
    monkeypatch.setattr(analisis, 'DatabaseConnector', lambda: DatabaseConnector(host='127.0.0.1', database=database))
    app = Flask(__name__)
    app.config.update(TESTING=True, JWT_SECRET_KEY='test-secret-key-for-score-integration')
    JWTManager(app)
    app.register_blueprint(analisis.bp)
    with app.app_context():
        token = create_access_token(identity='1')
    client = app.test_client()
    url = '/api/analisis/score-salud'
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['componentes'] == {'tasa_ahorro': 50.0, 'pct_gasto_fijo': 80.0, 'uso_tarjetas': 80.0}
    assert data['score'] == 67.0 and data['nivel'] == 'Estable'
    assert not data['razones']

    with db.conn.cursor() as cursor:
        cursor.execute('DELETE FROM tarjeta_credito')
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['score'] == 85.0 and data['componentes']['uso_tarjetas'] is None
    with db.conn.cursor() as cursor:
        cursor.execute("INSERT INTO tarjeta_credito VALUES (1,'activa',0,10)")
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['score'] is None and any('tarjetas activas' in r for r in data['razones'])

    with db.conn.cursor() as cursor:
        cursor.execute('DELETE FROM tarjeta_credito')
        cursor.execute('DELETE FROM presupuesto_detalle WHERE id_presupuesto=%s AND id_categoria=3', (budget_id,))
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['score'] is None and data['componentes']['pct_gasto_fijo'] is None
    assert 'Abono al banco' in data['razones'][0]

    with db.conn.cursor() as cursor:
        cursor.execute('UPDATE presupuesto_detalle SET es_fijo=0 WHERE id_presupuesto=%s AND id_categoria=1', (budget_id,))
        cursor.execute("INSERT INTO presupuesto_detalle (id_presupuesto,id_categoria,categoria_nombre,tipo,es_fijo,monto_estimado) VALUES (%s,1,'Comida','egreso',1,5)", (budget_id,))
        cursor.execute('DELETE FROM tarjeta_credito')
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['score'] is None and 'Comida' in data['razones'][0]
    assert data['componentes']['uso_tarjetas'] is None

    with db.conn.cursor() as cursor:
        cursor.execute('DELETE FROM movimiento')
        cursor.execute('DELETE FROM movimiento_tarjeta')
    db.conn.commit()
    data = client.get(url, headers=headers).get_json()
    assert data['score'] is None
    assert any('ingresos' in r for r in data['razones'])
    assert any('gastos' in r for r in data['razones'])

    with db.conn.cursor() as cursor:
        cursor.execute('DROP TABLE tarjeta_credito')
    db.conn.commit()
    assert client.get(url, headers=headers).status_code == 500
