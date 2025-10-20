-- =================================================================
-- PROCEDIMIENTOS ALMACENADOS
-- Proyecto: app-presupuesto
-- Descripción: Procedimientos para operaciones complejas y mantenimiento
-- =================================================================

DELIMITER $$

-- =================================================================
-- Procedimiento: sp_recalcular_saldo_cuenta
-- Descripción: Recalcula el saldo de una cuenta específica basado en todos sus movimientos
-- Parámetros: 
--   * p_id_cuenta (INT): ID de la cuenta a recalcular
-- Lógica:
--   * id_tipo=1: Ingresos (suman al saldo)
--   * id_tipo=2: Gastos (restan del saldo)
-- Uso: CALL sp_recalcular_saldo_cuenta(1);
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_cuenta`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_recalcular_saldo_cuenta` (IN `p_id_cuenta` INT)   
BEGIN
  -- Recalcula el saldo basado en la suma de todos los movimientos
  UPDATE cuenta
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN id_tipo = 1 THEN monto   -- id_tipo=1: ingreso (suma)
        WHEN id_tipo = 2 THEN -monto  -- id_tipo=2: gasto (resta)
        ELSE 0                        -- Otros tipos no afectan el saldo
      END
    ), 0)
    FROM movimiento
    WHERE id_cuenta = p_id_cuenta
  )
  WHERE id_cuenta = p_id_cuenta;
END$$

-- =================================================================
-- Procedimiento: sp_recalcular_saldo_prestamo
-- Descripción: Recalcula el saldo de un préstamo basado en sus movimientos
-- Parámetros:
--   * p_id_prestamo (INT): ID del préstamo a recalcular
-- Lógica: Suma todos los valores de movimientos del préstamo
-- Uso: CALL sp_recalcular_saldo_prestamo(1);
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_prestamo`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_recalcular_saldo_prestamo` (IN `p_id_prestamo` INT)   
BEGIN
  -- Actualiza el saldo del préstamo sumando todos los movimientos
  UPDATE prestamo
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN valor IS NOT NULL THEN valor  -- Solo suma valores no nulos
        ELSE 0
      END
    ), 0)
    FROM prestamo_movimiento
    WHERE prestamo_id_prestamo = p_id_prestamo
  )
  WHERE id_prestamo = p_id_prestamo;
END$$

-- =================================================================
-- Procedimiento: sp_recalcular_saldo_tarjeta
-- Descripción: Recalcula el saldo de una tarjeta de crédito basado en sus movimientos
-- Parámetros:
--   * p_id_tarjeta (INT): ID de la tarjeta a recalcular
-- Lógica:
--   * estado='abono': Reduce la deuda (valor negativo)
--   * estado='compra': Aumenta la deuda (valor positivo)
-- Uso: CALL sp_recalcular_saldo_tarjeta(1);
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_tarjeta`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_recalcular_saldo_tarjeta` (IN `p_id_tarjeta` INT)   
BEGIN
  -- Recalcula saldo considerando abonos y compras
  UPDATE tarjeta_credito
  SET saldo_actual = (
    SELECT IFNULL(SUM(
      CASE
        WHEN estado = 'abono' THEN -valor    -- Abonos reducen la deuda
        WHEN estado = 'compra' THEN valor    -- Compras aumentan la deuda
        ELSE 0                               -- Otros estados no afectan
      END
    ), 0)
    FROM movimiento_tarjeta
    WHERE id_tarjeta = p_id_tarjeta
  )
  WHERE id_tarjeta = p_id_tarjeta;
END$$

DELIMITER ;
