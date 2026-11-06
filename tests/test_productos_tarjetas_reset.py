import logging
import os
from datetime import date

from flask_jwt_extended import create_access_token

from app import create_app
from src.database.db_connector import DatabaseConnector


def test_list_productos_no_depende_de_vista_unificada(caplog):
    app = create_app('development')
    app.config['TESTING'] = True

    with app.app_context():
        db = DatabaseConnector()
        try:
            persona_id = 1
            token = create_access_token(identity=str(persona_id), fresh=True)

            with app.test_client() as client:
                with caplog.at_level(logging.ERROR):
                    response = client.get('/api/productos', headers={'Authorization': f'Bearer {token}'})

            assert response.status_code == 200
            assert not any('v_producto_unificado' in record.getMessage() for record in caplog.records)
        finally:
            db.close()


def test_list_productos_usa_movimientos_y_diferidos_cuando_saldo_actual_es_cero():
    app = create_app('development')
    app.config['TESTING'] = True

    with app.app_context():
        db = DatabaseConnector()
        try:
            persona_id = 1
            token = create_access_token(identity=str(persona_id), fresh=True)

            result = db.execute_non_query(
                """
                INSERT INTO tarjeta_credito (
                    numero_tarjeta, nombre_titular, banco, tipo_tarjeta,
                    limite_credito, saldo_inicial, saldo_actual, fecha_vencimiento,
                    fecha_corte, fecha_pago, estado, id_persona
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    '9999000011113333',
                    'Test Saldo',
                    'Banco Test',
                    'credito',
                    1000000,
                    0,
                    0,
                    date.today().isoformat(),
                    date.today().isoformat(),
                    date.today().isoformat(),
                    'activa',
                    persona_id,
                ),
            )
            tarjeta_id = int(result) if result not in (None, 0) else None
            assert tarjeta_id is not None

            db.execute_non_query(
                """
                INSERT INTO movimiento_tarjeta (
                    id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tarjeta_id,
                    persona_id,
                    date.today().isoformat(),
                    125000,
                    'compra',
                    'Movimiento de prueba',
                    'TX-SALDO-1',
                ),
            )

            db.execute_non_query(
                """
                INSERT INTO tarjeta_diferido (
                    id_tarjeta, id_persona, descripcion, valor_total, numero_cuotas,
                    tasa_mensual, sin_interes, cuota_mensual, total_intereses,
                    total_pagado_estimado, cuotas_pagadas, saldo_pendiente,
                    fecha_compra, fecha_proximo_pago, estado, numero_transaccion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tarjeta_id,
                    persona_id,
                    'Diferido de prueba',
                    525688,
                    7,
                    0,
                    0,
                    75098,
                    0,
                    525688,
                    0,
                    525688,
                    date.today().isoformat(),
                    date.today().isoformat(),
                    'activo',
                    'TX-DIF-2',
                ),
            )

            with app.test_client() as client:
                response = client.get('/api/productos', headers={'Authorization': f'Bearer {token}'})

            assert response.status_code == 200
            payload = response.get_json()
            tarjetas = payload.get('tarjetas') or []
            match = next((t for t in tarjetas if int(t.get('id')) == tarjeta_id), None)
            assert match is not None
            assert float(match.get('saldo_actual') or 0) == 650688.0
        finally:
            db.execute_non_query("DELETE FROM movimiento_tarjeta WHERE numero_transaccion = %s", ('TX-SALDO-1',))
            db.execute_non_query("DELETE FROM tarjeta_diferido WHERE numero_transaccion = %s", ('TX-DIF-2',))
            db.execute_non_query("DELETE FROM tarjeta_credito WHERE numero_tarjeta = %s", ('9999000011113333',))
            db.close()


def test_recetar_tarjeta_borra_movimientos_y_cero_saldo():
    app = create_app('development')
    app.config['TESTING'] = True

    with app.app_context():
        db = DatabaseConnector()
        try:
            persona_id = 1
            token = create_access_token(identity=str(persona_id), fresh=True)

            result = db.execute_non_query(
                """
                INSERT INTO tarjeta_credito (
                    numero_tarjeta, nombre_titular, banco, tipo_tarjeta,
                    limite_credito, saldo_inicial, saldo_actual, fecha_vencimiento,
                    fecha_corte, fecha_pago, estado, id_persona
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    '9999000011112222',
                    'Test Reset',
                    'Banco Test',
                    'credito',
                    1000000,
                    100000,
                    100000,
                    date.today().isoformat(),
                    date.today().isoformat(),
                    date.today().isoformat(),
                    'activa',
                    persona_id,
                ),
            )
            tarjeta_id = int(result) if result not in (None, 0) else None
            assert tarjeta_id is not None

            db.execute_non_query(
                """
                INSERT INTO movimiento_tarjeta (
                    id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tarjeta_id,
                    persona_id,
                    date.today().isoformat(),
                    125000,
                    'compra',
                    'Movimiento de prueba',
                    'TX-RESET-1',
                ),
            )

            db.execute_non_query(
                """
                INSERT INTO tarjeta_diferido (
                    id_tarjeta, id_persona, descripcion, valor_total, numero_cuotas,
                    tasa_mensual, sin_interes, cuota_mensual, total_intereses,
                    total_pagado_estimado, cuotas_pagadas, saldo_pendiente,
                    fecha_compra, fecha_proximo_pago, estado, numero_transaccion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    tarjeta_id,
                    persona_id,
                    'Diferido de prueba',
                    525688,
                    7,
                    0,
                    0,
                    75098,
                    0,
                    525688,
                    0,
                    525688,
                    date.today().isoformat(),
                    date.today().isoformat(),
                    'activo',
                    'TX-DIF-1',
                ),
            )

            with app.test_client() as client:
                response = client.post(
                    f'/api/productos/tarjetas/{tarjeta_id}/recetar',
                    headers={'Authorization': f'Bearer {token}'},
                )

            assert response.status_code == 200
            movements = db.execute_query(
                "SELECT COUNT(*) AS total FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s",
                (tarjeta_id, persona_id),
            ) or []
            assert int((movements[0] or {}).get('total') or 0) == 0

            diferidos = db.execute_query(
                "SELECT COUNT(*) AS total FROM tarjeta_diferido WHERE id_tarjeta = %s AND id_persona = %s",
                (tarjeta_id, persona_id),
            ) or []
            assert int((diferidos[0] or {}).get('total') or 0) == 0

            cards = db.execute_query(
                "SELECT saldo_actual, saldo_inicial FROM tarjeta_credito WHERE id_tarjeta = %s AND id_persona = %s",
                (tarjeta_id, persona_id),
            ) or []
            assert cards
            assert float((cards[0] or {}).get('saldo_actual') or 0) == 0.0
            assert float((cards[0] or {}).get('saldo_inicial') or 0) == 0.0
        finally:
            db.execute_non_query("DELETE FROM movimiento_tarjeta WHERE numero_transaccion = %s", ('TX-RESET-1',))
            db.execute_non_query("DELETE FROM tarjeta_diferido WHERE numero_transaccion = %s", ('TX-DIF-1',))
            db.execute_non_query("DELETE FROM tarjeta_credito WHERE numero_tarjeta = %s", ('9999000011112222',))
            db.close()
