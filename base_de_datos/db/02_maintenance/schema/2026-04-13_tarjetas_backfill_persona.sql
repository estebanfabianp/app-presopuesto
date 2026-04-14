-- ================================================================
-- MIGRACION: backfill de propietario en tarjeta_credito
-- Fecha: 2026-04-13
-- Objetivo:
--   Completar id_persona en tarjetas legacy que quedaron en NULL
--   usando la relacion existente en movimiento_tarjeta.
-- ================================================================

START TRANSACTION;

UPDATE tarjeta_credito tc
JOIN (
    SELECT id_tarjeta, MIN(id_persona) AS id_persona
    FROM movimiento_tarjeta
    GROUP BY id_tarjeta
) mt ON mt.id_tarjeta = tc.id_tarjeta
SET tc.id_persona = mt.id_persona
WHERE tc.id_persona IS NULL;

COMMIT;
