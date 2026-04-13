USE `app_presupuesto`;

CREATE TABLE IF NOT EXISTS `presupuesto_detalle` (
  `id_detalle` INT NOT NULL AUTO_INCREMENT,
  `id_presupuesto` INT NOT NULL,
  `id_categoria` INT NULL,
  `categoria_nombre` VARCHAR(150) NULL,
  `frecuencia` VARCHAR(30) NOT NULL DEFAULT 'Ninguno',
  `tolerancia_pct` DECIMAL(6,2) NOT NULL DEFAULT 10.00,
  `monto_importe` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `monto_estimado` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `notas` TEXT NULL,
  `orden` INT NOT NULL DEFAULT 0,
  `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_detalle`),
  KEY `idx_presupuesto_detalle_presupuesto` (`id_presupuesto`),
  KEY `idx_presupuesto_detalle_categoria` (`id_categoria`),
  CONSTRAINT `fk_presupuesto_detalle_presupuesto`
    FOREIGN KEY (`id_presupuesto`) REFERENCES `presupuesto` (`id_presupuesto`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_presupuesto_detalle_categoria`
    FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET @exists_tol := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'presupuesto_detalle'
    AND COLUMN_NAME = 'tolerancia_pct'
);

SET @sql_tol := IF(
  @exists_tol = 0,
  'ALTER TABLE presupuesto_detalle ADD COLUMN tolerancia_pct DECIMAL(6,2) NOT NULL DEFAULT 10.00 AFTER frecuencia',
  'SELECT 1'
);

PREPARE stmt_tol FROM @sql_tol;
EXECUTE stmt_tol;
DEALLOCATE PREPARE stmt_tol;
