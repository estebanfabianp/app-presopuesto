from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector


OUTPUT_CSV = ROOT_DIR / "storage" / "temp" / "auditoria_diferidos_1654.csv"


def main() -> None:
    db = DatabaseConnector()
    try:
        rows = db.execute_query(
            """
            SELECT
                mt.id_movimiento_tarjeta,
                mt.fecha,
                DATE_FORMAT(mt.fecha, '%Y-%m') AS mes,
                mt.numero_transaccion,
                mt.nota,
                mt.valor AS valor_movimiento,
                mt.cuotas AS cuotas_movimiento,
                td.id_diferido,
                td.fecha_compra,
                td.numero_cuotas,
                td.cuotas_pagadas,
                td.cuota_mensual,
                td.valor_total,
                td.saldo_pendiente,
                td.estado AS estado_diferido,
                ROUND(mt.valor - td.saldo_pendiente, 2) AS delta_mov_vs_saldo,
                ROUND(mt.valor - td.cuota_mensual, 2) AS delta_mov_vs_cuota
            FROM movimiento_tarjeta mt
            LEFT JOIN tarjeta_diferido td
              ON td.id_tarjeta = mt.id_tarjeta
             AND (
                  td.numero_transaccion = mt.numero_transaccion
                  OR (td.numero_transaccion IS NULL AND mt.numero_transaccion IS NULL)
                 )
            WHERE mt.id_tarjeta = 33
              AND mt.estado = 'diferido'
            ORDER BY mt.fecha, mt.id_movimiento_tarjeta
            """
        )

        if not rows:
            print("No hay movimientos diferidos para exportar")
            return

        df = pd.DataFrame(rows)
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

        print(f"CSV generado en: {OUTPUT_CSV}")
        print(f"Filas exportadas: {len(df)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
