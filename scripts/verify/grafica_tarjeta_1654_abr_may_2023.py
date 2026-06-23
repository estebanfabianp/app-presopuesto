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
FECHA_INICIO = "2023-04-01"
FECHA_FIN = "2023-05-31"
OUTPUT_PATH = Path("storage/temp/grafica_tarjeta_1654_abr_may_2023.png")


def main() -> None:
    db = DatabaseConnector()
    try:
        tarjeta_rows = db.execute_query(
            """
            SELECT id_tarjeta, numero_tarjeta
            FROM tarjeta_credito
            WHERE RIGHT(numero_tarjeta, 4) = %s
            ORDER BY id_tarjeta DESC
            LIMIT 1
            """,
            (ULTIMOS_4,),
        )
        if not tarjeta_rows:
            raise RuntimeError("No se encontro tarjeta terminada en 1654")

        id_tarjeta = int(tarjeta_rows[0]["id_tarjeta"])

        mov_rows = db.execute_query(
            """
            SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
                   SUM(CASE WHEN estado = 'compra' THEN valor ELSE 0 END) AS compras,
                   SUM(CASE WHEN estado = 'abono' THEN valor ELSE 0 END) AS abonos
            FROM movimiento_tarjeta
            WHERE id_tarjeta = %s
              AND fecha BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(fecha, '%Y-%m')
            ORDER BY mes
            """,
            (id_tarjeta, FECHA_INICIO, FECHA_FIN),
        )

        dif_rows = db.execute_query(
            """
            SELECT DATE_FORMAT(fecha_compra, '%Y-%m') AS mes,
                   SUM(saldo_pendiente) AS saldo_diferido
            FROM tarjeta_diferido
            WHERE id_tarjeta = %s
              AND fecha_compra BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(fecha_compra, '%Y-%m')
            ORDER BY mes
            """,
            (id_tarjeta, FECHA_INICIO, FECHA_FIN),
        )

        meses_base = pd.DataFrame({"mes": ["2023-04", "2023-05"]})
        df_mov = pd.DataFrame(mov_rows)
        df_dif = pd.DataFrame(dif_rows)

        if df_mov.empty:
            df_mov = pd.DataFrame(columns=["mes", "compras", "abonos"])
        if df_dif.empty:
            df_dif = pd.DataFrame(columns=["mes", "saldo_diferido"])

        for col in ["compras", "abonos"]:
            if col in df_mov.columns:
                df_mov[col] = pd.to_numeric(df_mov[col], errors="coerce").fillna(0.0)
        if "saldo_diferido" in df_dif.columns:
            df_dif["saldo_diferido"] = pd.to_numeric(df_dif["saldo_diferido"], errors="coerce").fillna(0.0)

        df = meses_base.merge(df_mov, on="mes", how="left").merge(df_dif, on="mes", how="left").fillna(0.0)

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots(figsize=(11, 6))
        x = range(len(df))
        width = 0.24

        ax.bar([i - width for i in x], df["compras"], width=width, label="Compras", color="#2563eb")
        ax.bar(x, df["abonos"], width=width, label="Abonos", color="#16a34a")
        ax.bar([i + width for i in x], df["saldo_diferido"], width=width, label="Saldo diferido", color="#dc2626")

        ax.set_title("Tarjeta 1654 - Abril a Mayo 2023")
        ax.set_ylabel("COP")
        ax.set_xlabel("Mes")
        ax.set_xticks(list(x))
        ax.set_xticklabels(df["mes"].tolist())
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="best")

        fig.tight_layout()
        fig.savefig(OUTPUT_PATH, dpi=150)

        print("Grafica generada en:", OUTPUT_PATH)
        for _, row in df.iterrows():
            print(
                f"{row['mes']} | compras={row['compras']:.2f} | "
                f"abonos={row['abonos']:.2f} | saldo_diferido={row['saldo_diferido']:.2f}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
