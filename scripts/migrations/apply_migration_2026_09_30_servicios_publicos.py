"""Migración: partir la categoría 'Servicios Públicos' en Luz, Agua, Gas y Triple Play."""

import logging
from src.database.db_connector import DatabaseConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_servicios_publicos():
    db = DatabaseConnector()
    try:
        # 1. Convertir 'Servicios Públicos' (id 13) en categoría principal
        db.execute_non_query("UPDATE categoria SET parent_id = NULL WHERE id_categoria = 13")
        logger.info("Servicios Públicos (id 13) configurado como categoría principal.")

        # 2. Crear o actualizar subcategorías
        subcats = [
            ("Luz", "fa-bolt", "#f59e0b"),
            ("Agua", "fa-faucet-drip", "#0284c7"),
            ("Gas", "fa-fire-flame-simple", "#ea580c"),
            ("Triple Play", "fa-tv", "#8b5cf6"),
        ]

        ids = {}
        for nombre, icono, color in subcats:
            rows = db.execute_query(
                "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
                (nombre,),
            )
            if rows:
                cat_id = rows[0]["id_categoria"]
                db.execute_non_query(
                    "UPDATE categoria SET parent_id = 13, icono = %s, color = %s, estado = 1 WHERE id_categoria = %s",
                    (icono, color, cat_id),
                )
                logger.info("Subcategoría existente '%s' actualizada (id=%s).", nombre, cat_id)
            else:
                cat_id = db.execute_non_query(
                    "INSERT INTO categoria (nombre, parent_id, icono, color, estado) VALUES (%s, 13, %s, %s, 1)",
                    (nombre, icono, color),
                )
                logger.info("Subcategoría '%s' creada (id=%s).", nombre, cat_id)
            ids[nombre.lower()] = cat_id

        # 3. Reclasificar movimientos históricos de id_categoria = 13
        # ENEL -> Luz
        if "luz" in ids:
            n_luz = db.execute_non_query(
                "UPDATE movimiento SET id_categoria = %s WHERE id_categoria = 13 AND (LOWER(nota) LIKE %s)",
                (ids["luz"], "%enel%"),
            )
            logger.info("Movimientos ENEL reclasificados a Luz: %s", n_luz)

        # VANTI -> Gas
        if "gas" in ids:
            n_gas = db.execute_non_query(
                "UPDATE movimiento SET id_categoria = %s WHERE id_categoria = 13 AND (LOWER(nota) LIKE %s)",
                (ids["gas"], "%vanti%"),
            )
            logger.info("Movimientos VANTI reclasificados a Gas: %s", n_gas)

        # Acueducto -> Agua
        if "agua" in ids:
            n_agua = db.execute_non_query(
                "UPDATE movimiento SET id_categoria = %s WHERE id_categoria = 13 AND (LOWER(nota) LIKE %s)",
                (ids["agua"], "%acueducto%"),
            )
            logger.info("Movimientos Acueducto reclasificados a Agua: %s", n_agua)

        # 4. Actualizar reglas automáticas en categoria_regla si la tabla existe
        table_regla = db.execute_query(
            "SELECT COUNT(*) AS total FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'categoria_regla'"
        )
        if table_regla and table_regla[0].get("total", 0) > 0:
            if "luz" in ids:
                db.execute_non_query(
                    "UPDATE categoria_regla SET id_categoria = %s WHERE LOWER(concepto) LIKE %s",
                    (ids["luz"], "%enel%"),
                )
            if "gas" in ids:
                db.execute_non_query(
                    "UPDATE categoria_regla SET id_categoria = %s WHERE LOWER(concepto) LIKE %s",
                    (ids["gas"], "%vanti%"),
                )
            if "agua" in ids:
                db.execute_non_query(
                    "UPDATE categoria_regla SET id_categoria = %s WHERE LOWER(concepto) LIKE %s",
                    (ids["agua"], "%acueducto%"),
                )
            logger.info("Reglas de categoria_regla actualizadas a las nuevas subcategorías.")

        # Verificar si quedó algún movimiento en id 13
        restantes = db.execute_query("SELECT COUNT(*) AS total FROM movimiento WHERE id_categoria = 13")
        logger.info("Movimientos restantes en id 13 (Servicios Públicos): %s", restantes[0]["total"] if restantes else 0)

        print("MIGRACION_COMPLETADA_EXITOSAMENTE")
    except Exception as exc:
        logger.error("Error en migración: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_servicios_publicos()
