"""
Script que agrega 2 tarjetas de crédito adicionales con datos de prueba realistas.

Uso:
  python scripts/seed/add_more_cards_and_data.py
  python scripts/seed/add_more_cards_and_data.py --user-id 1 --clean
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_connector import DatabaseConnector

TAG_CARD = "CARD-TST"
TAG_MOV = "MOV-TST-CARD"
BANCOSDATA = [
    {"nombre": "Visa Platinum", "banco": "Banco Bogotá", "limite": 8000000},
    {"nombre": "Mastercard Gold", "banco": "Banco Caja Social", "limite": 6500000},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agregar 2 tarjetas adicionales con datos de prueba")
    parser.add_argument("--user-id", type=int, default=1, help="ID de persona")
    parser.add_argument("--clean", action="store_true", help="Limpiar tarjetas y datos previos creados por este script")
    parser.add_argument("--seed", type=int, default=20260412, help="Semilla random")
    parser.add_argument("--movements", type=int, default=25, help="Movimientos por tarjeta")
    parser.add_argument("--diferidos", type=int, default=4, help="Diferidos por tarjeta")
    return parser.parse_args()


def random_date(months_back: int = 6) -> date:
    """Genera una fecha aleatoria en los últimos N meses."""
    end = date.today()
    start = end - timedelta(days=max(30, months_back * 30))
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def create_cards(cursor, user_id: int, clean: bool = False) -> list[int]:
    """Crea 2 tarjetas nuevas."""
    if clean:
        # Limpiar en orden: primero diferidos, luego movimientos, luego tarjetas
        print("  Limpiando datos previos...")
        cursor.execute(
            f"DELETE FROM tarjeta_diferido_pago WHERE id_diferido IN (SELECT id_diferido FROM tarjeta_diferido WHERE numero_transaccion LIKE '{TAG_MOV}%')"
        )
        cursor.execute(
            f"DELETE FROM tarjeta_diferido WHERE numero_transaccion LIKE 'DIF-%'"
        )
        cursor.execute(
            f"DELETE FROM movimiento_tarjeta WHERE numero_transaccion LIKE '{TAG_MOV}%'"
        )
        cursor.execute(
            f"DELETE FROM tarjeta_credito WHERE numero_tarjeta LIKE '{TAG_CARD}%'"
        )
        print(f"  Limpieza completada")

    # Obtener estado activo
    cursor.execute("SELECT id_estado FROM estado_tarjeta WHERE nombre = 'Activa' OR nombre LIKE '%active%' LIMIT 1")
    est_row = cursor.fetchone()
    estado_id = int(est_row[0]) if est_row else 1

    card_ids = []
    hoy = date.today()
    
    for i, card_info in enumerate(BANCOSDATA):
        numero = f"{TAG_CARD}-{i+1}-" + str(random.randint(100000000000, 999999999999))[:12]
        fecha_corte = hoy.replace(day=min(20, 28)) if hoy.day < 20 else (hoy + timedelta(days=10)).replace(day=20)
        fecha_pago = hoy.replace(day=min(5, 28)) if hoy.day < 5 else (hoy + timedelta(days=5)).replace(day=5)
        
        cursor.execute(
            """
            INSERT INTO tarjeta_credito
                (numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, id_estado)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (numero, card_info["limite"], 0, fecha_corte, fecha_pago, estado_id)
        )
        card_id = int(cursor.lastrowid)
        card_ids.append(card_id)
        print(f"  Tarjeta creada: {card_info['nombre']} (ID: {card_id}, Límite: ${card_info['limite']:,})")
    
    return card_ids


def load_catalogs(cursor) -> tuple[list[int], list[int]]:
    """Carga categorías y beneficiarios."""
    cursor.execute("SELECT id_categoria FROM categoria WHERE estado = 1 ORDER BY RAND() LIMIT 10")
    categorias = [int(r[0]) for r in (cursor.fetchall() or [])]
    
    cursor.execute("SELECT id_beneficiario FROM beneficiario WHERE estado = 1 ORDER BY RAND() LIMIT 10")
    beneficiarios = [int(r[0]) for r in (cursor.fetchall() or [])]
    
    return categorias, beneficiarios


