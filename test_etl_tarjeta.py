"""
Script de prueba para validar el ETL de tarjeta de crédito.

Nota: Ejecutar desde la raíz del proyecto.
"""

from src.business.services.etl_tarjeta_credito import ETLTarjetaCredito, validate_excel_file
from src.database.db_connector import DatabaseConnector

def test_validate_excel():
    """Prueba validación de archivo Excel."""
    print("=" * 60)
    print("TEST: Validación de archivo Excel")
    print("=" * 60)
    
    # Crear un archivo Excel de prueba
    import pandas as pd
    import tempfile
    from pathlib import Path
    
    # Archivo válido
    df = pd.DataFrame({
        'Fecha': ['2026-04-07', '2026-04-08'],
        'Concepto': ['Supermercado', 'Gasolina'],
        'Monto': [150000, 80000],
        'Categoría': ['Compras', 'Transporte'],
        'Cuotas': [1, 1],
        'Referencia': ['Ref-001', 'Ref-002']
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
    
    # Obtener datos del usuario y tarjeta desde BD
    db = DatabaseConnector()
    
    # Usuario
    user_rows = db.execute_query(
        "SELECT id_persona FROM persona WHERE estado = 1 ORDER BY id_persona DESC LIMIT 1"
    )
    if not user_rows:
        print("✗ No hay usuario activo en la BD")
        db.close()
        return
    
    id_persona = int(user_rows[0]['id_persona'])
    print(f"✓ Usuario encontrado: ID {id_persona}")
    
    # Tarjeta
    tarjeta_rows = db.execute_query(
        """
        SELECT tc.id_tarjeta 
        FROM tarjeta_credito tc
        LIMIT 1
        """
    )
    if not tarjeta_rows:
        print("✗ No hay tarjeta de crédito en la BD")
        db.close()
        return
    
    id_tarjeta = int(tarjeta_rows[0]['id_tarjeta'])
    print(f"✓ Tarjeta encontrada: ID {id_tarjeta}")
    
    # Crear archivo de prueba
    df = pd.DataFrame({
        'Fecha': ['2026-04-07', '2026-04-08', '2026-04-09'],
        'Concepto': ['Supermercado', 'Gasolina', 'Restaurante'],
        'Monto': [150000, 80000, 45000],
        'Categoría': ['Compras', 'Transporte', 'Alimentos'],
        'Cuotas': [1, 1, 3],
        'Referencia': ['Ref-001', 'Ref-002', 'Ref-003']
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        temp_file = tmp.name
    
    try:
        print(f"\n✓ Archivo de prueba creado: {temp_file}")
        
        # Ejecutar ETL
        etl = ETLTarjetaCredito(db)
        processed, errors = etl.process_file(temp_file, id_persona, id_tarjeta)
        
        print(f"\n✓ Procesadas: {processed} transacción(es)")
        if errors:
            print(f"\n⚠ Errores encontrados: {len(errors)}")
            for err in errors[:3]:
                print(f"  - Fila {err.get('row', '?')}: {err.get('errors', [])}")
        
        # Verificar en BD
        mov_rows = db.execute_query(
            "SELECT COUNT(*) as cnt FROM movimiento WHERE id_producto = %s",
            (id_tarjeta,)
        )
        mov_count = int(mov_rows[0]['cnt']) if mov_rows else 0
        print(f"\n✓ Movimientos en BD: {mov_count}")
        
        mov_tarjeta_rows = db.execute_query(
            "SELECT COUNT(*) as cnt FROM movimiento_tarjeta WHERE id_tarjeta = %s",
            (id_tarjeta,)
        )
        tarjeta_count = int(mov_tarjeta_rows[0]['cnt']) if mov_tarjeta_rows else 0
        print(f"✓ Movimientos de tarjeta en BD: {tarjeta_count}")
        
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
