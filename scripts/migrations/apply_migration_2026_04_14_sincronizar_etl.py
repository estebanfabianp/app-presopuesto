#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sincroniza la cuenta "cuanto de ahorros" usando el ETL oficial."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.business.services.etl_cuenta_bancaria import ETLCuentaBancaria
from src.database.db_connector import DatabaseConnector


def main() -> int:
    xlsx_path = ROOT_DIR / "cuenta_bancaria.xlsx"
    saldo_inicial_correcto = 466003.46

    print("\n" + "=" * 100)
    print("SINCRONIZACION DE MOVIMIENTOS DESDE EXCEL A BD")
    print("=" * 100)

    db = DatabaseConnector()
    cursor = db.conn.cursor()

    try:
        cursor.execute(
            "SELECT id_cuenta, id_persona FROM cuenta WHERE nombre LIKE %s LIMIT 1",
            ("%cuanto%",),
        )
        result = cursor.fetchone()
        if not result:
            print("No se encontro la cuenta 'cuanto de ahorros'.")
            return 1

        id_cuenta, id_persona = result
        print(f"Cuenta encontrada: ID {id_cuenta}, persona {id_persona}")

        print("\nDesactivando recalculo destructivo en objetos SQL...")
        cursor.execute("DROP TRIGGER IF EXISTS tr_update_saldo_cuenta_after_insert")
        cursor.execute("DROP TRIGGER IF EXISTS tr_update_saldo_cuenta_after_update")
        cursor.execute("DROP TRIGGER IF EXISTS tr_update_saldo_cuenta_after_delete")
        cursor.execute(
            """
            CREATE TRIGGER tr_update_saldo_cuenta_after_insert
            AFTER INSERT ON movimiento
            FOR EACH ROW
            BEGIN
              SET @noop_cuenta_insert = 1;
            END
            """
        )
        cursor.execute(
            """
            CREATE TRIGGER tr_update_saldo_cuenta_after_update
            AFTER UPDATE ON movimiento
            FOR EACH ROW
            BEGIN
              SET @noop_cuenta_update = 1;
            END
            """
        )
        cursor.execute(
            """
            CREATE TRIGGER tr_update_saldo_cuenta_after_delete
            AFTER DELETE ON movimiento
            FOR EACH ROW
            BEGIN
              SET @noop_cuenta_delete = 1;
            END
            """
        )
        cursor.execute("DROP PROCEDURE IF EXISTS sp_recalcular_saldo_cuenta")
        cursor.execute(
            """
            CREATE PROCEDURE sp_recalcular_saldo_cuenta(IN p_id_cuenta INT)
            BEGIN
              SELECT p_id_cuenta AS id_cuenta;
            END
            """
        )
        db.conn.commit()
        print("OK: triggers y procedimiento ajustados")

        print("\nLimpiando movimientos actuales de la cuenta...")
        cursor.execute("DELETE FROM movimiento WHERE id_cuenta = %s", (id_cuenta,))
        print(f"Movimientos eliminados: {cursor.rowcount}")

        print("\nRestaurando saldo inicial correcto...")
        cursor.execute(
            "UPDATE cuenta SET saldo_inicial = %s WHERE id_cuenta = %s",
            (saldo_inicial_correcto, id_cuenta),
        )
        db.conn.commit()

        print("\nCargando archivo con ETL oficial...")
        etl = ETLCuentaBancaria(db)
        processed, row_errors = etl.process_file(str(xlsx_path), id_persona, id_cuenta)
        print(f"Movimientos cargados: {processed}")
        if row_errors:
            print(f"Errores por fila: {len(row_errors)}")

        print("\nReafirmando saldo inicial despues de la carga...")
        cursor.execute(
            "UPDATE cuenta SET saldo_inicial = %s WHERE id_cuenta = %s",
            (saldo_inicial_correcto, id_cuenta),
        )
        db.conn.commit()

        print("\nActualizando vistas de saldo...")
        cursor.execute("DROP VIEW IF EXISTS v_cuenta_saldos")
        cursor.execute(
            """
            CREATE VIEW v_cuenta_saldos AS
            SELECT
                c.id_cuenta,
                c.id_persona,
                c.nombre AS nombre_cuenta,
                c.tipo AS tipo_cuenta,
                c.moneda,
                c.saldo_inicial,
                COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS saldo_movimientos,
                CAST(c.saldo_inicial + COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS DECIMAL(15,2)) AS saldo_actual
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
            GROUP BY c.id_cuenta, c.id_persona, c.nombre, c.tipo, c.moneda, c.saldo_inicial
            """
        )
        cursor.execute("DROP VIEW IF EXISTS v_producto_unificado")
        cursor.execute(
            """
            CREATE VIEW v_producto_unificado AS
            SELECT
                c.id_persona,
                c.id_cuenta AS id_producto,
                'cuenta_bancaria' AS tipo_producto,
                c.nombre,
                CAST(c.saldo_inicial + COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS DECIMAL(15,2)) AS saldo_actual,
                CAST(c.saldo_inicial + COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS DECIMAL(15,2)) AS saldo_disponible,
                CAST(0 AS DECIMAL(15,2)) AS limite_credito,
                CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
                c.fecha_creacion AS fecha_apertura,
                'ACTIVO' AS estado,
                'Cuenta Bancaria' AS tipo_display,
                CAST(c.saldo_inicial + COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS DECIMAL(15,2)) AS valor_efectivo,
                'cuenta' AS origen_tabla
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
            GROUP BY c.id_persona, c.id_cuenta, c.nombre, c.saldo_inicial, c.fecha_creacion
            UNION ALL
            SELECT
                mtp.id_persona,
                tc.id_tarjeta AS id_producto,
                'tarjeta_credito' AS tipo_producto,
                CONCAT('Tarjeta ', RIGHT(tc.numero_tarjeta, 4)) AS nombre,
                CAST(COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS saldo_actual,
                CAST(COALESCE(tc.limite_credito, 0) - COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS saldo_disponible,
                CAST(COALESCE(tc.limite_credito, 0) AS DECIMAL(15,2)) AS limite_credito,
                CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
                tc.fecha_creacion AS fecha_apertura,
                'ACTIVO' AS estado,
                'Tarjeta de Credito' AS tipo_display,
                CAST(COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS valor_efectivo,
                'tarjeta_credito' AS origen_tabla
            FROM tarjeta_credito tc
            LEFT JOIN (SELECT id_tarjeta, MIN(id_persona) AS id_persona FROM movimiento_tarjeta GROUP BY id_tarjeta) mtp ON mtp.id_tarjeta = tc.id_tarjeta
            UNION ALL
            SELECT
                p.id_persona,
                p.id_prestamo AS id_producto,
                'prestamo' AS tipo_producto,
                CONCAT('Prestamo #', p.id_prestamo) AS nombre,
                CAST(COALESCE(p.saldo_pendiente, p.saldo_inicial, 0) AS DECIMAL(15,2)) AS saldo_actual,
                CAST(0 AS DECIMAL(15,2)) AS saldo_disponible,
                CAST(0 AS DECIMAL(15,2)) AS limite_credito,
                CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
                p.fecha_creacion AS fecha_apertura,
                UPPER(COALESCE(ep.nombre, 'ACTIVO')) AS estado,
                'Prestamo' AS tipo_display,
                CAST(-ABS(COALESCE(p.saldo_pendiente, p.saldo_inicial, 0)) AS DECIMAL(15,2)) AS valor_efectivo,
                'prestamo' AS origen_tabla
            FROM prestamo p
            LEFT JOIN estado_prestamo ep ON ep.id_estado = p.id_estado
            """
        )
        db.conn.commit()

        print("\nVerificando saldo final...")
        cursor.execute(
            """
            SELECT c.saldo_inicial,
                   COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS saldo_movimientos,
                   c.saldo_inicial + COALESCE(SUM(CASE WHEN m.id_tipo = 1 THEN m.monto WHEN m.id_tipo = 2 THEN -m.monto ELSE 0 END), 0) AS saldo_actual
            FROM cuenta c
            LEFT JOIN movimiento m ON m.id_cuenta = c.id_cuenta
            WHERE c.id_cuenta = %s
            GROUP BY c.id_cuenta, c.saldo_inicial
            """,
            (id_cuenta,),
        )
        saldo_inicial, saldo_movimientos, saldo_actual = cursor.fetchone()
        print(f"Saldo inicial: {float(saldo_inicial):.2f}")
        print(f"Saldo movimientos: {float(saldo_movimientos):.2f}")
        print(f"Saldo actual: {float(saldo_actual):.2f}")
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
