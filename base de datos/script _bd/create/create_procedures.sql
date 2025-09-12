
-- Procedimiento para recalcular el saldo de una cuenta
DELIMITER $$

CREATE PROCEDURE sp_recalcular_saldo_cuenta(IN p_id_cuenta INT)
BEGIN
  UPDATE cuenta
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN id_tipo = 1 THEN monto   -- id_tipo=1: ingreso
        WHEN id_tipo = 2 THEN -monto  -- id_tipo=2: gasto
        ELSE 0
      END
    ), 0)
    FROM movimiento
    WHERE id_cuenta = p_id_cuenta
  )
  WHERE id_cuenta = p_id_cuenta;
END$$

-- Procedimiento para recalcular el saldo de una tarjeta de crédito
CREATE PROCEDURE sp_recalcular_saldo_tarjeta(IN p_id_tarjeta INT)
BEGIN
  UPDATE tarjeta_credito
  SET saldo_actual = (
    SELECT IFNULL(SUM(
      CASE
        WHEN estado = 'abono' THEN -valor
        WHEN estado = 'compra' THEN valor
        ELSE 0
      END
    ), 0)
    FROM movimiento_tarjeta
    WHERE id_tarjeta = p_id_tarjeta
  )
  WHERE id_tarjeta = p_id_tarjeta;
END$$

-- Procedimiento para recalcular el saldo de un préstamo
CREATE PROCEDURE sp_recalcular_saldo_prestamo(IN p_id_prestamo INT)
BEGIN
  UPDATE prestamo
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN valor IS NOT NULL THEN valor
        ELSE 0
      END
    ), 0)
    FROM prestamo_movimiento
    WHERE prestamo_id_prestamo = p_id_prestamo
  )
  WHERE id_prestamo = p_id_prestamo;
END$$

DELIMITER ;
