-- ================================================================
-- MIGRACION: categoria, beneficiario y constantes por usuario
-- Fecha: 2026-04-13
-- Objetivo:
--   1) Agregar id_persona en tablas de catalogo
--   2) Backfill de datos existentes
--   3) Forzar NOT NULL + FK + indices de soporte
--   4) Ajustar unicidad de constantes por usuario
-- ================================================================

START TRANSACTION;

-- ------------------------------------------------
-- categoria
-- ------------------------------------------------
SET @cat_col_exists := (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'categoria'
      AND column_name = 'id_persona'
);

SET @sql_cat_add_col := IF(
    @cat_col_exists = 0,
    'ALTER TABLE categoria ADD COLUMN id_persona INT(11) NULL AFTER id_categoria',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cat_add_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE categoria c
LEFT JOIN (
    SELECT m.id_categoria, MIN(cu.id_persona) AS id_persona
    FROM movimiento m
    INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
    WHERE m.id_categoria IS NOT NULL
    GROUP BY m.id_categoria
) x ON x.id_categoria = c.id_categoria
SET c.id_persona = COALESCE(c.id_persona, x.id_persona, (SELECT MIN(id_persona) FROM persona))
WHERE c.id_persona IS NULL;

ALTER TABLE categoria
MODIFY COLUMN id_persona INT(11) NOT NULL;

SET @cat_idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'categoria'
      AND index_name = 'idx_categoria_persona'
);

SET @sql_cat_add_idx := IF(
    @cat_idx_exists = 0,
    'ALTER TABLE categoria ADD INDEX idx_categoria_persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cat_add_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @cat_fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'categoria'
      AND constraint_name = 'fk_categoria_persona'
);

SET @sql_cat_add_fk := IF(
    @cat_fk_exists = 0,
    'ALTER TABLE categoria ADD CONSTRAINT fk_categoria_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cat_add_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ------------------------------------------------
-- beneficiario
-- ------------------------------------------------
SET @ben_col_exists := (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'beneficiario'
      AND column_name = 'id_persona'
);

SET @sql_ben_add_col := IF(
    @ben_col_exists = 0,
    'ALTER TABLE beneficiario ADD COLUMN id_persona INT(11) NULL AFTER id_beneficiario',
    'SELECT 1'
);
PREPARE stmt FROM @sql_ben_add_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE beneficiario b
LEFT JOIN (
    SELECT m.id_beneficiario, MIN(cu.id_persona) AS id_persona
    FROM movimiento m
    INNER JOIN cuenta cu ON cu.id_cuenta = m.id_cuenta
    WHERE m.id_beneficiario IS NOT NULL
    GROUP BY m.id_beneficiario
) x ON x.id_beneficiario = b.id_beneficiario
SET b.id_persona = COALESCE(b.id_persona, x.id_persona, (SELECT MIN(id_persona) FROM persona))
WHERE b.id_persona IS NULL;

ALTER TABLE beneficiario
MODIFY COLUMN id_persona INT(11) NOT NULL;

SET @ben_idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'beneficiario'
      AND index_name = 'idx_beneficiario_persona'
);

SET @sql_ben_add_idx := IF(
    @ben_idx_exists = 0,
    'ALTER TABLE beneficiario ADD INDEX idx_beneficiario_persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_ben_add_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ben_fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'beneficiario'
      AND constraint_name = 'fk_beneficiario_persona'
);

SET @sql_ben_add_fk := IF(
    @ben_fk_exists = 0,
    'ALTER TABLE beneficiario ADD CONSTRAINT fk_beneficiario_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_ben_add_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ------------------------------------------------
-- constantes
-- ------------------------------------------------
SET @cons_col_exists := (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'constantes'
      AND column_name = 'id_persona'
);

SET @sql_cons_add_col := IF(
    @cons_col_exists = 0,
    'ALTER TABLE constantes ADD COLUMN id_persona INT(11) NULL AFTER id_constante',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cons_add_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE constantes
SET id_persona = COALESCE(id_persona, (SELECT MIN(id_persona) FROM persona))
WHERE id_persona IS NULL;

ALTER TABLE constantes
MODIFY COLUMN id_persona INT(11) NOT NULL;

SET @cons_idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'constantes'
      AND index_name = 'idx_constante_persona'
);

SET @sql_cons_add_idx := IF(
    @cons_idx_exists = 0,
    'ALTER TABLE constantes ADD INDEX idx_constante_persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cons_add_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @cons_fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'constantes'
      AND constraint_name = 'fk_constante_persona'
);

SET @sql_cons_add_fk := IF(
    @cons_fk_exists = 0,
    'ALTER TABLE constantes ADD CONSTRAINT fk_constante_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cons_add_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @cons_uk_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'constantes'
      AND index_name = 'uk_constante_persona_nombre'
);

SET @sql_cons_drop_uk := (
    SELECT IF(
        EXISTS (
            SELECT 1
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = 'constantes'
              AND index_name = 'uk_constante_nombre'
        ),
        'ALTER TABLE constantes DROP INDEX uk_constante_nombre',
        'SELECT 1'
    )
);
PREPARE stmt FROM @sql_cons_drop_uk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql_cons_add_uk := IF(
    @cons_uk_exists = 0,
    'ALTER TABLE constantes ADD UNIQUE KEY uk_constante_persona_nombre (id_persona, categoria, nombre)',
    'SELECT 1'
);
PREPARE stmt FROM @sql_cons_add_uk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
