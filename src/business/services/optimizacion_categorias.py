# -*- coding: utf-8 -*-
"""
Servicio de Optimización de Categorías.

Automatiza la clasificación de gastos basándose en el historial de categorización
de los movimientos de tarjeta de crédito.

Reglas de negocio:
- Si un `concepto` (nota) aparece siempre con la misma categoría → regla automática.
- Si el mismo `concepto` ha tenido múltiples categorías → conflicto (requiere
  intervención manual).
- Las reglas confirmadas explícitamente por el usuario prevalecen sobre las derivadas.
- Un concepto puede marcarse como "ignorar" (id_categoria=NULL en categoria_regla)
  para que nunca se autoclasifique.

Tabla persistente:
    categoria_regla(id_regla, id_persona, concepto, id_categoria, ...)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DDL idempotente
# ---------------------------------------------------------------------------

_CREATE_CATEGORIA_REGLA = """
CREATE TABLE IF NOT EXISTS categoria_regla (
    id_regla       INT AUTO_INCREMENT PRIMARY KEY,
    id_persona     INT          NOT NULL,
    concepto       VARCHAR(500) NOT NULL,
    id_categoria   INT          NULL
        COMMENT 'NULL = ignorar (no autoclasificar)',
    fecha_creacion DATETIME     DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_regla_persona_concepto (id_persona, concepto(255)),
    CONSTRAINT fk_cr_persona   FOREIGN KEY (id_persona)
        REFERENCES persona(id_persona)   ON DELETE CASCADE,
    CONSTRAINT fk_cr_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


class OptimizacionCategoriasService:
    """Servicio de análisis y aplicación de reglas de categorización."""

    def __init__(self, db) -> None:
        """
        Args:
            db: Instancia de DatabaseConnector.
        """
        self.db = db
        self._ensure_table()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    def _ensure_table(self) -> None:
        """Crea `categoria_regla` si no existe (idempotente)."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(_CREATE_CATEGORIA_REGLA)
            self.db.conn.commit()
            cursor.close()
        except Exception as exc:
            logger.warning("No se pudo crear tabla categoria_regla: %s", exc)

    # ------------------------------------------------------------------
    # Lectura de datos
    # ------------------------------------------------------------------

    def get_categorias(self, id_persona: int) -> List[Dict]:
        """Retorna todas las categorías activas del usuario."""
        rows = self.db.execute_query(
            """
            SELECT id_categoria, nombre, icono, color
            FROM categoria
            WHERE id_persona = %s AND estado = 1
            ORDER BY nombre
            """,
            (id_persona,),
        )
        return rows or []

    def get_reglas(self, id_persona: int) -> List[Dict]:
        """
        Retorna reglas de categorización disponibles para el usuario.

        Combina:
        1. Reglas **confirmadas** almacenadas en `categoria_regla`
           (con id_categoria NOT NULL).
        2. Reglas **automáticas** derivadas del historial de `movimiento_tarjeta`
           (concepto → exactamente 1 categoría distinta).
           Se excluyen conceptos ya presentes en `categoria_regla`.

        Returns:
            Lista de dicts con claves:
                concepto, id_categoria, nombre_categoria, total_movimientos,
                fuente ('confirmada' | 'automatica')
        """
        # 1. Reglas confirmadas
        confirmadas = self.db.execute_query(
            """
            SELECT
                cr.concepto,
                cr.id_categoria,
                c.nombre  AS nombre_categoria,
                (SELECT COUNT(*) FROM movimiento_tarjeta mt2
                 WHERE mt2.id_persona = cr.id_persona
                   AND mt2.nota = cr.concepto) AS total_movimientos,
                'confirmada' AS fuente
            FROM categoria_regla cr
            JOIN categoria c ON c.id_categoria = cr.id_categoria
            WHERE cr.id_persona = %s AND cr.id_categoria IS NOT NULL
            ORDER BY cr.concepto
            """,
            (id_persona,),
        ) or []

        conceptos_confirmados = {r["concepto"] for r in confirmadas}

        # 2. Reglas automáticas (historia con 1 sola categoría)
        automaticas_raw = self.db.execute_query(
            """
            SELECT
                mt.nota                  AS concepto,
                MAX(mt.id_categoria)     AS id_categoria,
                COUNT(*)                 AS total_movimientos
            FROM movimiento_tarjeta mt
            WHERE mt.id_persona = %s
              AND mt.id_categoria IS NOT NULL
              AND mt.nota IS NOT NULL
              AND mt.nota <> ''
            GROUP BY mt.nota
            HAVING COUNT(DISTINCT mt.id_categoria) = 1
            ORDER BY mt.nota
            """,
            (id_persona,),
        ) or []

        # Enriquecer con nombre de categoría y excluir ya confirmadas
        automaticas: List[Dict] = []
        for row in automaticas_raw:
            if row["concepto"] in conceptos_confirmados:
                continue
            cat = self.db.execute_query(
                "SELECT nombre FROM categoria WHERE id_categoria = %s",
                (row["id_categoria"],),
            )
            nombre = cat[0]["nombre"] if cat else "—"
            automaticas.append({
                "concepto": row["concepto"],
                "id_categoria": row["id_categoria"],
                "nombre_categoria": nombre,
                "total_movimientos": row["total_movimientos"],
                "fuente": "automatica",
            })

        return confirmadas + automaticas

    def get_conflictos(self, id_persona: int) -> List[Dict]:
        """
        Retorna conceptos con más de una categoría histórica
        y sin regla confirmada/ignorada.

        Returns:
            Lista de dicts con claves:
                concepto, num_categorias, categorias=[{id_categoria, nombre, total}]
        """
        # Conceptos problemáticos (>1 categoría, sin regla)
        raw = self.db.execute_query(
            """
            SELECT mt.nota AS concepto, COUNT(DISTINCT mt.id_categoria) AS num_categorias
            FROM movimiento_tarjeta mt
            WHERE mt.id_persona = %s
              AND mt.id_categoria IS NOT NULL
              AND mt.nota IS NOT NULL AND mt.nota <> ''
              AND mt.nota NOT IN (
                  SELECT cr.concepto FROM categoria_regla cr WHERE cr.id_persona = %s
              )
            GROUP BY mt.nota
            HAVING COUNT(DISTINCT mt.id_categoria) > 1
            ORDER BY num_categorias DESC, mt.nota
            """,
            (id_persona, id_persona),
        ) or []

        resultado: List[Dict] = []
        for row in raw:
            cats = self.db.execute_query(
                """
                SELECT mt.id_categoria, c.nombre, COUNT(*) AS total
                FROM movimiento_tarjeta mt
                JOIN categoria c ON c.id_categoria = mt.id_categoria
                WHERE mt.id_persona = %s
                  AND mt.nota = %s
                  AND mt.id_categoria IS NOT NULL
                GROUP BY mt.id_categoria, c.nombre
                ORDER BY total DESC
                """,
                (id_persona, row["concepto"]),
            ) or []
            resultado.append({
                "concepto": row["concepto"],
                "num_categorias": row["num_categorias"],
                "categorias": cats,
            })
        return resultado

    def get_sin_categoria(self, id_persona: int, limit: int = 200) -> List[Dict]:
        """
        Retorna movimientos de tarjeta sin categoría asignada.

        Returns:
            Lista de dicts: id_movimiento_tarjeta, concepto, fecha, valor
        """
        rows = self.db.execute_query(
            """
            SELECT id_movimiento_tarjeta, nota AS concepto, fecha, valor
            FROM movimiento_tarjeta
            WHERE id_persona = %s AND id_categoria IS NULL
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (id_persona, limit),
        )
        return rows or []

    def get_stats(self, id_persona: int) -> Dict:
        """Retorna conteos de resumen para el encabezado de la vista."""
        def _count(q, *p):
            r = self.db.execute_query(q, p)
            return int(r[0]["c"]) if r else 0

        reglas       = len(self.get_reglas(id_persona))
        conflictos   = len(self.get_conflictos(id_persona))
        sin_cat      = _count(
            "SELECT COUNT(*) AS c FROM movimiento_tarjeta WHERE id_persona=%s AND id_categoria IS NULL",
            id_persona
        )
        return {"reglas": reglas, "conflictos": conflictos, "sin_categoria": sin_cat}

    # ------------------------------------------------------------------
    # Escritura / acción
    # ------------------------------------------------------------------

    def aplicar_reglas(self, id_persona: int) -> int:
        """
        Aplica todas las reglas disponibles a los movimientos sin categoría.

        Orden de precedencia:
        1. Reglas confirmadas en `categoria_regla`.
        2. Reglas automáticas derivadas del historial.

        Returns:
            Número de movimientos actualizados.
        """
        total = 0
        for regla in self.get_reglas(id_persona):
            updated = self._aplicar_una_regla(
                id_persona, regla["concepto"], regla["id_categoria"]
            )
            total += updated
        logger.info("[OptimizacionCategorias] Actualizados %d movimientos", total)
        return total

    def confirmar_regla(
        self, concepto: str, id_categoria: int, id_persona: int
    ) -> bool:
        """
        Guarda una regla confirmada por el usuario y aplica inmediatamente a
        los movimientos sin categoría con ese concepto.
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO categoria_regla (id_persona, concepto, id_categoria)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id_categoria = VALUES(id_categoria),
                    fecha_actualizacion = NOW()
                """,
                (id_persona, concepto, id_categoria),
            )
            self.db.conn.commit()
            cursor.close()
            self._aplicar_una_regla(id_persona, concepto, id_categoria)
            return True
        except Exception as exc:
            logger.error("confirmar_regla error: %s", exc)
            return False

    def limpiar_regla(self, concepto: str, id_persona: int) -> bool:
        """
        Elimina la entrada de `categoria_regla` para que el concepto vuelva
        a ser clasificado automáticamente por el historial.
        """
        result = self.db.execute_non_query(
            "DELETE FROM categoria_regla WHERE id_persona = %s AND concepto = %s",
            (id_persona, concepto),
        )
        return result is not None

    def ignorar_concepto(self, concepto: str, id_persona: int) -> bool:
        """
        Marca un concepto como "nunca autoclasificar" (id_categoria=NULL).
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO categoria_regla (id_persona, concepto, id_categoria)
                VALUES (%s, %s, NULL)
                ON DUPLICATE KEY UPDATE id_categoria = NULL, fecha_actualizacion = NOW()
                """,
                (id_persona, concepto),
            )
            self.db.conn.commit()
            cursor.close()
            return True
        except Exception as exc:
            logger.error("ignorar_concepto error: %s", exc)
            return False

    def asignar_categoria_movimiento(
        self, id_movimiento_tarjeta: int, id_categoria: int, id_persona: int
    ) -> bool:
        """Asigna categoría a un movimiento específico."""
        result = self.db.execute_non_query(
            """
            UPDATE movimiento_tarjeta
            SET id_categoria = %s
            WHERE id_movimiento_tarjeta = %s AND id_persona = %s
            """,
            (id_categoria, id_movimiento_tarjeta, id_persona),
        )
        return result is not None

    # ------------------------------------------------------------------
    # Auxiliar privado
    # ------------------------------------------------------------------

    def _aplicar_una_regla(
        self, id_persona: int, concepto: str, id_categoria: int
    ) -> int:
        """UPDATE movimiento_tarjeta donde nota=concepto y categoría es NULL."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                UPDATE movimiento_tarjeta
                SET id_categoria = %s
                WHERE id_persona = %s
                  AND nota = %s
                  AND id_categoria IS NULL
                """,
                (id_categoria, id_persona, concepto),
            )
            affected = cursor.rowcount
            self.db.conn.commit()
            cursor.close()
            return affected
        except Exception as exc:
            logger.error("_aplicar_una_regla error: %s", exc)
            return 0
