#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar la migración de mejoras al modelo de datos
- Tabla movimiento_tarjeta_item (desglose de items)
- Tabla detalle_diferido_movimiento (relación diferido ↔ movimiento)
- Tabla movimiento_rechazo (auditoría de rechazos)

Uso:
    python scripts/migrations/apply_migration_2026_04_12.py

Requisitos:
    - Base de datos app_presupuesto existente
    - Credenciales de acceso a MySQL
    - Las tablas base (movimiento_tarjeta, tarjeta_diferido, etc.) deben existir
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector
from src.utils.logger import logger

def apply_migration():
    """Aplica la migración de mejoras al modelo de datos."""
    db = DatabaseConnector()
    
    try:
        logger.info("=" * 70)
        logger.info("INICIANDO MIGRACIÓN: Items Desglosados, Diferidos y Rechazos")
        logger.info("=" * 70)
        
        # Leer el script de migración SQL
        migration_file = ROOT_DIR / "base_de_datos/db/02_maintenance/schema/2026-04-12_items_diferidos_rechazos.sql"
        if not migration_file.exists():
            logger.error(f"Archivo de migración no encontrado: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir el contenido en statements individuales (simple split por ;)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        logger.info(f"Se encontraron {len(statements)} statements SQL para ejecutar")
        
        executed = 0
        skipped = 0
        errors = 0
        
        for i, statement in enumerate(statements, start=1):
            if not statement or statement.startswith('--'):
                continue
            
            try:
                # Ejecutar y capturar mensajes
                result = db.execute_non_query(statement + ';')
                executed += 1
                logger.info(f"[{i}/{len(statements)}] ✓ Ejecutado: {statement[:60]}...")
            except Exception as e:
                error_msg = str(e)
                # Algunos errores son esperados (tabla ya existe, etc.)
                if "already exists" in error_msg or "Duplicate" in error_msg:
                    skipped += 1
                    logger.warning(f"[{i}/{len(statements)}] ⊘ Saltado (ya existe): {statement[:60]}...")
                else:
                    errors += 1
                    logger.error(f"[{i}/{len(statements)}] ✗ Error en: {statement[:60]}...")
                    logger.error(f"    Detalle: {error_msg}")
        
        logger.info("=" * 70)
        logger.info(f"RESUMEN DE MIGRACIÓN:")
        logger.info(f"  - Ejecutados:  {executed}")
        logger.info(f"  - Saltados:    {skipped} (ya existentes)")
        logger.info(f"  - Errores:     {errors}")
        logger.info("=" * 70)
        
        if errors > 0:
            logger.warning("La migración completó con errores. Revise los logs anteriores.")
            return False
        
        logger.info("✓ Migración completada exitosamente")
        
        # Verificar que las tablas se crearon
        logger.info("\nVERIFICACIÓN DE TABLAS:")
        tables_to_check = [
            'movimiento_tarjeta_item',
            'detalle_diferido_movimiento',
            'movimiento_rechazo'
        ]
        
        for table_name in tables_to_check:
            result = db.execute_query(
                f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema='app_presupuesto' AND table_name='{table_name}'"
            )
            if result and result[0]['count'] > 0:
                logger.info(f"  ✓ Tabla {table_name}: EXISTE")
            else:
                logger.warning(f"  ✗ Tabla {table_name}: NO ENCONTRADA")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fatale en la migración: {e}", exc_info=True)
        return False
    finally:
        db.close()


def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Aplica la migración de mejoras al modelo de datos'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Solo verifica si las tablas existen sin aplicar cambios'
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        logger.info("Verificando estado de las tablas...")
        db = DatabaseConnector()
        try:
            tables = ['movimiento_tarjeta_item', 'detalle_diferido_movimiento', 'movimiento_rechazo']
            for table in tables:
                result = db.execute_query(
                    f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema='app_presupuesto' AND table_name='{table}'"
                )
                status = "✓ EXISTE" if result and result[0]['count'] > 0 else "✗ NO EXISTE"
                logger.info(f"  {table}: {status}")
        finally:
            db.close()
    else:
        success = apply_migration()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
