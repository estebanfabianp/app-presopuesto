-- Habilitar eventos si es necesario
SET GLOBAL event_scheduler = ON;

DELIMITER $$

CREATE EVENT IF NOT EXISTS limpiar_movimientos_antiguos
ON SCHEDULE EVERY 1 YEAR
DO
BEGIN
    DELETE FROM movimiento WHERE fecha_creacion < DATE_SUB(NOW(), INTERVAL 5 YEAR);
END $$

DELIMITER ;
