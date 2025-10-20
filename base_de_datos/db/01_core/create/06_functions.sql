-- =================================================================
-- FUNCIONES
-- Proyecto: app-presupuesto
-- Descripción: Funciones para cálculos y operaciones específicas
-- =================================================================

DELIMITER $$

-- =================================================================
-- Función: obtener_total_movimientos
-- Descripción: Calcula el total de movimientos para una persona específica
-- Parámetros:
--   * p_id_persona (INT): ID de la persona
-- Retorna: DECIMAL(15,2) - Total de movimientos de la persona
-- Uso: SELECT obtener_total_movimientos(1);
-- NOTA: Función requiere corrección - falta JOIN con tabla cuenta
-- =================================================================
DROP FUNCTION IF EXISTS `obtener_total_movimientos`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `obtener_total_movimientos` (`p_id_persona` INT) 
RETURNS DECIMAL(15,2) 
DETERMINISTIC 
BEGIN
    DECLARE total DECIMAL(15,2);
    -- NOTA: Esta consulta necesita corrección para funcionar correctamente
    -- Debería hacer JOIN con tabla cuenta para obtener movimientos por persona
    SELECT SUM(monto) INTO total FROM movimiento WHERE id_persona = p_id_persona;
    RETURN IFNULL(total, 0);
END$$

-- =================================================================
-- Función: reclasificar_categoria_movimientos
-- Descripción: Cambia la categoría de movimientos en un rango de fechas
-- Parámetros:
--   * p_id_categoria_nueva (INT): Nueva categoría a asignar
--   * p_fecha_inicio (DATE): Fecha de inicio del rango
--   * p_fecha_fin (DATE): Fecha de fin del rango
-- Retorna: INT - Número de movimientos reclasificados
-- Uso: SELECT reclasificar_categoria_movimientos(5, '2025-01-01', '2025-01-31');
-- =================================================================
DROP FUNCTION IF EXISTS `reclasificar_categoria_movimientos`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `reclasificar_categoria_movimientos` (
    `p_id_categoria_nueva` INT, 
    `p_fecha_inicio` DATE, 
    `p_fecha_fin` DATE
) 
RETURNS INT(11) 
DETERMINISTIC 
BEGIN
    DECLARE movimientos_afectados INT DEFAULT 0;
    
    -- Actualiza la categoría de movimientos en el rango especificado
    UPDATE movimiento
    SET id_categoria = p_id_categoria_nueva
    WHERE fecha_creacion BETWEEN p_fecha_inicio AND p_fecha_fin;
    
    -- Obtiene el número de filas afectadas
    SELECT ROW_COUNT() INTO movimientos_afectados;
    RETURN movimientos_afectados;
END$$

DELIMITER ;
