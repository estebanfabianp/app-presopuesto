#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica migracion para ON DELETE CASCADE en todas las FK de persona.

Uso:
    python scripts/migrations/apply_migration_2026_04_13_persona_delete_cascade.py
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

    total = len(statements)
    for i, stmt in enumerate(statements, start=1):
        lines = [ln for ln in stmt.splitlines() if ln.strip() and not ln.strip().startswith('--')]
        if not lines:
            continue
        sql = '\n'.join(lines)
        result = db.execute_non_query(sql + ';')
        if result is None:
            logger.error(f"[{i}/{total}] Fallo ejecutando sentencia")
            return False
        logger.info(f"[{i}/{total}] OK")

    logger.info("Script SQL ejecutado correctamente")
    return True


def apply_migration() -> bool:
    db = DatabaseConnector()
    try:
        logger.info("Iniciando migracion de ON DELETE CASCADE para persona...")
        sql_file = ROOT_DIR / "base_de_datos/db/02_maintenance/schema/2026-04-13_persona_delete_cascade.sql"
        ok = _run_sql_script(db, sql_file)
        if not ok:
            return False

        rows = db.execute_query(
            """
            SELECT kcu.table_name, rc.delete_rule
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.referential_constraints rc
              ON rc.constraint_schema = kcu.constraint_schema
             AND rc.constraint_name = kcu.constraint_name
            WHERE kcu.referenced_table_schema = DATABASE()
              AND kcu.referenced_table_name = 'persona'
            """
        )

        invalid = [r for r in (rows or []) if (r.get('delete_rule') or '').upper() != 'CASCADE']
        if invalid:
            logger.error(f"Se encontraron FK sin CASCADE: {invalid}")
            return False

        logger.info("Migracion completada con exito")
        return True
    finally:
        db.close()


if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
