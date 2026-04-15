#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar categoría "Moto" y mejorar nombres de categorías existentes

Cambios realizados:
1. Agrega "Moto" como categoría independiente (para: gasolina, mantenimiento, 
   accesorios, seguridad, lavado)
2. Mejora nombres inconsistentes:
   - "Combustible" → "Gasolina/Combustible" 
   - "Transporte - Taxi/Uber" → "Taxi/Uber"
   - "Mercado y Supermercado" → "Supermercado"

Uso:
    python scripts/migrations/apply_migration_2026_04_14_moto_categoria.py

Requisitos:
    - Base de datos app_presupuesto existente
    - Credenciales de acceso a MySQL
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
    """Aplica la migración de mejora de categorías."""
    db = DatabaseConnector()
    
    try:
        logger.info("=" * 70)
        logger.info("INICIANDO MIGRACIÓN: Agregar 'Moto' y mejorar categorías")
        logger.info("=" * 70)
        
        cursor = db.conn.cursor()
        
        # 0. Obtener el id_persona del primer usuario disponible
        logger.info("\n0. Obteniendo id_persona del usuario disponible...")
        cursor.execute("SELECT MIN(id_persona) FROM persona")
        result = cursor.fetchone()
        id_persona = result[0] if result and result[0] else 1
        logger.info(f"   Usando id_persona: {id_persona}")
        
        # 1. Agregar categoría "Moto" en GASTOS FIJOS
        logger.info("\n1. Agregando categoría 'Moto'...")
        try:
            sql_moto = f"""
            INSERT INTO `app_presupuesto`.`categoria` (`id_persona`, `nombre`) 
            VALUES ({id_persona}, 'Moto - Gasolina, Mantenimiento, Accesorios, Seguridad')
            """
            cursor.execute(sql_moto)
            db.conn.commit()
            logger.info("   ✓ Categoría 'Moto' agregada exitosamente")
        except Exception as e:
            if "Duplicate" in str(e):
                logger.warning("   ⊘ Categoría 'Moto' ya existe")
            else:
                raise
        
        # 2. Mejorar nombre de "Combustible" → "Gasolina/Combustible"
        logger.info("\n2. Actualizando 'Combustible' → 'Gasolina/Combustible'...")
        try:
            sql_combustible = """
            UPDATE `app_presupuesto`.`categoria` 
            SET `nombre` = 'Gasolina/Combustible' 
            WHERE `nombre` = 'Combustible'
            """
            cursor.execute(sql_combustible)
            rows = cursor.rowcount
            db.conn.commit()
            if rows > 0:
                logger.info(f"   ✓ Actualizado: {rows} registro(s)")
            else:
                logger.warning("   ⊘ No se encontró 'Combustible' para actualizar")
        except Exception as e:
            if "Duplicate" in str(e):
                logger.warning("   ⊘ Ya existe 'Gasolina/Combustible'")
            else:
                raise
        
        # 3. Mejorar nombre "Transporte - Taxi/Uber" → "Taxi/Uber"
        logger.info("\n3. Actualizando 'Transporte - Taxi/Uber' → 'Taxi/Uber'...")
        try:
            sql_uber = """
            UPDATE `app_presupuesto`.`categoria` 
            SET `nombre` = 'Taxi/Uber' 
            WHERE `nombre` = 'Transporte - Taxi/Uber'
            """
            cursor.execute(sql_uber)
            rows = cursor.rowcount
            db.conn.commit()
            if rows > 0:
                logger.info(f"   ✓ Actualizado: {rows} registro(s)")
            else:
                logger.warning("   ⊘ No se encontró 'Transporte - Taxi/Uber' para actualizar")
        except Exception as e:
            if "Duplicate" in str(e):
                logger.warning("   ⊘ Ya existe 'Taxi/Uber'")
            else:
                raise
        
        # 4. Mejorar nombre "Mercado y Supermercado" → "Supermercado"
        logger.info("\n4. Actualizando 'Mercado y Supermercado' → 'Supermercado'...")
        try:
            sql_mercado = """
            UPDATE `app_presupuesto`.`categoria` 
            SET `nombre` = 'Supermercado' 
            WHERE `nombre` = 'Mercado y Supermercado'
            """
            cursor.execute(sql_mercado)
            rows = cursor.rowcount
            db.conn.commit()
            if rows > 0:
                logger.info(f"   ✓ Actualizado: {rows} registro(s)")
            else:
                logger.warning("   ⊘ No se encontró 'Mercado y Supermercado' para actualizar")
        except Exception as e:
            if "Duplicate" in str(e):
                logger.warning("   ⊘ Ya existe 'Supermercado'")
            else:
                raise
        
        # Listar todas las categorías relacionadas con transporte/moto
        logger.info("\n5. Verificando categorías finales:")
        sql_verify = """
        SELECT id_categoria, nombre 
        FROM `app_presupuesto`.`categoria`
        WHERE nombre LIKE '%oto%' OR nombre LIKE '%ransporte%' OR nombre LIKE '%taxi%' 
              OR nombre LIKE '%axi%' OR nombre LIKE '%Uber%' OR nombre LIKE '%Gasolina%' 
              OR nombre LIKE '%Supermercado%'
        ORDER BY id_categoria
        """
        cursor.execute(sql_verify)
        results = cursor.fetchall()
        
        if results:
            logger.info("   Categorías relacionadas:")
            for row in results:
                logger.info(f"   - {row[1]} (ID: {row[0]})")
        
        cursor.close()
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ Migración completada exitosamente")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        if db.conn:
            db.conn.rollback()
        return False
    finally:
        if db.conn:
            db.conn.close()

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
