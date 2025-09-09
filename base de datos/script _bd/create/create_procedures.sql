DELIMITER $$

CREATE PROCEDURE sp_listar_movimientos_por_persona(IN p_id_persona INT)
BEGIN
    SELECT * FROM movimiento WHERE id_persona = p_id_persona;
END $$

DELIMITER ;
