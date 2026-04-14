#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica migracion para asociar categoria, beneficiario y constantes al usuario.

Uso:
    python scripts/migrations/apply_migration_2026_04_13_catalogos_usuario.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_connector import DatabaseConnector
from src.utils.logger import logger


def _run_sql_script(db: DatabaseConnector, file_path: Path) -> bool:
    if not file_path.exists():
        logger.error(f"No existe el archivo SQL: {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")
    db._reconnect()  # pylint: disable=protected-access
    if not db.conn:
        logger.error("No hay conexion activa para ejecutar la migracion")
        return False

    try:
        with db.conn.cursor() as cursor:
            for result in cursor.execute(content, multi=True):
                # Consumir resultados de SELECT internos para evitar "Unread result found"
                if result.with_rows:
                    _ = result.fetchall()
        db.conn.commit()
        logger.info("Script SQL ejecutado correctamente")
        return True
    except Exception as exc:
        logger.error(f"Error ejecutando script SQL: {exc}")
        try:
            db.conn.rollback()
        except Exception as rollback_exc:
            logger.warning(f"No se pudo hacer rollback: {rollback_exc}")
        return False


def apply_migration() -> bool:
    db = DatabaseConnector()
    try:
        logger.info("Iniciando migracion de catalogos por usuario...")
        sql_file = ROOT_DIR / "base_de_datos/db/02_maintenance/schema/2026-04-13_catalogos_por_usuario.sql"
        ok = _run_sql_script(db, sql_file)
        if not ok:
            return False

        checks = db.execute_query(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name IN ('categoria', 'beneficiario', 'constantes')
              AND column_name = 'id_persona'
            """
        )
        if len(checks or []) != 3:
            logger.error("No se completo la creacion de id_persona en los 3 catalogos")
            return False

        logger.info("Migracion completada con exito")
        return True
    finally:
        db.close()


if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
