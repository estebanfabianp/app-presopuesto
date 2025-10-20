-- 1. Agregar la columna parent_id a la tabla categoria
ALTER TABLE categoria
ADD COLUMN parent_id INT NULL;

-- 2. Crear la relación recursiva (una categoría puede tener otra categoría como padre)
ALTER TABLE `persona` CHANGE `hash_contrasena` `clave` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL;