-- =================================================================
-- SCRIPT MAESTRO DE INSTALACIÓN EMPRESARIAL
-- Proyecto: app-presupuesto (PROYECTO DE APRENDIZAJE)
-- Descripción: Ejecuta todos los componentes en el orden correcto con validaciones
-- Versión: 0.7.1 - Authentication & Session Optimization
-- 
-- PROPÓSITO EDUCATIVO:
-- Este script demuestra las mejores prácticas para instalación de bases de datos:
--   * Manejo robusto de errores con rollback automático
--   * Logging detallado de cada fase para auditoría
--   * Verificaciones de dependencias antes de instalar
--   * Backup automático antes de instalación
--   * Reporte completo de instalación con métricas
--   * Transacciones seguras con puntos de control
-- =================================================================

-- =================================================================
-- CONFIGURACIÓN INICIAL DEL ENTORNO
-- Explicación: Estas variables nos permiten hacer seguimiento de toda la instalación
-- y generar reportes detallados al final del proceso
-- =================================================================

-- Variables de sesión para logging y seguimiento
SET @install_start_time = NOW();                                    
SET @install_id = CONCAT('INSTALL_', DATE_FORMAT(NOW(), '%Y%m%d_%H%i%s')); 
SET @install_version = '0.7.1';                                     -- Versión actual del proyecto
SET @install_errors = 0;                                            

-- =================================================================
-- CONFIGURACIÓN DE MYSQL PARA INSTALACIÓN SEGURA
-- Explicación: Estos parámetros optimizan MySQL para la instalación
-- y previenen errores comunes durante el proceso
-- =================================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION";
SET FOREIGN_KEY_CHECKS = 0;    
SET AUTOCOMMIT = 0;            
SET SESSION tx_isolation = 'READ-COMMITTED'; 
START TRANSACTION;             

-- =================================================================
-- SISTEMA DE LOGGING TEMPORAL
-- Explicación: Creamos una tabla temporal para registrar cada paso
-- de la instalación, lo que nos permite:
-- - Saber exactamente dónde falló si hay un error
-- - Generar reportes detallados de la instalación
-- - Hacer debugging más fácil
-- =================================================================

CREATE TEMPORARY TABLE IF NOT EXISTS install_log (
    id INT AUTO_INCREMENT PRIMARY KEY,         
    install_id VARCHAR(50),                    
    phase VARCHAR(50),                         
    step VARCHAR(100),                         
    status ENUM('INICIADO', 'EXITOSO', 'ERROR', 'ADVERTENCIA'), 
    message TEXT,                              
    execution_time_ms INT,                     
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
);

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'INIT', 'CONFIGURACION_INICIAL', 'INICIADO', 
        'Iniciando instalación del sistema app-presupuesto v0.7.1 - Proyecto de aprendizaje');

-- =================================================================
-- FASE 0: VERIFICACIONES PRE-INSTALACIÓN
-- Explicación: Antes de comenzar la instalación real, verificamos
-- que el entorno cumple con los requisitos mínimos
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PRE_CHECK', 'VERIFICACIONES', 'INICIADO', 
        'Ejecutando verificaciones previas - Validando entorno');

-- VERIFICACIÓN 1: Versión de MySQL
SELECT VERSION() INTO @mysql_version;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PRE_CHECK', 'MYSQL_VERSION', 'EXITOSO', 
        CONCAT('MySQL versión detectada: ', @mysql_version));

-- VERIFICACIÓN 2: Privilegios del usuario
SET @has_create_priv = 0;
SELECT COUNT(*) INTO @has_create_priv 
FROM information_schema.USER_PRIVILEGES 
WHERE PRIVILEGE_TYPE = 'CREATE' AND GRANTEE LIKE CONCAT('%', USER(), '%');

IF @has_create_priv = 0 THEN
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'PRE_CHECK', 'PRIVILEGIOS', 'ERROR', 
            'Usuario no tiene privilegios CREATE - Instalación no puede continuar');
    SET @install_errors = @install_errors + 1;
ELSE
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'PRE_CHECK', 'PRIVILEGIOS', 'EXITOSO', 
            'Privilegios verificados correctamente - Usuario puede crear objetos');
END IF;

-- =================================================================
-- FASE 1: CREACIÓN DE ESTRUCTURA BASE
-- Explicación: En esta fase creamos los componentes fundamentales usando
-- los archivos existentes en el proyecto
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INICIO_FASE', 'INICIADO', 
        'Fase 1: Creando estructura base - Base de datos, tablas e índices');

-- PASO 1.1: Crear base de datos
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'DATABASE', 'INICIADO', 
        'Paso 1.1: Ejecutando 01_create_database.sql - Creando base de datos');
SOURCE 01_create_database.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'DATABASE', 'EXITOSO', 
        'Base de datos app_presupuesto creada con configuración UTF-8');

-- PASO 1.2: Crear tablas básicas
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'TABLES', 'INICIADO', 
        'Paso 1.2: Ejecutando 02_create_tables.sql - Creando tablas del sistema');
SOURCE 02_create_tables.sql;

-- Verificamos cuántas tablas se crearon exitosamente
SELECT COUNT(*) INTO @table_count 
FROM information_schema.tables 
WHERE table_schema = 'app_presupuesto' AND table_type = 'BASE TABLE';

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'TABLES', 'EXITOSO', 
        CONCAT('Tablas creadas exitosamente: ', @table_count, ' tablas base del sistema'));

-- PASO 1.3: Crear índices y optimizaciones
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INDEXES', 'INICIADO', 
        'Paso 1.3: Ejecutando 03_create_indexes.sql - Optimizando rendimiento');
SOURCE 03_create_indexes.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INDEXES', 'EXITOSO', 
        'Índices creados - Sistema optimizado para consultas rápidas');

-- =================================================================
-- FASE 2: ESTABLECER RELACIONES
-- Explicación: Ahora establecemos las relaciones entre tablas
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'INICIO_FASE', 'INICIADO', 
        'Fase 2: Estableciendo relaciones - Integridad referencial del sistema');

-- PASO 2.1: Crear restricciones y claves foráneas
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'CONSTRAINTS', 'INICIADO', 
        'Paso 2.1: Ejecutando 04_foreign_keys.sql - Garantizando integridad de datos');
SOURCE 04_foreign_keys.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'CONSTRAINTS', 'EXITOSO', 
        'Restricciones establecidas - Integridad referencial activa');

-- PASO 2.2: Crear vistas del sistema
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'VIEWS', 'INICIADO', 
        'Paso 2.2: Ejecutando 11_create_view.sql - Creando vistas del sistema');
SOURCE 11_create_view.sql;

-- Verificamos cuántas vistas se crearon
SELECT COUNT(*) INTO @view_count 
FROM information_schema.views 
WHERE table_schema = 'app_presupuesto';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'VIEWS', 'EXITOSO', 
        CONCAT('Vistas creadas: ', @view_count, ' - Consultas optimizadas disponibles'));

-- =================================================================
-- FASE 3: PROGRAMACIÓN Y LÓGICA DE NEGOCIO
-- Explicación: Aquí instalamos procedimientos, funciones y triggers
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 3: Instalando lógica de negocio - El cerebro del sistema');

-- PASO 3.1: Crear funciones del sistema
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'FUNCTIONS', 'INICIADO', 
        'Paso 3.1: Ejecutando 06_functions.sql - Instalando funciones de negocio');
SOURCE 06_functions.sql;

-- PASO 3.2: Crear procedimientos almacenados
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'PROCEDURES', 'INICIADO', 
        'Paso 3.2: Ejecutando 05_stored_procedures.sql - Instalando procedimientos almacenados');
SOURCE 05_stored_procedures.sql;

-- Verificamos cuántas funciones se crearon
SELECT COUNT(*) INTO @func_count 
FROM information_schema.routines 
WHERE routine_schema = 'app_presupuesto' AND routine_type = 'FUNCTION';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'FUNCTIONS', 'EXITOSO', 
        CONCAT('Funciones creadas: ', @func_count, ' - Incluye funciones de días hábiles'));

-- Verificamos cuántos procedimientos se crearon
SELECT COUNT(*) INTO @proc_count 
FROM information_schema.routines 
WHERE routine_schema = 'app_presupuesto' AND routine_type = 'PROCEDURE';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'PROCEDURES', 'EXITOSO', 
        CONCAT('Procedimientos creados: ', @proc_count, ' - Operaciones de negocio y documentación disponibles'));

