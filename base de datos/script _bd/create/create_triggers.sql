DELIMITER $$

CREATE TRIGGER tr_actualizar_fecha_actualizacion_persona
BEFORE UPDATE ON persona
FOR EACH ROW
BEGIN
    SET NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
END $$

DELIMITER;