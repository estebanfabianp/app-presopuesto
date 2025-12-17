-- =================================================================
-- PROCEDIMIENTOS DE DOCUMENTACIÓN Y REPORTES DEL SISTEMA
-- Proyecto: app-presupuesto
-- Descripción: Procedimientos para generar reportes de documentación y arquitectura
-- Propósito: Facilitar la gestión y reporte de documentación técnica
-- Versión: 1.0 - Procedimientos de documentación
-- =================================================================

-- =================================================================
-- PROCEDIMIENTO DE GENERACIÓN DE REPORTE DE DOCUMENTACIÓN
-- =================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_generar_reporte_documentacion`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_generar_reporte_documentacion`(
    IN p_tipo_componente VARCHAR(50) DEFAULT NULL,
    IN p_nivel_detalle ENUM('BASICO', 'COMPLETO', 'TECNICO') DEFAULT 'COMPLETO'
)
BEGIN
    DECLARE v_total_componentes INT DEFAULT 0;
    DECLARE v_componentes_documentados INT DEFAULT 0;
    DECLARE v_cobertura_documentacion DECIMAL(5,2) DEFAULT 0;

    -- Contar total de objetos en la base de datos
    SELECT 
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'app_presupuesto') +
        (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'app_presupuesto') +
        (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'app_presupuesto') +
        (SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'app_presupuesto') +
        (SELECT COUNT(*) FROM information_schema.events WHERE event_schema = 'app_presupuesto')
    INTO v_total_componentes;

    -- Contar objetos documentados
    SELECT COUNT(*) INTO v_componentes_documentados FROM documentacion_sistema
    WHERE (p_tipo_componente IS NULL OR tipo = p_tipo_componente);

    -- Calcular cobertura
    SET v_cobertura_documentacion = (v_componentes_documentados * 100.0) / v_total_componentes;

    -- Reporte de cobertura
    SELECT 
        'RESUMEN DE DOCUMENTACIÓN' AS seccion,
        v_total_componentes AS total_componentes_sistema,
        v_componentes_documentados AS componentes_documentados,
        CONCAT(ROUND(v_cobertura_documentacion, 2), '%') AS cobertura_documentacion,
        CASE 
            WHEN v_cobertura_documentacion >= 90 THEN 'Excelente'
            WHEN v_cobertura_documentacion >= 70 THEN 'Buena'
            WHEN v_cobertura_documentacion >= 50 THEN 'Aceptable'
            ELSE 'Necesita mejora'
        END AS evaluacion_cobertura;

    -- Reporte por tipo de componente
    SELECT 
        'DISTRIBUCIÓN POR TIPO' AS seccion,
        tipo,
        COUNT(*) AS cantidad,
        ROUND(COUNT(*) * 100.0 / v_componentes_documentados, 2) AS porcentaje
    FROM documentacion_sistema
    WHERE (p_tipo_componente IS NULL OR tipo = p_tipo_componente)
    GROUP BY tipo
    ORDER BY cantidad DESC;

    -- Reporte detallado según nivel solicitado
    IF p_nivel_detalle = 'COMPLETO' OR p_nivel_detalle = 'TECNICO' THEN
        SELECT 
            'DOCUMENTACIÓN DETALLADA' AS seccion,
            tipo,
            nombre_objeto,
            descripcion_corta,
            CASE WHEN LENGTH(casos_uso) > 100 THEN CONCAT(LEFT(casos_uso, 100), '...') ELSE casos_uso END AS casos_uso_resumen,
            version,
            fecha_creacion
        FROM documentacion_sistema
        WHERE (p_tipo_componente IS NULL OR tipo = p_tipo_componente)
        ORDER BY tipo, nombre_objeto;
    END IF;

    -- Información técnica adicional
    IF p_nivel_detalle = 'TECNICO' THEN
        SELECT 
            'MÉTRICAS TÉCNICAS' AS seccion,
            'Tablas con triggers automáticos' AS metrica,
            COUNT(*) AS valor
        FROM information_schema.triggers 
        WHERE trigger_schema = 'app_presupuesto'
        
        UNION ALL
        
        SELECT 
            'MÉTRICAS TÉCNICAS' AS seccion,
            'Procedimientos almacenados' AS metrica,
            COUNT(*) AS valor
        FROM information_schema.routines 
        WHERE routine_schema = 'app_presupuesto' AND routine_type = 'PROCEDURE'
        
        UNION ALL
        
        SELECT 
            'MÉTRICAS TÉCNICAS' AS seccion,
            'Eventos programados' AS metrica,
            COUNT(*) AS valor
        FROM information_schema.events 
        WHERE event_schema = 'app_presupuesto';
    END IF;

END$$

DELIMITER ;

-- =================================================================
-- PROCEDIMIENTO PARA REPORTE DE ARQUITECTURA
-- =================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_generar_reporte_arquitectura`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_generar_reporte_arquitectura`(
    IN p_tipo_componente VARCHAR(50) DEFAULT NULL
)
BEGIN
    -- Reporte de componentes de arquitectura
    SELECT 
        'COMPONENTES DE ARQUITECTURA' AS seccion,
        nombre_componente,
        tipo_componente,
        descripcion,
        responsabilidades,
        version,
        fecha_creacion
    FROM arquitectura_sistema
    WHERE (p_tipo_componente IS NULL OR tipo_componente = p_tipo_componente)
    ORDER BY 
        FIELD(tipo_componente, 'CAPA', 'MODULO', 'SERVICIO', 'INTEGRACION', 'HERRAMIENTA'),
        nombre_componente;

    -- Reporte de dependencias
    SELECT 
        'MAPA DE DEPENDENCIAS' AS seccion,
        nombre_componente AS componente,
        dependencias AS componentes_dependientes,
        tecnologias AS stack_tecnologico
    FROM arquitectura_sistema
    WHERE (p_tipo_componente IS NULL OR tipo_componente = p_tipo_componente)
    ORDER BY nombre_componente;

    -- Estadísticas de arquitectura
    SELECT 
        'ESTADÍSTICAS DE ARQUITECTURA' AS seccion,
        tipo_componente,
        COUNT(*) AS total_componentes
    FROM arquitectura_sistema
    WHERE (p_tipo_componente IS NULL OR tipo_componente = p_tipo_componente)
    GROUP BY tipo_componente
    ORDER BY total_componentes DESC;

END$$

DELIMITER ;

-- Script completado exitosamente
SELECT 'PROCEDIMIENTOS DE DOCUMENTACIÓN CREADOS EXITOSAMENTE' AS resultado;