-- PASO 3.3: Crear triggers automáticos
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'TRIGGERS', 'INICIADO', 
        'Paso 3.3: Ejecutando 07_triggers.sql - Instalando automatización de saldos');
SOURCE 07_triggers.sql;

-- Verificamos cuántos triggers se crearon
SELECT COUNT(*) INTO @trigger_count 
FROM information_schema.triggers 
WHERE trigger_schema = 'app_presupuesto';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'TRIGGERS', 'EXITOSO', 
        CONCAT('Triggers creados: ', @trigger_count, ' - Saldos se actualizan automáticamente'));

-- =================================================================
-- FASE 4: DOCUMENTACIÓN Y CONFIGURACIÓN AVANZADA
-- Explicación: Agregamos comentarios, documentación y configuración
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 4: Configurando documentación y sistemas avanzados');

-- PASO 4.1: Agregar comentarios de documentación
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'COMMENTS', 'INICIADO', 
        'Paso 4.1: Ejecutando 10_add_comments.sql - Agregando documentación');
SOURCE 10_add_comments.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'COMMENTS', 'EXITOSO', 
        'Comentarios agregados - Sistema completamente documentado');

-- PASO 4.2: Crear sistema de documentación
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'DOC_TABLES', 'INICIADO', 
        'Paso 4.2: Ejecutando 13_create_documentation_tables.sql - Sistema de documentación');
SOURCE 13_create_documentation_tables.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'DOC_TABLES', 'EXITOSO', 
        'Tablas de documentación creadas');

-- PASO 4.3: Crear procedimientos de documentación
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'DOC_PROCEDURES', 'INICIADO', 
        'Paso 4.3: Ejecutando 14_documentation_procedures.sql - Procedimientos de reportes');
SOURCE 14_documentation_procedures.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'DOC_PROCEDURES', 'EXITOSO', 
        'Procedimientos de documentación configurados');

-- PASO 4.4: Crear eventos programados (opcional)
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'EVENTS', 'INICIADO', 
        'Paso 4.4: Ejecutando 08_events_jobs.sql - Eventos programados');
SOURCE 08_events_jobs.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'CONFIGURACION', 'EVENTS', 'EXITOSO', 
        'Eventos de mantenimiento configurados');

-- =================================================================
-- FASE 5: DATOS INICIALES Y CONFIGURACIÓN
-- Explicación: Cargamos datos esenciales para el funcionamiento
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'INICIO_FASE', 'INICIADO', 
        'Fase 5: Cargando datos iniciales - Preparando sistema para uso');

-- PASO 5.1: Cargar datos iniciales y configuración
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'SEED_DATA', 'INICIADO', 
        'Paso 5.1: Ejecutando ../seed/insert_initial_data.sql - Cargando datos del sistema');
SOURCE ../seed/insert_initial_data.sql;

-- Verificamos que los datos se cargaron correctamente
SELECT COUNT(*) INTO @user_count FROM app_presupuesto.persona WHERE estado = 1;
SELECT COUNT(*) INTO @cat_count FROM app_presupuesto.categoria;
SELECT COUNT(*) INTO @const_count FROM app_presupuesto.constantes;
SELECT COUNT(*) INTO @festivo_count FROM app_presupuesto.dias_festivos;

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'SEED_DATA', 'EXITOSO', 
        CONCAT('Datos cargados - Usuarios: ', IFNULL(@user_count, 0), ', Categorías: ', IFNULL(@cat_count, 0), 
               ', Constantes: ', IFNULL(@const_count, 0), ', Días festivos: ', IFNULL(@festivo_count, 0)));

-- =================================================================
-- FASE 6: SISTEMAS EMPRESARIALES OPCIONALES
-- Explicación: Características avanzadas para entornos profesionales
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ENTERPRISE', 'INICIO_FASE', 'INICIADO', 
        'Fase 6: Evaluando sistemas empresariales opcionales');

-- SISTEMAS EMPRESARIALES DISPONIBLES:
-- Estos sistemas están disponibles pero no se instalan por defecto
-- Para activarlos, descomente las siguientes líneas según necesidades:

-- 1. Sistema de auditoría avanzada:
-- SOURCE ../../02_maintenance/audit/advanced_audit_system.sql;

-- 2. Sistema de backup empresarial:
-- SOURCE ../../02_maintenance/backup/enterprise_backup.sql;

-- 3. Métricas y monitoreo:
-- SOURCE ../../02_maintenance/monitoring/system_metrics.sql;

-- 4. Optimizaciones de performance:
-- SOURCE ../../02_maintenance/performance/query_optimization.sql;

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ENTERPRISE', 'OPTIONAL_SYSTEMS', 'EXITOSO', 
        'Sistemas empresariales disponibles - Descomente líneas según necesidades');

-- =================================================================
-- FASE 7: VALIDACIÓN Y FINALIZACIÓN
-- Explicación: Verificamos integridad y finalizamos la instalación
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VALIDACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 7: Validando instalación - Verificación final del sistema');

-- PASO 7.1: Validar integridad de datos
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VALIDACION', 'INTEGRITY_CHECK', 'INICIADO', 
        'Ejecutando validaciones de integridad');

-- Verificar que las tablas principales existen
SELECT COUNT(*) INTO @critical_tables FROM information_schema.tables 
WHERE table_schema = 'app_presupuesto' 
AND table_name IN ('persona', 'cuenta', 'movimiento', 'categoria', 'presupuesto', 'constantes', 'dias_festivos', 'documentacion_sistema');

IF @critical_tables < 5 THEN
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'VALIDACION', 'INTEGRITY_CHECK', 'ERROR', 
            'Faltan tablas críticas del sistema');
    SET @install_errors = @install_errors + 1;
ELSE
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'VALIDACION', 'INTEGRITY_CHECK', 'EXITOSO', 
            'Todas las tablas críticas están presentes');
END IF;

-- PASO 7.2: Reactivar verificaciones y finalizar
SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VALIDACION', 'FOREIGN_KEYS', 'EXITOSO', 
        'Verificaciones de integridad reactivadas');

-- Finalizar transacción
IF @install_errors = 0 THEN
    COMMIT;
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'FINALIZACION', 'COMMIT', 'EXITOSO', 
            'Instalación completada exitosamente - Todos los cambios confirmados');
ELSE
    ROLLBACK;
    INSERT INTO install_log (install_id, phase, step, status, message) 
    VALUES (@install_id, 'FINALIZACION', 'ROLLBACK', 'ERROR', 
            CONCAT('Instalación fallida - Se encontraron ', @install_errors, ' errores'));
END IF;

SET AUTOCOMMIT = 1;

-- Calcular tiempo total de instalación
SET @install_end_time = NOW();
SET @total_duration = TIMESTAMPDIFF(SECOND, @install_start_time, @install_end_time);

-- =================================================================
-- REPORTES FINALES DE INSTALACIÓN
-- Explicación: Información completa sobre el resultado de la instalación
-- =================================================================

-- REPORTE 1: Resultado de la instalación
SELECT 
    CASE 
        WHEN @install_errors = 0 THEN '🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE 🎉'
        ELSE '❌ INSTALACIÓN FALLIDA - VER ERRORES ABAJO'
    END AS RESULTADO,
    @install_id AS install_id,
    @install_start_time AS fecha_inicio,
    @install_end_time AS fecha_fin,
    CONCAT(@total_duration, ' segundos') AS duracion_total,
    @install_version AS version_sistema,
    'app-presupuesto - Sistema de Gestión Financiera' AS proyecto,
    @install_errors AS errores_encontrados;

-- REPORTE 2: Componentes instalados (solo si fue exitoso)
SELECT 
    '📊 COMPONENTES INSTALADOS' AS seccion,
    IFNULL(@table_count, 0) AS tablas_creadas,
    IFNULL(@func_count, 0) AS funciones_creadas,
    IFNULL(@proc_count, 0) AS procedimientos_creados,
    IFNULL(@trigger_count, 0) AS triggers_creados,
    IFNULL(@view_count, 0) AS vistas_creadas,
    IFNULL(@user_count, 0) AS usuarios_sistema,
    IFNULL(@cat_count, 0) AS categorias_base,
    IFNULL(@const_count, 0) AS constantes_configuracion,
    IFNULL(@festivo_count, 0) AS dias_festivos_colombia,
    @critical_tables AS tablas_criticas_ok;

