"""
Generador de datos sintéticos financieros (3 años).

Qué hace:
- Usa el usuario activo/registrado más reciente (o --user-id)
- Crea productos base del usuario:
  1) Cuenta de ahorros
  2) Tarjeta de crédito
  3) Préstamo
  4) Fondo de inversión (tabla activo)
- Genera historial mensual (36 meses) de ingresos y gastos por categoría
- Aplica lógica financiera:
  * Cuota de préstamo que reduce saldo mensual
  * Fondo con crecimiento promedio 0.8% mensual
- Inserta datos en MySQL para análisis de Ingresos vs Gastos

Uso:
  python scripts/generate_synthetic_financial_data.py
  python scripts/generate_synthetic_financial_data.py --user-id 1
  python scripts/generate_synthetic_financial_data.py --dry-run
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple

import mysql.connector
import pandas as pd


DB_CONFIG = {
    "host": "localhost",
    "database": "app_presupuesto",
    "user": "root",
    "password": "",
}

SCRIPT_TAG = "SYN3Y"


@dataclass
class ProductIds:
    id_cuenta: int
    id_tarjeta: int
    id_prestamo: int
    id_fondo_activo: int


@dataclass
class LookupIds:
    id_tipo_ingreso: int
    id_tipo_gasto: int
    id_estado_realizado: int
    id_categoria_ingresos: int
    id_categoria_compras: int
    id_categoria_servicios: int
    id_categoria_cuotas: int
    id_beneficiario_empresa: int


def money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def month_end(day: dt.date) -> dt.date:
    last_day = calendar.monthrange(day.year, day.month)[1]
    return day.replace(day=last_day)


def add_months(base: dt.date, months: int) -> dt.date:
    year = base.year + (base.month - 1 + months) // 12
    month = (base.month - 1 + months) % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return dt.date(year, month, day)


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_one(cur, query: str, params: Tuple = ()):
    cur.execute(query, params)
    return cur.fetchone()


GET_OR_CREATE_SQL = {
    "tipo_movimiento": (
        "SELECT id_tipo FROM tipo_movimiento WHERE nombre = %s LIMIT 1",
        "INSERT INTO tipo_movimiento (nombre) VALUES (%s)",
    ),
    "categoria": (
        "SELECT id_categoria FROM categoria WHERE nombre = %s LIMIT 1",
        "INSERT INTO categoria (nombre) VALUES (%s)",
    ),
    "beneficiario": (
        "SELECT id_beneficiario FROM beneficiario WHERE nombre = %s LIMIT 1",
        "INSERT INTO beneficiario (nombre) VALUES (%s)",
    ),
}


def get_or_create_lookup(cur, key: str, value: str) -> int:
    if key not in GET_OR_CREATE_SQL:
        raise ValueError(f"Lookup no soportado: {key}")

    select_sql, insert_sql = GET_OR_CREATE_SQL[key]

    cur.execute(select_sql, (value,))
    row = cur.fetchone()
    if row:
        return int(row[0])

    cur.execute(insert_sql, (value,))
    return int(cur.lastrowid)


def get_or_create_tipo_movimiento(cur) -> Tuple[int, int]:
    id_ingreso = get_or_create_lookup(cur, "tipo_movimiento", "ingreso")
    id_gasto = get_or_create_lookup(cur, "tipo_movimiento", "gasto")
    return id_ingreso, id_gasto


def get_or_create_estado_realizado(cur) -> int:
    # Si no existe "realizado", usa el primer estado disponible.
    cur.execute("SELECT id_estado FROM estado_movimiento WHERE nombre = 'realizado' LIMIT 1")
    row = cur.fetchone()
    if row:
        return int(row[0])

    cur.execute("SELECT id_estado FROM estado_movimiento ORDER BY id_estado LIMIT 1")
    row = cur.fetchone()
    if row:
        return int(row[0])

    cur.execute("INSERT INTO estado_movimiento (nombre) VALUES ('realizado')")
    return int(cur.lastrowid)


def get_current_user(cur, forced_user_id: Optional[int] = None) -> Tuple[int, str]:
    if forced_user_id is not None:
        cur.execute("SELECT id_persona, nombre FROM persona WHERE id_persona = %s", (forced_user_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"No existe id_persona={forced_user_id}")
        return int(row[0]), str(row[1] or f"Usuario {row[0]}")

    cur.execute(
        """
        SELECT id_persona, nombre
        FROM persona
        WHERE estado = 1
        ORDER BY COALESCE(fecha_actualizacion, fecha_creacion) DESC, id_persona DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row:
        return int(row[0]), str(row[1] or f"Usuario {row[0]}")

    cur.execute(
        "INSERT INTO persona (nombre, correo_electronico, usuario, clave, fecha_creacion, estado) VALUES (%s, %s, %s, %s, NOW(), 1)",
        ("Usuario Demo", "demo@app.local", "demo", "demo"),
    )
    new_id = int(cur.lastrowid)
    return new_id, "Usuario Demo"


