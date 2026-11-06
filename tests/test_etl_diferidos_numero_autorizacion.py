import os
import uuid
from datetime import date

import pandas as pd

from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito
from src.database.db_connector import DatabaseConnector


def test_etl_crea_diferido_con_numero_autorizacion_numerico(tmp_path):
    db = DatabaseConnector()
    persona_id = 1
    numero_tarjeta = f"99990000{uuid.uuid4().int % 100000:05d}"

    try:
        result = db.execute_non_query(
            """
            INSERT INTO tarjeta_credito (
                numero_tarjeta, nombre_titular, banco, tipo_tarjeta,
                limite_credito, saldo_inicial, saldo_actual, fecha_vencimiento,
                fecha_corte, fecha_pago, estado, id_persona
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                numero_tarjeta,
                'Test ETL Diferido',
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

        df = pd.DataFrame([
            {
                'Número de Autorización': 2,
                'Fecha de Transacción': '2026-04-11',
                'Descripción': 'COMPRA DIFERIDA PRUEBA',
                'Valor Original': '787.600,00',
                'Tasa Pactada': '19.957%',
                'Tasa EA Facturada': '26,76%',
                'Cargos y Abonos': '78.448,00',
                'Saldo a Diferir': '470.688,00',
                'Cuotas': '1/7',
            }
        ])
        file_path = tmp_path / 'test_diferido.xlsx'
        df.to_excel(file_path, index=False)

        etl = ETLTarjetaCredito(db)
        processed, errors = etl.process_file(str(file_path), persona_id, tarjeta_id)

        assert processed == 1
        assert errors == []

        diferidos = db.execute_query(
            "SELECT COUNT(*) AS total FROM tarjeta_diferido WHERE id_persona = %s AND id_tarjeta = %s",
            (persona_id, tarjeta_id),
        ) or []
        assert int((diferidos[0] or {}).get('total') or 0) == 1
    finally:
        db.execute_non_query(
            "DELETE FROM tarjeta_diferido WHERE id_persona = %s AND id_tarjeta IN (SELECT id_tarjeta FROM tarjeta_credito WHERE numero_tarjeta = %s)",
            (persona_id, numero_tarjeta),
        )
        db.execute_non_query("DELETE FROM tarjeta_credito WHERE numero_tarjeta = %s", (numero_tarjeta,))
        db.close()