def insert_movements(cursor, user_id: int, card_ids: list[int], num_movements: int = 25):
    """Inserta movimientos variados para las tarjetas."""
    print(f"\n  Insertando {num_movements} movimientos por tarjeta...")
    
    categorias, beneficiarios = load_catalogs(cursor)
    
    categorias_desc = {
        "compra": ["Compra en comercio", "Consumo diario", "Compra online", "Compra supermercado", "Gasto planificado"],
        "abono": ["Pago parcial", "Abono automático", "Pago extra", "Pago PSE", "Transferencia"],
        "diferido": ["Compra diferida - Electrónica", "Compra diferida - Muebles", "Compra diferida - Vestuario"],
        "pendiente": ["Movimiento pendiente", "Compra no confirmada"],
        "aprobado": ["Movimiento aprobado", "Transacción aprobada"],
    }
    
    insert_count = 0
    for card_idx, card_id in enumerate(card_ids):
        for i in range(num_movements):
            estado = random.choices(
                population=["compra", "abono", "diferido", "pendiente", "aprobado"],
                weights=[55, 25, 12, 5, 3],
                k=1,
            )[0]
            
            fecha = random_date(months_back=6)
            
            if estado == "abono":
                valor = round(random.uniform(100000, 1500000), 2)
                cuotas = 1
                id_categoria = None
                id_beneficiario = None
            else:
                valor = round(random.uniform(25000, 800000), 2)
                cuotas = random.randint(2, 18) if estado == "diferido" else 1
                id_categoria = random.choice(categorias) if categorias and random.random() > 0.2 else None
                id_beneficiario = random.choice(beneficiarios) if beneficiarios and random.random() > 0.3 else None
            
            nota = random.choice(categorias_desc.get(estado, ["Transacción"]))
            num_tx = f"{TAG_MOV}-{card_idx+1}-{fecha.strftime('%Y%m%d')}-{i:04d}"
            
            cursor.execute(
                """
                INSERT INTO movimiento_tarjeta
                    (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, cuotas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (card_id, user_id, fecha, valor, estado, nota, num_tx, id_categoria, id_beneficiario, cuotas)
            )
            insert_count += 1
    
    print(f"  Movimientos insertados: {insert_count}")
    return insert_count


def insert_diferidos(cursor, user_id: int, card_ids: list[int], num_diferidos: int = 4):
    """Inserta diferidos activos para las tarjetas."""
    print(f"\n  Insertando {num_diferidos} diferidos por tarjeta...")
    
    hoy = date.today()
    insert_count = 0
    
    for card_idx, card_id in enumerate(card_ids):
        for i in range(num_diferidos):
            # Datos del diferido
            valor_total = round(random.uniform(500000, 3500000), 2)
            num_cuotas = random.choice([3, 6, 9, 12])
            tasa_mensual = round(random.uniform(0.5, 3.5), 2)
            sin_interes = random.choice([True, False]) if tasa_mensual < 1.0 else False
            
            descripciones = [
                "Refrigerador LG 18 pies",
                "Sofá de cuero 3 puestos",
                "Televisor Samsung 55 pulgadas",
                "Laptop HP Pavilion",
                "Aire acondicionado Fujitsu",
                "Horno microondas Electrolux",
                "Cama King Size con colchón",
                "Comedor 6 puestos",
            ]
            descripcion = random.choice(descripciones)
            
            fecha_compra = hoy - timedelta(days=random.randint(10, 90))
            numero_transaccion = f"DIF-{card_idx+1}-{fecha_compra.strftime('%Y%m%d')}-{i:04d}"
            
            # Calcular cuota mensual y saldo
            if sin_interes:
                cuota_mensh = valor_total / num_cuotas
                total_intereses = 0
            else:
                tasaMensual = tasa_mensual / 100
                factor = pow(1 + tasaMensual, num_cuotas)
                cuota_mens = (valor_total * tasaMensual * factor) / (factor - 1)
                total_intereses = max(0, (cuota_mens * num_cuotas) - valor_total)
            
            total_pagado_est = valor_total + total_intereses
            
            try:
                cursor.execute(
                    """
                    INSERT INTO tarjeta_diferido
                        (id_tarjeta, id_persona, descripcion, valor_total, numero_cuotas, 
                         tasa_mensual, sin_interes, cuota_mensual, total_intereses, 
                         total_pagado_estimado, saldo_pendiente, fecha_compra, 
                         numero_transaccion, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'activo')
                    """,
                    (card_id, user_id, descripcion, valor_total, num_cuotas, 
                     tasa_mensual, 1 if sin_interes else 0, cuota_mens if not sin_interes else cuota_mensh,
                     total_intereses, total_pagado_est, valor_total, fecha_compra, numero_transaccion)
                )
                insert_count += 1
                
            except Exception as e:
                print(f"  Advertencia al insertar diferido: {e}")
    
    print(f"  Diferidos insertados: {insert_count}")
    return insert_count


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    
    db = DatabaseConnector()
    if not db.conn:
        print("❌ ERROR: No se pudo conectar a la base de datos")
        return 1
    
    conn = db.conn
    cursor = conn.cursor()
    
    try:
        print(f"🔄 Agregando 2 tarjetas de prueba para usuario {args.user_id}...\n")
        
        # Crear tarjetas
        print("📍 Creando tarjetas...")
        card_ids = create_cards(cursor, args.user_id, clean=args.clean)
        conn.commit()
        
        # Insertar movimientos
        print(f"\n📍 Agregando movimientos...")
        mov_count = insert_movements(cursor, args.user_id, card_ids, args.movements)
        conn.commit()
        
        # Insertar diferidos
        print(f"\n📍 Agregando diferidos activos...")
        dif_count = insert_diferidos(cursor, args.user_id, card_ids, args.diferidos)
        conn.commit()
        
        # Resumen
        print(f"\n✅ ÉXITO - Datos de prueba agregados:")
        print(f"   • Tarjetas: {len(card_ids)}")
        print(f"   • Movimientos: {mov_count}")
        print(f"   • Diferidos: {dif_count}")
        print(f"\n💡 Para limpiar estos datos después, ejecuta:")
        print(f"   python scripts/seed/add_more_cards_and_data.py --user-id {args.user_id} --clean")
        
        return 0
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
