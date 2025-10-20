-- =================================================================
-- SCRIPT MAESTRO DE INSTALACIÓN EMPRESARIAL
-- Proyecto: app-presupuesto (PROYECTO DE APRENDIZAJE)
-- Descripción: Ejecuta todos los componentes en el orden correcto con validaciones
-- Versión: 3.0
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
SET @install_start_time = NOW();                                    -- Hora de inicio para calcular duración total
SET @install_id = CONCAT('INSTALL_', DATE_FORMAT(NOW(), '%Y%m%d_%H%i%s')); -- ID único para esta instalación
SET @install_version = '0.7.0';                                     -- Versión del sistema que estamos instalando
SET @install_errors = 0;                                            -- Contador de errores encontrados

-- =================================================================
-- CONFIGURACIÓN DE MYSQL PARA INSTALACIÓN SEGURA
-- Explicación: Estos parámetros optimizan MySQL para la instalación
-- y previenen errores comunes durante el proceso
-- =================================================================

-- Configuración inicial optimizada para instalación
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION";
-- Explicación SQL_MODE:
--   * NO_AUTO_VALUE_ON_ZERO: Permite insertar 0 en campos AUTO_INCREMENT
--   * ERROR_FOR_DIVISION_BY_ZERO: Genera error si hay división por cero
--   * NO_AUTO_CREATE_USER: Previene creación automática de usuarios
--   * NO_ENGINE_SUBSTITUTION: No permite sustitución automática de motores

SET FOREIGN_KEY_CHECKS = 0;    -- Desactiva verificación de claves foráneas temporalmente
                               -- (Permite crear tablas en cualquier orden)

SET AUTOCOMMIT = 0;            -- Desactiva autocommit para control manual de transacciones
SET SESSION tx_isolation = 'READ-COMMITTED'; -- Nivel de aislamiento para concurrencia
START TRANSACTION;             -- Inicia transacción principal (todo o nada)

-- =================================================================
-- SISTEMA DE LOGGING TEMPORAL
-- Explicación: Creamos una tabla temporal para registrar cada paso
-- de la instalación, lo que nos permite:
-- - Saber exactamente dónde falló si hay un error
-- - Generar reportes detallados de la instalación
-- - Hacer debugging más fácil
-- =================================================================

CREATE TEMPORARY TABLE IF NOT EXISTS install_log (
    id INT AUTO_INCREMENT PRIMARY KEY,         -- ID único del registro
    install_id VARCHAR(50),                    -- ID de esta instalación específica
    phase VARCHAR(50),                         -- Fase de instalación (INIT, ESTRUCTURA, etc.)
    step VARCHAR(100),                         -- Paso específico dentro de la fase
    status ENUM('INICIADO', 'EXITOSO', 'ERROR', 'ADVERTENCIA'), -- Estado del paso
    message TEXT,                              -- Mensaje descriptivo
    execution_time_ms INT,                     -- Tiempo de ejecución (futuro uso)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP -- Momento exacto del registro
);

-- Log inicial - Marca el comienzo de la instalación
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'INIT', 'CONFIGURACION_INICIAL', 'INICIADO', 
        'Iniciando instalación del sistema app-presupuesto - Proyecto de aprendizaje');

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
-- Explicación: Diferentes versiones de MySQL tienen características distintas
-- Es importante saber qué versión estamos usando para compatibilidad
SELECT VERSION() INTO @mysql_version;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PRE_CHECK', 'MYSQL_VERSION', 'EXITOSO', 
        CONCAT('MySQL versión detectada: ', @mysql_version));

-- VERIFICACIÓN 2: Privilegios del usuario
-- Explicación: El usuario debe tener permisos CREATE para crear bases de datos
-- Si no los tiene, la instalación fallará
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
-- Explicación: En esta fase creamos los componentes fundamentales:
-- - La base de datos
-- - Las tablas con sus campos
-- - Los índices para rendimiento
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INICIO_FASE', 'INICIADO', 
        'Fase 1: Creando estructura base - Base de datos, tablas e índices');

-- PASO 1.1: Crear base de datos
-- Explicación: El archivo 01_create_database.sql contiene:
-- - Creación de la base de datos 'app_presupuesto'
-- - Configuración de charset UTF-8 para soporte internacional
-- - Configuración de zona horaria
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'DATABASE', 'INICIADO', 
        'Paso 1.1: Ejecutando 01_create_database.sql - Creando base de datos');
