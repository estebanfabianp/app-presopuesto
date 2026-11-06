CREATE TABLE IF NOT EXISTS meta_ahorro (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_persona INT NOT NULL,
  nombre VARCHAR(120) NOT NULL,
  objetivo DECIMAL(15,2) NOT NULL,
  fecha_objetivo DATE NULL,
  referencia CHAR(36) NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_meta_referencia (referencia),
  KEY idx_meta_persona (id_persona),
  CONSTRAINT fk_meta_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS meta_ahorro_movimiento (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_meta INT NOT NULL,
  tipo VARCHAR(10) NOT NULL,
  monto DECIMAL(15,2) NOT NULL,
  nota VARCHAR(255) NOT NULL DEFAULT '',
  referencia CHAR(36) NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_meta_movimiento_referencia (referencia),
  KEY idx_meta_movimiento (id_meta),
  CONSTRAINT fk_meta_movimiento FOREIGN KEY (id_meta) REFERENCES meta_ahorro(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
