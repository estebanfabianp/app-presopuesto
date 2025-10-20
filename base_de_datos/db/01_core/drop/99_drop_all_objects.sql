-- =================================================================
-- SCRIPT DE ELIMINACIÓN COMPLETA DE OBJETOS
-- Proyecto: app-presupuesto
-- Descripción: Elimina todos los objetos de la base de datos de forma segura
-- ADVERTENCIA: Este script elimina TODOS los datos y estructura
-- =================================================================
-- IMPORTANTE: 
-- * Hacer backup antes de ejecutar
-- * Verificar que estás en la base de datos correcta
-- * Este proceso es IRREVERSIBLE
-- =================================================================

USE `app_presupuesto`;

-- =================================================================
-- VERIFICACIÓN DE SEGURIDAD
-- =================================================================

-- Mostrar información de la base de datos actual
SELECT 
    'ADVERTENCIA: Eliminando objetos de la base de datos:' AS mensaje,
    DATABASE() AS base_datos_actual,
    NOW() AS fecha_hora;

-- Pausa para confirmación (descomentar si se desea confirmación manual)
-- SELECT 'PRESIONA ENTER PARA CONTINUAR O CTRL+C PARA CANCELAR' AS confirmacion;

-- =================================================================
-- PASO 1: ELIMINAR EVENTOS PROGRAMADOS
-- Descripción: Eliminar eventos antes que otros objetos
-- =================================================================

DROP EVENT IF EXISTS `limpiar_movimientos_antiguos`;

SELECT 'Eventos eliminados correctamente' AS paso_1;

-- =================================================================
-- PASO 2: ELIMINAR TRIGGERS
-- Descripción: Eliminar triggers antes de eliminar tablas
-- =================================================================

-- Triggers de tabla movimiento
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_delete`;
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_insert`;
DROP TRIGGER IF EXISTS `tr_update_saldo_cuenta_after_update`;

-- Triggers de tabla movimiento_tarjeta
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_delete`;
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_insert`;
DROP TRIGGER IF EXISTS `tr_update_saldo_tarjeta_after_update`;

-- Triggers de tabla prestamo_movimiento
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_delete`;
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_insert`;
DROP TRIGGER IF EXISTS `tr_update_saldo_prestamo_after_update`;

SELECT 'Triggers eliminados correctamente' AS paso_2;

-- =================================================================
-- PASO 3: ELIMINAR FUNCIONES
-- Descripción: Eliminar funciones definidas por el usuario
-- =================================================================

DROP FUNCTION IF EXISTS `obtener_total_movimientos`;
DROP FUNCTION IF EXISTS `reclasificar_categoria_movimientos`;

SELECT 'Funciones eliminadas correctamente' AS paso_3;

-- =================================================================
-- PASO 4: ELIMINAR PROCEDIMIENTOS ALMACENADOS
-- Descripción: Eliminar procedimientos antes de eliminar tablas
-- =================================================================

DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_cuenta`;
DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_prestamo`;
DROP PROCEDURE IF EXISTS `sp_recalcular_saldo_tarjeta`;

SELECT 'Procedimientos almacenados eliminados correctamente' AS paso_4;

-- =================================================================
-- PASO 5: ELIMINAR VISTAS
-- Descripción: Eliminar vistas que dependen de las tablas
-- =================================================================

DROP VIEW IF EXISTS `v_cuenta_saldos`;
DROP VIEW IF EXISTS `v_movimientos_detalle`;
DROP VIEW IF EXISTS `v_prestamo_saldos`;
DROP VIEW IF EXISTS `v_saldos`;
DROP VIEW IF EXISTS `v_tarjeta_saldos`;

SELECT 'Vistas eliminadas correctamente' AS paso_5;

-- =================================================================
-- PASO 6: DESHABILITAR VERIFICACIÓN DE CLAVES FORÁNEAS
-- Descripción: Permitir eliminación de tablas sin problemas de FK
-- =================================================================

SET FOREIGN_KEY_CHECKS = 0;

SELECT 'Verificación de claves foráneas deshabilitada' AS paso_6;

-- =================================================================
-- PASO 7: ELIMINAR TABLAS EN ORDEN LÓGICO
-- Descripción: Eliminar tablas dependientes primero, luego principales
-- =================================================================

-- Tablas de relaciones y movimientos (tablas dependientes)
DROP TABLE IF EXISTS `prestamo_movimiento`;
DROP TABLE IF EXISTS `movimiento_tarjeta`;
DROP TABLE IF EXISTS `movimiento`;
DROP TABLE IF EXISTS `presupuesto_categoria`;
DROP TABLE IF EXISTS `transaccion_programada`;

-- Tablas de productos financieros
DROP TABLE IF EXISTS `tarjeta_credito`;
DROP TABLE IF EXISTS `prestamo`;
DROP TABLE IF EXISTS `cuenta`;
DROP TABLE IF EXISTS `deuda_financiada`;
DROP TABLE IF EXISTS `presupuesto`;

-- Tablas de inversiones y activos
DROP TABLE IF EXISTS `accion`;
DROP TABLE IF EXISTS `activo`;

-- Tablas de catálogos y configuración
DROP TABLE IF EXISTS `beneficiario`;
DROP TABLE IF EXISTS `categoria`;
DROP TABLE IF EXISTS `constantes`;

-- Tablas de estados (catálogos)
DROP TABLE IF EXISTS `estado_movimiento`;
DROP TABLE IF EXISTS `estado_prestamo`;
DROP TABLE IF EXISTS `estado_tarjeta`;
DROP TABLE IF EXISTS `tipo_movimiento`;

