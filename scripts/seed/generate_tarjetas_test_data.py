"""
Genera datos de prueba para el modulo de tarjetas.

Uso:
  python scripts/seed/generate_tarjetas_test_data.py
  python scripts/seed/generate_tarjetas_test_data.py --user-id 1 --rows 120 --months 12 --clean
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

TAG = "TST-TAR"
ESTADOS = ["compra", "abono", "diferido", "pendiente", "aprobado"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generador de datos de prueba para tarjetas")
    parser.add_argument("--user-id", type=int, default=1, help="ID de persona")
    parser.add_argument("--rows", type=int, default=80, help="Cantidad de movimientos a insertar")
    parser.add_argument("--months", type=int, default=8, help="Rango en meses hacia atras")
    parser.add_argument("--clean", action="store_true", help="Eliminar semillas previas del script")
    parser.add_argument("--seed", type=int, default=20260412, help="Semilla random para resultados repetibles")
    return parser.parse_args()


def random_date(months_back: int) -> date:
    end = date.today()
    start = end - timedelta(days=max(30, months_back * 30))
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def pick_estado() -> str:
    # Compras predominan; abonos frecuentes; resto menor.
    return random.choices(
        population=ESTADOS,
        weights=[62, 22, 6, 7, 3],
        k=1,
    )[0]


def get_or_create_tarjeta(cursor, user_id: int) -> int:
    cursor.execute(
        """
        SELECT DISTINCT tc.id_tarjeta
        FROM tarjeta_credito tc
        JOIN movimiento_tarjeta mt ON mt.id_tarjeta = tc.id_tarjeta
        WHERE mt.id_persona = %s
        ORDER BY tc.id_tarjeta
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        return int(row[0])

    numero = "9999" + str(random.randint(100000000000, 999999999999))
    cursor.execute("SELECT id_estado FROM estado_tarjeta ORDER BY id_estado LIMIT 1")
    st = cursor.fetchone()
    estado_id = int(st[0]) if st else 1

    cursor.execute(
        """
        INSERT INTO tarjeta_credito
            (id_producto, numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, fecha_creacion, id_estado)
        VALUES
            (NULL, %s, %s, %s, %s, %s, NOW(), %s)
        """,
        (numero[:16], 5000000, 0, date.today().replace(day=20), date.today().replace(day=5), estado_id),
    )
    return int(cursor.lastrowid)


def load_catalogs(cursor):
    cursor.execute("SELECT id_categoria FROM categoria WHERE estado = 1 ORDER BY id_categoria")
    categorias = [int(r[0]) for r in (cursor.fetchall() or [])]

    cursor.execute("SELECT id_beneficiario FROM beneficiario WHERE estado = 1 ORDER BY id_beneficiario")
    beneficiarios = [int(r[0]) for r in (cursor.fetchall() or [])]

    return categorias, beneficiarios


def build_row(user_id: int, id_tarjeta: int, categorias: list[int], beneficiarios: list[int], months: int, idx: int):
    estado = pick_estado()
    fecha = random_date(months)

    if estado == "abono":
        valor = round(random.uniform(60000, 1200000), 2)
        cuotas = 1
        id_categoria = None
        id_beneficiario = None
        nota = random.choice([
            "Pago parcial de tarjeta",
            "Abono automatico",
            "Pago extra",
            "Abono por PSE",
        ])
    else:
        valor = round(random.uniform(18000, 700000), 2)
        cuotas = random.randint(2, 12) if estado == "diferido" else 1
        id_categoria = random.choice(categorias) if categorias and random.random() > 0.08 else None
        id_beneficiario = random.choice(beneficiarios) if beneficiarios and random.random() > 0.15 else None
        nota = random.choice([
            "Compra en comercio",
            "Consumo diario",
            "Pago de servicio",
            "Compra online",
            "Gasto planificado",
            "Compra supermercado",
        ])

    num_tx = f"{TAG}-{user_id}-{fecha.strftime('%Y%m%d')}-{idx:04d}-{random.randint(100,999)}"

    return (
        id_tarjeta,
        user_id,
        fecha,
        valor,
        estado,
        nota,
        num_tx,
        id_categoria,
        id_beneficiario,
        cuotas,
    )


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    db = DatabaseConnector()
    if not db.conn:
        print("ERROR: no se pudo conectar a la BD")
        return 1

    conn = db.conn
    cursor = conn.cursor()

    try:
        id_tarjeta = get_or_create_tarjeta(cursor, args.user_id)
        categorias, beneficiarios = load_catalogs(cursor)

        if args.clean:
            cursor.execute(
                "DELETE FROM movimiento_tarjeta WHERE id_persona = %s AND numero_transaccion LIKE %s",
                (args.user_id, f"{TAG}-%"),
            )
            print(f"Limpieza: {cursor.rowcount} movimientos eliminados")

        insert_sql = """
            INSERT INTO movimiento_tarjeta
                (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, cuotas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        rows = [
            build_row(args.user_id, id_tarjeta, categorias, beneficiarios, args.months, i + 1)
            for i in range(args.rows)
        ]
        cursor.executemany(insert_sql, rows)
        conn.commit()

        cursor.execute(
            """
            SELECT estado, COUNT(*)
            FROM movimiento_tarjeta
            WHERE id_persona = %s AND numero_transaccion LIKE %s
            GROUP BY estado
            ORDER BY COUNT(*) DESC
            """,
            (args.user_id, f"{TAG}-%"),
        )
        stats = cursor.fetchall() or []

        print("OK: datos de prueba creados")
        print(f"Usuario: {args.user_id}")
        print(f"Tarjeta usada: {id_tarjeta}")
        print(f"Movimientos insertados: {args.rows}")
        for estado, cnt in stats:
            print(f"  - {estado}: {cnt}")
        print(f"Filtro para limpiar luego: numero_transaccion LIKE '{TAG}-%'")
        return 0

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        return 1
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
