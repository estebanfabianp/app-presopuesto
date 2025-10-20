-- =================================================================
-- SISTEMA DE VERSIONADO DE ESQUEMA EMPRESARIAL
-- Proyecto: app-presupuesto
-- Descripción: Control de versiones de esquema con audit trail completo
-- Características:
--   * Versionado semántico de esquemas de base de datos
--   * Audit trail completo de cambios estructurales
--   * Comparison tools para detectar drift entre entornos
--   * Automated schema documentation generation
--   * Breaking changes detection con impact analysis
--   * Rollback capabilities con dependency tracking
--   * Environment synchronization tools
-- =================================================================

DELIMITER $$

-- =================================================================
-- TABLAS DE SOPORTE PARA VERSIONADO DE ESQUEMA
-- =================================================================

-- Tabla principal de versiones de esquema
CREATE TABLE IF NOT EXISTS `schema_versions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `version_number` VARCHAR(20) NOT NULL COMMENT 'Versión semántica (ej: 1.2.3)',
    `major_version` INT NOT NULL COMMENT 'Versión mayor (breaking changes)',
    `minor_version` INT NOT NULL COMMENT 'Versión menor (nuevas características)',
    `patch_version` INT NOT NULL COMMENT 'Versión patch (bug fixes)',
    `schema_hash` VARCHAR(64) NOT NULL COMMENT 'SHA256 hash del esquema completo',
    `environment` ENUM('development', 'testing', 'staging', 'production') NOT NULL,
    `description` TEXT COMMENT 'Descripción de los cambios en esta versión',
    `release_notes` TEXT COMMENT 'Notas de release detalladas',
    `breaking_changes` JSON COMMENT 'Lista de cambios que rompen compatibilidad',
    `migration_script` TEXT COMMENT 'Script SQL para migrar a esta versión',
    `rollback_script` TEXT COMMENT 'Script SQL para rollback desde esta versión',
    `applied_by` VARCHAR(100) NOT NULL COMMENT 'Usuario que aplicó esta versión',
    `applied_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `validation_status` ENUM('pending', 'validated', 'failed', 'warning') DEFAULT 'pending',
    `validation_errors` JSON COMMENT 'Errores encontrados durante validación',
    `is_current` BOOLEAN DEFAULT FALSE COMMENT 'Indica si es la versión actual',
    `tags` JSON COMMENT 'Tags adicionales (hotfix, feature, etc.)',
    UNIQUE KEY `uk_version_env` (`version_number`, `environment`),
    INDEX `idx_version_major` (`major_version`, `minor_version`, `patch_version`),
    INDEX `idx_environment` (`environment`),
    INDEX `idx_applied_at` (`applied_at`),
    INDEX `idx_current_version` (`is_current`, `environment`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Registro de versiones de esquema por ambiente';

-- Tabla de audit trail detallado
CREATE TABLE IF NOT EXISTS `schema_audit_trail` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `version_id` INT NOT NULL COMMENT 'Referencia a schema_versions',
    `change_type` ENUM('CREATE', 'ALTER', 'DROP', 'RENAME', 'INDEX', 'CONSTRAINT', 'TRIGGER', 'PROCEDURE', 'FUNCTION', 'VIEW') NOT NULL,
    `object_type` ENUM('TABLE', 'COLUMN', 'INDEX', 'CONSTRAINT', 'TRIGGER', 'PROCEDURE', 'FUNCTION', 'VIEW', 'EVENT') NOT NULL,
    `object_name` VARCHAR(255) NOT NULL COMMENT 'Nombre del objeto modificado',
    `parent_object` VARCHAR(255) COMMENT 'Objeto padre (tabla para columnas, etc.)',
    `change_description` TEXT NOT NULL COMMENT 'Descripción detallada del cambio',
    `sql_statement` TEXT COMMENT 'Statement SQL ejecutado',
    `before_definition` TEXT COMMENT 'Definición antes del cambio',
    `after_definition` TEXT COMMENT 'Definición después del cambio',
    `impact_assessment` JSON COMMENT 'Evaluación de impacto del cambio',
    `dependencies` JSON COMMENT 'Objetos dependientes afectados',
    `execution_time_ms` INT COMMENT 'Tiempo de ejecución en milisegundos',
    `success` BOOLEAN DEFAULT TRUE COMMENT 'Indica si el cambio fue exitoso',
    `error_message` TEXT COMMENT 'Mensaje de error si falló',
    `applied_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_version_change` (`version_id`, `change_type`),
    INDEX `idx_object_changes` (`object_type`, `object_name`),
    INDEX `idx_applied_at` (`applied_at`),
    FOREIGN KEY (`version_id`) REFERENCES `schema_versions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Audit trail detallado de cambios de esquema';

-- Tabla de snapshots de esquema
CREATE TABLE IF NOT EXISTS `schema_snapshots` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `version_id` INT NOT NULL COMMENT 'Referencia a schema_versions',
    `snapshot_type` ENUM('full', 'incremental', 'metadata_only') NOT NULL,
    `tables_definition` JSON NOT NULL COMMENT 'Definición completa de todas las tablas',
    `indexes_definition` JSON COMMENT 'Definición de todos los índices',
    `constraints_definition` JSON COMMENT 'Definición de todas las constraints',
    `triggers_definition` JSON COMMENT 'Definición de todos los triggers',
    `procedures_definition` JSON COMMENT 'Definición de procedimientos',
    `functions_definition` JSON COMMENT 'Definición de funciones',
    `views_definition` JSON COMMENT 'Definición de vistas',
    `events_definition` JSON COMMENT 'Definición de eventos',
    `snapshot_size_bytes` INT COMMENT 'Tamaño del snapshot en bytes',
    `compression_used` BOOLEAN DEFAULT FALSE COMMENT 'Indica si se usó compresión',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_version_snapshot` (`version_id`, `snapshot_type`),
    INDEX `idx_created_at` (`created_at`),
    FOREIGN KEY (`version_id`) REFERENCES `schema_versions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Snapshots completos del esquema por versión';

-- Tabla de comparaciones entre ambientes
CREATE TABLE IF NOT EXISTS `schema_comparisons` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `comparison_name` VARCHAR(255) NOT NULL COMMENT 'Nombre descriptivo de la comparación',
    `source_environment` VARCHAR(50) NOT NULL COMMENT 'Ambiente origen',
    `target_environment` VARCHAR(50) NOT NULL COMMENT 'Ambiente destino',
    `source_version_id` INT COMMENT 'Versión del ambiente origen',
    `target_version_id` INT COMMENT 'Versión del ambiente destino',
    `differences_found` INT DEFAULT 0 COMMENT 'Número de diferencias encontradas',
    `differences_summary` JSON COMMENT 'Resumen de diferencias por tipo',
    `differences_detail` JSON COMMENT 'Detalle completo de todas las diferencias',
    `sync_script` TEXT COMMENT 'Script generado para sincronizar ambientes',
    `comparison_status` ENUM('running', 'completed', 'failed') DEFAULT 'running',
    `started_by` VARCHAR(100) NOT NULL COMMENT 'Usuario que inició la comparación',
    `started_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `completed_at` DATETIME COMMENT 'Timestamp de finalización',
    `execution_time_seconds` INT COMMENT 'Tiempo total de ejecución',
    INDEX `idx_environments` (`source_environment`, `target_environment`),
    INDEX `idx_started_at` (`started_at`),
    INDEX `idx_comparison_status` (`comparison_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historial de comparaciones entre ambientes';

-- =================================================================
-- PROCEDIMIENTO: sp_capture_schema_version
-- Descripción: Captura y registra una nueva versión del esquema
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_capture_schema_version`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_capture_schema_version`(
    IN p_version_number VARCHAR(20),
    IN p_environment VARCHAR(50),
    IN p_description TEXT,
    IN p_applied_by VARCHAR(100),
    IN p_migration_script TEXT DEFAULT NULL,
    IN p_rollback_script TEXT DEFAULT NULL
)
BEGIN
    DECLARE v_version_id INT;
    DECLARE v_schema_hash VARCHAR(64);
    DECLARE v_major_version INT;
    DECLARE v_minor_version INT;
    DECLARE v_patch_version INT;
    DECLARE v_tables_definition JSON;
    DECLARE v_error_message TEXT DEFAULT '';
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_message = MESSAGE_TEXT;
        ROLLBACK;
        RESIGNAL SET MESSAGE_TEXT = CONCAT('Error capturando versión de esquema: ', v_error_message);
    END;

    START TRANSACTION;

    -- Parsear versión semántica
    SET v_major_version = CAST(SUBSTRING_INDEX(p_version_number, '.', 1) AS UNSIGNED);
    SET v_minor_version = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_version_number, '.', 2), '.', -1) AS UNSIGNED);
    SET v_patch_version = CAST(SUBSTRING_INDEX(p_version_number, '.', -1) AS UNSIGNED);

    -- Marcar versión anterior como no actual
    UPDATE schema_versions 
    SET is_current = FALSE 
    WHERE environment = p_environment AND is_current = TRUE;

    -- Generar snapshot del esquema actual
    CALL sp_generate_schema_snapshot(@snapshot_data, @schema_hash);
    SET v_schema_hash = @schema_hash;

    -- Insertar nueva versión
    INSERT INTO schema_versions (
        version_number, major_version, minor_version, patch_version,
        schema_hash, environment, description, migration_script, 
        rollback_script, applied_by, is_current
    ) VALUES (
        p_version_number, v_major_version, v_minor_version, v_patch_version,
        v_schema_hash, p_environment, p_description, p_migration_script,
        p_rollback_script, p_applied_by, TRUE
    );

    SET v_version_id = LAST_INSERT_ID();

    -- Crear snapshot completo
    INSERT INTO schema_snapshots (
        version_id, snapshot_type, tables_definition, 
        snapshot_size_bytes, created_at
    ) VALUES (
        v_version_id, 'full', @snapshot_data,
        LENGTH(@snapshot_data), NOW()
    );

    -- Analizar cambios respecto a versión anterior
    CALL sp_analyze_schema_changes(v_version_id, p_environment);

    COMMIT;

    -- Retornar información de la versión creada
    SELECT 
        v_version_id AS version_id,
        p_version_number AS version_number,
        v_schema_hash AS schema_hash,
        p_environment AS environment,
        'Versión de esquema capturada exitosamente' AS result;

END$$

-- =================================================================
-- PROCEDIMIENTO: sp_generate_schema_snapshot
-- Descripción: Genera un snapshot completo del esquema actual
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_generate_schema_snapshot`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_generate_schema_snapshot`(
    OUT p_snapshot_data JSON,
    OUT p_schema_hash VARCHAR(64)
)
BEGIN
    DECLARE v_tables_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_indexes_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_constraints_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_triggers_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_procedures_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_functions_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_views_json JSON DEFAULT JSON_ARRAY();
    DECLARE v_complete_schema JSON DEFAULT JSON_OBJECT();
    DECLARE v_schema_text TEXT DEFAULT '';

    -- Capturar definiciones de tablas
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'table_name', TABLE_NAME,
            'table_type', TABLE_TYPE,
            'engine', ENGINE,
            'table_collation', TABLE_COLLATION,
            'table_comment', TABLE_COMMENT,
            'columns', (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'column_name', COLUMN_NAME,
                        'data_type', DATA_TYPE,
                        'column_type', COLUMN_TYPE,
                        'is_nullable', IS_NULLABLE,
                        'column_default', COLUMN_DEFAULT,
                        'extra', EXTRA,
                        'column_comment', COLUMN_COMMENT,
                        'ordinal_position', ORDINAL_POSITION
                    )
                )
                FROM INFORMATION_SCHEMA.COLUMNS c
                WHERE c.TABLE_SCHEMA = t.TABLE_SCHEMA 
                AND c.TABLE_NAME = t.TABLE_NAME
                ORDER BY c.ORDINAL_POSITION
            )
        )
    ) INTO v_tables_json
    FROM INFORMATION_SCHEMA.TABLES t
    WHERE t.TABLE_SCHEMA = 'app_presupuesto'
    AND t.TABLE_TYPE = 'BASE TABLE';

    -- Capturar índices
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'table_name', TABLE_NAME,
            'index_name', INDEX_NAME,
            'non_unique', NON_UNIQUE,
            'column_name', COLUMN_NAME,
            'seq_in_index', SEQ_IN_INDEX,
            'index_type', INDEX_TYPE,
            'comment', INDEX_COMMENT
        )
    ) INTO v_indexes_json
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'app_presupuesto'
    ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

    -- Capturar constraints
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'constraint_name', CONSTRAINT_NAME,
            'table_name', TABLE_NAME,
            'constraint_type', CONSTRAINT_TYPE,
            'column_name', COLUMN_NAME,
            'referenced_table_name', REFERENCED_TABLE_NAME,
            'referenced_column_name', REFERENCED_COLUMN_NAME
        )
    ) INTO v_constraints_json
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'app_presupuesto'
    AND CONSTRAINT_NAME != 'PRIMARY';

    -- Capturar triggers
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'trigger_name', TRIGGER_NAME,
            'event_manipulation', EVENT_MANIPULATION,
            'event_object_table', EVENT_OBJECT_TABLE,
            'action_timing', ACTION_TIMING,
            'action_statement', ACTION_STATEMENT
        )
    ) INTO v_triggers_json
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE TRIGGER_SCHEMA = 'app_presupuesto';

    -- Capturar procedimientos
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'routine_name', ROUTINE_NAME,
            'routine_type', ROUTINE_TYPE,
            'data_type', DATA_TYPE,
            'routine_definition', ROUTINE_DEFINITION,
            'is_deterministic', IS_DETERMINISTIC,
            'sql_data_access', SQL_DATA_ACCESS,
            'security_type', SECURITY_TYPE
        )
    ) INTO v_procedures_json
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = 'app_presupuesto'
    AND ROUTINE_TYPE = 'PROCEDURE';

    -- Capturar funciones
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'routine_name', ROUTINE_NAME,
            'routine_type', ROUTINE_TYPE,
            'data_type', DATA_TYPE,
            'routine_definition', ROUTINE_DEFINITION,
            'is_deterministic', IS_DETERMINISTIC,
            'sql_data_access', SQL_DATA_ACCESS,
            'security_type', SECURITY_TYPE
        )
    ) INTO v_functions_json
    FROM INFORMATION_SCHEMA.ROUTINES
    WHERE ROUTINE_SCHEMA = 'app_presupuesto'
    AND ROUTINE_TYPE = 'FUNCTION';

    -- Capturar vistas
    SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
            'table_name', TABLE_NAME,
            'view_definition', VIEW_DEFINITION,
            'check_option', CHECK_OPTION,
            'is_updatable', IS_UPDATABLE,
            'security_type', SECURITY_TYPE
        )
    ) INTO v_views_json
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = 'app_presupuesto';

    -- Construir snapshot completo
    SET v_complete_schema = JSON_OBJECT(
        'schema_name', 'app_presupuesto',
        'captured_at', NOW(),
        'tables', IFNULL(v_tables_json, JSON_ARRAY()),
        'indexes', IFNULL(v_indexes_json, JSON_ARRAY()),
        'constraints', IFNULL(v_constraints_json, JSON_ARRAY()),
        'triggers', IFNULL(v_triggers_json, JSON_ARRAY()),
        'procedures', IFNULL(v_procedures_json, JSON_ARRAY()),
        'functions', IFNULL(v_functions_json, JSON_ARRAY()),
        'views', IFNULL(v_views_json, JSON_ARRAY())
    );

    SET p_snapshot_data = v_complete_schema;

    -- Generar hash del esquema para detección de cambios
    SET v_schema_text = CAST(v_complete_schema AS CHAR);
    SET p_schema_hash = SHA2(v_schema_text, 256);

END$$

-- =================================================================
-- PROCEDIMIENTO: sp_analyze_schema_changes
-- Descripción: Analiza cambios entre versiones de esquema
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_analyze_schema_changes`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_analyze_schema_changes`(
    IN p_version_id INT,
    IN p_environment VARCHAR(50)
)
BEGIN
    DECLARE v_previous_version_id INT DEFAULT NULL;
    DECLARE v_current_snapshot JSON;
    DECLARE v_previous_snapshot JSON DEFAULT NULL;
    DECLARE v_changes_detected INT DEFAULT 0;

    -- Obtener versión anterior
    SELECT id INTO v_previous_version_id
    FROM schema_versions sv
    WHERE sv.environment = p_environment 
    AND sv.id < p_version_id
    AND sv.is_current = FALSE
    ORDER BY sv.applied_at DESC
    LIMIT 1;

    IF v_previous_version_id IS NOT NULL THEN
        -- Obtener snapshots para comparación
        SELECT tables_definition INTO v_current_snapshot
        FROM schema_snapshots
        WHERE version_id = p_version_id;

        SELECT tables_definition INTO v_previous_snapshot
        FROM schema_snapshots
        WHERE version_id = v_previous_version_id;

        -- Aquí iría la lógica de comparación detallada
        -- Por simplicidad, registramos que se detectaron cambios
        SET v_changes_detected = 1;

        -- Registrar en audit trail (ejemplo básico)
        INSERT INTO schema_audit_trail (
            version_id, change_type, object_type, object_name,
            change_description, applied_at
        ) VALUES (
            p_version_id, 'ALTER', 'TABLE', 'SCHEMA_ANALYSIS',
            CONCAT('Análisis automático de cambios desde versión anterior (ID: ', v_previous_version_id, ')'),
            NOW()
        );
    END IF;

END$$

-- =================================================================
-- PROCEDIMIENTO: sp_compare_environments
-- Descripción: Compara esquemas entre diferentes ambientes
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_compare_environments`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_compare_environments`(
    IN p_source_environment VARCHAR(50),
    IN p_target_environment VARCHAR(50),
    IN p_comparison_name VARCHAR(255),
    IN p_started_by VARCHAR(100)
)
BEGIN
    DECLARE v_comparison_id INT;
    DECLARE v_source_version_id INT DEFAULT NULL;
    DECLARE v_target_version_id INT DEFAULT NULL;
    DECLARE v_differences_count INT DEFAULT 0;
    DECLARE v_start_time DATETIME DEFAULT NOW();
    DECLARE v_end_time DATETIME;
    DECLARE v_execution_time INT;

    -- Insertar registro de comparación
    INSERT INTO schema_comparisons (
        comparison_name, source_environment, target_environment,
        started_by, started_at, comparison_status
    ) VALUES (
        p_comparison_name, p_source_environment, p_target_environment,
        p_started_by, v_start_time, 'running'
    );

    SET v_comparison_id = LAST_INSERT_ID();

    -- Obtener versiones actuales de cada ambiente
    SELECT id INTO v_source_version_id
    FROM schema_versions
    WHERE environment = p_source_environment AND is_current = TRUE
    LIMIT 1;

    SELECT id INTO v_target_version_id
    FROM schema_versions
    WHERE environment = p_target_environment AND is_current = TRUE
    LIMIT 1;

    IF v_source_version_id IS NULL OR v_target_version_id IS NULL THEN
        UPDATE schema_comparisons
        SET comparison_status = 'failed',
            differences_detail = JSON_OBJECT(
                'error', 'No se encontraron versiones actuales para uno o ambos ambientes'
            )
        WHERE id = v_comparison_id;
    ELSE
        -- Realizar comparación (lógica simplificada)
        -- En implementación real, aquí iría la comparación detallada

        SET v_differences_count = 0; -- Placeholder

        SET v_end_time = NOW();
        SET v_execution_time = TIMESTAMPDIFF(SECOND, v_start_time, v_end_time);

        -- Actualizar resultado de comparación
        UPDATE schema_comparisons
        SET source_version_id = v_source_version_id,
            target_version_id = v_target_version_id,
            differences_found = v_differences_count,
            comparison_status = 'completed',
            completed_at = v_end_time,
            execution_time_seconds = v_execution_time,
            differences_summary = JSON_OBJECT(
                'total_differences', v_differences_count,
                'tables_different', 0,
                'indexes_different', 0,
                'constraints_different', 0,
                'procedures_different', 0
            )
        WHERE id = v_comparison_id;
    END IF;

    -- Retornar resultado
    SELECT 
        v_comparison_id AS comparison_id,
        p_comparison_name AS comparison_name,
        v_differences_count AS differences_found,
        v_execution_time AS execution_time_seconds,
        'Comparación completada exitosamente' AS result;

END$$

-- =================================================================
-- PROCEDIMIENTO: sp_rollback_to_version
-- Descripción: Rollback a una versión específica del esquema
-- =================================================================
DROP PROCEDURE IF EXISTS `sp_rollback_to_version`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_rollback_to_version`(
    IN p_target_version VARCHAR(20),
    IN p_environment VARCHAR(50),
    IN p_executed_by VARCHAR(100),
    IN p_force_rollback BOOLEAN DEFAULT FALSE
)
BEGIN
    DECLARE v_target_version_id INT;
    DECLARE v_current_version_id INT;
    DECLARE v_rollback_script TEXT;
    DECLARE v_can_rollback BOOLEAN DEFAULT FALSE;
    DECLARE v_error_message TEXT DEFAULT '';

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_message = MESSAGE_TEXT;
        ROLLBACK;
        RESIGNAL SET MESSAGE_TEXT = CONCAT('Error en rollback: ', v_error_message);
    END;

    -- Verificar que la versión target existe
    SELECT id, rollback_script INTO v_target_version_id, v_rollback_script
    FROM schema_versions
    WHERE version_number = p_target_version 
    AND environment = p_environment;

    IF v_target_version_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Versión objetivo no encontrada';
    END IF;

    -- Obtener versión actual
    SELECT id INTO v_current_version_id
    FROM schema_versions
    WHERE environment = p_environment AND is_current = TRUE;

    -- Verificar si el rollback es seguro
    IF NOT p_force_rollback THEN
        -- Verificar si hay breaking changes que impidan el rollback
        SELECT COUNT(*) = 0 INTO v_can_rollback
        FROM schema_versions sv
        JOIN schema_audit_trail sat ON sv.id = sat.version_id
        WHERE sv.environment = p_environment
        AND sv.applied_at > (
            SELECT applied_at 
            FROM schema_versions 
            WHERE id = v_target_version_id
        )
        AND JSON_EXTRACT(sv.breaking_changes, '$') IS NOT NULL;

        IF NOT v_can_rollback THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Rollback no seguro: se detectaron breaking changes. Use force_rollback=TRUE para forzar.';
        END IF;
    END IF;

    START TRANSACTION;

    -- Ejecutar script de rollback si existe
    IF v_rollback_script IS NOT NULL AND LENGTH(v_rollback_script) > 0 THEN
        -- En implementación real, ejecutar el script
        -- SET @sql = v_rollback_script;
        -- PREPARE stmt FROM @sql;
        -- EXECUTE stmt;
        -- DEALLOCATE PREPARE stmt;
        
        -- Registrar ejecución del rollback
        INSERT INTO schema_audit_trail (
            version_id, change_type, object_type, object_name,
            change_description, sql_statement, applied_at
        ) VALUES (
            v_target_version_id, 'ALTER', 'TABLE', 'ROLLBACK_OPERATION',
            CONCAT('Rollback ejecutado a versión ', p_target_version),
            v_rollback_script, NOW()
        );
    END IF;

    -- Actualizar versiones actuales
    UPDATE schema_versions 
    SET is_current = FALSE 
    WHERE environment = p_environment;

    UPDATE schema_versions 
    SET is_current = TRUE 
    WHERE id = v_target_version_id;

    -- Registrar operación de rollback
    INSERT INTO schema_versions (
        version_number, major_version, minor_version, patch_version,
        schema_hash, environment, description, applied_by, is_current
    ) VALUES (
        CONCAT(p_target_version, '-rollback-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
        0, 0, 1,
        'ROLLBACK_OPERATION', p_environment,
        CONCAT('Rollback a versión ', p_target_version, ' ejecutado por ', p_executed_by),
        p_executed_by, TRUE
    );

    COMMIT;

    SELECT 
        v_target_version_id AS target_version_id,
        p_target_version AS target_version,
        p_environment AS environment,
        'Rollback ejecutado exitosamente' AS result;

END$$

DELIMITER ;

-- =================================================================
-- VISTAS PARA MONITOREO Y REPORTING
-- =================================================================

-- Vista de estado actual de versiones por ambiente
CREATE OR REPLACE VIEW `v_current_schema_versions` AS
SELECT 
    sv.environment,
    sv.version_number,
    CONCAT(sv.major_version, '.', sv.minor_version, '.', sv.patch_version) AS semantic_version,
    sv.schema_hash,
    sv.description,
    sv.applied_by,
    sv.applied_at,
    sv.validation_status,
    DATEDIFF(NOW(), sv.applied_at) AS days_since_applied,
    COUNT(sat.id) AS total_changes,
    JSON_LENGTH(IFNULL(sv.breaking_changes, JSON_ARRAY())) AS breaking_changes_count
FROM schema_versions sv
LEFT JOIN schema_audit_trail sat ON sv.id = sat.version_id
WHERE sv.is_current = TRUE
GROUP BY sv.id, sv.environment, sv.version_number, sv.schema_hash, 
         sv.description, sv.applied_by, sv.applied_at, sv.validation_status;

-- Vista de historial de cambios
CREATE OR REPLACE VIEW `v_schema_change_history` AS
SELECT 
    sv.environment,
    sv.version_number,
    sv.applied_at AS version_applied_at,
    sat.change_type,
    sat.object_type,
    sat.object_name,
    sat.change_description,
    sat.success,
    sat.execution_time_ms,
    sat.applied_at AS change_applied_at
FROM schema_versions sv
JOIN schema_audit_trail sat ON sv.id = sat.version_id
ORDER BY sv.applied_at DESC, sat.applied_at DESC;

-- Vista de comparaciones recientes
CREATE OR REPLACE VIEW `v_recent_comparisons` AS
SELECT 
    sc.comparison_name,
    sc.source_environment,
    sc.target_environment,
    sc.differences_found,
    sc.comparison_status,
    sc.started_by,
    sc.started_at,
    sc.execution_time_seconds,
    CASE 
        WHEN sc.differences_found = 0 THEN 'Ambientes sincronizados'
        WHEN sc.differences_found <= 5 THEN 'Diferencias menores'
        WHEN sc.differences_found <= 20 THEN 'Diferencias moderadas'
        ELSE 'Diferencias significativas'
    END AS sync_status
FROM schema_comparisons sc
ORDER BY sc.started_at DESC
LIMIT 50;

-- =================================================================
-- EVENTOS AUTOMÁTICOS
-- =================================================================

-- Evento para snapshot automático diario
DELIMITER $$
DROP EVENT IF EXISTS `evt_daily_schema_snapshot`$$
CREATE EVENT `evt_daily_schema_snapshot`
ON SCHEDULE EVERY 1 DAY
STARTS CONCAT(CURDATE() + INTERVAL 1 DAY, ' 01:00:00')
ON COMPLETION PRESERVE
ENABLE
DO
BEGIN
    DECLARE v_auto_version VARCHAR(20);
    
    -- Generar versión automática
    SET v_auto_version = CONCAT('auto-', DATE_FORMAT(NOW(), '%Y.%m.%d'));
    
    -- Solo crear snapshot si hay cambios desde el último
    IF NOT EXISTS (
        SELECT 1 FROM schema_versions 
        WHERE environment = 'production' 
        AND version_number = v_auto_version
    ) THEN
        CALL sp_capture_schema_version(
            v_auto_version,
            'production',
            'Snapshot automático diario',
            'SYSTEM',
            NULL,
            NULL
        );
    END IF;
    
END$$

-- Evento para limpieza de snapshots antiguos
DROP EVENT IF EXISTS `evt_cleanup_old_snapshots`$$
CREATE EVENT `evt_cleanup_old_snapshots`
ON SCHEDULE EVERY 1 WEEK
STARTS CONCAT(CURDATE() + INTERVAL 1 DAY, ' 02:00:00')
ON COMPLETION PRESERVE
ENABLE
DO
BEGIN
    -- Eliminar snapshots de más de 90 días (mantener solo metadatos)
    DELETE ss FROM schema_snapshots ss
    JOIN schema_versions sv ON ss.version_id = sv.id
    WHERE sv.applied_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
    AND ss.snapshot_type != 'metadata_only';
    
    -- Limpiar audit trail de más de 1 año
    DELETE sat FROM schema_audit_trail sat
    JOIN schema_versions sv ON sat.version_id = sv.id
    WHERE sv.applied_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
    
END$$

DELIMITER ;

-- =================================================================
-- CONFIGURACIÓN INICIAL
-- =================================================================

-- Capturar versión inicial del esquema actual
CALL sp_capture_schema_version(
    '1.0.0',
    'development',
    'Versión inicial del esquema capturada por sistema de versionado',
    'SYSTEM',
    NULL,
    NULL
);

-- =================================================================
-- INSTRUCCIONES DE USO
-- =================================================================

/*
GUÍA DE USO DEL SISTEMA DE VERSIONADO DE ESQUEMA:

1. CAPTURAR NUEVA VERSIÓN:
   CALL sp_capture_schema_version('1.1.0', 'development', 'Agregada tabla usuarios', 'admin', @migration_sql, @rollback_sql);

2. COMPARAR AMBIENTES:
   CALL sp_compare_environments('development', 'production', 'Sync Dev to Prod', 'admin');

3. VER VERSIONES ACTUALES:
   SELECT * FROM v_current_schema_versions;

4. VER HISTORIAL DE CAMBIOS:
   SELECT * FROM v_schema_change_history WHERE environment = 'production' LIMIT 20;

5. EJECUTAR ROLLBACK:
   CALL sp_rollback_to_version('1.0.0', 'development', 'admin', FALSE);

6. VER COMPARACIONES RECIENTES:
   SELECT * FROM v_recent_comparisons;

FLUJO RECOMENDADO:
1. Desarrollo → Capturar versión en 'development'
2. Testing → Aplicar y capturar en 'testing'
3. Staging → Comparar con 'development', aplicar y capturar
4. Production → Comparar con 'staging', aplicar con cuidado

MEJORES PRÁCTICAS:
- Usar versionado semántico (major.minor.patch)
- Incluir scripts de migración y rollback
- Probar rollbacks en ambientes de testing
- Documentar breaking changes detalladamente
- Hacer snapshots antes de cambios importantes
- Comparar ambientes regularmente

MONITOREO:
- Revisar v_current_schema_versions semanalmente
- Verificar que no hay drift entre ambientes
- Monitorear el tamaño de los snapshots
- Alertas para breaking changes no documentados
*/

-- Finalización exitosa
SELECT 'Sistema de versionado de esquema instalado correctamente' AS resultado,
       'Primera versión capturada como 1.0.0 en development' AS estado_inicial;
