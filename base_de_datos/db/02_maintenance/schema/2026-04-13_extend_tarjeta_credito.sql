-- =================================================================
-- Migración: Extender esquema de tarjeta_credito (2026-04-13)
-- Objetivo:
-- 1) Agregar campos faltantes a tarjeta_credito para productos módulo
-- 2) Agregar FK a persona para relacionar tarjetas con propietario
-- 3) Agregar tipo_tarjeta (credito/debito/prepago)
-- 4) Agregar fecha_vencimiento
-- 5) Agregar columna estado (VARCHAR) para complementar id_estado
-- =================================================================

USE app_presupuesto;

-- ─────────────────────────────────────────────────────────────────
-- 1) Verificar integridad referencial antes de cambios
-- ─────────────────────────────────────────────────────────────────
SELECT 'PRE-MIGRATION CHECK: tarjeta_credito' AS check_name;

-- ─────────────────────────────────────────────────────────────────
-- 2) Agregar columnas faltantes a tarjeta_credito
-- ─────────────────────────────────────────────────────────────────

-- Agregar id_persona (FK a persona)
ALTER TABLE tarjeta_credito
  ADD COLUMN id_persona INT(11) DEFAULT NULL COMMENT 'Propietario de la tarjeta' AFTER id_tarjeta;

-- Agregar nombre_titular
ALTER TABLE tarjeta_credito
  ADD COLUMN nombre_titular VARCHAR(100) DEFAULT NULL COMMENT 'Nombre del titular de la tarjeta' AFTER numero_tarjeta;

-- Agregar banco (opcional)
ALTER TABLE tarjeta_credito
  ADD COLUMN banco VARCHAR(100) DEFAULT NULL COMMENT 'Banco emisor de la tarjeta' AFTER nombre_titular;

-- Agregar tipo_tarjeta (ENUM: credito, debito, prepago)
ALTER TABLE tarjeta_credito
  ADD COLUMN tipo_tarjeta ENUM('credito','debito','prepago') DEFAULT 'credito' COMMENT 'Tipo de tarjeta' AFTER banco;

-- Agregar fecha_vencimiento
ALTER TABLE tarjeta_credito
  ADD COLUMN fecha_vencimiento DATE DEFAULT NULL COMMENT 'Fecha de vencimiento de la tarjeta' AFTER fecha_pago;

-- Agregar estado VARCHAR (complemento a id_estado)
ALTER TABLE tarjeta_credito
  ADD COLUMN estado ENUM('activa','bloqueada','vencida','inactiva') DEFAULT 'activa' COMMENT 'Estado de la tarjeta' AFTER fecha_vencimiento;

-- ─────────────────────────────────────────────────────────────────
-- 3) Agregar FK a persona
-- ─────────────────────────────────────────────────────────────────
ALTER TABLE tarjeta_credito
  ADD CONSTRAINT fk_tarjeta_persona 
  FOREIGN KEY (id_persona) REFERENCES persona (id_persona)
  ON DELETE SET NULL ON UPDATE CASCADE;

-- ─────────────────────────────────────────────────────────────────
-- 4) Agregar índices para consultas frecuentes
-- ─────────────────────────────────────────────────────────────────
ALTER TABLE tarjeta_credito
  ADD INDEX idx_tarjeta_persona (id_persona),
  ADD INDEX idx_tarjeta_tipo (tipo_tarjeta),
  ADD INDEX idx_tarjeta_estado (estado);

-- ─────────────────────────────────────────────────────────────────
-- 5) POST-MIGRATION: Verificar integridad
-- ─────────────────────────────────────────────────────────────────
SELECT 'POST-MIGRATION CHECK: Estructura actualizada' AS check_name;

DESCRIBE tarjeta_credito;

-- Verificar que no hay huérfanos (id_persona que no existe en persona)
SELECT tc.id_tarjeta, tc.id_persona
FROM tarjeta_credito tc
LEFT JOIN persona p ON p.id_persona = tc.id_persona
WHERE tc.id_persona IS NOT NULL AND p.id_persona IS NULL;

-- ─────────────────────────────────────────────────────────────────
-- 6) Notas de reversión (si algo falla)
-- ─────────────────────────────────────────────────────────────────
-- Para deshacer esta migración:
-- ALTER TABLE tarjeta_credito
--   DROP FOREIGN KEY fk_tarjeta_personas,
--   DROP INDEX idx_tarjeta_persona,
--   DROP INDEX idx_tarjeta_tipo,
--   DROP INDEX idx_tarjeta_estado,
--   DROP COLUMN id_persona,
--   DROP COLUMN nombre_titular,
--   DROP COLUMN banco,
--   DROP COLUMN tipo_tarjeta,
--   DROP COLUMN fecha_vencimiento,
--   DROP COLUMN estado;