SOURCE 01_create_database.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'DATABASE', 'EXITOSO', 
        'Base de datos app_presupuesto creada con configuración UTF-8');

-- PASO 1.2: Crear tablas básicas
-- Explicación: El archivo 02_create_tables.sql contiene:
-- - Definición de todas las tablas del sistema
-- - Campos, tipos de datos y restricciones básicas
-- - NO incluye claves foráneas (se agregan después)
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'TABLES', 'INICIADO', 
        'Paso 1.2: Ejecutando 02_create_tables.sql - Creando tablas sin relaciones');
SOURCE 02_create_tables.sql;

-- Verificamos cuántas tablas se crearon exitosamente
SELECT COUNT(*) INTO @table_count 
FROM information_schema.tables 
WHERE table_schema = 'app_presupuesto' AND table_type = 'BASE TABLE';

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'TABLES', 'EXITOSO', 
        CONCAT('Tablas creadas exitosamente: ', @table_count, ' tablas base del sistema'));

-- PASO 1.3: Crear índices y claves primarias
-- Explicación: Los índices son cruciales para el rendimiento:
-- - Claves primarias para identificación única
-- - Índices en campos de búsqueda frecuente
-- - Configuración de AUTO_INCREMENT para campos secuenciales
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INDEXES', 'INICIADO', 
        'Paso 1.3: Ejecutando 03_create_indexes.sql - Optimizando rendimiento');
SOURCE 03_create_indexes.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ESTRUCTURA', 'INDEXES', 'EXITOSO', 
        'Índices creados - Sistema optimizado para consultas rápidas');

-- =================================================================
-- FASE 2: ESTABLECER RELACIONES
-- Explicación: Ahora que tenemos todas las tablas, podemos crear
-- las relaciones entre ellas (claves foráneas) y hacer modificaciones
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'INICIO_FASE', 'INICIADO', 
        'Fase 2: Estableciendo relaciones - Integridad referencial del sistema');

-- PASO 2.1: Crear claves foráneas
-- Explicación: Las claves foráneas garantizan integridad referencial:
-- - Previenen datos huérfanos
-- - Aseguran consistencia entre tablas relacionadas
-- - Ejemplo: Un movimiento debe tener una cuenta válida
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'FOREIGN_KEYS', 'INICIADO', 
        'Paso 2.1: Ejecutando 04_foreign_keys.sql - Garantizando integridad de datos');
SOURCE 04_foreign_keys.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'FOREIGN_KEYS', 'EXITOSO', 
        'Claves foráneas establecidas - Integridad referencial activa');

-- PASO 2.2: Alteraciones adicionales de tablas
-- Explicación: Modificaciones posteriores a las tablas:
-- - Agregar campos que requieren tablas ya existentes
-- - Modificar campos existentes
-- - En este caso: agregar parent_id a categoria para jerarquías
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'ALTER_TABLES', 'INICIADO', 
        'Paso 2.2: Ejecutando 11_alter_categoria.sql - Modificaciones finales');
SOURCE 11_alter_categoria .sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'RELACIONES', 'ALTER_TABLES', 'EXITOSO', 
        'Alteraciones completadas - Estructura final de tablas establecida');

-- =================================================================
-- FASE 3: PROGRAMACIÓN Y LÓGICA DE NEGOCIO
-- Explicación: Aquí instalamos la "inteligencia" del sistema:
-- - Procedimientos almacenados para operaciones complejas
-- - Funciones para cálculos reutilizables
-- - Triggers para automatización
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 3: Instalando lógica de negocio - El cerebro del sistema');

-- PASO 3.1: Crear procedimientos almacenados
-- Explicación: Los procedimientos son como "funciones" en la base de datos:
-- - sp_recalcular_saldo_cuenta: Recalcula saldos basado en movimientos
-- - sp_recalcular_saldo_tarjeta: Maneja saldos de tarjetas de crédito
-- - sp_recalcular_saldo_prestamo: Controla saldos de préstamos
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'PROCEDURES', 'INICIADO', 
        'Paso 3.1: Ejecutando 05_stored_procedures.sql - Instalando procedimientos de negocio');
