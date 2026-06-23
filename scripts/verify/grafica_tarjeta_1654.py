from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector


ID_TARJETA = 33
OUTPUT_PATH = Path("storage/temp/grafica_tarjeta_1654.png")


def main() -> None:
    db = DatabaseConnector()
    try:
        tarjeta = db.execute_query(
            """
            SELECT id_tarjeta, numero_tarjeta, saldo_inicial, saldo_actual, limite_credito
            FROM tarjeta_credito
            WHERE id_tarjeta = %s
            """,
            (ID_TARJETA,),
        )
        if not tarjeta:
            raise RuntimeError(f"No existe la tarjeta {ID_TARJETA}")

        t = tarjeta[0]
        saldo_inicial = float(t["saldo_inicial"] or 0)
        saldo_actual = float(t["saldo_actual"] or 0)

        movimientos = db.execute_query(
            """
            SELECT DATE_FORMAT(fecha,'%Y-%m') AS mes,
                   SUM(CASE WHEN estado='compra' THEN valor WHEN estado='abono' THEN -valor ELSE 0 END) AS impacto_neto,
                   SUM(CASE WHEN estado='compra' THEN valor ELSE 0 END) AS compras,
                   SUM(CASE WHEN estado='abono' THEN valor ELSE 0 END) AS abonos
            FROM movimiento_tarjeta
            WHERE id_tarjeta = %s
            GROUP BY DATE_FORMAT(fecha,'%Y-%m')
            ORDER BY mes
            """,
            (ID_TARJETA,),
        )

        diferidos = db.execute_query(
            """
            SELECT DATE_FORMAT(fecha_compra,'%Y-%m') AS mes,
                   SUM(valor_total) AS diferido_total_origen,
                   SUM(saldo_pendiente) AS diferido_pendiente_origen
            FROM tarjeta_diferido
            WHERE id_tarjeta = %s
            GROUP BY DATE_FORMAT(fecha_compra,'%Y-%m')
            ORDER BY mes
            """,
            (ID_TARJETA,),
        )

        df_mov = pd.DataFrame(movimientos)
        df_dif = pd.DataFrame(diferidos)

        if df_mov.empty:
            raise RuntimeError("No hay movimientos para graficar")

        for col in ["impacto_neto", "compras", "abonos"]:
            df_mov[col] = pd.to_numeric(df_mov[col], errors="coerce").fillna(0.0)

        if df_dif.empty:
            df_dif = pd.DataFrame(columns=["mes", "diferido_total_origen", "diferido_pendiente_origen"])
        for col in ["diferido_total_origen", "diferido_pendiente_origen"]:
            if col in df_dif.columns:
                df_dif[col] = pd.to_numeric(df_dif[col], errors="coerce").fillna(0.0)

        df = df_mov.merge(df_dif, on="mes", how="left").fillna(0.0)
        df["saldo_mov_acumulado"] = saldo_inicial + df["impacto_neto"].cumsum()

        dif_activo_actual = float(
            db.execute_query(
                """
                SELECT COALESCE(SUM(saldo_pendiente), 0) AS total
                FROM tarjeta_diferido
                WHERE id_tarjeta = %s AND estado = 'activo'
                """,
                (ID_TARJETA,),
            )[0]["total"]
            or 0
        )

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
        x = df["mes"].tolist()

        ax1.plot(x, df["saldo_mov_acumulado"], marker="o", linewidth=2, label="Saldo acumulado por movimientos")
        ax1.axhline(saldo_actual, color="red", linestyle="--", linewidth=1.5, label=f"Saldo actual BD: {saldo_actual:,.2f}")
        ax1.axhline(
            df["saldo_mov_acumulado"].iloc[-1] + dif_activo_actual,
            color="purple",
            linestyle=":",
            linewidth=1.5,
            label=f"Mov acumulado + diferido activo actual: {df['saldo_mov_acumulado'].iloc[-1] + dif_activo_actual:,.2f}",
        )
        ax1.set_title("Tarjeta 1654 - Evolucion mensual y validacion del saldo")
        ax1.set_ylabel("COP")
        ax1.grid(alpha=0.3)
        ax1.legend(loc="best")

        width = 0.25
        idx = range(len(x))
        ax2.bar([i - width for i in idx], df["compras"], width=width, label="Compras")
        ax2.bar(idx, df["abonos"], width=width, label="Abonos")
        ax2.bar([i + width for i in idx], df["diferido_pendiente_origen"], width=width, label="Diferido pendiente originado")
        ax2.set_ylabel("COP")
        ax2.set_xlabel("Mes")
        ax2.set_xticks(list(idx))
        ax2.set_xticklabels(x, rotation=45)
        ax2.grid(alpha=0.3)
        ax2.legend(loc="best")

        fig.tight_layout()
        fig.savefig(OUTPUT_PATH, dpi=150)

        print("Grafica generada en:", OUTPUT_PATH)
        print("Saldo inicial:", f"{saldo_inicial:,.2f}")
        print("Saldo actual BD:", f"{saldo_actual:,.2f}")
        print("Saldo por movimientos acumulado ultimo mes:", f"{df['saldo_mov_acumulado'].iloc[-1]:,.2f}")
        print("Diferido activo actual:", f"{dif_activo_actual:,.2f}")
        print(
            "Control (mov acumulado + diferido activo):",
            f"{(df['saldo_mov_acumulado'].iloc[-1] + dif_activo_actual):,.2f}",
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