-- Tablas de referencia
DROP TABLE IF EXISTS `moneda`;

-- Tabla principal (usuarios)
DROP TABLE IF EXISTS `persona`;

-- Tabla de documentación (si existe)
DROP TABLE IF EXISTS `documentacion_sistema`;

SELECT 'Tablas eliminadas correctamente' AS paso_7;

-- =================================================================
-- PASO 8: REHABILITAR VERIFICACIÓN DE CLAVES FORÁNEAS
-- Descripción: Restaurar configuración normal de MySQL
-- =================================================================

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Verificación de claves foráneas rehabilitada' AS paso_8;

-- =================================================================
-- PASO 9: VERIFICACIÓN FINAL
-- Descripción: Confirmar que todos los objetos han sido eliminados
-- =================================================================

-- Verificar tablas restantes
SELECT 
    'Tablas restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_tablas
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'app_presupuesto' 
AND TABLE_TYPE = 'BASE TABLE';

-- Verificar vistas restantes
SELECT 
    'Vistas restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_vistas
FROM INFORMATION_SCHEMA.VIEWS 
WHERE TABLE_SCHEMA = 'app_presupuesto';

-- Verificar procedimientos restantes
SELECT 
    'Procedimientos restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_procedimientos
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'app_presupuesto' 
AND ROUTINE_TYPE = 'PROCEDURE';

-- Verificar funciones restantes
SELECT 
    'Funciones restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_funciones
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'app_presupuesto' 
AND ROUTINE_TYPE = 'FUNCTION';

-- Verificar triggers restantes
SELECT 
    'Triggers restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_triggers
FROM INFORMATION_SCHEMA.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'app_presupuesto';

-- Verificar eventos restantes
SELECT 
    'Eventos restantes en la base de datos:' AS verificacion,
    COUNT(*) AS cantidad_eventos
FROM INFORMATION_SCHEMA.EVENTS 
WHERE EVENT_SCHEMA = 'app_presupuesto';

-- =================================================================
-- RESUMEN FINAL
-- =================================================================

SELECT 
    '====== ELIMINACIÓN COMPLETADA ======' AS resultado,
    'Todos los objetos han sido eliminados' AS estado,
    'Base de datos lista para reinstalación' AS siguiente_paso,
    NOW() AS fecha_finalizacion;

-- =================================================================
-- OPCIONAL: ELIMINAR LA BASE DE DATOS COMPLETA
-- Descripción: Descomentar las siguientes líneas para eliminar toda la BD
-- =================================================================

-- ¡CUIDADO! Las siguientes líneas eliminan la base de datos completa
-- Descomenta solo si realmente quieres eliminar toda la base de datos

-- USE mysql;
-- DROP DATABASE IF EXISTS `app_presupuesto`;
-- SELECT 'Base de datos app_presupuesto eliminada completamente' AS resultado_final;

-- =================================================================
-- SCRIPT ALTERNATIVO PARA ELIMINACIÓN AUTOMÁTICA COMPLETA
-- Descripción: Query para generar comandos de eliminación dinámicamente
-- =================================================================

/*
-- Script para generar comandos de eliminación automáticamente
-- Ejecutar estas consultas para obtener los comandos DROP correspondientes

-- Generar DROP para todas las tablas
SELECT CONCAT('DROP TABLE IF EXISTS `', TABLE_NAME, '`;') AS drop_statements
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'app_presupuesto' 
AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Generar DROP para todas las vistas
SELECT CONCAT('DROP VIEW IF EXISTS `', TABLE_NAME, '`;') AS drop_statements
FROM INFORMATION_SCHEMA.VIEWS 
WHERE TABLE_SCHEMA = 'app_presupuesto'
ORDER BY TABLE_NAME;

-- Generar DROP para todos los procedimientos
SELECT CONCAT('DROP PROCEDURE IF EXISTS `', ROUTINE_NAME, '`;') AS drop_statements
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'app_presupuesto' 
AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

-- Generar DROP para todas las funciones
SELECT CONCAT('DROP FUNCTION IF EXISTS `', ROUTINE_NAME, '`;') AS drop_statements
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'app_presupuesto' 
AND ROUTINE_TYPE = 'FUNCTION'
ORDER BY ROUTINE_NAME;
*/

-- =================================================================
-- NOTAS DE USO
-- =================================================================

/*
INSTRUCCIONES DE USO:

1. BACKUP OBLIGATORIO:
   - Hacer respaldo completo antes de ejecutar
   - mysqldump -u usuario -p app_presupuesto > backup_fecha.sql

2. VERIFICACIÓN:
   - Asegurarse de estar en la base de datos correcta
   - Revisar que no hay otras aplicaciones usando la BD

3. EJECUCIÓN:
   - Ejecutar este script completo
   - Verificar los mensajes de confirmación

4. POST-EJECUCIÓN:
   - Verificar que todos los objetos fueron eliminados
   - Ejecutar script de creación para reinstalar

5. TROUBLESHOOTING:
   - Si hay errores de FK, verificar que FOREIGN_KEY_CHECKS=0
   - Si quedan objetos, usar los scripts de generación automática
   - En caso de problemas, restaurar desde backup

CASOS DE USO:
- Reinstalación completa del sistema
- Actualización de estructura de BD
- Limpieza para desarrollo/testing
- Migración a nueva versión
*/
