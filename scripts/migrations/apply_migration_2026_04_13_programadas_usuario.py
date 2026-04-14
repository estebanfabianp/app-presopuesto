#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica migracion para asociar transacciones programadas a usuario.

Uso:
    python scripts/migrations/apply_migration_2026_04_13_programadas_usuario.py
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
    statements = [s.strip() for s in content.split(';') if s.strip()]

    for i, stmt in enumerate(statements, start=1):
        if stmt.startswith('--'):
            continue
        try:
            db.execute_non_query(stmt + ';')
            logger.info(f"[{i}/{len(statements)}] OK")
        except Exception as exc:
            logger.error(f"[{i}/{len(statements)}] Error: {exc}")
            return False

    return True


def apply_migration() -> bool:
    db = DatabaseConnector()
    try:
        logger.info("Iniciando migracion de programadas por usuario...")
        sql_file = ROOT_DIR / "base_de_datos/db/02_maintenance/schema/2026-04-13_programadas_por_usuario.sql"
        ok = _run_sql_script(db, sql_file)
        if not ok:
            return False

        check = db.execute_query(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'transaccion_programada'
              AND column_name = 'id_persona'
            """
        )
        if not check:
            logger.error("No se encontro columna id_persona en transaccion_programada")
            return False

        logger.info("Migracion completada con exito")
        return True
    finally:
        db.close()


if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
