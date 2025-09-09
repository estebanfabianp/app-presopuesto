DELIMITER $$

CREATE FUNCTION obtener_total_movimientos(p_id_persona INT) RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(15,2);
    SELECT SUM(monto) INTO total FROM movimiento WHERE id_persona = p_id_persona;
    RETURN IFNULL(total, 0);
END $$

DELIMITER;