-- ================================================================
-- MIGRACION: eliminación en cascada para persona
-- Fecha: 2026-04-13
-- Objetivo:
--   Asegurar ON DELETE CASCADE en todas las relaciones a persona
-- ================================================================

START TRANSACTION;

-- accion.id_persona
SET @fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'accion'
      AND constraint_name = 'fk_accion_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE accion DROP FOREIGN KEY fk_accion_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE accion
  ADD CONSTRAINT fk_accion_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- activo.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'activo' AND constraint_name = 'fk_activo_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE activo DROP FOREIGN KEY fk_activo_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE activo
  ADD CONSTRAINT fk_activo_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- cuenta.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'cuenta' AND constraint_name = 'fk_cuenta_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE cuenta DROP FOREIGN KEY fk_cuenta_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE cuenta
  ADD CONSTRAINT fk_cuenta_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- prestamo.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'prestamo' AND constraint_name = 'fk_prestamo_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE prestamo DROP FOREIGN KEY fk_prestamo_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE prestamo
  ADD CONSTRAINT fk_prestamo_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- movimiento_tarjeta.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'movimiento_tarjeta' AND constraint_name = 'fk_mt_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE movimiento_tarjeta DROP FOREIGN KEY fk_mt_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE movimiento_tarjeta
  ADD CONSTRAINT fk_mt_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- prestamo_movimiento.persona_id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'prestamo_movimiento' AND constraint_name = 'fk_persona_has_prestamo_persona1'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE prestamo_movimiento DROP FOREIGN KEY fk_persona_has_prestamo_persona1', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE prestamo_movimiento
  ADD CONSTRAINT fk_persona_has_prestamo_persona1
  FOREIGN KEY (persona_id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- transaccion_programada.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'transaccion_programada' AND constraint_name = 'fk_tp_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE transaccion_programada DROP FOREIGN KEY fk_tp_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE transaccion_programada
  ADD CONSTRAINT fk_tp_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- tarjeta_credito.id_persona (antes SET NULL)
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'tarjeta_credito' AND constraint_name = 'fk_tarjeta_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE tarjeta_credito DROP FOREIGN KEY fk_tarjeta_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE tarjeta_credito
  ADD CONSTRAINT fk_tarjeta_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- categoria.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'categoria' AND constraint_name = 'fk_categoria_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE categoria DROP FOREIGN KEY fk_categoria_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE categoria
  ADD CONSTRAINT fk_categoria_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- beneficiario.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'beneficiario' AND constraint_name = 'fk_beneficiario_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE beneficiario DROP FOREIGN KEY fk_beneficiario_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE beneficiario
  ADD CONSTRAINT fk_beneficiario_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- constantes.id_persona
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'constantes' AND constraint_name = 'fk_constante_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE constantes DROP FOREIGN KEY fk_constante_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE constantes
  ADD CONSTRAINT fk_constante_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- presupuesto.id_persona (si faltaba FK)
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'presupuesto' AND constraint_name = 'fk_presupuesto_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE presupuesto DROP FOREIGN KEY fk_presupuesto_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE presupuesto
  ADD CONSTRAINT fk_presupuesto_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- deuda_financiada.id_persona (agregar FK si faltaba)
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'deuda_financiada' AND constraint_name = 'fk_df_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE deuda_financiada DROP FOREIGN KEY fk_df_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE deuda_financiada
  ADD CONSTRAINT fk_df_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- tarjeta_diferido.id_persona (agregar FK si faltaba)
SET @fk_exists := (
    SELECT COUNT(*) FROM information_schema.referential_constraints
    WHERE constraint_schema = DATABASE() AND table_name = 'tarjeta_diferido' AND constraint_name = 'fk_td_persona'
);
SET @sql := IF(@fk_exists = 1, 'ALTER TABLE tarjeta_diferido DROP FOREIGN KEY fk_td_persona', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
ALTER TABLE tarjeta_diferido
  ADD CONSTRAINT fk_td_persona
  FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
  ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;
