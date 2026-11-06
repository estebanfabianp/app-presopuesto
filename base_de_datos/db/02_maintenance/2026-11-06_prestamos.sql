CREATE TABLE IF NOT EXISTS prestamo (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_persona INT NOT NULL,
  nombre VARCHAR(120) NOT NULL,
  acreedor VARCHAR(120) NOT NULL,
  capital DECIMAL(15,2) NOT NULL,
  tasa_ea DECIMAL(9,4) NOT NULL,
  numero_cuotas INT NOT NULL,
  frecuencia VARCHAR(20) NOT NULL,
  metodo VARCHAR(20) NOT NULL,
  primera_fecha DATE NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_prestamo_persona (id_persona),
  CONSTRAINT fk_prestamo_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prestamo_cuota (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_prestamo INT NOT NULL,
  numero INT NOT NULL,
  fecha DATE NOT NULL,
  capital DECIMAL(15,2) NOT NULL,
  interes DECIMAL(15,2) NOT NULL,
  capital_pagado DECIMAL(15,2) NOT NULL DEFAULT 0,
  interes_pagado DECIMAL(15,2) NOT NULL DEFAULT 0,
  cancelada BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE KEY uq_prestamo_cuota (id_prestamo, numero),
  CONSTRAINT fk_prestamo_cuota FOREIGN KEY (id_prestamo) REFERENCES prestamo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prestamo_cargo (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_cuota INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  monto DECIMAL(15,2) NOT NULL,
  pagado DECIMAL(15,2) NOT NULL DEFAULT 0,
  KEY idx_cargo_cuota (id_cuota),
  CONSTRAINT fk_prestamo_cargo FOREIGN KEY (id_cuota) REFERENCES prestamo_cuota(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prestamo_pago (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_prestamo INT NOT NULL,
  id_cuota INT NULL,
  fecha DATE NOT NULL,
  total DECIMAL(15,2) NOT NULL,
  capital DECIMAL(15,2) NOT NULL,
  interes DECIMAL(15,2) NOT NULL,
  cargos JSON NOT NULL,
  id_movimiento INT NULL,
  referencia CHAR(36) NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_prestamo_pago_referencia (referencia),
  KEY idx_pago_prestamo (id_prestamo),
  CONSTRAINT fk_pago_prestamo FOREIGN KEY (id_prestamo) REFERENCES prestamo(id) ON DELETE CASCADE,
  CONSTRAINT fk_pago_cuota FOREIGN KEY (id_cuota) REFERENCES prestamo_cuota(id),
  CONSTRAINT fk_pago_movimiento FOREIGN KEY (id_movimiento) REFERENCES movimiento(id_movimiento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
