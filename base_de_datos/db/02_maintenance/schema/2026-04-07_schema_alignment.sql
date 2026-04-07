-- =================================================================
-- Migracion de alineacion de esquema (2026-04-07)
-- Objetivo:
-- 1) Aplicar FKs faltantes del DDL
-- 2) Redisenar prestamo_movimiento con PK autoincremental
-- 3) Renombrar prestamo.limite_credito -> saldo_pendiente
-- =================================================================

USE app_presupuesto;

-- PRECHECKS (deben retornar 0 para evitar fallos en FKs)
SELECT 'cuenta.id_persona->persona' AS rel, COUNT(*) AS huerfanos
FROM cuenta c LEFT JOIN persona p ON p.id_persona=c.id_persona
WHERE c.id_persona IS NOT NULL AND p.id_persona IS NULL;

SELECT 'movimiento.id_cuenta->cuenta' AS rel, COUNT(*) AS huerfanos
FROM movimiento m LEFT JOIN cuenta c ON c.id_cuenta=m.id_cuenta
WHERE m.id_cuenta IS NOT NULL AND c.id_cuenta IS NULL;

SELECT 'movimiento.id_tipo->tipo_movimiento' AS rel, COUNT(*) AS huerfanos
FROM movimiento m LEFT JOIN tipo_movimiento t ON t.id_tipo=m.id_tipo
WHERE m.id_tipo IS NOT NULL AND t.id_tipo IS NULL;

SELECT 'movimiento.id_estado->estado_movimiento' AS rel, COUNT(*) AS huerfanos
FROM movimiento m LEFT JOIN estado_movimiento e ON e.id_estado=m.id_estado
WHERE m.id_estado IS NOT NULL AND e.id_estado IS NULL;

SELECT 'movimiento.id_categoria->categoria' AS rel, COUNT(*) AS huerfanos
FROM movimiento m LEFT JOIN categoria c ON c.id_categoria=m.id_categoria
WHERE m.id_categoria IS NOT NULL AND c.id_categoria IS NULL;

SELECT 'movimiento.id_beneficiario->beneficiario' AS rel, COUNT(*) AS huerfanos
FROM movimiento m LEFT JOIN beneficiario b ON b.id_beneficiario=m.id_beneficiario
WHERE m.id_beneficiario IS NOT NULL AND b.id_beneficiario IS NULL;

SELECT 'prestamo.id_persona->persona' AS rel, COUNT(*) AS huerfanos
FROM prestamo p LEFT JOIN persona pe ON pe.id_persona=p.id_persona
WHERE p.id_persona IS NOT NULL AND pe.id_persona IS NULL;

SELECT 'prestamo.id_estado->estado_prestamo' AS rel, COUNT(*) AS huerfanos
FROM prestamo p LEFT JOIN estado_prestamo ep ON ep.id_estado=p.id_estado
WHERE p.id_estado IS NOT NULL AND ep.id_estado IS NULL;

SELECT 'tarjeta_credito.id_estado->estado_tarjeta' AS rel, COUNT(*) AS huerfanos
FROM tarjeta_credito tc LEFT JOIN estado_tarjeta et ON et.id_estado=tc.id_estado
WHERE tc.id_estado IS NOT NULL AND et.id_estado IS NULL;

SELECT 'prestamo_movimiento.persona_id_persona->persona' AS rel, COUNT(*) AS huerfanos
FROM prestamo_movimiento pm LEFT JOIN persona p ON p.id_persona=pm.persona_id_persona
WHERE p.id_persona IS NULL;

SELECT 'prestamo_movimiento.prestamo_id_prestamo->prestamo' AS rel, COUNT(*) AS huerfanos
FROM prestamo_movimiento pm LEFT JOIN prestamo p ON p.id_prestamo=pm.prestamo_id_prestamo
WHERE p.id_prestamo IS NULL;

-- 1) Rediseno de prestamo_movimiento
ALTER TABLE prestamo_movimiento DROP PRIMARY KEY;

ALTER TABLE prestamo_movimiento
  ADD COLUMN id_prestamo_movimiento INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE prestamo_movimiento
  ADD KEY idx_pm_persona_prestamo (persona_id_persona, prestamo_id_prestamo),
  ADD UNIQUE KEY uk_pm_persona_prestamo_numtx (persona_id_persona, prestamo_id_prestamo, numero_transaccion);

-- 2) Renombrar columna en prestamo
ALTER TABLE prestamo
  CHANGE COLUMN limite_credito saldo_pendiente DECIMAL(15,2) DEFAULT NULL;

-- 3) Aplicar FKs faltantes
ALTER TABLE cuenta
  ADD CONSTRAINT fk_cuenta_persona
  FOREIGN KEY (id_persona) REFERENCES persona (id_persona);

ALTER TABLE movimiento
  ADD CONSTRAINT fk_movimiento_beneficiario FOREIGN KEY (id_beneficiario) REFERENCES beneficiario (id_beneficiario),
  ADD CONSTRAINT fk_movimiento_categoria FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria),
  ADD CONSTRAINT fk_movimiento_tipo FOREIGN KEY (id_tipo) REFERENCES tipo_movimiento (id_tipo),
  ADD CONSTRAINT fk_movimiento_estado FOREIGN KEY (id_estado) REFERENCES estado_movimiento (id_estado),
  ADD CONSTRAINT fk_movimiento_cuenta FOREIGN KEY (id_cuenta) REFERENCES cuenta (id_cuenta) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE prestamo
  ADD CONSTRAINT fk_prestamo_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona),
  ADD CONSTRAINT fk_prestamo_estado FOREIGN KEY (id_estado) REFERENCES estado_prestamo (id_estado);

ALTER TABLE tarjeta_credito
  ADD CONSTRAINT fk_tc_estado FOREIGN KEY (id_estado) REFERENCES estado_tarjeta (id_estado);

ALTER TABLE prestamo_movimiento
  ADD CONSTRAINT fk_persona_has_prestamo_persona1 FOREIGN KEY (persona_id_persona) REFERENCES persona (id_persona) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT fk_persona_has_prestamo_prestamo1 FOREIGN KEY (prestamo_id_prestamo) REFERENCES prestamo (id_prestamo) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- POSTCHECK DE FKs
SELECT table_name, constraint_name
FROM information_schema.table_constraints
WHERE table_schema = 'app_presupuesto'
  AND table_name IN ('cuenta','movimiento','prestamo','tarjeta_credito','prestamo_movimiento')
  AND constraint_type = 'FOREIGN KEY'
ORDER BY table_name, constraint_name;
