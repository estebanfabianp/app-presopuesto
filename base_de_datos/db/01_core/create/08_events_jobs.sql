-- =================================================================
-- EVENTOS Y TRABAJOS PROGRAMADOS
-- Proyecto: app-presupuesto
-- Descripción: Eventos automáticos para mantenimiento de la base de datos
-- =================================================================

DELIMITER $$

-- =================================================================
-- Evento: limpiar_movimientos_antiguos
-- Descripción: Elimina movimientos anteriores a 5 años para optimizar rendimiento
-- Frecuencia: Anual
-- Propósito: Mantener el tamaño de la base de datos controlado
-- NOTA: Considerar mover a tabla histórica en lugar de eliminar
-- =================================================================
DROP EVENT IF EXISTS `limpiar_movimientos_antiguos`$$
CREATE DEFINER=`root`@`localhost` EVENT `limpiar_movimientos_antiguos` 
ON SCHEDULE EVERY 1 YEAR 
STARTS '2025-10-06 23:54:15' 
ON COMPLETION NOT PRESERVE 
ENABLE 
DO BEGIN
    -- Elimina movimientos con más de 5 años de antigüedad
    -- CUIDADO: Esta operación es irreversible
    DELETE FROM movimiento 
    WHERE fecha_creacion < DATE_SUB(NOW(), INTERVAL 5 YEAR);
    
    -- TODO: Implementar logging de la operación
    -- TODO: Considerar mover a tabla de archivo histórico
END$$

-- =================================================================
-- Evento: recalcular_saldos_mensual
-- Descripción: Recalcula todos los saldos mensualmente para mantener consistencia
-- Frecuencia: Mensual (primer día del mes)
-- =================================================================
DROP EVENT IF EXISTS `recalcular_saldos_mensual`$$
CREATE DEFINER=`root`@`localhost` EVENT `recalcular_saldos_mensual` 
ON SCHEDULE EVERY 1 MONTH 
STARTS '2025-01-01 02:00:00' 
ON COMPLETION NOT PRESERVE 
ENABLE 
DO BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE cuenta_id INT;
    DECLARE tarjeta_id INT;
    DECLARE prestamo_id INT;
    
    -- Cursor para cuentas
    DECLARE cursor_cuentas CURSOR FOR 
        SELECT id_cuenta FROM cuenta WHERE estado = 1;
    
    -- Cursor para tarjetas
    DECLARE cursor_tarjetas CURSOR FOR 
        SELECT id_tarjeta FROM tarjeta_credito;
    
    -- Cursor para préstamos
    DECLARE cursor_prestamos CURSOR FOR 
        SELECT id_prestamo FROM prestamo;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Recalcular saldos de cuentas
    OPEN cursor_cuentas;
    recalc_cuentas: LOOP
        FETCH cursor_cuentas INTO cuenta_id;
        IF done THEN
            LEAVE recalc_cuentas;
        END IF;
        CALL sp_recalcular_saldo_cuenta(cuenta_id);
    END LOOP;
    CLOSE cursor_cuentas;
    
    SET done = FALSE;
    
    -- Recalcular saldos de tarjetas
    OPEN cursor_tarjetas;
    recalc_tarjetas: LOOP
        FETCH cursor_tarjetas INTO tarjeta_id;
        IF done THEN
            LEAVE recalc_tarjetas;
        END IF;
        CALL sp_recalcular_saldo_tarjeta(tarjeta_id);
    END LOOP;
    CLOSE cursor_tarjetas;
    
    SET done = FALSE;
    
    -- Recalcular saldos de préstamos
    OPEN cursor_prestamos;
    recalc_prestamos: LOOP
        FETCH cursor_prestamos INTO prestamo_id;
        IF done THEN
            LEAVE recalc_prestamos;
        END IF;
        CALL sp_recalcular_saldo_prestamo(prestamo_id);
    END LOOP;
    CLOSE cursor_prestamos;
    
END$$

-- =================================================================
-- Evento: backup_constantes_semanal
-- Descripción: Crea respaldo de constantes críticas semanalmente
-- Frecuencia: Semanal (domingos a las 3:00 AM)
-- =================================================================
DROP EVENT IF EXISTS `backup_constantes_semanal`$$
CREATE DEFINER=`root`@`localhost` EVENT `backup_constantes_semanal` 
ON SCHEDULE EVERY 1 WEEK 
STARTS '2025-01-05 03:00:00' 
ON COMPLETION NOT PRESERVE 
ENABLE 
DO BEGIN
    -- Crear tabla de backup si no existe
    CREATE TABLE IF NOT EXISTS constantes_backup (
        id_backup INT AUTO_INCREMENT PRIMARY KEY,
        fecha_backup DATETIME DEFAULT CURRENT_TIMESTAMP,
        id_constante INT,
        categoria VARCHAR(50),
        nombre VARCHAR(100),
        valor TEXT,
        tipo_dato ENUM('STRING','INTEGER','DECIMAL','BOOLEAN','JSON','DATE'),
        INDEX idx_backup_fecha (fecha_backup)
    );
    
    -- Insertar backup de constantes críticas
    INSERT INTO constantes_backup (id_constante, categoria, nombre, valor, tipo_dato)
    SELECT id_constante, categoria, nombre, valor, tipo_dato
    FROM constantes 
    WHERE es_editable = 1 AND estado = 1;
    
    -- Limpiar backups antiguos (mantener solo los últimos 12)
    DELETE FROM constantes_backup 
    WHERE fecha_backup < (
        SELECT fecha_backup 
        FROM (
            SELECT fecha_backup 
            FROM constantes_backup 
            ORDER BY fecha_backup DESC 
            LIMIT 12,1
        ) AS t
    );
END$$

DELIMITER ;
