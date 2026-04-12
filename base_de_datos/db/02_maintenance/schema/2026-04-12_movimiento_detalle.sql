-- =================================================================
-- Migración: tabla movimiento_detalle
-- Fecha: 2026-04-12
-- Propósito: Permite descomponer un movimiento en múltiples
--            categorías con montos parciales (ej: Baile $20 + Comida $40 = $60).
-- =================================================================

CREATE TABLE IF NOT EXISTS `movimiento_detalle` (
  `id_detalle`      INT AUTO_INCREMENT PRIMARY KEY,
  `id_movimiento`   INT NOT NULL,
  `id_categoria`    INT DEFAULT NULL,
  `monto`           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `descripcion`     VARCHAR(200) DEFAULT NULL,
  CONSTRAINT fk_detalle_movimiento
    FOREIGN KEY (`id_movimiento`) REFERENCES `movimiento` (`id_movimiento`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
