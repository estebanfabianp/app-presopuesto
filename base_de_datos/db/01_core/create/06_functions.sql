-- =================================================================
-- ARCHIVO DE FUNCIONES PERSONALIZADAS
-- =================================================================
-- Proyecto: app-presupuesto
-- Archivo: 06_functions.sql
-- Descripción: Funciones para cálculos y operaciones específicas del sistema
-- Autor: Sistema de Presupuesto Personal
-- Fecha creación: Diciembre 2025
-- Última modificación: 16 de diciembre de 2025
-- Versión: 1.2.0
-- 
-- PROPÓSITO:
-- Este archivo contiene funciones personalizadas para:
--   * Cálculos financieros y de movimientos
--   * Manejo de fechas y días hábiles
--   * Reclasificación de categorías
--   * Validaciones de negocio
--
-- DEPENDENCIAS:
--   * Tabla: movimiento
--   * Tabla: cuenta
--   * Tabla: categoria
--
-- NOTAS IMPORTANTES:
--   * Todas las funciones son DETERMINISTIC para optimización
--   * Los días hábiles se consideran de lunes a viernes (no incluye feriados)
--   * Usar DEFINER=`root`@`localhost` para permisos adecuados
-- =================================================================

DELIMITER $$

-- =================================================================
-- FUNCIÓN: obtener_total_movimientos
-- =================================================================
-- PROPÓSITO:
--   Calcula el total acumulado de movimientos financieros para una persona específica
--
-- PARÁMETROS:
--   * p_id_persona (INT NOT NULL): Identificador único de la persona
--                                  Debe existir en la tabla persona
--                                  Rango válido: > 0
--
-- RETORNA:
--   * DECIMAL(15,2): Suma total de movimientos en formato monetario
--                    Retorna 0.00 si no hay movimientos
--                    Incluye decimales para centavos
--
-- EJEMPLOS DE USO:
--   SELECT obtener_total_movimientos(1);              -- Usuario ID 1
--   SELECT obtener_total_movimientos(@usuario_actual); -- Variable
--
-- LÓGICA DE NEGOCIO:
--   1. Busca todos los movimientos asociados al ID de persona
--   2. Suma los montos (positivos y negativos)
--   3. Retorna 0 si no encuentra movimientos
--
-- ESTADO: ⚠️  REQUIERE CORRECCIÓN
--   * Falta JOIN con tabla cuenta para relación correcta
--   * Validar que la relación persona->cuenta->movimiento sea correcta
--
-- RENDIMIENTO: O(n) donde n = número de movimientos de la persona
-- TRANSACCIONAL: Función de solo lectura, no afecta datos
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
-- FUNCIÓN: reclasificar_categoria_movimientos
-- =================================================================
-- PROPÓSITO:
--   Reclasifica masivamente movimientos a una nueva categoría dentro de un rango de fechas
--   Útil para corrección de categorizaciones y reorganización de presupuestos
--
-- PARÁMETROS:
--   * p_id_categoria_nueva (INT NOT NULL): ID de la nueva categoría destino
--                                          Debe existir en tabla categoria
--                                          Rango válido: > 0
--   * p_fecha_inicio (DATE NOT NULL): Fecha de inicio del rango (inclusiva)
--                                     Formato: 'YYYY-MM-DD'
--   * p_fecha_fin (DATE NOT NULL): Fecha de fin del rango (inclusiva)
--                                  Debe ser >= p_fecha_inicio
--
-- RETORNA:
--   * INT: Número de movimientos que fueron reclasificados
--          0 = No se encontraron movimientos en el rango
--          >0 = Cantidad de registros modificados exitosamente
--
-- EJEMPLOS DE USO:
--   -- Reclasificar enero 2025 a categoría "Gastos varios"
--   SELECT reclasificar_categoria_movimientos(5, '2025-01-01', '2025-01-31');
--   
--   -- Reclasificar solo un día específico
--   SELECT reclasificar_categoria_movimientos(3, '2025-12-15', '2025-12-15');
--
-- LÓGICA DE NEGOCIO:
--   1. Busca movimientos por fecha_creacion en el rango especificado
--   2. Actualiza id_categoria para todos los movimientos encontrados
--   3. Utiliza ROW_COUNT() para retornar cantidad de filas afectadas
--
-- VALIDACIONES RECOMENDADAS:
--   * Verificar que p_fecha_fin >= p_fecha_inicio
--   * Validar existencia de p_id_categoria_nueva antes de ejecutar
--   * Considerar backup antes de reclasificaciones masivas
--
-- RENDIMIENTO: O(n) donde n = movimientos en el rango de fechas
-- TRANSACCIONAL: ⚠️  Modifica datos - usar dentro de transacciones
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

