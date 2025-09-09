-- Habilitar el programador de eventos si es necesario
SET GLOBAL event_scheduler = ON;

-- Ejemplo: evento para limpiar movimientos antiguos
DELIMITER $$

CREATE EVENT IF NOT EXISTS limpiar_movimientos_antiguos
ON SCHEDULE EVERY 1 YEAR
DO
BEGIN
    DELETE FROM movimiento WHERE fecha_creacion < DATE_SUB(NOW(), INTERVAL 5 YEAR);
END $$

DELIMITER;

-- Agrega aquí otros eventos de mantenimiento según sea necesario.