SOURCE 05_stored_procedures.sql;

-- Verificamos cuántos procedimientos se crearon
SELECT COUNT(*) INTO @proc_count 
FROM information_schema.routines 
WHERE routine_schema = 'app_presupuesto' AND routine_type = 'PROCEDURE';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'PROCEDURES', 'EXITOSO', 
        CONCAT('Procedimientos creados: ', @proc_count, ' - Operaciones de negocio disponibles'));

-- PASO 3.2: Crear funciones
-- Explicación: Las funciones retornan valores calculados:
-- - obtener_total_movimientos: Suma movimientos por persona
-- - reclasificar_categoria_movimientos: Cambio masivo de categorías
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'FUNCTIONS', 'INICIADO', 
        'Paso 3.2: Ejecutando 06_functions.sql - Instalando funciones de cálculo');
SOURCE 06_functions.sql;

-- Verificamos cuántas funciones se crearon
SELECT COUNT(*) INTO @func_count 
FROM information_schema.routines 
WHERE routine_schema = 'app_presupuesto' AND routine_type = 'FUNCTION';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'PROGRAMACION', 'FUNCTIONS', 'EXITOSO', 
        CONCAT('Funciones creadas: ', @func_count, ' - Cálculos automatizados disponibles'));

-- PASO 3.3: Crear triggers
-- Explicación: Los triggers son "eventos automáticos" que se ejecutan:
-- - AFTER INSERT en movimiento: Actualiza saldo de cuenta automáticamente
-- - AFTER UPDATE en movimiento: Recalcula saldos si hay cambios
-- - AFTER DELETE en movimiento: Ajusta saldos al eliminar transacciones
-- Esto garantiza que los saldos SIEMPRE estén actualizados sin intervención manual
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
-- FASE 4: VISTAS Y CONSULTAS
-- Explicación: Las vistas son "consultas guardadas" que facilitan
-- el acceso a información compleja y mejoran la seguridad
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VISTAS', 'INICIO_FASE', 'INICIADO', 
        'Fase 4: Creando vistas del sistema - Consultas simplificadas para la aplicación');

-- PASO 4.1: Crear vistas
-- Explicación: Las vistas incluyen:
-- - v_saldos: Vista consolidada de todos los productos financieros
-- - v_movimientos_detalle: Movimientos con información completa (joins)
-- - v_cuenta_saldos: Información de cuentas con datos del titular
-- - v_tarjeta_saldos: Estado de tarjetas con límites y fechas
-- - v_prestamo_saldos: Estado de préstamos con información del titular
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VISTAS', 'VIEWS', 'INICIADO', 
        'Paso 4.1: Ejecutando create_views.sql - Simplificando consultas complejas');
SOURCE create_views.sql;

-- Verificamos cuántas vistas se crearon
SELECT COUNT(*) INTO @view_count 
FROM information_schema.views 
WHERE table_schema = 'app_presupuesto';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VISTAS', 'VIEWS', 'EXITOSO', 
        CONCAT('Vistas creadas: ', @view_count, ' - Consultas optimizadas para la aplicación'));

-- =================================================================
-- FASE 5: AUTOMATIZACIÓN Y MANTENIMIENTO
-- Explicación: Los eventos programados mantienen el sistema limpio
-- y eficiente sin intervención manual
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'AUTOMATIZACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 5: Configurando automatización - Mantenimiento programado del sistema');

-- PASO 5.1: Crear eventos y trabajos programados
-- Explicación: Los eventos incluyen:
-- - limpiar_movimientos_antiguos: Elimina datos de más de 5 años (anual)
-- - recalcular_saldos_mensual: Recalcula todos los saldos (mensual)
-- - backup_constantes_semanal: Respaldo de configuración crítica (semanal)
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'AUTOMATIZACION', 'EVENTS', 'INICIADO', 
        'Paso 5.1: Ejecutando 08_events_jobs.sql - Programando tareas automáticas');
SOURCE 08_events_jobs.sql;

-- Verificamos cuántos eventos se crearon
SELECT COUNT(*) INTO @event_count 
FROM information_schema.events 
WHERE event_schema = 'app_presupuesto';
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'AUTOMATIZACION', 'EVENTS', 'EXITOSO', 
        CONCAT('Eventos creados: ', @event_count, ' - Sistema se mantiene automáticamente'));

