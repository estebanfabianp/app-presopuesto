-- =================================================================
-- TRIGGERS
-- Proyecto: app-presupuesto
-- Descripción: Triggers para automatización de cálculos de saldos
-- =================================================================

DELIMITER $$

-- =================================================================
-- TRIGGERS PARA TABLA MOVIMIENTO
-- Descripción: Actualización automática de saldos de cuenta
-- Funcionamiento: Se ejecutan en INSERT, UPDATE y DELETE
-- =================================================================

-- Trigger: Eliminar movimiento - Recalcula saldo de cuenta
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_delete`$$
CREATE TRIGGER `tr_update_saldo_cuenta_after_delete` 
AFTER DELETE ON `movimiento` 
FOR EACH ROW 
BEGIN
  -- Recalcula el saldo de la cuenta después de eliminar un movimiento
  UPDATE cuenta
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN id_tipo = 1 THEN monto   -- Ingresos suman
        WHEN id_tipo = 2 THEN -monto  -- Gastos restan
        ELSE 0
      END
    ), 0)
    FROM movimiento
    WHERE id_cuenta = OLD.id_cuenta
  )
  WHERE id_cuenta = OLD.id_cuenta;
END$$

-- Trigger: Insertar movimiento - Actualiza saldo de cuenta
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_insert`$$
CREATE TRIGGER `tr_update_saldo_cuenta_after_insert` 
AFTER INSERT ON `movimiento` 
FOR EACH ROW 
BEGIN
  -- Actualiza el saldo de la cuenta después de insertar un movimiento
  UPDATE cuenta
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN id_tipo = 1 THEN monto   -- id_tipo=1: ingreso (suma)
        WHEN id_tipo = 2 THEN -monto  -- id_tipo=2: gasto (resta)
        ELSE 0
      END
    ), 0)
    FROM movimiento
    WHERE id_cuenta = NEW.id_cuenta
  )
  WHERE id_cuenta = NEW.id_cuenta;
END$$

-- Trigger: Actualizar movimiento - Recalcula saldos afectados
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_update`$$
CREATE TRIGGER `tr_update_saldo_cuenta_after_update` 
AFTER UPDATE ON `movimiento` 
FOR EACH ROW 
BEGIN
  -- Si el movimiento cambió de cuenta, actualizar la cuenta anterior
  IF OLD.id_cuenta <> NEW.id_cuenta THEN
    UPDATE cuenta
    SET saldo_inicial = (
      SELECT IFNULL(SUM(
        CASE
          WHEN id_tipo = 1 THEN monto
          WHEN id_tipo = 2 THEN -monto
          ELSE 0
        END
      ), 0)
      FROM movimiento
      WHERE id_cuenta = OLD.id_cuenta
    )
    WHERE id_cuenta = OLD.id_cuenta;
  END IF;

  -- Actualizar el saldo de la cuenta nueva/actual
  UPDATE cuenta
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN id_tipo = 1 THEN monto
        WHEN id_tipo = 2 THEN -monto
        ELSE 0
      END
    ), 0)
    FROM movimiento
    WHERE id_cuenta = NEW.id_cuenta
  )
  WHERE id_cuenta = NEW.id_cuenta;
END$$

-- =================================================================
-- TRIGGERS PARA TABLA MOVIMIENTO_TARJETA
-- Descripción: Actualización automática de saldos de tarjeta
-- =================================================================

-- Trigger: Eliminar movimiento de tarjeta
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_delete`$$
CREATE TRIGGER `tr_update_saldo_tarjeta_after_delete` 
AFTER DELETE ON `movimiento_tarjeta` 
FOR EACH ROW 
BEGIN
  -- Recalcula el saldo de la tarjeta después de eliminar un movimiento
  UPDATE tarjeta_credito
  SET saldo_actual = (
    SELECT IFNULL(SUM(
      CASE
        WHEN estado = 'abono' THEN -valor    -- Abonos reducen la deuda
        WHEN estado = 'compra' THEN valor    -- Compras aumentan la deuda
        ELSE 0
      END
    ), 0)
    FROM movimiento_tarjeta
    WHERE id_tarjeta = OLD.id_tarjeta
  )
  WHERE id_tarjeta = OLD.id_tarjeta;
