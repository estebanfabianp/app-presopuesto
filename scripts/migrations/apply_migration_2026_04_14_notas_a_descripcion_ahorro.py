#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra Nota -> Codigo (Descripcion) para la cuenta de ahorro objetivo."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector


def main() -> int:
    db = DatabaseConnector()
    cursor = db.conn.cursor(dictionary=True)

    try:
        # Cuenta objetivo (la que se ha venido ajustando en la sesion)
        cursor.execute(
            "SELECT id_cuenta, nombre FROM cuenta WHERE nombre LIKE %s LIMIT 1",
            ("%cuanto de ahorros%",),
        )
        cuenta = cursor.fetchone()
        if not cuenta:
            print("No se encontro la cuenta objetivo.")
            return 1

        id_cuenta = int(cuenta["id_cuenta"])
        print(f"Cuenta objetivo: {cuenta['nombre']} (ID: {id_cuenta})")

        # Copiar nota -> codigo (campo usado como descripcion)
        update_sql = """
            UPDATE movimiento
            SET codigo = LEFT(TRIM(nota), 45)
            WHERE id_cuenta = %s
              AND nota IS NOT NULL
              AND TRIM(nota) <> ''
        """
        cursor.execute(update_sql, (id_cuenta,))
        updated = cursor.rowcount
        db.conn.commit()
        print(f"Registros actualizados: {updated}")

        # Verificacion rapida
        cursor.execute(
            """
            SELECT id_movimiento, codigo, nota
            FROM movimiento
            WHERE id_cuenta = %s
            ORDER BY fecha_creacion DESC, id_movimiento DESC
            LIMIT 5
            """,
            (id_cuenta,),
        )
        rows = cursor.fetchall()
        print("Muestra de verificacion (top 5):")
        for r in rows:
            print(f"  {r['id_movimiento']} | codigo={r['codigo']} | nota={r['nota']}")

        return 0
    except Exception as exc:
        db.conn.rollback()
        print(f"ERROR: {exc}")
        return 1
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