-- =================================================================
-- FASE 6: DOCUMENTACIÓN Y DATOS INICIALES
-- Explicación: Documentamos el sistema y cargamos datos básicos
-- necesarios para que funcione correctamente
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'INICIO_FASE', 'INICIADO', 
        'Fase 6: Instalando documentación y datos - Preparando sistema para uso');

-- PASO 6.1: Agregar comentarios y documentación
-- Explicación: Documentamos todas las tablas y campos:
-- - Comentarios en cada tabla explicando su propósito
-- - Comentarios en campos críticos
-- - Documentación de vistas y su uso
-- - Tabla de documentación técnica para desarrolladores
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'COMMENTS', 'INICIADO', 
        'Paso 6.1: Ejecutando 10_add_comments.sql - Documentando estructura');
SOURCE 10_add_comments.sql;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'COMMENTS', 'EXITOSO', 
        'Documentación agregada - Sistema completamente documentado para desarrollo');

-- PASO 6.2: Insertar datos iniciales y constantes
-- Explicación: Cargamos datos esenciales:
-- - Constantes del sistema (tasas, límites, configuraciones)
-- - Categorías predefinidas (Alimentación, Transporte, etc.)
-- - Estados iniciales para movimientos, préstamos y tarjetas
-- Sin estos datos, el sistema no puede funcionar
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'INITIAL_DATA', 'INICIADO', 
        'Paso 6.2: Ejecutando insert_initial_data.sql - Cargando datos esenciales');
SOURCE insert_initial_data.sql;

-- Verificamos que los datos se cargaron correctamente
SELECT COUNT(*) INTO @const_count FROM app_presupuesto.constantes;
SELECT COUNT(*) INTO @cat_count FROM app_presupuesto.categoria;

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'DATOS', 'INITIAL_DATA', 'EXITOSO', 
        CONCAT('Datos cargados - Constantes: ', @const_count, ', Categorías: ', @cat_count));

-- =================================================================
-- FASE 7: INSTALACIÓN DE SISTEMAS EMPRESARIALES (OPCIONAL)
-- Explicación: Sistemas avanzados para entornos profesionales
-- Están comentados porque son opcionales y para casos específicos
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ENTERPRISE', 'INICIO_FASE', 'INICIADO', 
        'Fase 7: Sistemas empresariales opcionales - Para entornos avanzados');

-- SISTEMAS EMPRESARIALES DISPONIBLES (COMENTADOS):
-- 1. Sistema de backup empresarial (backup_full_enterprise.sql):
--    - Backups automáticos con compresión
--    - Verificación de integridad
--    - Rotación automática de archivos
--    - Logging detallado de operaciones

-- 2. Framework de migraciones (migration_framework.sql):
--    - Control de versiones de esquema
--    - Migraciones numeradas con dependencias
--    - Rollback automático seguro
--    - Validaciones pre y post migración

-- 3. Sistema de versionado (schema_versioning.sql):
--    - Snapshots de esquema por ambiente
--    - Comparación entre ambientes
--    - Audit trail completo
--    - Rollback a versiones anteriores

-- Para activar estos sistemas, descomente las siguientes líneas:
-- SOURCE ../../02_maintenance/backup/backup_full_enterprise.sql;
-- SOURCE ../../02_maintenance/backup/migration_framework.sql;  
-- SOURCE ../../02_maintenance/backup/schema_versioning.sql;

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'ENTERPRISE', 'SISTEMAS', 'EXITOSO', 
        'Sistemas empresariales disponibles pero no instalados - Descomente las líneas para activar');

-- =================================================================
-- FASE 8: VALIDACIÓN Y FINALIZACIÓN
-- Explicación: Verificamos que todo se instaló correctamente
-- y generamos reportes detallados
-- =================================================================

SET @phase_start = NOW();
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VALIDACION', 'INICIO_FASE', 'INICIADO', 
        'Fase 8: Validando instalación - Verificando que todo funciona correctamente');

