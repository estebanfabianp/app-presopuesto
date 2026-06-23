from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector


ULTIMOS_4 = "1654"
OUT_REF = Path("storage/temp/comparativa_1654_por_referencia.png")
OUT_MES = Path("storage/temp/comparativa_1654_mensual.png")


def main() -> None:
    db = DatabaseConnector()
    try:
        card = db.execute_query(
            """
            SELECT id_tarjeta, numero_tarjeta
            FROM tarjeta_credito
            WHERE RIGHT(numero_tarjeta, 4) = %s
            ORDER BY id_tarjeta DESC
            LIMIT 1
            """,
            (ULTIMOS_4,),
        )
        if not card:
            raise RuntimeError("No se encontro tarjeta terminada en 1654")

        id_tarjeta = int(card[0]["id_tarjeta"])

        rows = db.execute_query(
            """
            SELECT
                td.id_diferido,
                td.fecha_compra,
                COALESCE(td.numero_transaccion, CONCAT('SIN_REF_', td.id_diferido)) AS referencia,
                td.numero_cuotas,
                td.cuotas_pagadas,
                td.cuota_mensual AS cuota_despues,
                td.saldo_pendiente AS saldo_despues,
                mt.valor AS valor_movimiento,
                mt.estado AS estado_mov
            FROM tarjeta_diferido td
            JOIN movimiento_tarjeta mt ON mt.id_movimiento_tarjeta = td.id_movimiento_tarjeta
            WHERE td.id_tarjeta = %s
              AND td.numero_cuotas > 1
              AND mt.estado = 'diferido'
            ORDER BY td.fecha_compra, td.id_diferido
            """,
            (id_tarjeta,),
        )

        if not rows:
            raise RuntimeError("No hay diferidos para comparar")

        df = pd.DataFrame(rows)
        for col in ["numero_cuotas", "cuotas_pagadas", "cuota_despues", "saldo_despues", "valor_movimiento"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Reconstruccion del 'antes' con la logica antigua:
        # cuota_antes = valor_movimiento, saldo_antes = cuota_antes * (n - pagadas - 1)
        df["cuota_antes"] = df["valor_movimiento"]
        df["saldo_antes"] = (df["cuota_antes"] * (df["numero_cuotas"] - df["cuotas_pagadas"] - 1)).clip(lower=0)

        # ---------- Grafica por referencia ----------
        OUT_REF.parent.mkdir(parents=True, exist_ok=True)
        top = df.copy()
        top = top.sort_values("saldo_antes", ascending=False).head(12)

        x = range(len(top))
        width = 0.36

        fig1, ax1 = plt.subplots(figsize=(14, 7))
        ax1.bar([i - width / 2 for i in x], top["saldo_antes"], width=width, label="Saldo pendiente antes", color="#ef4444")
        ax1.bar([i + width / 2 for i in x], top["saldo_despues"], width=width, label="Saldo pendiente despues", color="#16a34a")
        ax1.set_title("Tarjeta 1654 - Diferidos por referencia (antes vs despues)")
        ax1.set_ylabel("COP")
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(top["referencia"].tolist(), rotation=45, ha="right")
        ax1.grid(axis="y", alpha=0.3)
        ax1.legend(loc="best")
        fig1.tight_layout()
        fig1.savefig(OUT_REF, dpi=150)

        # ---------- Grafica mensual ----------
        df["mes"] = pd.to_datetime(df["fecha_compra"]).dt.strftime("%Y-%m")
        mensual = (
            df.groupby("mes", as_index=False)[["saldo_antes", "saldo_despues", "cuota_antes", "cuota_despues"]]
            .sum()
            .sort_values("mes")
        )

        fig2, ax2 = plt.subplots(figsize=(13, 7))
        ax2.plot(mensual["mes"], mensual["saldo_antes"], marker="o", label="Saldo pendiente antes", color="#ef4444")
        ax2.plot(mensual["mes"], mensual["saldo_despues"], marker="o", label="Saldo pendiente despues", color="#16a34a")
        ax2.plot(mensual["mes"], mensual["cuota_despues"], marker="o", label="Cuota mensual despues", color="#2563eb")
        ax2.set_title("Tarjeta 1654 - Comparativo mensual antes vs despues")
        ax2.set_ylabel("COP")
        ax2.set_xlabel("Mes")
        ax2.grid(alpha=0.3)
        ax2.legend(loc="best")
        plt.xticks(rotation=45)
        fig2.tight_layout()
        fig2.savefig(OUT_MES, dpi=150)

        total_antes = float(df["saldo_antes"].sum())
        total_despues = float(df["saldo_despues"].sum())

        print("Grafica por referencia:", OUT_REF)
        print("Grafica mensual:", OUT_MES)
        print("Total saldo pendiente antes:", f"{total_antes:,.2f}")
        print("Total saldo pendiente despues:", f"{total_despues:,.2f}")
        print("Reduccion:", f"{(total_antes - total_despues):,.2f}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
