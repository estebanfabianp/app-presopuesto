-- ================================================================
-- MIGRACION: password por defecto en persona
-- Fecha: 2026-04-13
-- Objetivo:
--   1) Asignar clave por defecto (123456 en SHA-256) a inserts directos en BD
--   2) Corregir filas existentes con clave NULL o vacia
-- ================================================================

START TRANSACTION;

-- Hash SHA-256 de '123456'
SET @default_hash := '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92';

UPDATE persona
SET clave = @default_hash
WHERE clave IS NULL OR TRIM(clave) = '';

COMMIT;

DROP TRIGGER IF EXISTS trg_persona_default_password;
CREATE TRIGGER trg_persona_default_password
BEFORE INSERT ON persona
FOR EACH ROW
SET NEW.clave = IF(
    NEW.clave IS NULL OR TRIM(NEW.clave) = '',
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
    NEW.clave
);
