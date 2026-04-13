"""Genera datos de prueba para transaccion_programada.

Uso:
  python scripts/seed/generate_programadas_test_data.py --cantidad 30
  python scripts/seed/generate_programadas_test_data.py --cantidad 20 --reset
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_connector import DatabaseConnector


def _pick_random(rows, key):
    if not rows:
        return None
    return random.choice(rows).get(key)


def _build_numero(i: int, when: date) -> str:
    return f"TP-{when.strftime('%Y%m%d')}-{i:03d}"


def _random_fecha() -> date:
    # Mezcla de fechas pasadas/actuales/futuras para validar UI y KPIs.
    return date.today() + timedelta(days=random.randint(-20, 120))


def _random_monto(tipo_nombre: str) -> float:
    if (tipo_nombre or "").lower() == "ingreso":
        return round(random.uniform(150000, 3500000), 2)
    return round(random.uniform(20000, 1200000), 2)


def generate(cantidad: int, reset: bool) -> int:
    db = DatabaseConnector()
    conn = db.conn
    if not conn:
        raise RuntimeError("No se pudo conectar a la base de datos")

    inserted = 0
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_tipo, nombre FROM tipo_movimiento ORDER BY id_tipo")
        tipos = cursor.fetchall() or []
        if not tipos:
            raise RuntimeError("No hay tipos de movimiento en tabla tipo_movimiento")

        cursor.execute("SELECT id_categoria FROM categoria WHERE estado = 1 ORDER BY id_categoria")
        categorias = cursor.fetchall() or []

        cursor.execute("SELECT id_beneficiario FROM beneficiario WHERE estado = 1 ORDER BY id_beneficiario")
        beneficiarios = cursor.fetchall() or []

        if reset:
            cursor.execute("DELETE FROM transaccion_programada")
            conn.commit()

        insert_sql = """
            INSERT INTO transaccion_programada
                (fecha, id_tipo, numero_transaccion, monto, repeticion, id_categoria, id_beneficiario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        repeticiones = [0, 1, 2, 3, 6, 12, 24]

        for i in range(1, cantidad + 1):
            tipo_row = random.choice(tipos)
            fecha = _random_fecha()
            id_tipo = tipo_row["id_tipo"]
            tipo_nombre = tipo_row.get("nombre", "")
            monto = _random_monto(tipo_nombre)

            numero = _build_numero(i, fecha)
            repeticion = random.choice(repeticiones)
            id_categoria = _pick_random(categorias, "id_categoria")
            id_beneficiario = _pick_random(beneficiarios, "id_beneficiario")

            cursor.execute(
                insert_sql,
                (fecha, id_tipo, numero, monto, repeticion, id_categoria, id_beneficiario),
            )
            inserted += 1

        conn.commit()
        return inserted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generar datos de prueba para transacciones programadas")
    parser.add_argument("--cantidad", type=int, default=25, help="Cantidad de registros a generar")
    parser.add_argument("--reset", action="store_true", help="Elimina registros existentes antes de insertar")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para resultados reproducibles")
    args = parser.parse_args()

    if args.cantidad <= 0:
        raise SystemExit("La cantidad debe ser mayor que 0")

    random.seed(args.seed)
    total = generate(args.cantidad, args.reset)
    print(f"OK: se insertaron {total} transacciones programadas de prueba")


if __name__ == "__main__":
    main()
