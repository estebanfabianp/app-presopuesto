"""
Script de prueba para validar el ETL de tarjeta de crédito.

Cubre:
  - Validación de columnas
  - Procesamiento de movimientos normales (cuotas=1)
  - Procesamiento de diferidos con formato N/X (cuotas=1/3, 2/3, 3/3)
  - Upsert en tarjeta_diferido (segunda importación del mismo código)

Nota: Ejecutar desde la raíz del proyecto.
"""

from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito, validate_excel_file
from src.database.db_connector import DatabaseConnector

def test_validate_excel():
    """Prueba validación de archivo Excel."""
    print("=" * 60)
    print("TEST: Validación de archivo Excel")
    print("=" * 60)
    
    import pandas as pd
    import tempfile
    from pathlib import Path
    
    # Archivo válido con columnas mínimas
    df = pd.DataFrame({
        'Fecha': ['07/04/2026', '08/04/2026'],
        'Concepto': ['Supermercado', 'Gasolina'],
        'Monto': [150000, 80000],
        'Cuotas': ['1/1', '1/1'],
        'Referencia': ['REF-T01', 'REF-T02']
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        temp_file = tmp.name
    
    try:
        is_valid, errors = validate_excel_file(temp_file)
        print(f"\n✓ Archivo válido: {is_valid}")
        if errors:
            print(f"  Errores: {errors}")
        print(f"✓ Archivo de prueba: {temp_file}")
    finally:
        Path(temp_file).unlink()


def test_process_file():
    """Prueba procesamiento completo de archivo."""
    print("\n" + "=" * 60)
    print("TEST: Procesamiento completo de Excel -> BD")
    print("=" * 60)
    
    import pandas as pd
    import tempfile
    from pathlib import Path
    
    db = DatabaseConnector()
    
    # Usuario de prueba (esteban)
    user_rows = db.execute_query(
        "SELECT id_persona FROM persona WHERE id_persona = 1031150232"
    )
    if not user_rows:
        user_rows = db.execute_query(
            "SELECT id_persona FROM persona WHERE estado = 1 ORDER BY id_persona DESC LIMIT 1"
        )
    if not user_rows:
        print("✗ No hay usuario activo en la BD")
        db.close()
        return
    
    id_persona = int(user_rows[0]['id_persona'])
    print(f"✓ Usuario: ID {id_persona}")
    
    # Tarjeta de ese usuario
    tarjeta_rows = db.execute_query(
        "SELECT id_tarjeta FROM tarjeta_credito WHERE id_persona = %s LIMIT 1",
        (id_persona,)
    )
    if not tarjeta_rows:
        tarjeta_rows = db.execute_query(
            "SELECT id_tarjeta FROM tarjeta_credito LIMIT 1"
        )
    if not tarjeta_rows:
        print("✗ No hay tarjeta de crédito en la BD")
        db.close()
        return
    
    id_tarjeta = int(tarjeta_rows[0]['id_tarjeta'])
    print(f"✓ Tarjeta: ID {id_tarjeta}")
    
    # --- Archivo de prueba: simula extracto bancario ---
    # Fila 1-2: movimientos normales (cuota 1/1)
    # Fila 3:   primera cuota de un diferido (1/6)
    # Fila 4:   diferido de 1 sola cuota (no debe ir a tarjeta_diferido)
    TRACKING_CODE = 'TEST-ETL-DIFE-0001'
    df = pd.DataFrame({
        'Fecha':           ['07/04/2026', '08/04/2026', '09/04/2026', '10/04/2026'],
        'Concepto':        ['Supermercado', 'Gasolina', 'Televisor Samsung', 'Servicio internet'],
        'Monto':           [150000, 80000, 200000, 60000],
        'Cuotas':          ['1/1', '1/1', '1/6', '1/1'],
        'Valor Cuota':     [None, None, 35500, None],
        'Interes Mensual': [None, None, 2.1, None],
        'Saldo Pendiente': [None, None, 1170000, None],
        'Referencia':      ['REF-T01', 'REF-T02', TRACKING_CODE, 'REF-T04'],
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        temp_file = tmp.name
    
    try:
        print(f"\nArchivo de prueba: {temp_file}")
        
        # Contar registros previos para comparar
        pre_mov = db.execute_query(
            "SELECT COUNT(*) as c FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        pre_dif = db.execute_query(
            "SELECT COUNT(*) as c FROM tarjeta_diferido WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        pre_cnt_mov = int(pre_mov[0]['c']) if pre_mov else 0
        pre_cnt_dif = int(pre_dif[0]['c']) if pre_dif else 0

        # --- PRIMERA IMPORTACIÓN ---
        print("\n[1/2] Primera importación...")
        etl = ETLTarjetaCredito(db)
        processed, errors = etl.process_file(temp_file, id_persona, id_tarjeta)
        
        print(f"  Procesadas: {processed} | Errores: {len(errors)}")
        if errors:
            for err in errors:
                print(f"    Fila {err.get('row','?')}: {err.get('errors', err)}")
        
        # Verificar
        post1_mov = db.execute_query(
            "SELECT COUNT(*) as c FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        post1_dif = db.execute_query(
            "SELECT COUNT(*) as c FROM tarjeta_diferido WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        nuevos_mov1 = int(post1_mov[0]['c']) - pre_cnt_mov
        nuevos_dif1 = int(post1_dif[0]['c']) - pre_cnt_dif
        print(f"  movimiento_tarjeta nuevos: {nuevos_mov1} (esperado 4)")
        print(f"  tarjeta_diferido nuevos:   {nuevos_dif1} (esperado 1)")
        assert nuevos_mov1 == 4, f"ERROR: esperaba 4 movimientos, got {nuevos_mov1}"
        assert nuevos_dif1 == 1, f"ERROR: esperaba 1 diferido, got {nuevos_dif1}"
        print("  [OK] Primera importación correcta")

        # --- SEGUNDA IMPORTACIÓN del mismo archivo (upsert) ---
        # Simula cuota 2/6 del mismo diferido
        df2 = pd.DataFrame({
            'Fecha':           ['10/05/2026'],
            'Concepto':        ['Televisor Samsung'],
            'Monto':           [35500],
            'Cuotas':          ['2/6'],
            'Valor Cuota':     [35500],
            'Interes Mensual': [2.1],
            'Saldo Pendiente': [1134500],
            'Referencia':      [TRACKING_CODE],
        })
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp2:
            df2.to_excel(tmp2.name, index=False)
            temp_file2 = tmp2.name

        print("\n[2/2] Segunda importación (upsert de diferido)...")
        etl2 = ETLTarjetaCredito(db)
        processed2, errors2 = etl2.process_file(temp_file2, id_persona, id_tarjeta)
        Path(temp_file2).unlink()

        print(f"  Procesadas: {processed2} | Errores: {len(errors2)}")
        if errors2:
            for err in errors2:
                print(f"    Fila {err.get('row','?')}: {err.get('errors', err)}")

        post2_mov = db.execute_query(
            "SELECT COUNT(*) as c FROM movimiento_tarjeta WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        post2_dif = db.execute_query(
            "SELECT COUNT(*) as c FROM tarjeta_diferido WHERE id_tarjeta = %s AND id_persona = %s",
            (id_tarjeta, id_persona)
        )
        dif_row = db.execute_query(
            "SELECT cuotas_pagadas, saldo_pendiente, estado FROM tarjeta_diferido "
            "WHERE id_tarjeta = %s AND id_persona = %s AND numero_transaccion = %s",
            (id_tarjeta, id_persona, TRACKING_CODE)
        )
        nuevos_mov2 = int(post2_mov[0]['c']) - int(post1_mov[0]['c'])
        total_dif2  = int(post2_dif[0]['c']) - pre_cnt_dif
        print(f"  movimiento_tarjeta nuevos: {nuevos_mov2} (esperado 1)")
        print(f"  tarjeta_diferido total:    {total_dif2} (esperado 1, upsert no duplica)")
        if dif_row:
            d = dif_row[0]
            print(f"  cuotas_pagadas={d['cuotas_pagadas']}, saldo={d['saldo_pendiente']}, estado={d['estado']}")
        assert nuevos_mov2 == 1, f"ERROR: esperaba 1 movimiento nuevo, got {nuevos_mov2}"
        assert total_dif2  == 1, f"ERROR: upsert duplicó el diferido, got {total_dif2}"
        print("  [OK] Segunda importación (upsert) correcta")

    finally:
        Path(temp_file).unlink()
        db.close()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("TESTS: ETL TARJETA DE CRÉDITO")
    print("=" * 60)
    
    test_validate_excel()
    test_process_file()
    
    print("\n" + "=" * 60)
    print("✓ Tests completados")
    print("=" * 60 + "\n")
