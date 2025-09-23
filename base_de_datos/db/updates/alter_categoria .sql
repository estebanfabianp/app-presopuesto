-- 1. Agregar la columna parent_id a la tabla categoria
ALTER TABLE categoria
ADD COLUMN parent_id INT NULL;

-- 2. Crear la relación recursiva (una categoría puede tener otra categoría como padre)
ALTER TABLE categoria
ADD CONSTRAINT fk_categoria_parent
FOREIGN KEY (parent_id) REFERENCES categoria(id)
ON DELETE CASCADE
ON UPDATE CASCADE;
