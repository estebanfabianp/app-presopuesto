DELIMITER $$

CREATE FUNCTION obtener_total_movimientos(p_id_persona INT) RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(15,2);
    SELECT SUM(monto) INTO total FROM movimiento WHERE id_persona = p_id_persona;
    RETURN IFNULL(total, 0);
END $$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION reclasificar_categoria_movimientos(
    p_id_categoria_nueva INT,
    p_fecha_inicio DATE,
    p_fecha_fin DATE
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE movimientos_afectados INT DEFAULT 0;
    UPDATE movimiento
    SET id_categoria = p_id_categoria_nueva
    WHERE fecha_creacion BETWEEN p_fecha_inicio AND p_fecha_fin;
    SELECT ROW_COUNT() INTO movimientos_afectados;
    RETURN movimientos_afectados;
END $$

DELIMITER ;