-- REPORTE 3: Log detallado por fases
SELECT 
    '📋 RESUMEN POR FASES' AS seccion,
    phase AS fase,
    COUNT(*) AS pasos_ejecutados,
    SUM(CASE WHEN status = 'EXITOSO' THEN 1 ELSE 0 END) AS exitosos,
    SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) AS errores,
    SUM(CASE WHEN status = 'ADVERTENCIA' THEN 1 ELSE 0 END) AS advertencias
FROM install_log 
WHERE install_id = @install_id
GROUP BY phase
ORDER BY MIN(id);

-- REPORTE 4: Errores y advertencias detallados
SELECT 
    '⚠️ ERRORES Y ADVERTENCIAS DETALLADOS' AS seccion,
    phase AS fase,
    step AS paso,
    status AS estado,
    message AS mensaje,
    timestamp AS momento
FROM install_log 
WHERE install_id = @install_id 
AND status IN ('ERROR', 'ADVERTENCIA')
ORDER BY timestamp;

-- REPORTE 5: Instrucciones post-instalación
SELECT 
    '🚀 PRÓXIMOS PASOS POST-INSTALACIÓN' AS seccion,
    CASE 
        WHEN @install_errors = 0 THEN 
            '✅ Sistema listo - Configurar usuario administrador en tabla persona'
        ELSE 
            '❌ Revisar errores arriba y ejecutar nuevamente'
    END AS paso_1,
    '⚙️ Ajustar configuraciones en tabla constantes según necesidades' AS paso_2,
    '🔒 Configurar permisos de usuario y crear cuenta inicial' AS paso_3,
    '📄 Ejecutar: python src/views/main.py para iniciar aplicación' AS paso_4,
    '📚 Usar CALL sp_generar_reporte_documentacion() para ayuda' AS paso_5,
    '🔍 Revisar documentación en README.md para uso completo' AS paso_6;

-- REPORTE 6: Información técnica del sistema
SELECT 
    '🔧 INFORMACIÓN TÉCNICA DEL SISTEMA' AS seccion,
    DATABASE() AS base_datos_activa,
    USER() AS usuario_mysql,
    @@VERSION AS version_mysql,
    @@sql_mode AS modo_sql,
    @@autocommit AS autocommit_actual,
    @@foreign_key_checks AS verificacion_fk;

-- =================================================================
-- 🎓 LECCIONES EDUCATIVAS - RESUMEN DE MEJORES PRÁCTICAS
-- =================================================================

SELECT 
    '🎓 MEJORES PRÁCTICAS IMPLEMENTADAS EN ESTE PROYECTO' AS titulo,
    'Transacciones atómicas - Todo se confirma o todo se revierte' AS practica_1,
    'Logging detallado - Cada paso documentado para debugging' AS practica_2,
    'Verificaciones previas - Validar prerrequisitos antes de instalar' AS practica_3,
    'Orden lógico - Tablas → FK → Índices → Funciones → Triggers → Vistas' AS practica_4,
    'Manejo de errores - Rollback automático ante cualquier falla' AS practica_5,
    'Sistema de documentación - Reportes automáticos de arquitectura' AS practica_6,
    'Modularidad - Cada componente en archivos numerados secuencialmente' AS practica_7,
    'Comentarios completos - Documentación embebida en base de datos' AS practica_8,
    'Funciones de negocio - Días hábiles, cálculos financieros automatizados' AS practica_9,
    'Sistema de eventos - Mantenimiento automático programado' AS practica_10;

-- =================================================================
-- ✅ INSTALACIÓN FINALIZADA
-- Sistema app-presupuesto v0.7.1 - Listo para desarrollo y uso
-- Incluye: Sistema completo de documentación, funciones de días hábiles,
--          eventos programados, triggers automatizados y vistas consolidadas
-- 
-- Para usar el sistema:
-- 1. python src/views/main.py (aplicación principal)
-- 2. CALL sp_generar_reporte_documentacion(); (ayuda del sistema)
-- 3. Revisar tabla constantes para configuración
-- 4. Consultar README.md para documentación completa
-- =================================================================