-- =================================================================
-- FUNCIÓN: obtener_ultimo_dia_habil_mes
-- =================================================================
-- PROPÓSITO:
--   Calcula el último día hábil (lunes a viernes) del mes para una fecha dada
--   Esencial para cálculos de nóminas, vencimientos y cierres contables
--
-- PARÁMETROS:
--   * p_fecha (DATE NOT NULL): Fecha de referencia para determinar mes/año
--                              Puede ser cualquier día del mes objetivo
--                              Formato: 'YYYY-MM-DD'
--
-- RETORNA:
--   * DATE: Último día hábil del mes en formato 'YYYY-MM-DD'
--           Siempre será un día de lunes a viernes
--           Nunca retorna sábados o domingos
--
-- EJEMPLOS DE USO:
--   SELECT obtener_ultimo_dia_habil_mes('2025-12-15');  -- ➜ 2025-12-31 (martes)
--   SELECT obtener_ultimo_dia_habil_mes('2025-02-01');  -- ➜ 2025-02-28 (viernes)
--   SELECT obtener_ultimo_dia_habil_mes(CURDATE());     -- ➜ Último día hábil del mes actual
--
-- LÓGICA DE CÁLCULO:
--   1. Obtiene el último día del mes con LAST_DAY()
--   2. Determina día de la semana con DAYOFWEEK() (1=Dom, 7=Sáb)
--   3. Ajusta según el día:
--      * Si es domingo (1): retrocede 2 días → viernes
--      * Si es sábado (7): retrocede 1 día → viernes  
--      * Si es lun-vie (2-6): mantiene el día
--
-- CASOS DE USO COMUNES:
--   * Cálculo de fechas de pago de nóminas
--   * Determinación de vencimientos de facturas
--   * Cierres contables mensuales
--   * Reportes que deben generarse en días laborables
--
-- LIMITACIONES:
--   ⚠️  No considera feriados nacionales o locales
--   ⚠️  Solo evalúa fines de semana (sáb/dom)
--
-- RENDIMIENTO: O(1) - Cálculo constante independiente del mes
-- ZONA HORARIA: Utiliza la zona horaria del servidor MySQL
-- =================================================================
DROP FUNCTION IF EXISTS `obtener_ultimo_dia_habil_mes`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `obtener_ultimo_dia_habil_mes` (`p_fecha` DATE) 
RETURNS DATE 
DETERMINISTIC 
BEGIN
    DECLARE ultimo_dia DATE;
    DECLARE dia_semana INT;
    
    -- Obtener el último día del mes
    SET ultimo_dia = LAST_DAY(p_fecha);
    
    -- Obtener el día de la semana (1=Domingo, 2=Lunes, ..., 7=Sábado)
    SET dia_semana = DAYOFWEEK(ultimo_dia);
    
    -- Ajustar para obtener un día hábil (lunes a viernes)
    CASE dia_semana
        WHEN 1 THEN -- Domingo, retroceder 2 días al viernes
            SET ultimo_dia = DATE_SUB(ultimo_dia, INTERVAL 2 DAY);
        WHEN 7 THEN -- Sábado, retroceder 1 día al viernes
            SET ultimo_dia = DATE_SUB(ultimo_dia, INTERVAL 1 DAY);
        ELSE -- Lunes a viernes (2-6), mantener el día
            SET ultimo_dia = ultimo_dia;
    END CASE;
    
    RETURN ultimo_dia;
END$$

-- =================================================================
-- FUNCIÓN: es_dia_habil (Función Auxiliar)
-- =================================================================
-- PROPÓSITO:
--   Valida si una fecha específica corresponde a un día hábil empresarial
--   Función de utilidad para validaciones de negocio y cálculos temporales
--
-- PARÁMETROS:
--   * p_fecha (DATE NOT NULL): Fecha a evaluar
--                              Formato: 'YYYY-MM-DD'
--                              Acepta fechas pasadas, presentes o futuras
--
-- RETORNA:
--   * BOOLEAN: TRUE (1) si la fecha es día hábil (lunes-viernes)
--              FALSE (0) si la fecha es fin de semana (sábado-domingo)
--
-- EJEMPLOS DE USO:
--   SELECT es_dia_habil('2025-12-16');  -- ➜ TRUE (lunes)
--   SELECT es_dia_habil('2025-12-14');  -- ➜ FALSE (sábado)
--   SELECT es_dia_habil(CURDATE());     -- ➜ Evalúa día actual
--   
--   -- Uso en condiciones WHERE
--   SELECT * FROM movimiento 
--   WHERE es_dia_habil(fecha_creacion) = TRUE;
--
-- LÓGICA DE EVALUACIÓN:
--   1. Calcula día de la semana con DAYOFWEEK()
--   2. Mapeo de días: 1=Domingo, 2=Lunes, 3=Martes, ..., 7=Sábado
--   3. Retorna TRUE si el día está en rango 2-6 (lunes-viernes)
--
-- CASOS DE USO:
--   * Validación antes de programar transacciones automáticas
--   * Filtrado de reportes por días laborables
--   * Validaciones en triggers y procedimientos
--   * Cálculos de días hábiles transcurridos
--
-- CONSIDERACIONES:
--   ✅ Función pura sin efectos secundarios
--   ⚠️  No considera feriados bancarios/nacionales
--   ⚠️  Basado únicamente en día de la semana
--
-- RENDIMIENTO: O(1) - Evaluación instantánea
-- USO RECOMENDADO: Como función auxiliar en queries complejas
-- =================================================================
DROP FUNCTION IF EXISTS `es_dia_habil`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `es_dia_habil` (`p_fecha` DATE) 
RETURNS BOOLEAN 
DETERMINISTIC 
BEGIN
    DECLARE dia_semana INT;
    
    -- Obtener el día de la semana (1=Domingo, 2=Lunes, ..., 7=Sábado)
    SET dia_semana = DAYOFWEEK(p_fecha);
    
    -- Retornar TRUE si es lunes a viernes (2-6)
    RETURN dia_semana BETWEEN 2 AND 6;