def ensure_products(cur, id_persona: int, start_date: dt.date) -> ProductIds:
    # 1) Cuenta de ahorros
    cur.execute(
        """
        SELECT id_cuenta
        FROM cuenta
        WHERE id_persona = %s AND nombre = %s
        LIMIT 1
        """,
        (id_persona, "Cuenta Ahorros Sintetica"),
    )
    row = cur.fetchone()
    if row:
        id_cuenta = int(row[0])
    else:
        cur.execute(
            """
            INSERT INTO cuenta (id_persona, nombre, tipo, saldo_inicial, moneda, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_persona, "Cuenta Ahorros Sintetica", "ahorro", money(3000000), "COP", start_date),
        )
        id_cuenta = int(cur.lastrowid)

    # 2) Tarjeta de crédito
    cur.execute("SELECT id_estado FROM estado_tarjeta WHERE nombre='activa' LIMIT 1")
    row = cur.fetchone()
    if row:
        id_estado_tarjeta = int(row[0])
    else:
        cur.execute("SELECT id_estado FROM estado_tarjeta ORDER BY id_estado LIMIT 1")
        row = cur.fetchone()
        if row:
            id_estado_tarjeta = int(row[0])
        else:
            cur.execute("INSERT INTO estado_tarjeta (nombre) VALUES ('activa')")
            id_estado_tarjeta = int(cur.lastrowid)

    numero_tarjeta = f"9999{id_persona:04d}12345678"
    cur.execute(
        """
        SELECT tc.id_tarjeta
        FROM tarjeta_credito tc
        JOIN movimiento_tarjeta mt ON mt.id_tarjeta = tc.id_tarjeta
        WHERE mt.id_persona = %s
        ORDER BY tc.id_tarjeta
        LIMIT 1
        """,
        (id_persona,),
    )
    row = cur.fetchone()
    if row:
        id_tarjeta = int(row[0])
    else:
        cur.execute("SELECT id_tarjeta FROM tarjeta_credito WHERE numero_tarjeta = %s LIMIT 1", (numero_tarjeta,))
        row = cur.fetchone()
        if row:
            id_tarjeta = int(row[0])
        else:
            cur.execute(
                """
                INSERT INTO tarjeta_credito
                (id_producto, numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, fecha_creacion, id_estado)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    numero_tarjeta,
                    money(8000000),
                    money(0),
                    dt.date.today().replace(day=20),
                    dt.date.today().replace(day=5),
                    start_date,
                    id_estado_tarjeta,
                ),
            )
            id_tarjeta = int(cur.lastrowid)

    # 3) Préstamo
    cur.execute("SELECT id_estado FROM estado_prestamo WHERE nombre='activo' LIMIT 1")
    row = cur.fetchone()
    if row:
        id_estado_prestamo = int(row[0])
    else:
        cur.execute("SELECT id_estado FROM estado_prestamo ORDER BY id_estado LIMIT 1")
        row = cur.fetchone()
        if row:
            id_estado_prestamo = int(row[0])
        else:
            cur.execute("INSERT INTO estado_prestamo (nombre) VALUES ('activo')")
            id_estado_prestamo = int(cur.lastrowid)

    cur.execute(
        """
        SELECT id_prestamo
        FROM prestamo
        WHERE id_persona = %s
        ORDER BY id_prestamo
        LIMIT 1
        """,
        (id_persona,),
    )
    row = cur.fetchone()
    if row:
        id_prestamo = int(row[0])
    else:
        cur.execute(
            """
            INSERT INTO prestamo
            (fecha, id_estado, moneda, saldo_inicial, saldo_pendiente, fecha_creacion, id_persona)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (start_date, id_estado_prestamo, "COP", money(18000000), money(18000000), start_date, id_persona),
        )
        id_prestamo = int(cur.lastrowid)

    # 4) Fondo de inversión (activo)
    cur.execute(
        """
        SELECT id_activo
        FROM activo
        WHERE id_persona = %s AND nombre_activo = %s
        LIMIT 1
        """,
        (id_persona, "Fondo Inversion Sintetico"),
    )
    row = cur.fetchone()
    if row:
        id_fondo = int(row[0])
    else:
        cur.execute(
            """
            INSERT INTO activo (nombre_activo, valor, depreciacion, id_persona, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("Fondo Inversion Sintetico", money(7000000), money(0), id_persona, start_date),
        )
        id_fondo = int(cur.lastrowid)

    return ProductIds(
        id_cuenta=id_cuenta,
        id_tarjeta=id_tarjeta,
        id_prestamo=id_prestamo,
        id_fondo_activo=id_fondo,
    )


def ensure_lookups(cur) -> LookupIds:
    id_tipo_ingreso, id_tipo_gasto = get_or_create_tipo_movimiento(cur)
    id_estado_realizado = get_or_create_estado_realizado(cur)

    id_categoria_ingresos = get_or_create_lookup(cur, "categoria", "Ingresos")
    id_categoria_compras = get_or_create_lookup(cur, "categoria", "Compras")
    id_categoria_servicios = get_or_create_lookup(cur, "categoria", "Servicios")
    id_categoria_cuotas = get_or_create_lookup(cur, "categoria", "Cuotas de prestamos")

    id_beneficiario_empresa = get_or_create_lookup(cur, "beneficiario", "Proveedor Sintetico")

    return LookupIds(
        id_tipo_ingreso=id_tipo_ingreso,
        id_tipo_gasto=id_tipo_gasto,
        id_estado_realizado=id_estado_realizado,
        id_categoria_ingresos=id_categoria_ingresos,
        id_categoria_compras=id_categoria_compras,
        id_categoria_servicios=id_categoria_servicios,
        id_categoria_cuotas=id_categoria_cuotas,
        id_beneficiario_empresa=id_beneficiario_empresa,
    )


def cleanup_previous_synthetic(cur, id_persona: int) -> None:
    # Primero elimina transacciones con etiqueta del script (sin tocar datos reales)
    cur.execute("DELETE FROM movimiento_tarjeta WHERE numero_transaccion LIKE %s", (f"{SCRIPT_TAG}-%",))
    cur.execute("DELETE FROM movimiento WHERE codigo LIKE %s", (f"{SCRIPT_TAG}-%",))

    # Tabla prestamo_movimiento tiene PK compuesta (persona_id_persona, prestamo_id_prestamo)
    # se mantiene una fila de estado final para no romper la clave.
    cur.execute("DELETE FROM prestamo_movimiento WHERE numero_transaccion LIKE %s", (f"{SCRIPT_TAG}-%",))

    # Elimina productos sintéticos anteriores del usuario (si existen)
    cur.execute(
        "DELETE FROM activo WHERE id_persona = %s AND nombre_activo = 'Fondo Inversion Sintetico'",
        (id_persona,),
    )
    cur.execute(
        "DELETE FROM cuenta WHERE id_persona = %s AND nombre = 'Cuenta Ahorros Sintetica'",
        (id_persona,),
    )


def build_monthly_dataset(months: int = 36) -> pd.DataFrame:
    start_month = dt.date.today().replace(day=1)
    start_month = add_months(start_month, -(months - 1))

    base_income = 4500000.0
    annual_growth = 0.04

    rows: List[Dict[str, float | dt.date]] = []
    for i in range(months):
        d = add_months(start_month, i)
        years_since_start = i // 12
        seasonal = 1 + 0.015 * math.sin(i * math.pi / 6)

        ingreso = base_income * ((1 + annual_growth) ** years_since_start) * seasonal
        compras = ingreso * (0.34 + 0.02 * math.sin(i * math.pi / 3))
        servicios = ingreso * (0.17 + 0.015 * math.cos(i * math.pi / 4))

        rows.append(
            {
                "periodo": d,
                "ingreso": round(ingreso, 2),
                "gasto_compras": round(compras, 2),
                "gasto_servicios": round(servicios, 2),
            }
        )

    return pd.DataFrame(rows)


def insert_monthly_history(
    cur,
    id_persona: int,
    products: ProductIds,
    lookups: LookupIds,
    df: pd.DataFrame,
) -> Dict[str, float]:
    saldo_tarjeta = Decimal("0")
    saldo_prestamo = Decimal("18000000")
    tasa_prestamo_mensual = Decimal("0.013")

    n = len(df)
    cuota = (saldo_prestamo * tasa_prestamo_mensual * (1 + tasa_prestamo_mensual) ** n) / (((1 + tasa_prestamo_mensual) ** n) - 1)
    cuota = cuota.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    fondo_valor = Decimal("7000000")
    fondo_growth = Decimal("0.008")

    for _, row in df.iterrows():
        fecha = month_end(row["periodo"])
        ingreso = money(float(row["ingreso"]))
        compras = money(float(row["gasto_compras"]))
        servicios = money(float(row["gasto_servicios"]))

        interes_mes = (saldo_prestamo * tasa_prestamo_mensual).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        pago_principal = max(Decimal("0"), cuota - interes_mes)
        if pago_principal > saldo_prestamo:
            pago_principal = saldo_prestamo
        saldo_prestamo = (saldo_prestamo - pago_principal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Movimiento: Ingreso mensual (salario)
        cur.execute(
            """
            INSERT INTO movimiento
            (codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s, %s, %s, %s, NULL, %s, NULL, %s, %s, %s, %s)
            """,
            (
                f"{SCRIPT_TAG}-ING-{fecha.strftime('%Y%m')}",
                ingreso,
                lookups.id_tipo_ingreso,
                lookups.id_estado_realizado,
                lookups.id_categoria_ingresos,
                f"{SCRIPT_TAG}-TX-ING-{fecha.strftime('%Y%m')}",
                "Ingreso mensual sintetico",
                fecha,
                products.id_cuenta,
            ),
        )

        # Movimiento: Gasto compras
        cur.execute(
            """
            INSERT INTO movimiento
            (codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"{SCRIPT_TAG}-GAS-COM-{fecha.strftime('%Y%m')}",
                compras,
                lookups.id_tipo_gasto,
                lookups.id_estado_realizado,
                lookups.id_categoria_compras,
                lookups.id_beneficiario_empresa,
                f"{SCRIPT_TAG}-TX-COM-{fecha.strftime('%Y%m')}",
                "Gasto compras sintetico",
                fecha,
                products.id_cuenta,
            ),
        )

        # Movimiento: Gasto servicios
        cur.execute(
            """
            INSERT INTO movimiento
            (codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"{SCRIPT_TAG}-GAS-SER-{fecha.strftime('%Y%m')}",
                servicios,
                lookups.id_tipo_gasto,
                lookups.id_estado_realizado,
                lookups.id_categoria_servicios,
                lookups.id_beneficiario_empresa,
                f"{SCRIPT_TAG}-TX-SER-{fecha.strftime('%Y%m')}",
                "Gasto servicios sintetico",
                fecha,
                products.id_cuenta,
            ),
        )

        # Movimiento: Cuota préstamo
        cur.execute(
            """
            INSERT INTO movimiento
            (codigo, monto, id_tipo, id_estado, id_producto, id_categoria, id_beneficiario, numero_transaccion, nota, fecha_creacion, id_cuenta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"{SCRIPT_TAG}-GAS-PRS-{fecha.strftime('%Y%m')}",
                cuota,
                lookups.id_tipo_gasto,
                lookups.id_estado_realizado,
                products.id_prestamo,
                lookups.id_categoria_cuotas,
                lookups.id_beneficiario_empresa,
                f"{SCRIPT_TAG}-TX-PRS-{fecha.strftime('%Y%m')}",
                "Cuota prestamo sintetica",
                fecha,
                products.id_cuenta,
            ),
        )

        # Simula uso y pago de tarjeta de crédito
        compra_tc = (compras * Decimal("0.62")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        pago_tc = (compras * Decimal("0.48") + servicios * Decimal("0.16")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        saldo_tarjeta = (saldo_tarjeta + compra_tc - pago_tc).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if saldo_tarjeta < Decimal("0"):
            saldo_tarjeta = Decimal("0")

        cur.execute(
            """
            INSERT INTO movimiento_tarjeta
            (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, saldo, cuotas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                products.id_tarjeta,
                id_persona,
                fecha,
                compra_tc,
                "compra",
                "Compra tarjeta sintetica",
                f"{SCRIPT_TAG}-TC-COM-{fecha.strftime('%Y%m')}",
                lookups.id_categoria_compras,
                lookups.id_beneficiario_empresa,
                saldo_tarjeta,
                1,
            ),
        )

        cur.execute(
            """
            INSERT INTO movimiento_tarjeta
            (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, saldo, cuotas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s, %s)
            """,
            (
                products.id_tarjeta,
                id_persona,
                fecha,
                pago_tc,
                "abono",
                "Abono tarjeta sintetico",
                f"{SCRIPT_TAG}-TC-ABO-{fecha.strftime('%Y%m')}",
                saldo_tarjeta,
                1,
            ),
        )

        # Fondo de inversión: crecimiento 0.8% mensual
        fondo_valor = (fondo_valor * (Decimal("1") + fondo_growth)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Actualiza saldos finales de tarjeta y fondo
    cur.execute(
        "UPDATE tarjeta_credito SET saldo_actual = %s WHERE id_tarjeta = %s",
        (saldo_tarjeta, products.id_tarjeta),
    )
    cur.execute(
        "UPDATE activo SET valor = %s WHERE id_activo = %s",
        (fondo_valor, products.id_fondo_activo),
    )

    # Guarda estado final del préstamo en prestamo_movimiento
    cur.execute(
        """
        INSERT INTO prestamo_movimiento
        (persona_id_persona, prestamo_id_prestamo, valor, interes, numero_transaccion, seguro, saldo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            valor = VALUES(valor),
            interes = VALUES(interes),
            numero_transaccion = VALUES(numero_transaccion),
            seguro = VALUES(seguro),
            saldo = VALUES(saldo)
        """,
        (
            id_persona,
            products.id_prestamo,
            money(float(cuota)),
            money(float(tasa_prestamo_mensual * Decimal("100"))),
            f"{SCRIPT_TAG}-PRS-FINAL",
            money(0),
            saldo_prestamo,
        ),
    )

    # Ajusta saldo referencial del préstamo en tabla principal
    cur.execute(
        "UPDATE prestamo SET saldo_pendiente = %s WHERE id_prestamo = %s",
        (saldo_prestamo, products.id_prestamo),
    )

    return {
        "saldo_tarjeta_final": float(saldo_tarjeta),
        "saldo_prestamo_final": float(saldo_prestamo),
        "valor_fondo_final": float(fondo_valor),
    }


def build_income_vs_expense_report(df: pd.DataFrame, cuota_referencia: float) -> pd.DataFrame:
    report = df.copy()
    report["gasto_cuota_prestamo"] = cuota_referencia
    report["gasto_total"] = report["gasto_compras"] + report["gasto_servicios"] + report["gasto_cuota_prestamo"]
    report["balance_neto"] = report["ingreso"] - report["gasto_total"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera datos sintéticos financieros de 3 años")
    parser.add_argument("--user-id", type=int, default=None, help="ID de persona a usar")
    parser.add_argument("--dry-run", action="store_true", help="No inserta, solo muestra resumen")
    args = parser.parse_args()

    conn = get_connection()
    cur = conn.cursor()

    try:
        user_id, user_name = get_current_user(cur, args.user_id)

        df = build_monthly_dataset(months=36)

        if args.dry_run:
            tmp_report = build_income_vs_expense_report(df, cuota_referencia=620000.0)
            print("DRY RUN - No se insertaron datos")
            print(f"Usuario seleccionado: {user_id} - {user_name}")
            print(tmp_report.tail(6).to_string(index=False))
            return

        cleanup_previous_synthetic(cur, user_id)
        products = ensure_products(cur, user_id, start_date=df.iloc[0]["periodo"])
        lookups = ensure_lookups(cur)
        metrics = insert_monthly_history(cur, user_id, products, lookups, df)

        conn.commit()

        # Cuota aproximada para reporte
        cuota_aprox = float((Decimal("18000000") * Decimal("0.013") * (Decimal("1.013") ** 36) / ((Decimal("1.013") ** 36) - 1)).quantize(Decimal("0.01")))
        report = build_income_vs_expense_report(df, cuota_referencia=cuota_aprox)

        print("Datos sintéticos insertados correctamente")
        print(f"Usuario: {user_id} - {user_name}")
        print(f"Cuenta ahorro ID: {products.id_cuenta}")
        print(f"Tarjeta ID: {products.id_tarjeta}")
        print(f"Préstamo ID: {products.id_prestamo}")
        print(f"Fondo (activo) ID: {products.id_fondo_activo}")
        print("---")
        print(f"Saldo tarjeta final: {metrics['saldo_tarjeta_final']:,.2f}")
        print(f"Saldo préstamo final: {metrics['saldo_prestamo_final']:,.2f}")
        print(f"Valor fondo final: {metrics['valor_fondo_final']:,.2f}")
        print("--- Preview Ingresos vs Gastos (últimos 6 meses) ---")
        print(report.tail(6).to_string(index=False))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
