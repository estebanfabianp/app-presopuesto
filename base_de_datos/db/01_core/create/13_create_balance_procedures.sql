-- =================================================================
-- PROCEDIMIENTOS Y TRIGGERS PARA GESTIÓN DE SALDOS
-- Gestión de cálculo, validación y auditoría de saldos
-- =================================================================

USE app_presupuesto;

-- -----------------------------------------------------------------
-- TABLA DE AUDITORIA: Registro de cambios de saldo
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auditoria_saldo_cuenta (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    id_cuenta INT NOT NULL,
    id_persona INT NOT NULL,
    saldo_anterior DECIMAL(15,2),
    saldo_nuevo DECIMAL(15,2),
    diferencia DECIMAL(15,2),
    tipo_cambio ENUM('ingreso', 'gasto', 'ajuste_manual', 'recalculo', 'correccion') DEFAULT 'recalculo',
    razon VARCHAR(255),
    id_movimiento INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_sistema VARCHAR(100) DEFAULT 'system',
    FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta) ON DELETE CASCADE,
    FOREIGN KEY (id_persona) REFERENCES persona(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_movimiento) REFERENCES movimiento(id_movimiento) ON DELETE SET NULL,
    INDEX idx_cuenta (id_cuenta),
    INDEX idx_persona (id_persona),
    INDEX idx_fecha (fecha_registro),
    INDEX idx_tipo (tipo_cambio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------
-- PROCEDIMIENTO: Calcular saldo actual de una cuenta
-- Retorna: saldo_inicial + ingresos - gastos
-- -----------------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE calc_saldo_cuenta(
    IN p_id_cuenta INT,
    OUT p_saldo_calculado DECIMAL(15,2),
    OUT p_total_ingresos DECIMAL(15,2),
    OUT p_total_gastos DECIMAL(15,2),
    OUT p_error VARCHAR(255)
)
READS SQL DATA
BEGIN
    DECLARE saldo_ini DECIMAL(15,2) DEFAULT 0;
    DECLARE ingresos DECIMAL(15,2) DEFAULT 0;
    DECLARE gastos DECIMAL(15,2) DEFAULT 0;
    
    SET p_error = NULL;
    
    -- Obtener saldo inicial de la cuenta
    SELECT COALESCE(saldo_inicial, 0) INTO saldo_ini
    FROM cuenta
    WHERE id_cuenta = p_id_cuenta;
    
    IF saldo_ini IS NULL THEN
        SET p_error = 'Cuenta no encontrada';
        SET p_saldo_calculado = 0;
        SET p_total_ingresos = 0;
        SET p_total_gastos = 0;
        LEAVE;
    END IF;
    
    -- Calcular suma de ingresos
    SELECT COALESCE(SUM(m.monto), 0) INTO ingresos
    FROM movimiento m
    INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
    WHERE m.id_cuenta = p_id_cuenta 
      AND LOWER(TRIM(tm.nombre)) = 'ingreso'
      AND m.monto > 0;
    
    -- Calcular suma de gastos
    SELECT COALESCE(SUM(m.monto), 0) INTO gastos
    FROM movimiento m
    INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
    WHERE m.id_cuenta = p_id_cuenta 
      AND LOWER(TRIM(tm.nombre)) = 'gasto'
      AND m.monto > 0;
    
    -- Calcular saldo final
    SET p_saldo_calculado = saldo_ini + ingresos - gastos;
    SET p_total_ingresos = ingresos;
    SET p_total_gastos = gastos;
    
END$$

DELIMITER ;

-- -----------------------------------------------------------------
-- PROCEDIMIENTO: Validar integridad de saldos
-- Verifica que el saldo en BD coincida con el calculado
-- -----------------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE validar_integridad_saldos(
    IN p_id_persona INT
)
READS SQL DATA
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id_cuenta INT;
    DECLARE v_saldo_calc DECIMAL(15,2);
    DECLARE v_ingresos DECIMAL(15,2);
    DECLARE v_gastos DECIMAL(15,2);
    DECLARE v_error VARCHAR(255);
    
    DECLARE cur CURSOR FOR
        SELECT id_cuenta FROM cuenta WHERE id_persona = p_id_persona;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Crear tabla temporal para resultados
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_validacion_saldos (
        id_cuenta INT,
        saldo_calculado DECIMAL(15,2),
        total_ingresos DECIMAL(15,2),
        total_gastos DECIMAL(15,2),
        es_valido BOOLEAN
    );
    
    OPEN cur;
    
    lectura: LOOP
        FETCH cur INTO v_id_cuenta;
        IF done THEN
            LEAVE lectura;
        END IF;
        
        -- Llamar al procedimiento de cálculo
        CALL calc_saldo_cuenta(
            v_id_cuenta,
            v_saldo_calc,
            v_ingresos,
            v_gastos,
            v_error
        );
        
        -- Insertar resultado en tabla temporal
        INSERT INTO tmp_validacion_saldos VALUES (
            v_id_cuenta,
            v_saldo_calc,
            v_ingresos,
            v_gastos,
            v_error IS NULL
        );
        
    END LOOP;
    
    CLOSE cur;
    
    -- Retornar resultados
    SELECT * FROM tmp_validacion_saldos;
    
    DROP TEMPORARY TABLE tmp_validacion_saldos;
    
END$$

DELIMITER ;

-- -----------------------------------------------------------------
-- PROCEDIMIENTO: Registrar cambio de saldo en auditoría
-- -----------------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE registrar_cambio_saldo(
    IN p_id_cuenta INT,
    IN p_id_persona INT,
    IN p_saldo_anterior DECIMAL(15,2),
    IN p_saldo_nuevo DECIMAL(15,2),
    IN p_tipo_cambio VARCHAR(50),
    IN p_razon VARCHAR(255),
    IN p_id_movimiento INT DEFAULT NULL,
    IN p_usuario VARCHAR(100) DEFAULT 'system'
)
MODIFIES SQL DATA
BEGIN
    DECLARE v_diferencia DECIMAL(15,2);
    
    SET v_diferencia = p_saldo_nuevo - p_saldo_anterior;
    
    INSERT INTO auditoria_saldo_cuenta (
        id_cuenta,
        id_persona,
        saldo_anterior,
        saldo_nuevo,
        diferencia,
        tipo_cambio,
        razon,
        id_movimiento,
        usuario_sistema
    ) VALUES (
        p_id_cuenta,
        p_id_persona,
        p_saldo_anterior,
        p_saldo_nuevo,
        v_diferencia,
        p_tipo_cambio,
        p_razon,
        p_id_movimiento,
        p_usuario
    );
    
END$$

DELIMITER ;

-- -----------------------------------------------------------------
-- TRIGGER: Auditar cambios en tabla movimiento
-- Se ejecuta cuando se crea o elimina un movimiento
-- -----------------------------------------------------------------
DELIMITER $$

CREATE TRIGGER tr_audit_movimiento_insert
AFTER INSERT ON movimiento 
FOR EACH ROW
BEGIN
    DECLARE v_id_persona INT;
    DECLARE v_saldo_anterior DECIMAL(15,2);
    DECLARE v_saldo_nuevo DECIMAL(15,2);
    DECLARE v_ingresos DECIMAL(15,2);
    DECLARE v_gastos DECIMAL(15,2);
    DECLARE v_error VARCHAR(255);
    
    -- Obtener id_persona de la cuenta
    SELECT id_persona INTO v_id_persona 
    FROM cuenta 
    WHERE id_cuenta = NEW.id_cuenta;
    
    -- Obtener saldo anterior (suma de movimientos previos - 1)
    SELECT saldo_inicial + COALESCE(SUM(
        CASE 
            WHEN LOWER(TRIM(tm.nombre)) = 'ingreso' THEN m.monto
            WHEN LOWER(TRIM(tm.nombre)) = 'gasto' THEN -m.monto
            ELSE 0
        END
    ), 0) INTO v_saldo_anterior
    FROM cuenta c
    LEFT JOIN movimiento m ON c.id_cuenta = m.id_cuenta
    LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
    WHERE c.id_cuenta = NEW.id_cuenta AND m.id_movimiento < NEW.id_movimiento;
    
    -- Calcular saldo nuevo
    CALL calc_saldo_cuenta(
        NEW.id_cuenta,
        v_saldo_nuevo,
        v_ingresos,
        v_gastos,
        v_error
    );
    
    -- Registrar en auditoría
    IF v_error IS NULL THEN
        CALL registrar_cambio_saldo(
            NEW.id_cuenta,
            v_id_persona,
            COALESCE(v_saldo_anterior, 0),
            v_saldo_nuevo,
            LOWER(TRIM((SELECT nombre FROM tipo_movimiento WHERE id_tipo = NEW.id_tipo))),
            COALESCE(NEW.nota, 'Movimiento registrado'),
            NEW.id_movimiento,
            'trigger_insert'
        );
    END IF;
    
END$$

DELIMITER ;

-- -----------------------------------------------------------------
-- Índices para mejora de performance
-- -----------------------------------------------------------------
CREATE INDEX idx_movimiento_cuenta_tipo ON movimiento(id_cuenta, id_tipo);
CREATE INDEX idx_movimiento_monto ON movimiento(monto) WHERE monto > 0;
CREATE INDEX idx_cuenta_persona ON cuenta(id_persona, id_cuenta);

-- -----------------------------------------------------------------
-- VIEW: Resumen de saldos por persona
-- -----------------------------------------------------------------
CREATE OR REPLACE VIEW v_resumen_saldos_persona AS
SELECT
    c.id_persona,
    COUNT(DISTINCT c.id_cuenta) AS num_cuentas,
    SUM(c.saldo_inicial) AS saldo_inicial_total,
    SUM(COALESCE(
        (SELECT COALESCE(SUM(m.monto), 0) 
         FROM movimiento m 
         INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo 
         WHERE m.id_cuenta = c.id_cuenta AND LOWER(tm.nombre) = 'ingreso'), 
        0
    )) AS total_ingresos,
    SUM(COALESCE(
        (SELECT COALESCE(SUM(m.monto), 0) 
         FROM movimiento m 
         INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo 
         WHERE m.id_cuenta = c.id_cuenta AND LOWER(tm.nombre) = 'gasto'), 
        0
    )) AS total_gastos,
    SUM(c.saldo_inicial + COALESCE(
        (SELECT COALESCE(SUM(m.monto), 0) 
         FROM movimiento m 
         INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo 
         WHERE m.id_cuenta = c.id_cuenta AND LOWER(tm.nombre) = 'ingreso'), 0) -
        COALESCE(
        (SELECT COALESCE(SUM(m.monto), 0) 
         FROM movimiento m 
         INNER JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo 
         WHERE m.id_cuenta = c.id_cuenta AND LOWER(tm.nombre) = 'gasto'), 
        0)
    )) AS saldo_total_actual
FROM cuenta c
GROUP BY c.id_persona;

-- =================================================================
-- FIN DE PROCEDIMIENTOS Y TRIGGERS
-- =================================================================