END$$

-- =================================================================
-- Función: obtener_dia_habil_dia_15
-- Descripción: Obtiene el día hábil correspondiente al día 15 del mes
--              Si el 15 cae en día hábil, retorna el 15
--              Si el 15 cae en fin de semana, retorna el último día hábil previo
-- Parámetros:
--   * p_fecha (DATE): Fecha de referencia para obtener el mes/año
-- Retorna: DATE - Día hábil correspondiente al día 15 del mes
-- Uso: SELECT obtener_dia_habil_dia_15('2025-12-01');
--      SELECT obtener_dia_habil_dia_15(CURDATE());
-- =================================================================
DROP FUNCTION IF EXISTS `obtener_dia_habil_dia_15`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `obtener_dia_habil_dia_15` (`p_fecha` DATE) 
RETURNS DATE 
DETERMINISTIC 
BEGIN
    DECLARE dia_15 DATE;
    DECLARE dia_semana INT;
    
    -- Construir el día 15 del mes de la fecha proporcionada
    SET dia_15 = DATE(CONCAT(YEAR(p_fecha), '-', 
                            LPAD(MONTH(p_fecha), 2, '0'), '-15'));
    
    -- Obtener el día de la semana del día 15 (1=Domingo, 2=Lunes, ..., 7=Sábado)
    SET dia_semana = DAYOFWEEK(dia_15);
    
    -- Ajustar si cae en fin de semana
    CASE dia_semana
        WHEN 1 THEN -- Domingo, retroceder 2 días al viernes (día 13)
            SET dia_15 = DATE_SUB(dia_15, INTERVAL 2 DAY);
        WHEN 7 THEN -- Sábado, retroceder 1 día al viernes (día 14)
            SET dia_15 = DATE_SUB(dia_15, INTERVAL 1 DAY);
        ELSE -- Lunes a viernes (2-6), mantener el día 15
            SET dia_15 = dia_15;
    END CASE;
    
    RETURN dia_15;
END$$

-- =================================================================
-- Función: obtener_proximo_dia_habil_desde_15
-- Descripción: Si el día 15 cae en fin de semana, obtiene el siguiente día hábil
--              Si el 15 es día hábil, retorna el 15
-- Parámetros:
--   * p_fecha (DATE): Fecha de referencia para obtener el mes/año
-- Retorna: DATE - Día hábil desde el día 15 del mes (15 o posterior)
-- Uso: SELECT obtener_proximo_dia_habil_desde_15('2025-12-01');
-- =================================================================
DROP FUNCTION IF EXISTS `obtener_proximo_dia_habil_desde_15`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `obtener_proximo_dia_habil_desde_15` (`p_fecha` DATE) 
RETURNS DATE 
DETERMINISTIC 
BEGIN
    DECLARE dia_15 DATE;
    DECLARE dia_semana INT;
    
    -- Construir el día 15 del mes de la fecha proporcionada
    SET dia_15 = DATE(CONCAT(YEAR(p_fecha), '-', 
                            LPAD(MONTH(p_fecha), 2, '0'), '-15'));
    
    -- Obtener el día de la semana del día 15 (1=Domingo, 2=Lunes, ..., 7=Sábado)
    SET dia_semana = DAYOFWEEK(dia_15);
    
    -- Ajustar si cae en fin de semana (avanzar al siguiente día hábil)
    CASE dia_semana
        WHEN 1 THEN -- Domingo, avanzar 1 día al lunes (día 16)
            SET dia_15 = DATE_ADD(dia_15, INTERVAL 1 DAY);
        WHEN 7 THEN -- Sábado, avanzar 2 días al lunes (día 17)
            SET dia_15 = DATE_ADD(dia_15, INTERVAL 2 DAY);
        ELSE -- Lunes a viernes (2-6), mantener el día 15
            SET dia_15 = dia_15;
    END CASE;
    
    RETURN dia_15;
END$$

/*mirar donde aplicar esta función

def analizar_gasto_personal(descripcion, monto, fecha):
    # Usa tu base de datos de patrones personales
    patron_similar = buscar_gastos_similares(descripcion)
    es_inusual = monto > (patron_similar.promedio * 1.5)
    
    if es_inusual and fn_es_dia_habil(fecha):
        return "⚠️ Gasto alto en día laboral - ¿todo bien?"
    elif monto > presupuesto_diario() * 2:
        return f"💸 Gastaste 2x el presupuesto diario. Quedan {dias_habiles_restantes()} días hábiles"
    
    return "✅ Gasto normal para tu patrón"*/
DELIMITER ;
