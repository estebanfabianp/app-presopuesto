-- Migración: Cambiar columna 'activo' por 'estado' en tabla persona
-- Fecha: Diciembre 2024
-- Autor: Esteban Fabián Patiño Montealegre

-- Paso 1: Crear tabla de estados si no existe
CREATE TABLE IF NOT EXISTS estado_persona (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paso 2: Insertar estados básicos
INSERT IGNORE INTO estado_persona (id, nombre, descripcion) VALUES
(1, 'ACTIVO', 'Persona activa en el sistema'),
(2, 'INACTIVO', 'Persona inactiva temporalmente'),
(3, 'SUSPENDIDO', 'Persona suspendida por incumplimiento'),
(4, 'BLOQUEADO', 'Persona bloqueada por seguridad');

-- Paso 3: Agregar nueva columna estado a la tabla persona
ALTER TABLE persona 
ADD COLUMN id_estado INT DEFAULT 1,
ADD CONSTRAINT fk_persona_estado 
    FOREIGN KEY (id_estado) REFERENCES estado_persona(id);

-- Paso 4: Migrar datos existentes
-- Si activo = 1, entonces estado = 1 (ACTIVO)
-- Si activo = 0, entonces estado = 2 (INACTIVO)
UPDATE persona 
SET id_estado = CASE 
    WHEN activo = 1 THEN 1  -- ACTIVO
    WHEN activo = 0 THEN 2  -- INACTIVO
    ELSE 1                   -- Por defecto ACTIVO
END;

-- Paso 5: Hacer la columna estado obligatoria
ALTER TABLE persona 
MODIFY COLUMN id_estado INT NOT NULL;

-- Paso 6: Eliminar la columna activo antigua (comentado por seguridad)
-- Descomenta las siguientes líneas cuando estés seguro de la migración
-- ALTER TABLE persona DROP COLUMN activo;

-- Paso 7: Crear índice para optimizar consultas por estado
CREATE INDEX idx_persona_estado ON persona(id_estado);

-- Verificación de la migración
SELECT 
    p.id,
    p.nombre,
    p.id_estado,
    ep.nombre as estado_nombre,
    ep.descripcion as estado_descripcion
FROM persona p
LEFT JOIN estado_persona ep ON p.id_estado = ep.id
LIMIT 10;