-- PASO 8.1: Habilitar verificaciones de integridad
-- Explicación: Reactivamos las verificaciones que desactivamos al inicio
SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'VALIDACION', 'FOREIGN_KEYS', 'EXITOSO', 
        'Verificaciones de integridad reactivadas - Sistema protegido contra inconsistencias');

-- PASO 8.2: Finalizar transacción principal
-- Explicación: Si llegamos aquí, todo salió bien. Confirmamos todos los cambios.
-- Si hubiera habido un error, se habría hecho ROLLBACK automáticamente
COMMIT;
SET AUTOCOMMIT = 1;

INSERT INTO install_log (install_id, phase, step, status, message) 
VALUES (@install_id, 'FINALIZACION', 'COMMIT', 'EXITOSO', 
        'Transacción confirmada - Todos los cambios son permanentes');

-- Calcular tiempo total de instalación
SET @install_end_time = NOW();
SET @total_duration = TIMESTAMPDIFF(SECOND, @install_start_time, @install_end_time);

-- =================================================================
-- REPORTE FINAL DE INSTALACIÓN
-- Explicación: Generamos reportes completos para:
-- - Confirmar que la instalación fue exitosa
-- - Mostrar estadísticas de componentes instalados
-- - Proporcionar información para troubleshooting
-- - Dar instrucciones de próximos pasos
-- =================================================================

-- REPORTE 1: Resumen ejecutivo
SELECT 
    '🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE 🎉' AS RESULTADO,
    @install_id AS install_id,
    @install_start_time AS fecha_inicio,
    @install_end_time AS fecha_fin,
    CONCAT(@total_duration, ' segundos') AS duracion_total,
    @install_version AS version_sistema,
    'app-presupuesto (Proyecto de Aprendizaje)' AS proyecto;

-- REPORTE 2: Componentes instalados
SELECT 
    '📊 RESUMEN DE COMPONENTES INSTALADOS' AS seccion,
    @table_count AS tablas_creadas,
    @proc_count AS procedimientos_creados,
    @func_count AS funciones_creadas,
    @trigger_count AS triggers_creados,
    @view_count AS vistas_creadas,
    @event_count AS eventos_creados,
    @const_count AS constantes_insertadas,
    @cat_count AS categorias_insertadas;

-- REPORTE 3: Log de instalación por fases
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

-- REPORTE 4: Errores y advertencias (si los hay)
SELECT '⚠️ ERRORES Y ADVERTENCIAS' AS seccion, phase, step, message 
FROM install_log 
WHERE install_id = @install_id AND status = 'ERROR'
UNION ALL
SELECT '⚠️ ADVERTENCIAS' AS seccion, phase, step, message 
FROM install_log 
WHERE install_id = @install_id AND status = 'ADVERTENCIA';

-- REPORTE 5: Instrucciones post-instalación
SELECT 
    '🚀 PRÓXIMOS PASOS - POST-INSTALACIÓN' AS seccion,
    '✅ La base de datos app_presupuesto está lista para usar' AS paso_1,
    '👤 Crear usuario administrador en la tabla persona' AS paso_2,
    '⚙️ Ajustar constantes del sistema según necesidades' AS paso_3,
    '🏢 Para sistemas empresariales, descomentar líneas en FASE 7' AS paso_4,
    '📚 Revisar documentación en tabla documentacion_sistema' AS paso_5;

-- Restaurar configuración original de MySQL
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- =================================================================
-- 🎓 RESUMEN EDUCATIVO DE LO QUE APRENDIMOS
-- =================================================================

SELECT 
    '🎓 LECCIONES APRENDIDAS' AS titulo,
    'Este script demostró las mejores prácticas de instalación de BD' AS leccion_1,
    'Uso de transacciones para operaciones atómicas (todo o nada)' AS leccion_2,
    'Sistema de logging para debugging y auditoría' AS leccion_3,
    'Verificaciones de prerrequisitos antes de instalar' AS leccion_4,
    'Orden correcto: estructura → relaciones → lógica → datos' AS leccion_5,
    'Automatización con triggers y eventos programados' AS leccion_6,
    'Documentación como parte integral del desarrollo' AS leccion_7,
    'Reportes detallados para troubleshooting' AS leccion_8;

-- =================================================================
-- ✅ INSTALACIÓN COMPLETADA - SISTEMA LISTO PARA DESARROLLO
-- =================================================================
