-- =================================================================
-- MIGRACION DE CONTRASENAS LEGACY A SHA-256
-- Fecha: 2026-04-12
-- Objetivo: convertir claves en texto plano de la tabla persona a SHA-256
-- Seguridad: script idempotente; no rehasea claves que ya tienen formato SHA-256
-- =================================================================

USE app_presupuesto;

SELECT
    COUNT(*) AS total_personas,
    SUM(
        CASE
            WHEN clave IS NULL OR clave = '' THEN 0
            WHEN CHAR_LENGTH(clave) = 64 AND clave REGEXP '^[0-9a-fA-F]{64}$' THEN 0
            ELSE 1
        END
    ) AS legacy_plain_before
FROM persona;

UPDATE persona
SET clave = SHA2(clave, 256)
WHERE clave IS NOT NULL
  AND clave <> ''
  AND NOT (
      CHAR_LENGTH(clave) = 64
      AND clave REGEXP '^[0-9a-fA-F]{64}$'
  );

SELECT ROW_COUNT() AS updated_rows;

SELECT
    COUNT(*) AS total_personas,
    SUM(
        CASE
            WHEN clave IS NULL OR clave = '' THEN 0
            WHEN CHAR_LENGTH(clave) = 64 AND clave REGEXP '^[0-9a-fA-F]{64}$' THEN 0
            ELSE 1
        END
    ) AS legacy_plain_after
FROM persona;