END$$

-- Trigger: Insertar movimiento de tarjeta - Actualiza saldo de tarjeta
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_insert`$$
CREATE TRIGGER `tr_update_saldo_tarjeta_after_insert` 
AFTER INSERT ON `movimiento_tarjeta` 
FOR EACH ROW 
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
    WHERE id_tarjeta = NEW.id_tarjeta
  )
  WHERE id_tarjeta = NEW.id_tarjeta;
END$$

-- Trigger: Actualizar movimiento de tarjeta - Recalcula saldos afectados
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_update`$$
CREATE TRIGGER `tr_update_saldo_tarjeta_after_update` 
AFTER UPDATE ON `movimiento_tarjeta` 
FOR EACH ROW 
BEGIN
  -- Si cambió la tarjeta, actualizar la tarjeta anterior
  IF OLD.id_tarjeta <> NEW.id_tarjeta THEN
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
      WHERE id_tarjeta = OLD.id_tarjeta
    )
    WHERE id_tarjeta = OLD.id_tarjeta;
  END IF;

  -- Actualizar la tarjeta nueva/actual
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
    WHERE id_tarjeta = NEW.id_tarjeta
  )
  WHERE id_tarjeta = NEW.id_tarjeta;
END$$

DELIMITER ;
-- =================================================================

-- Trigger: Después de insertar movimiento de préstamo
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_insert`$$
CREATE TRIGGER `tr_update_saldo_prestamo_after_insert` 
AFTER INSERT ON `prestamo_movimiento` 
FOR EACH ROW 
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
    WHERE prestamo_id_prestamo = NEW.prestamo_id_prestamo
  )
  WHERE id_prestamo = NEW.prestamo_id_prestamo;
END$$

-- Trigger: Después de actualizar movimiento de préstamo
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_update`$$
CREATE TRIGGER `tr_update_saldo_prestamo_after_update` 
AFTER UPDATE ON `prestamo_movimiento` 
FOR EACH ROW 
BEGIN
  -- Si cambió el préstamo, actualizar el préstamo anterior
  IF OLD.prestamo_id_prestamo <> NEW.prestamo_id_prestamo THEN
    UPDATE prestamo
    SET saldo_inicial = (
      SELECT IFNULL(SUM(
        CASE
          WHEN valor IS NOT NULL THEN valor
          ELSE 0
        END
      ), 0)
      FROM prestamo_movimiento
      WHERE prestamo_id_prestamo = OLD.prestamo_id_prestamo
    )
    WHERE id_prestamo = OLD.prestamo_id_prestamo;
  END IF;

  -- Actualizar el préstamo nuevo/actual
  UPDATE prestamo
  SET saldo_inicial = (
    SELECT IFNULL(SUM(
      CASE
        WHEN valor IS NOT NULL THEN valor
        ELSE 0
      END
    ), 0)
    FROM prestamo_movimiento
    WHERE prestamo_id_prestamo = NEW.prestamo_id_prestamo
  )
  WHERE id_prestamo = NEW.prestamo_id_prestamo;
END$$

-- Trigger: Después de eliminar movimiento de préstamo
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_delete`$$
CREATE TRIGGER `tr_update_saldo_prestamo_after_delete` 
AFTER DELETE ON `prestamo_movimiento` 
FOR EACH ROW 
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
    WHERE prestamo_id_prestamo = OLD.prestamo_id_prestamo
  )
  WHERE id_prestamo = OLD.prestamo_id_prestamo;
END$$

/*CREATE TRIGGER tr_alerta_gasto_alto aplicarlo en la tabla de movimientos personales
AFTER INSERT ON mis_transacciones
FOR EACH ROW
BEGIN
    -- Si gastas más de X en día no hábil (probablemente entretenimiento)
    IF NEW.monto > (SELECT valor FROM constantes WHERE clave = 'LIMITE_OCIO') 
       AND fn_es_dia_habil(NEW.fecha) = 0 THEN
        INSERT INTO alertas_personales (mensaje, fecha) 
        VALUES ('Gasto alto en día no hábil - revisar', NOW());
    END IF;
END;/*
DELIMITER ;
