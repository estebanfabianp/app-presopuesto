-- TRIGGERS PARA ACTUALIZAR SALDOS EN CUENTA, TARJETA_CREDITO Y PRESTAMO

DELIMITER $$

-- Trigger para actualizar saldo_inicial en cuenta después de cambios en movimiento
CREATE TRIGGER tr_update_saldo_cuenta_after_insert
AFTER INSERT ON movimiento
FOR EACH ROW
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
    WHERE id_cuenta = NEW.id_cuenta
  )
  WHERE id_cuenta = NEW.id_cuenta;
END$$

CREATE TRIGGER tr_update_saldo_cuenta_after_update
AFTER UPDATE ON movimiento
FOR EACH ROW
BEGIN
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

CREATE TRIGGER tr_update_saldo_cuenta_after_delete
AFTER DELETE ON movimiento
FOR EACH ROW
BEGIN
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
END$$

-- Trigger para actualizar saldo_actual en tarjeta_credito después de cambios en movimiento_tarjeta
CREATE TRIGGER tr_update_saldo_tarjeta_after_insert
AFTER INSERT ON movimiento_tarjeta
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

CREATE TRIGGER tr_update_saldo_tarjeta_after_update
AFTER UPDATE ON movimiento_tarjeta
FOR EACH ROW
BEGIN
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

CREATE TRIGGER tr_update_saldo_tarjeta_after_delete
AFTER DELETE ON movimiento_tarjeta
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
    WHERE id_tarjeta = OLD.id_tarjeta
  )
  WHERE id_tarjeta = OLD.id_tarjeta;
END$$

-- Trigger para actualizar saldo_inicial en prestamo después de cambios en prestamo_movimiento
CREATE TRIGGER tr_update_saldo_prestamo_after_insert
AFTER INSERT ON prestamo_movimiento
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

CREATE TRIGGER tr_update_saldo_prestamo_after_update
AFTER UPDATE ON prestamo_movimiento
FOR EACH ROW
BEGIN
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

CREATE TRIGGER tr_update_saldo_prestamo_after_delete
AFTER DELETE ON prestamo_movimiento
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

DELIMITER;