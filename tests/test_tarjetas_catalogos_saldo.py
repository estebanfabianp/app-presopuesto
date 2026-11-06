from datetime import date

from flask_jwt_extended import create_access_token

from app import create_app
from src.database.db_connector import DatabaseConnector


def test_catalogos_tarjetas_usa_movimientos_y_diferidos_cuando_saldo_actual_es_cero():
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
                    '9999000011114444',
                    'Test Catalogo',
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
                    'TX-CAT-1',
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
                    'TX-DIF-3',
                ),
            )

            with app.test_client() as client:
                response = client.get('/api/tarjetas/catalogos', headers={'Authorization': f'Bearer {token}'})

            assert response.status_code == 200
            payload = response.get_json()
            tarjetas = payload.get('tarjetas') or []
            match = next((t for t in tarjetas if int(t.get('id_tarjeta')) == tarjeta_id), None)
            assert match is not None
            assert float(match.get('saldo_actual') or 0) == 650688.0
        finally:
            db.execute_non_query("DELETE FROM movimiento_tarjeta WHERE numero_transaccion = %s", ('TX-CAT-1',))
            db.execute_non_query("DELETE FROM tarjeta_diferido WHERE numero_transaccion = %s", ('TX-DIF-3',))
            db.execute_non_query("DELETE FROM tarjeta_credito WHERE numero_tarjeta = %s", ('9999000011114444',))
            db.close()
