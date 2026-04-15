#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consolidar, corregir y mejorar categorías

Cambios:
1. Corregir ortografía (Cuotas de prestamos → Cuotas de Préstamos)
2. Estandarizar mayúsculas (salud → Salud)
3. Eliminar duplicados manteniendo la mejor opción
4. Agregar categorías faltantes
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector
from src.utils.logger import logger

def consolidate_categories():
    """Consolida y mejora categorías."""
    db = DatabaseConnector()
    cursor = db.conn.cursor()
    
    try:
        logger.info("=" * 80)
        logger.info("CONSOLIDACIÓN Y MEJORA DE CATEGORÍAS")
        logger.info("=" * 80)
        
        # 1. CORREGIR ORTOGRAFÍA Y MAYÚSCULAS
        logger.info("\n1. CORRIGIENDO ORTOGRAFÍA Y MAYÚSCULAS:")
        corrections = {
            4: ("Cuotas de prestamos", "Cuotas de Préstamos"),
            207: ("Mantenimiento y reparacion", "Mantenimiento y Reparación"),
            213: ("estadia", "Estadía"),
            228: ("salud", "Salud"),
            229: ("citas", "Citas Médicas"),
            230: ("cepillo de dientes", "Cuidado Dental"),
            231: ("cuidado de la piel", "Cuidado Personal"),
            232: ("peluquero", "Peluquería/Barbería"),
            234: ("impuestos", "Impuestos"),
            235: ("hogar", "Cuidado del Hogar"),
            236: ("moto", "Moto"),
            237: ("declaracion de renta", "Declaración de Renta"),
        }
        
        for cat_id, (old_name, new_name) in corrections.items():
            sql = "UPDATE categoria SET nombre = %s WHERE id_categoria = %s"
            cursor.execute(sql, (new_name, cat_id))
            logger.info(f"   {old_name:40s} → {new_name}")
        
        db.conn.commit()
        
        # 2. INFORMACIÓN SOBRE DUPLICADOS A CONSOLIDAR
        logger.info("\n2. DUPLICADOS A CONSOLIDAR (VALIDAR):")
        
        duplicates = {
            "Ingresos": [1, 189],
            "Transporte": [7, 183, 212],
            "Alimentación": [8, 9, 185],
            "Otros Ingresos": [14, 166],
            "Entretenimiento": [36, 182],
            "Educación": [35, 186],
            "Ocio/Entretenimiento": [52, 181],
            "Gasolina": [25, 179],
            "Parqueadero": [28, 180],
            "Gimnasio": [41, 169],
            "Streaming": [47, 176],
            "Agua": [22, 193],
            "Electricidad/Luz": [21, 194],
            "Gas": [23, 195],
            "Telefonía": [24, 174],
            "Cine": [46, 204],
            "Servicios": [3, 184],
        }
        
        logger.warning("\n   VALIDAR MANUALMENTE EN BD:")
        for group, ids in duplicates.items():
            logger.warning(f"   - {group}: IDs {ids} (consolidar en uno)")
        
        # 3. CATEGORÍAS FALTANTES A AGREGAR
        logger.info("\n3. CATEGORÍAS FALTANTES QUE SE DEBEN AGREGAR:")
        missing = [
            "Donaciones y Contribuciones",
            "Lavandería/Lavado de Ropa",
            "Lavado de Vehículo",
            "Seguros - Vehículo",
            "Seguros - Hogar",
            "Seguros - Vida",
            "Seguros - Otros",
            "Vivienda - Arriendo",
            "Vivienda - Hipoteca",
            "Servicios Domésticos",
            "Reparación y Mantenimiento de Hogar",
            "Animales de Compañía - Veterinario",
            "Animales de Compañía - Alimentos",
            "Animales de Compañía - Otros",
            "Accesorios Personales",
            "Cosméticos y Perfumes",
            "Pasatiempos",
            "Compras en Línea",
            "Devoluciones y Reembolsos",
            "Efectivo/ATM",
        ]
        
        logger.info("\n   Categorías recomendadas:")
        for cat in missing:
            logger.info(f"   - {cat}")
        
        logger.info("\n" + "=" * 80)
        logger.info("RESUMEN:")
        logger.info("=" * 80)
        logger.info("✓ Ortografía y mayúsculas corregidas")
        logger.warning("ⓘ Revisar duplicados marcados arriba")
        logger.info("ℹ  Considerar agregar categorías faltantes")
        logger.info("\nNOTA: Ejecutar consolidación de duplicados de forma manual")
        logger.info("      para validar que no hay datos relacionados a mantener")
        logger.info("=" * 80)
        
        cursor.close()
        db.conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.conn.rollback()
        db.conn.close()
        return False

if __name__ == "__main__":
    success = consolidate_categories()
    sys.exit(0 if success else 1)
