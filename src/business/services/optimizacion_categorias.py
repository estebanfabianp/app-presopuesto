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

_CREATE_BENEFICIARIO_REGLA = """
CREATE TABLE IF NOT EXISTS beneficiario_regla (
    id_regla       INT AUTO_INCREMENT PRIMARY KEY,
    id_persona     INT          NOT NULL,
    concepto       VARCHAR(500) NOT NULL,
    id_beneficiario INT         NULL
        COMMENT 'NULL = ignorar (no autoasignar)',
    fecha_creacion DATETIME     DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_bregla_persona_concepto (id_persona, concepto(255)),
    CONSTRAINT fk_br_persona FOREIGN KEY (id_persona)
        REFERENCES persona(id_persona) ON DELETE CASCADE,
    CONSTRAINT fk_br_beneficiario FOREIGN KEY (id_beneficiario)
        REFERENCES beneficiario(id_beneficiario) ON DELETE SET NULL
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
        self._ensure_beneficiario_table()

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

    def _ensure_beneficiario_table(self) -> None:
        """Crea `beneficiario_regla` si no existe (idempotente)."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(_CREATE_BENEFICIARIO_REGLA)
            self.db.conn.commit()
            cursor.close()
        except Exception as exc:
            logger.warning("No se pudo crear tabla beneficiario_regla: %s", exc)

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

    def get_beneficiarios(self, id_persona: int) -> List[Dict]:
        """Retorna beneficiarios activos del usuario."""
        rows = self.db.execute_query(
            """
            SELECT id_beneficiario, nombre
            FROM beneficiario
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
                (
                    SELECT COUNT(*)
                    FROM (
                        SELECT NULLIF(TRIM(mt2.nota), '') AS concepto
                        FROM movimiento_tarjeta mt2
                        WHERE mt2.id_persona = %s

                        UNION ALL

                        SELECT COALESCE(NULLIF(TRIM(m2.codigo), ''), NULLIF(TRIM(m2.nota), '')) AS concepto
                        FROM movimiento m2
                        INNER JOIN cuenta c2 ON c2.id_cuenta = m2.id_cuenta
                        WHERE c2.id_persona = %s
                    ) z
                    WHERE z.concepto = cr.concepto
                ) AS total_movimientos,
                (
                    SELECT COUNT(*)
                    FROM (
                        SELECT NULLIF(TRIM(mt3.nota), '') AS concepto, mt3.id_categoria
                        FROM movimiento_tarjeta mt3
                        WHERE mt3.id_persona = %s

                        UNION ALL

                        SELECT COALESCE(NULLIF(TRIM(m3.codigo), ''), NULLIF(TRIM(m3.nota), '')) AS concepto, m3.id_categoria
                        FROM movimiento m3
                        INNER JOIN cuenta c3 ON c3.id_cuenta = m3.id_cuenta
                        WHERE c3.id_persona = %s
                    ) p
                    WHERE p.concepto = cr.concepto
                      AND p.id_categoria IS NULL
                ) AS pendientes,
                'confirmada' AS fuente
            FROM categoria_regla cr
            JOIN categoria c ON c.id_categoria = cr.id_categoria
            WHERE cr.id_persona = %s AND cr.id_categoria IS NOT NULL
            ORDER BY cr.concepto
            """,
            (id_persona, id_persona, id_persona, id_persona, id_persona),
        ) or []

        conceptos_reglados_rows = self.db.execute_query(
            "SELECT concepto FROM categoria_regla WHERE id_persona = %s",
            (id_persona,),
        ) or []
        conceptos_reglados = {r["concepto"] for r in conceptos_reglados_rows}

        # 2. Reglas automáticas (historia con 1 sola categoría)
        automaticas_raw = self.db.execute_query(
            """
            SELECT
                d.concepto,
                MAX(d.id_categoria) AS id_categoria,
                COUNT(*) AS total_movimientos,
                SUM(CASE WHEN d.id_categoria IS NULL THEN 1 ELSE 0 END) AS pendientes
            FROM (
                SELECT NULLIF(TRIM(mt.nota), '') AS concepto, mt.id_categoria
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s

                UNION ALL

                SELECT COALESCE(NULLIF(TRIM(m.codigo), ''), NULLIF(TRIM(m.nota), '')) AS concepto, m.id_categoria
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s
            ) d
            WHERE d.concepto IS NOT NULL AND d.concepto <> ''
            GROUP BY d.concepto
            HAVING COUNT(DISTINCT CASE WHEN d.id_categoria IS NOT NULL THEN d.id_categoria END) = 1
               AND pendientes > 0
            ORDER BY d.concepto
            """,
            (id_persona, id_persona),
        ) or []

        # Mostrar reglas confirmadas solo si tienen pendientes por categorizar.
        confirmadas = [r for r in confirmadas if int(r.get("pendientes") or 0) > 0]

        # Enriquecer con nombre de categoría y excluir ya regladas (confirmadas o ignoradas)
        automaticas: List[Dict] = []
        for row in automaticas_raw:
            if row["concepto"] in conceptos_reglados:
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
        Retorna movimientos sin categoría asignada de tarjeta y cuenta bancaria.

        Returns:
            Lista de dicts con claves:
            - origen: 'tarjeta' | 'cuenta'
            - id_movimiento
            - concepto
            - fecha
            - valor
        """
        rows = self.db.execute_query(
            """
            SELECT * FROM (
                SELECT
                    'tarjeta' AS origen,
                    mt.id_movimiento_tarjeta AS id_movimiento,
                    mt.nota AS concepto,
                    mt.fecha,
                    mt.valor
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s
                  AND mt.id_categoria IS NULL

                UNION ALL

                SELECT
                    'cuenta' AS origen,
                    m.id_movimiento AS id_movimiento,
                    COALESCE(NULLIF(m.codigo, ''), m.nota, 'Sin descripción') AS concepto,
                    DATE(m.fecha_creacion) AS fecha,
                    m.monto AS valor
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s
                  AND m.id_categoria IS NULL
            ) t
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (id_persona, id_persona, limit),
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
            """
            SELECT (
                COALESCE((SELECT COUNT(*) FROM movimiento_tarjeta mt WHERE mt.id_persona=%s AND mt.id_categoria IS NULL), 0)
                +
                COALESCE((
                    SELECT COUNT(*)
                    FROM movimiento m
                    INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                    WHERE c.id_persona=%s AND m.id_categoria IS NULL
                ), 0)
            ) AS c
            """,
            id_persona,
            id_persona,
        )
        reglas_benef = len(self.get_reglas_beneficiario(id_persona))
        conflictos_benef = len(self.get_conflictos_beneficiario(id_persona))
        sin_benef = _count(
            """
            SELECT (
                COALESCE((SELECT COUNT(*) FROM movimiento_tarjeta mt WHERE mt.id_persona=%s AND mt.id_beneficiario IS NULL), 0)
                +
                COALESCE((
                    SELECT COUNT(*)
                    FROM movimiento m
                    INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                    WHERE c.id_persona=%s AND m.id_beneficiario IS NULL
                ), 0)
            ) AS c
            """,
            id_persona,
            id_persona,
        )

        return {
            "reglas": reglas,
            "conflictos": conflictos,
            "sin_categoria": sin_cat,
            "reglas_beneficiario": reglas_benef,
            "conflictos_beneficiario": conflictos_benef,
            "sin_beneficiario": sin_benef,
        }

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
        self, origen: str, id_movimiento: int, id_categoria: int, id_persona: int
    ) -> bool:
        """Asigna categoría a un movimiento específico de tarjeta o cuenta."""
        if origen == 'cuenta':
            owner = self.db.execute_query(
                """
                SELECT 1
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE m.id_movimiento = %s AND c.id_persona = %s
                LIMIT 1
                """,
                (id_movimiento, id_persona),
            )
            if not owner:
                return False

            result = self.db.execute_non_query(
                """
                UPDATE movimiento
                SET id_categoria = %s
                WHERE id_movimiento = %s
                """,
                (id_categoria, id_movimiento),
            )
            return result is not None

        result = self.db.execute_non_query(
            """
            UPDATE movimiento_tarjeta
            SET id_categoria = %s
            WHERE id_movimiento_tarjeta = %s AND id_persona = %s
            """,
            (id_categoria, id_movimiento, id_persona),
        )
        return result is not None

    def get_reglas_beneficiario(self, id_persona: int) -> List[Dict]:
        """Retorna reglas de beneficiario confirmadas y automáticas."""
        confirmadas = self.db.execute_query(
            """
            SELECT
                br.concepto,
                br.id_beneficiario,
                b.nombre AS nombre_beneficiario,
                (
                    SELECT COUNT(*)
                    FROM (
                        SELECT NULLIF(TRIM(mt2.nota), '') AS concepto
                        FROM movimiento_tarjeta mt2
                        WHERE mt2.id_persona = %s

                        UNION ALL

                        SELECT COALESCE(NULLIF(TRIM(m2.codigo), ''), NULLIF(TRIM(m2.nota), '')) AS concepto
                        FROM movimiento m2
                        INNER JOIN cuenta c2 ON c2.id_cuenta = m2.id_cuenta
                        WHERE c2.id_persona = %s
                    ) z
                    WHERE z.concepto = br.concepto
                ) AS total_movimientos,
                (
                    SELECT COUNT(*)
                    FROM (
                        SELECT NULLIF(TRIM(mt3.nota), '') AS concepto, mt3.id_beneficiario
                        FROM movimiento_tarjeta mt3
                        WHERE mt3.id_persona = %s

                        UNION ALL

                        SELECT COALESCE(NULLIF(TRIM(m3.codigo), ''), NULLIF(TRIM(m3.nota), '')) AS concepto, m3.id_beneficiario
                        FROM movimiento m3
                        INNER JOIN cuenta c3 ON c3.id_cuenta = m3.id_cuenta
                        WHERE c3.id_persona = %s
                    ) p
                    WHERE p.concepto = br.concepto
                      AND p.id_beneficiario IS NULL
                ) AS pendientes,
                'confirmada' AS fuente
            FROM beneficiario_regla br
            JOIN beneficiario b ON b.id_beneficiario = br.id_beneficiario
            WHERE br.id_persona = %s AND br.id_beneficiario IS NOT NULL
            ORDER BY br.concepto
            """,
            (id_persona, id_persona, id_persona, id_persona, id_persona),
        ) or []

        conceptos_reglados_rows = self.db.execute_query(
            "SELECT concepto FROM beneficiario_regla WHERE id_persona = %s",
            (id_persona,),
        ) or []
        conceptos_reglados = {r["concepto"] for r in conceptos_reglados_rows}

        automaticas_raw = self.db.execute_query(
            """
            SELECT
                d.concepto,
                MAX(d.id_beneficiario) AS id_beneficiario,
                COUNT(*) AS total_movimientos,
                SUM(CASE WHEN d.id_beneficiario IS NULL THEN 1 ELSE 0 END) AS pendientes
            FROM (
                SELECT NULLIF(TRIM(mt.nota), '') AS concepto, mt.id_beneficiario
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s

                UNION ALL

                SELECT COALESCE(NULLIF(TRIM(m.codigo), ''), NULLIF(TRIM(m.nota), '')) AS concepto, m.id_beneficiario
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s
            ) d
            WHERE d.concepto IS NOT NULL AND d.concepto <> ''
            GROUP BY d.concepto
            HAVING COUNT(DISTINCT CASE WHEN d.id_beneficiario IS NOT NULL THEN d.id_beneficiario END) = 1
               AND pendientes > 0
            ORDER BY d.concepto
            """,
            (id_persona, id_persona),
        ) or []

        confirmadas = [r for r in confirmadas if int(r.get("pendientes") or 0) > 0]

        automaticas: List[Dict] = []
        for row in automaticas_raw:
            if row["concepto"] in conceptos_reglados:
                continue
            ben = self.db.execute_query(
                "SELECT nombre FROM beneficiario WHERE id_beneficiario = %s",
                (row["id_beneficiario"],),
            )
            nombre = ben[0]["nombre"] if ben else "—"
            automaticas.append({
                "concepto": row["concepto"],
                "id_beneficiario": row["id_beneficiario"],
                "nombre_beneficiario": nombre,
                "total_movimientos": row["total_movimientos"],
                "fuente": "automatica",
            })

        return confirmadas + automaticas

    def get_conflictos_beneficiario(self, id_persona: int) -> List[Dict]:
        """Retorna descripciones con más de un beneficiario histórico."""
        raw = self.db.execute_query(
            """
            SELECT x.concepto, COUNT(DISTINCT x.id_beneficiario) AS num_beneficiarios
            FROM (
                SELECT NULLIF(TRIM(mt.nota), '') AS concepto, mt.id_beneficiario
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s

                UNION ALL

                SELECT COALESCE(NULLIF(TRIM(m.codigo), ''), NULLIF(TRIM(m.nota), '')) AS concepto, m.id_beneficiario
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s
            ) x
            WHERE x.id_beneficiario IS NOT NULL
              AND x.concepto IS NOT NULL
              AND x.concepto <> ''
              AND x.concepto NOT IN (
                  SELECT br.concepto FROM beneficiario_regla br WHERE br.id_persona = %s
              )
            GROUP BY x.concepto
            HAVING COUNT(DISTINCT x.id_beneficiario) > 1
            ORDER BY num_beneficiarios DESC, x.concepto
            """,
            (id_persona, id_persona, id_persona),
        ) or []

        salida: List[Dict] = []
        for row in raw:
            detalle = self.db.execute_query(
                """
                SELECT y.id_beneficiario, b.nombre, COUNT(*) AS total
                FROM (
                    SELECT NULLIF(TRIM(mt.nota), '') AS concepto, mt.id_beneficiario
                    FROM movimiento_tarjeta mt
                    WHERE mt.id_persona = %s

                    UNION ALL

                    SELECT COALESCE(NULLIF(TRIM(m.codigo), ''), NULLIF(TRIM(m.nota), '')) AS concepto, m.id_beneficiario
                    FROM movimiento m
                    INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                    WHERE c.id_persona = %s
                ) y
                JOIN beneficiario b ON b.id_beneficiario = y.id_beneficiario
                WHERE y.concepto = %s
                  AND y.id_beneficiario IS NOT NULL
                GROUP BY y.id_beneficiario, b.nombre
                ORDER BY total DESC
                """,
                (id_persona, id_persona, row["concepto"]),
            ) or []
            salida.append({
                "concepto": row["concepto"],
                "num_beneficiarios": row["num_beneficiarios"],
                "beneficiarios": detalle,
            })

        return salida

    def get_sin_beneficiario(self, id_persona: int, limit: int = 200) -> List[Dict]:
        """Retorna movimientos sin beneficiario asignado."""
        rows = self.db.execute_query(
            """
            SELECT * FROM (
                SELECT
                    'tarjeta' AS origen,
                    mt.id_movimiento_tarjeta AS id_movimiento,
                    mt.nota AS concepto,
                    mt.fecha,
                    mt.valor
                FROM movimiento_tarjeta mt
                WHERE mt.id_persona = %s
                  AND mt.id_beneficiario IS NULL

                UNION ALL

                SELECT
                    'cuenta' AS origen,
                    m.id_movimiento AS id_movimiento,
                    COALESCE(NULLIF(m.codigo, ''), m.nota, 'Sin descripción') AS concepto,
                    DATE(m.fecha_creacion) AS fecha,
                    m.monto AS valor
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE c.id_persona = %s
                  AND m.id_beneficiario IS NULL
            ) t
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (id_persona, id_persona, limit),
        )
        return rows or []

    def aplicar_reglas_beneficiario(self, id_persona: int) -> int:
        """Aplica reglas de beneficiario a movimientos pendientes."""
        total = 0
        for regla in self.get_reglas_beneficiario(id_persona):
            total += self._aplicar_una_regla_beneficiario(
                id_persona,
                regla["concepto"],
                int(regla["id_beneficiario"]),
            )
        logger.info("[OptimizacionBeneficiarios] Actualizados %d movimientos", total)
        return total

    def confirmar_regla_beneficiario(self, concepto: str, id_beneficiario: int, id_persona: int) -> bool:
        """Guarda una regla confirmada de beneficiario y la aplica."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO beneficiario_regla (id_persona, concepto, id_beneficiario)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id_beneficiario = VALUES(id_beneficiario),
                    fecha_actualizacion = NOW()
                """,
                (id_persona, concepto, id_beneficiario),
            )
            self.db.conn.commit()
            cursor.close()
            self._aplicar_una_regla_beneficiario(id_persona, concepto, id_beneficiario)
            return True
        except Exception as exc:
            logger.error("confirmar_regla_beneficiario error: %s", exc)
            return False

    def limpiar_regla_beneficiario(self, concepto: str, id_persona: int) -> bool:
        """Elimina regla de beneficiario para un concepto."""
        result = self.db.execute_non_query(
            "DELETE FROM beneficiario_regla WHERE id_persona = %s AND concepto = %s",
            (id_persona, concepto),
        )
        return result is not None

    def ignorar_concepto_beneficiario(self, concepto: str, id_persona: int) -> bool:
        """Marca concepto para no autoasignar beneficiario."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO beneficiario_regla (id_persona, concepto, id_beneficiario)
                VALUES (%s, %s, NULL)
                ON DUPLICATE KEY UPDATE id_beneficiario = NULL, fecha_actualizacion = NOW()
                """,
                (id_persona, concepto),
            )
            self.db.conn.commit()
            cursor.close()
            return True
        except Exception as exc:
            logger.error("ignorar_concepto_beneficiario error: %s", exc)
            return False

    def asignar_beneficiario_movimiento(self, origen: str, id_movimiento: int, id_beneficiario: int, id_persona: int) -> bool:
        """Asigna beneficiario a un movimiento específico."""
        if origen == 'cuenta':
            owner = self.db.execute_query(
                """
                SELECT 1
                FROM movimiento m
                INNER JOIN cuenta c ON c.id_cuenta = m.id_cuenta
                WHERE m.id_movimiento = %s AND c.id_persona = %s
                LIMIT 1
                """,
                (id_movimiento, id_persona),
            )
            if not owner:
                return False
            result = self.db.execute_non_query(
                "UPDATE movimiento SET id_beneficiario = %s WHERE id_movimiento = %s",
                (id_beneficiario, id_movimiento),
            )
            return result is not None

        result = self.db.execute_non_query(
            """
            UPDATE movimiento_tarjeta
            SET id_beneficiario = %s
            WHERE id_movimiento_tarjeta = %s AND id_persona = %s
            """,
            (id_beneficiario, id_movimiento, id_persona),
        )
        return result is not None

    # ------------------------------------------------------------------
    # Auxiliar privado
    # ------------------------------------------------------------------

    def _aplicar_una_regla(
        self, id_persona: int, concepto: str, id_categoria: int
    ) -> int:
        """UPDATE en tarjeta y cuenta para concepto dado donde categoría es NULL."""
        try:
            cursor = self.db.conn.cursor()
            concepto = (concepto or '').strip()
            if not concepto:
                cursor.close()
                return 0

            total = 0

            cursor.execute(
                """
                UPDATE movimiento_tarjeta
                SET id_categoria = %s
                WHERE id_persona = %s
                  AND NULLIF(TRIM(nota), '') = %s
                  AND id_categoria IS NULL
                """,
                (id_categoria, id_persona, concepto),
            )
            total += cursor.rowcount

            cuentas = self.db.execute_query(
                "SELECT id_cuenta FROM cuenta WHERE id_persona = %s",
                (id_persona,),
            ) or []
            ids_cuenta = [int(r['id_cuenta']) for r in cuentas]

            if ids_cuenta:
                placeholders = ','.join(['%s'] * len(ids_cuenta))
                sql = (
                    "UPDATE movimiento "
                    "SET id_categoria = %s "
                    "WHERE id_categoria IS NULL "
                    f"AND id_cuenta IN ({placeholders}) "  # nosec B608 - sólo marcadores %s generados por longitud de lista
                    "AND COALESCE(NULLIF(TRIM(codigo), ''), NULLIF(TRIM(nota), '')) = %s"
                )
                params = [id_categoria] + ids_cuenta + [concepto]
                cursor.execute(sql, tuple(params))
                total += cursor.rowcount

            self.db.conn.commit()
            cursor.close()
            return total
        except Exception as exc:
            try:
                self.db.conn.rollback()
            except Exception as rollback_exc:
                logger.debug("Rollback falló en _aplicar_una_regla: %s", rollback_exc)
            logger.error("_aplicar_una_regla error: %s", exc)
            return 0

    def _aplicar_una_regla_beneficiario(self, id_persona: int, concepto: str, id_beneficiario: int) -> int:
        """Aplica una regla de beneficiario por concepto en tarjeta y cuenta."""
        try:
            cursor = self.db.conn.cursor()
            concepto = (concepto or '').strip()
            if not concepto:
                cursor.close()
                return 0

            total = 0

            cursor.execute(
                """
                UPDATE movimiento_tarjeta
                SET id_beneficiario = %s
                WHERE id_persona = %s
                  AND NULLIF(TRIM(nota), '') = %s
                  AND id_beneficiario IS NULL
                """,
                (id_beneficiario, id_persona, concepto),
            )
            total += cursor.rowcount

            cuentas = self.db.execute_query(
                "SELECT id_cuenta FROM cuenta WHERE id_persona = %s",
                (id_persona,),
            ) or []
            ids_cuenta = [int(r['id_cuenta']) for r in cuentas]

            if ids_cuenta:
                placeholders = ','.join(['%s'] * len(ids_cuenta))
                sql = (
                    "UPDATE movimiento "
                    "SET id_beneficiario = %s "
                    "WHERE id_beneficiario IS NULL "
                    f"AND id_cuenta IN ({placeholders}) "  # nosec B608 - sólo marcadores %s generados por longitud de lista
                    "AND COALESCE(NULLIF(TRIM(codigo), ''), NULLIF(TRIM(nota), '')) = %s"
                )
                params = [id_beneficiario] + ids_cuenta + [concepto]
                cursor.execute(sql, tuple(params))
                total += cursor.rowcount

            self.db.conn.commit()
            cursor.close()
            return total
        except Exception as exc:
            try:
                self.db.conn.rollback()
            except Exception as rollback_exc:
                logger.debug("Rollback falló en _aplicar_una_regla_beneficiario: %s", rollback_exc)
            logger.error("_aplicar_una_regla_beneficiario error: %s", exc)
            return 0
