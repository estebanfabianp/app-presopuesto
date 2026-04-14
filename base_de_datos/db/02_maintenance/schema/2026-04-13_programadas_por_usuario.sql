-- ================================================================
-- MIGRACION: transaccion_programada asociada al usuario
-- Fecha: 2026-04-13
-- Objetivo:
--   1) Agregar columna id_persona
--   2) Backfill para filas existentes
--   3) Crear indice y llave foranea a persona
-- ================================================================

START TRANSACTION;

-- 1) Agregar columna si no existe
SET @col_exists := (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'transaccion_programada'
      AND column_name = 'id_persona'
);

SET @sql_add_col := IF(
    @col_exists = 0,
    'ALTER TABLE transaccion_programada ADD COLUMN id_persona INT(11) NULL AFTER id_transaccion',
    'SELECT 1'
);
PREPARE stmt FROM @sql_add_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) Backfill: si existe id_persona nulo, usar un usuario existente
UPDATE transaccion_programada
SET id_persona = COALESCE(id_persona, (SELECT MIN(id_persona) FROM persona))
WHERE id_persona IS NULL;

-- 3) Asegurar columna NOT NULL
ALTER TABLE transaccion_programada
MODIFY COLUMN id_persona INT(11) NOT NULL;

-- 4) Crear indice si no existe
SET @idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'transaccion_programada'
      AND index_name = 'idx_tp_persona'
);

SET @sql_add_idx := IF(
    @idx_exists = 0,
    'ALTER TABLE transaccion_programada ADD INDEX idx_tp_persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_add_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5) Crear FK si no existe
SET @fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'transaccion_programada'
      AND constraint_name = 'fk_tp_persona'
);

SET @sql_add_fk := IF(
    @fk_exists = 0,
    'ALTER TABLE transaccion_programada ADD CONSTRAINT fk_tp_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_add_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
