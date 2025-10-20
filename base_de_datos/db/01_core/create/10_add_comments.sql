-- =================================================================
-- AGREGAR COMENTARIOS A TABLAS Y VISTAS - DOCUMENTACIÓN COMPLETA
-- Proyecto: app-presupuesto
-- Descripción: Script para documentar todas las tablas y vistas del sistema
-- Propósito: Mejorar la documentación y facilitar el mantenimiento
-- Versión: 3.0 - Documentación empresarial completa
-- =================================================================

-- =================================================================
-- COMENTARIOS DE TABLAS
-- Descripción: Documentación detallada de cada tabla del sistema
-- =================================================================

-- Tabla: accion - Inversiones en bolsa
ALTER TABLE `accion` COMMENT = 'Registro de acciones e inversiones bursátiles del usuario';
ALTER TABLE `accion` 
  MODIFY `id_accion` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la acción',
  MODIFY `simbolo` varchar(10) DEFAULT NULL COMMENT 'Símbolo bursátil de la acción (ej: ECOPETROL)',
  MODIFY `empresa` varchar(100) DEFAULT NULL COMMENT 'Nombre de la empresa emisora',
  MODIFY `cantidad` int(11) DEFAULT NULL COMMENT 'Número de acciones poseídas',
  MODIFY `precio_compra` decimal(15,2) DEFAULT NULL COMMENT 'Precio de compra por acción',
  MODIFY `fecha_compra` date DEFAULT NULL COMMENT 'Fecha de adquisición',
  MODIFY `precio_actual` decimal(15,2) DEFAULT NULL COMMENT 'Precio actual de mercado',
  MODIFY `mercado` varchar(50) DEFAULT NULL COMMENT 'Mercado donde cotiza (BVC, NASDAQ, etc.)',
  MODIFY `id_persona` int(11) DEFAULT NULL COMMENT 'Propietario de las acciones';

-- Tabla: activo - Bienes y patrimonio
ALTER TABLE `activo` COMMENT = 'Bienes y activos fijos del usuario';
ALTER TABLE `activo`
  MODIFY `id_activo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del activo',
  MODIFY `nombre_activo` varchar(100) DEFAULT NULL COMMENT 'Nombre descriptivo del bien',
  MODIFY `valor` decimal(15,2) DEFAULT NULL COMMENT 'Valor actual del activo',
  MODIFY `depreciacion` decimal(15,2) DEFAULT NULL COMMENT 'Valor de depreciación acumulada',
  MODIFY `id_persona` int(11) DEFAULT NULL COMMENT 'Propietario del activo',
  MODIFY `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de registro del activo';

-- Tabla: beneficiario - Catálogo de comercios y entidades
ALTER TABLE `beneficiario` COMMENT = 'Catálogo de beneficiarios y comercios para normalización de nombres';
ALTER TABLE `beneficiario`
  MODIFY `id_beneficiario` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del beneficiario',
  MODIFY `nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre del comercio, persona o entidad';

-- Tabla: categoria - Clasificación de movimientos
ALTER TABLE `categoria` COMMENT = 'Categorías para clasificación de movimientos financieros';
ALTER TABLE `categoria`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la categoría',
  MODIFY `nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre de la categoría financiera (Alimentación, Transporte, etc.)';

-- Tabla: constantes - Configuración del sistema
ALTER TABLE `constantes` COMMENT = 'Constantes y configuración dinámica del sistema';
-- Los comentarios ya están definidos en la estructura original

-- Tabla: cuenta - Cuentas bancarias
ALTER TABLE `cuenta` COMMENT = 'Cuentas bancarias y productos financieros';
ALTER TABLE `cuenta`
  MODIFY `id_cuenta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la cuenta',
  MODIFY `id_persona` int(11) NOT NULL COMMENT 'Propietario de la cuenta',
  MODIFY `nombre` varchar(100) NOT NULL COMMENT 'Nombre descriptivo de la cuenta',
  MODIFY `tipo` varchar(50) NOT NULL COMMENT 'Tipo de cuenta (Ahorro, Corriente, etc.)',
  MODIFY `saldo_inicial` decimal(15,2) NOT NULL DEFAULT 0.00 COMMENT 'Saldo actual (actualizado automáticamente por triggers)',
  MODIFY `moneda` varchar(10) NOT NULL DEFAULT 'COP' COMMENT 'Moneda de la cuenta (COP, USD, EUR, etc.)',
  MODIFY `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de apertura de la cuenta';

-- Tabla: deuda_financiada - Deudas a largo plazo
ALTER TABLE `deuda_financiada` COMMENT = 'Deudas financiadas y créditos a largo plazo';
ALTER TABLE `deuda_financiada`
  MODIFY `id_deuda` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la deuda',
  MODIFY `entidad` varchar(100) NOT NULL COMMENT 'Institución financiera o acreedor',
  MODIFY `monto_inicial` decimal(15,2) NOT NULL COMMENT 'Monto original de la deuda',
  MODIFY `saldo_actual` decimal(15,2) NOT NULL COMMENT 'Saldo pendiente de pago',
  MODIFY `numero_transaccion` varchar(45) DEFAULT NULL COMMENT 'Número de referencia del crédito',
  MODIFY `tasa_interes` decimal(5,2) NOT NULL COMMENT 'Tasa de interés anual (%)',
  MODIFY `fecha_inicio` date NOT NULL COMMENT 'Fecha de inicio del financiamiento',
  MODIFY `fecha_fin` date NOT NULL COMMENT 'Fecha de finalización programada',
  MODIFY `id_persona` int(11) DEFAULT NULL COMMENT 'Deudor responsable';

-- Tablas de estados
ALTER TABLE `estado_movimiento` COMMENT = 'Estados posibles para movimientos financieros (Pendiente, Conciliado, Anulado)';
ALTER TABLE `estado_movimiento`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
  MODIFY `nombre` varchar(50) NOT NULL COMMENT 'Nombre del estado del movimiento';

ALTER TABLE `estado_prestamo` COMMENT = 'Estados posibles para préstamos (Activo, Pagado, Vencido, Cancelado)';
ALTER TABLE `estado_prestamo`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
  MODIFY `nombre` varchar(50) NOT NULL COMMENT 'Nombre del estado del préstamo';

ALTER TABLE `estado_tarjeta` COMMENT = 'Estados posibles para tarjetas de crédito (Activa, Bloqueada, Cancelada, Vencida)';
ALTER TABLE `estado_tarjeta`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
  MODIFY `nombre` varchar(50) NOT NULL COMMENT 'Nombre del estado de la tarjeta';

-- Tabla: moneda - Catálogo de divisas
ALTER TABLE `moneda` COMMENT = 'Catálogo de monedas soportadas por el sistema';
ALTER TABLE `moneda`
  MODIFY `codigo` varchar(10) NOT NULL COMMENT 'Código ISO de la moneda (COP, USD, EUR)',
  MODIFY `nombre` varchar(50) NOT NULL COMMENT 'Nombre completo de la moneda';

-- Tabla: movimiento - Transacciones principales
ALTER TABLE `movimiento` COMMENT = 'Registro principal de movimientos financieros con triggers automáticos para actualizar saldos';
-- Los comentarios ya están definidos en la estructura original

-- Tabla: movimiento_tarjeta - Movimientos de tarjetas
ALTER TABLE `movimiento_tarjeta` COMMENT = 'Movimientos específicos de tarjetas de crédito con triggers para saldos automáticos';
-- Los comentarios ya están definidos en la estructura original

-- Tabla: persona - Usuarios del sistema
ALTER TABLE `persona` COMMENT = 'Usuarios del sistema de presupuestos con autenticación';
ALTER TABLE `persona`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del usuario',
  MODIFY `nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre completo del usuario',
  MODIFY `correo_electronico` varchar(100) DEFAULT NULL COMMENT 'Email único para login',
  MODIFY `usuario` varchar(45) DEFAULT NULL COMMENT 'Nombre de usuario único',
  MODIFY `clave` varchar(255) DEFAULT NULL COMMENT 'Contraseña hasheada (usar bcrypt o similar)',
  MODIFY `fecha_creacion` datetime DEFAULT NULL COMMENT 'Fecha de registro en el sistema',
  MODIFY `fecha_actualizacion` datetime DEFAULT NULL COMMENT 'Última actualización de datos',
  MODIFY `estado` tinyint(1) DEFAULT NULL COMMENT 'Estado activo(1)/inactivo(0)';

-- Tabla: prestamo - Créditos otorgados
ALTER TABLE `prestamo` COMMENT = 'Préstamos otorgados a usuarios con saldo automático';
-- Los comentarios ya están definidos en la estructura original

-- Tabla: prestamo_movimiento - Pagos de préstamos
ALTER TABLE `prestamo_movimiento` COMMENT = 'Movimientos y pagos de préstamos con triggers para actualizar saldos';
-- Los comentarios ya están definidos en la estructura original

-- Tabla: presupuesto - Presupuestos definidos
ALTER TABLE `presupuesto` COMMENT = 'Presupuestos definidos por los usuarios';
ALTER TABLE `presupuesto`
  MODIFY `id_presupuesto` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del presupuesto',
  MODIFY `nombre` varchar(100) DEFAULT NULL COMMENT 'Nombre descriptivo del presupuesto',
  MODIFY `descripcion` text DEFAULT NULL COMMENT 'Descripción detallada del presupuesto',
  MODIFY `monto_total` decimal(15,2) DEFAULT NULL COMMENT 'Monto total asignado al presupuesto',
  MODIFY `fecha_inicio` date DEFAULT NULL COMMENT 'Fecha de inicio del presupuesto',
  MODIFY `fecha_fin` date DEFAULT NULL COMMENT 'Fecha de fin del presupuesto',
  MODIFY `id_persona` int(11) DEFAULT NULL COMMENT 'Persona propietaria del presupuesto',
  MODIFY `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del presupuesto';

-- Tabla: presupuesto_categoria - Relación N:M
ALTER TABLE `presupuesto_categoria` COMMENT = 'Relación entre presupuestos y categorías (tabla asociativa)';
ALTER TABLE `presupuesto_categoria`
  MODIFY `id_presupuesto` int(11) NOT NULL COMMENT 'Identificador del presupuesto',
  MODIFY `id_categoria` int(11) NOT NULL COMMENT 'Identificador de la categoría';

-- Tabla: tarjeta_credito - Tarjetas de crédito
ALTER TABLE `tarjeta_credito` COMMENT = 'Tarjetas de crédito con saldo automático y control de límites';
ALTER TABLE `tarjeta_credito`
  MODIFY `id_tarjeta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la tarjeta',
  MODIFY `id_producto` int(11) DEFAULT NULL COMMENT 'Producto asociado a la tarjeta (uso futuro)',
  MODIFY `numero_tarjeta` char(16) DEFAULT NULL COMMENT 'Número único de la tarjeta (últimos 4 dígitos)',
  MODIFY `limite_credito` decimal(15,2) DEFAULT NULL COMMENT 'Límite máximo de crédito disponible',
  MODIFY `saldo_actual` decimal(15,2) DEFAULT NULL COMMENT 'Saldo actual/deuda (actualizado por triggers)',
  MODIFY `fecha_corte` date DEFAULT NULL COMMENT 'Fecha de corte mensual',
  MODIFY `fecha_pago` date DEFAULT NULL COMMENT 'Fecha límite de pago mensual',
  MODIFY `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de registro de la tarjeta',
  MODIFY `id_estado` int(11) DEFAULT NULL COMMENT 'Estado actual de la tarjeta';

-- Tabla: tipo_movimiento - Tipos de transacciones
ALTER TABLE `tipo_movimiento` COMMENT = 'Tipos de movimientos financieros (Ingreso, Gasto, Transferencia)';
ALTER TABLE `tipo_movimiento`
  MODIFY `id_tipo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tipo',
  MODIFY `nombre` varchar(20) DEFAULT NULL COMMENT 'Nombre del tipo de movimiento';

-- Tabla: transaccion_programada - Transacciones recurrentes
ALTER TABLE `transaccion_programada` COMMENT = 'Transacciones programadas y recurrentes por los usuarios';
ALTER TABLE `transaccion_programada`
  MODIFY `id_transaccion` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la transacción programada',
  MODIFY `fecha` date DEFAULT NULL COMMENT 'Fecha de ejecución de la transacción',
  MODIFY `id_tipo` int(11) DEFAULT NULL COMMENT 'Tipo de movimiento programado',
  MODIFY `numero_transaccion` varchar(45) DEFAULT NULL COMMENT 'Número de referencia de la transacción',
  MODIFY `monto` decimal(15,2) DEFAULT NULL COMMENT 'Monto de la transacción programada',
  MODIFY `repeticion` int(11) DEFAULT NULL COMMENT 'Cantidad de repeticiones (0=infinito)',
  MODIFY `id_categoria` int(11) DEFAULT NULL COMMENT 'Categoría de la transacción',
  MODIFY `id_beneficiario` int(11) DEFAULT NULL COMMENT 'Beneficiario de la transacción',
  MODIFY `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación de la transacción programada';

-- =================================================================
-- COMENTARIOS DE VISTAS
-- Descripción: Documentación de las vistas del sistema
-- =================================================================

-- Se agregan comentarios explicativos a las vistas mediante ALTER VIEW
-- Nota: MySQL no soporta COMMENT en vistas, se documentan mediante comentarios SQL

/*
=================================================================
DOCUMENTACIÓN DE VISTAS
=================================================================

Vista: v_cuenta_saldos
Propósito: Resumen completo de cuentas con información del titular
Uso: Dashboard principal, reportes de patrimonio
Campos principales:
  - id_cuenta: ID único de la cuenta
  - nombre_cuenta: Nombre descriptivo
  - tipo_cuenta: Tipo (Ahorro, Corriente, etc.)
  - moneda: Moneda (COP, USD, etc.)
  - saldo_actual: Saldo disponible
  - titular: Nombre del propietario
Joins: cuenta INNER JOIN persona
Rendimiento: Índices en id_persona para optimizar JOIN

Vista: v_movimientos_detalle
Propósito: Vista completa de movimientos con datos relacionados
Uso: Historial de transacciones, reportes detallados, análisis
Campos principales:
  - Datos del movimiento (id, fecha, monto, código)
  - Tipo de movimiento (ingreso/gasto/transferencia)
  - Estado (pendiente/conciliado/anulado)
  - Categoría (alimentación/transporte/etc.)
  - Beneficiario (comercio/persona)
  - Cuenta y titular asociados
Joins: Multiple LEFT JOINs para datos completos
Rendimiento: Usar filtros por fecha y persona para mejorar performance

Vista: v_prestamo_saldos
Propósito: Resumen de préstamos con estado y titular
Uso: Control de deudas, seguimiento de préstamos activos
Campos principales:
  - Datos del préstamo (id, fecha, saldos, límites)
  - Estado del préstamo (activo/pagado/vencido)
  - Información del titular
Joins: prestamo LEFT JOIN estado_prestamo LEFT JOIN persona
Rendimiento: Filtrar por estado para préstamos activos

Vista: v_saldos (CONSOLIDADA)
Propósito: Vista unificada de saldos de todos los productos
Uso: Dashboard principal, análisis de patrimonio total
Importante: 
  - Tarjetas: saldo_actual puede representar deuda
  - Cuentas: saldo_inicial representa dinero disponible
  - Se requiere lógica de negocio para interpretar correctamente
Estructura: UNION de tarjetas y cuentas
Rendimiento: Usar índices en tablas base

Vista: v_tarjeta_saldos
Propósito: Resumen completo de tarjetas de crédito
Uso: Control de límites, fechas de pago, estados
Campos principales:
  - Datos de la tarjeta (número, límites, saldos)
  - Fechas importantes (corte, pago)
  - Estado de la tarjeta
Joins: tarjeta_credito LEFT JOIN estado_tarjeta
Cálculos derivados: Crédito disponible = límite - saldo_actual

=================================================================
RECOMENDACIONES DE USO
=================================================================

1. Para reportes financieros principales usar v_cuenta_saldos y v_saldos
2. Para análisis detallado de transacciones usar v_movimientos_detalle
3. Para control de deudas usar v_prestamo_saldos y v_tarjeta_saldos
4. Siempre filtrar por usuario/persona para performance
5. Usar índices en fechas para consultas temporales
6. Considerar particionamiento por fecha en tablas grandes

=================================================================
*/

-- =================================================================
-- CREACIÓN DE TABLA DE DOCUMENTACIÓN (OPCIONAL)
-- Para mantener documentación técnica en la BD
-- =================================================================

CREATE TABLE IF NOT EXISTS `documentacion_sistema` (
  `id_doc` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único de documentación',
  `tipo` enum('TABLA','VISTA','PROCEDIMIENTO','FUNCION','TRIGGER','EVENTO') NOT NULL COMMENT 'Tipo de objeto documentado',
  `nombre_objeto` varchar(100) NOT NULL COMMENT 'Nombre del objeto de BD',
  `descripcion_corta` varchar(255) NOT NULL COMMENT 'Descripción breve del propósito',
  `descripcion_larga` text DEFAULT NULL COMMENT 'Documentación detallada',
  `casos_uso` text DEFAULT NULL COMMENT 'Casos de uso principales',
  `ejemplos` text DEFAULT NULL COMMENT 'Ejemplos de consultas o uso',
  `consideraciones` text DEFAULT NULL COMMENT 'Consideraciones especiales',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de documentación',
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Última actualización',
  `version` varchar(20) DEFAULT '1.0' COMMENT 'Versión de la documentación',
  PRIMARY KEY (`id_doc`),
  UNIQUE KEY `uk_doc_objeto` (`tipo`, `nombre_objeto`),
  KEY `idx_doc_tipo` (`tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Documentación técnica del sistema de base de datos';

-- =================================================================
-- INSERTAR DOCUMENTACIÓN INICIAL ACTUALIZADA
-- =================================================================

-- Limpiar documentación anterior
DELETE FROM `documentacion_sistema`;

-- Insertar documentación completa del sistema
INSERT INTO `documentacion_sistema` (`tipo`, `nombre_objeto`, `descripcion_corta`, `descripcion_larga`, `casos_uso`, `ejemplos`, `consideraciones`) VALUES

-- TABLAS PRINCIPALES
('TABLA', 'movimiento', 'Registro principal de transacciones financieras', 'Tabla central que almacena todos los movimientos financieros con triggers automáticos para actualizar saldos de cuentas. Incluye categorización automática y manual, notas descriptivas y vinculación con beneficiarios.', 'Dashboard principal, reportes de gastos, análisis de flujo de caja, categorización ML', 'SELECT * FROM v_movimientos_detalle WHERE fecha_creacion >= CURDATE() - INTERVAL 30 DAY', 'Los triggers actualizan automáticamente los saldos. No modificar directamente sin considerar impacto en triggers.'),

('TABLA', 'cuenta', 'Cuentas bancarias y productos financieros', 'Gestión de cuentas con saldo automático calculado por triggers al insertar/actualizar/eliminar movimientos. Soporte para múltiples monedas y tipos de cuenta.', 'Gestión de patrimonio, control de saldos, reportes de cuentas, dashboard financiero', 'CALL sp_recalcular_saldo_cuenta(1); SELECT * FROM v_cuenta_saldos WHERE id_persona = 1', 'El campo saldo_inicial se actualiza automáticamente. Para recálculo manual usar sp_recalcular_saldo_cuenta.'),

('TABLA', 'constantes', 'Configuración dinámica del sistema', 'Parámetros configurables organizados por categorías (FINANCIERO, SISTEMA, UI, ML, ALERTAS, SEGURIDAD, REPORTES) para evitar hardcodear valores en la aplicación. Soporte para diferentes tipos de datos.', 'Configuración de tasas, límites, parámetros ML, alertas, configuración UI', 'SELECT * FROM constantes WHERE categoria = \"ML\" AND estado = 1', 'Algunos parámetros son críticos para el funcionamiento. Verificar dependencias antes de modificar.'),

('TABLA', 'tarjeta_credito', 'Tarjetas de crédito con automatización', 'Gestión de tarjetas de crédito con cálculo automático de saldos, control de límites, fechas de corte y pago. Integración con movimiento_tarjeta para transacciones.', 'Control de deudas, límites de crédito, fechas de pago, reportes financieros', 'SELECT * FROM v_tarjeta_saldos WHERE fecha_pago <= CURDATE() + INTERVAL 7 DAY', 'Los saldos se calculan automáticamente. Verificar límites antes de aprobar transacciones.'),

('TABLA', 'prestamo', 'Gestión de préstamos y créditos', 'Sistema completo de préstamos con seguimiento de pagos, intereses, estados y fechas de vencimiento. Cálculo automático de saldos mediante triggers.', 'Control de préstamos, seguimiento de pagos, cálculo de intereses, reportes de deuda', 'CALL sp_recalcular_saldo_prestamo(1); SELECT * FROM v_prestamo_saldos WHERE id_estado = 1', 'Considerar impacto de tasas de interés en cálculos. Verificar fechas de vencimiento regularmente.'),

-- VISTAS DEL SISTEMA
('VISTA', 'v_saldos', 'Vista consolidada de todos los productos financieros', 'UNION de saldos de cuentas y tarjetas para análisis integral de patrimonio. Permite ver el estado financiero completo del usuario en una sola consulta.', 'Dashboard principal, KPIs financieros, reportes consolidados, análisis de patrimonio', 'SELECT * FROM v_saldos WHERE titular = \"Juan Pérez\" ORDER BY saldo DESC', 'Interpretar correctamente: tarjetas muestran deuda (positivo = debe), cuentas muestran disponible.'),

('VISTA', 'v_movimientos_detalle', 'Vista completa de movimientos con datos relacionados', 'Join de movimientos con todas las tablas relacionadas para consultas detalladas. Incluye información de cuenta, titular, categoría, beneficiario y estado.', 'Histórico de transacciones, análisis de gastos, reportes detallados, categorización', 'SELECT * FROM v_movimientos_detalle WHERE categoria = \"Alimentación\" AND MONTH(fecha_creacion) = MONTH(CURDATE())', 'Usar filtros por fecha y persona para optimizar rendimiento en consultas grandes.'),

('VISTA', 'v_cuenta_saldos', 'Información completa de cuentas con titular', 'Resumen completo de cuentas con información del titular, ideal para dashboards y reportes de patrimonio individual.', 'Dashboard principal, reportes de patrimonio, gestión de cuentas por usuario', 'SELECT * FROM v_cuenta_saldos WHERE saldo_actual > 1000000 ORDER BY saldo_actual DESC', 'Útil para análisis por usuario. Los saldos están actualizados en tiempo real.'),

('VISTA', 'v_tarjeta_saldos', 'Estado completo de tarjetas de crédito', 'Resumen de tarjetas con límites, saldos, fechas importantes y crédito disponible calculado automáticamente.', 'Control de límites, fechas de pago, estados de tarjetas, alertas de vencimiento', 'SELECT * FROM v_tarjeta_saldos WHERE (limite_credito - saldo_actual) < 500000', 'Monitorear crédito disponible. Configurar alertas para fechas de pago próximas.'),

('VISTA', 'v_prestamo_saldos', 'Estado de préstamos con información completa', 'Estado de préstamos con información del titular, montos, saldos y estado actual. Útil para seguimiento de deudas.', 'Control de deudas, seguimiento de préstamos activos, reportes de cartera', 'SELECT * FROM v_prestamo_saldos WHERE nombre_estado = \"Activo\" AND saldo_inicial > 0', 'Verificar estados regularmente. Considerar automatización para préstamos vencidos.'),

-- PROCEDIMIENTOS ALMACENADOS
('PROCEDIMIENTO', 'sp_recalcular_saldo_cuenta', 'Recalcula saldo de cuenta basado en movimientos', 'Procedimiento que recalcula el saldo de una cuenta específica sumando todos sus movimientos (ingresos positivos, gastos negativos). Útil para corrección de inconsistencias.', 'Mantenimiento de datos, corrección de saldos, migración de datos', 'CALL sp_recalcular_saldo_cuenta(1);', 'Ejecutar después de migraciones masivas o corrección de datos. Puede ser lento con muchos movimientos.'),

('PROCEDIMIENTO', 'sp_recalcular_saldo_tarjeta', 'Recalcula saldo de tarjeta de crédito', 'Recalcula el saldo de una tarjeta considerando compras (aumentan deuda) y abonos (reducen deuda). Mantiene consistencia en el sistema.', 'Mantenimiento de tarjetas, corrección de saldos, auditoría financiera', 'CALL sp_recalcular_saldo_tarjeta(1);', 'Verificar que movimiento_tarjeta tenga estados correctos antes de ejecutar.'),

('PROCEDIMIENTO', 'sp_recalcular_saldo_prestamo', 'Recalcula saldo de préstamo', 'Suma todos los pagos registrados en prestamo_movimiento para actualizar el saldo actual del préstamo.', 'Mantenimiento de préstamos, auditoría de pagos, corrección de datos', 'CALL sp_recalcular_saldo_prestamo(1);', 'Considerar intereses y cargos adicionales que puedan no estar reflejados en movimientos.'),

-- FUNCIONES DEL SISTEMA
('FUNCION', 'obtener_total_movimientos', 'Calcula total de movimientos por persona', 'Función que suma todos los movimientos de una persona específica. NOTA: Requiere corrección para incluir JOIN con tabla cuenta.', 'Reportes personalizados, análisis por usuario, dashboards', 'SELECT obtener_total_movimientos(1) AS total_persona;', 'FUNCIÓN REQUIERE CORRECCIÓN: falta JOIN con tabla cuenta para funcionar correctamente.'),

('FUNCION', 'reclasificar_categoria_movimientos', 'Reclasifica movimientos por rango de fechas', 'Cambia la categoría de múltiples movimientos en un rango de fechas específico. Retorna el número de movimientos afectados.', 'Corrección masiva de categorías, migración de datos, limpieza de información', 'SELECT reclasificar_categoria_movimientos(5, \"2024-01-01\", \"2024-01-31\");', 'Hacer backup antes de ejecutar. La operación afecta múltiples registros simultáneamente.'),

-- TRIGGERS DEL SISTEMA
('TRIGGER', 'tr_update_saldo_cuenta_after_insert', 'Actualiza saldo al insertar movimiento', 'Trigger que se ejecuta automáticamente después de insertar un movimiento, actualizando el saldo de la cuenta correspondiente según el tipo (ingreso/gasto).', 'Automatización de saldos, integridad de datos, tiempo real', 'INSERT INTO movimiento (monto, id_tipo, id_cuenta) VALUES (100000, 1, 1);', 'No desactivar sin considerar impacto. Los saldos no se actualizarían automáticamente.'),

('TRIGGER', 'tr_update_saldo_cuenta_after_update', 'Actualiza saldos al modificar movimiento', 'Maneja cambios en movimientos existentes, incluyendo cambios de cuenta. Actualiza tanto la cuenta origen como la destino si corresponde.', 'Corrección de movimientos, transferencias entre cuentas, mantenimiento', 'UPDATE movimiento SET id_cuenta = 2 WHERE id_movimiento = 1;', 'Trigger complejo que maneja múltiples escenarios. Verificar consistencia después de actualizaciones masivas.'),

('TRIGGER', 'tr_update_saldo_cuenta_after_delete', 'Recalcula saldo al eliminar movimiento', 'Recalcula automáticamente el saldo de la cuenta cuando se elimina un movimiento, manteniendo la consistencia del sistema.', 'Eliminación de movimientos erróneos, limpieza de datos, correcciones', 'DELETE FROM movimiento WHERE id_movimiento = 1;', 'La eliminación es irreversible. Considerar soft delete para datos importantes.'),

-- EVENTOS AUTOMÁTICOS
('EVENTO', 'limpiar_movimientos_antiguos', 'Limpieza automática de datos antiguos', 'Evento anual que elimina movimientos con más de 5 años de antigüedad para optimizar el rendimiento de la base de datos.', 'Mantenimiento automático, optimización de rendimiento, gestión de almacenamiento', 'Ejecuta automáticamente cada año', 'CUIDADO: Eliminación irreversible. Considerar archivar en lugar de eliminar. Implementar logging.'),

('EVENTO', 'recalcular_saldos_mensual', 'Recálculo mensual de saldos', 'Evento mensual que recalcula todos los saldos del sistema (cuentas, tarjetas, préstamos) para mantener consistencia y detectar discrepancias.', 'Mantenimiento preventivo, auditoría automática, detección de inconsistencias', 'Ejecuta el primer día de cada mes a las 2:00 AM', 'Proceso intensivo. Programar en horarios de baja actividad. Monitorear rendimiento.'),

('EVENTO', 'backup_constantes_semanal', 'Backup automático de configuración', 'Crea respaldos semanales de las constantes del sistema, manteniendo histórico de cambios en configuración crítica.', 'Backup de configuración, auditoría de cambios, recuperación de desastres', 'Ejecuta domingos a las 3:00 AM', 'Mantiene solo 12 backups. Configurar almacenamiento externo para backups críticos.'),

-- SISTEMAS EMPRESARIALES (OPCIONALES)
('SISTEMA', 'backup_full_enterprise', 'Sistema empresarial de backup completo', 'Sistema completo de backup con compresión, verificación de integridad, rotación automática y logging detallado. Incluye verificación post-backup y limpieza automática.', 'Backup empresarial, recuperación de desastres, compliance, auditoría', 'CALL sp_backup_full_enterprise(\"/backup/\", 30, 6, 4);', 'Sistema robusto para producción. Configurar rutas externas y monitoreo de espacio en disco.'),

('SISTEMA', 'migration_framework', 'Framework de migraciones empresarial', 'Sistema completo de migraciones con versionado, dependencias, rollback automático y validaciones. Control total de cambios de esquema entre ambientes.', 'Migraciones entre ambientes, control de versiones, deployment automatizado', 'CALL sp_execute_migrations(\"production\", \"1.0.0\", \"admin\", FALSE);', 'Crítico para ambientes productivos. Probar siempre en desarrollo antes de producción.'),

('SISTEMA', 'schema_versioning', 'Sistema de versionado de esquema', 'Control de versiones de esquema con snapshots, comparación entre ambientes, audit trail completo y capacidades de rollback seguro.', 'Control de versiones, comparación de ambientes, auditoría de cambios', 'CALL sp_capture_schema_version(\"1.1.0\", \"production\", \"Nueva funcionalidad\", \"admin\");', 'Esencial para equipos grandes. Automatizar comparaciones entre ambientes regularmente.'),

('SISTEMA', 'restore_automated', 'Sistema de restauración automatizada', 'Sistema de restauración con validación previa, rollback automático en caso de falla, verificación post-restauración y logging completo.', 'Recuperación de desastres, restauración de backups, testing de restauración', 'CALL sp_restore_database_automated(\"/backup/file.sql.gz\", \"development\", \"FULL\", \"admin\", FALSE, FALSE);', 'Probar restauraciones regularmente. Validar integridad antes y después de restaurar.'),

-- CONFIGURACIÓN Y MONITOREO
('CONFIGURACION', 'constantes_ml', 'Configuración para Machine Learning', 'Parámetros específicos para algoritmos de ML: precisión mínima, días de entrenamiento, detección de anomalías, límites de sugerencias.', 'Configuración de IA, ajuste de modelos, optimización de precisión', 'SELECT * FROM constantes WHERE categoria = \"ML\";', 'Ajustar según rendimiento de modelos. Documentar cambios para tracking de experimentos.'),

('CONFIGURACION', 'constantes_seguridad', 'Configuración de seguridad del sistema', 'Parámetros de seguridad: longitud de contraseñas, complejidad requerida, intentos de login, tiempo de sesión.', 'Seguridad de la aplicación, control de acceso, políticas de contraseñas', 'SELECT * FROM constantes WHERE categoria = \"SEGURIDAD\";', 'Cambios afectan seguridad general. Evaluar impacto antes de modificar.'),

-- MEJORES PRÁCTICAS Y CONSIDERACIONES
('DOCUMENTACION', 'mejores_practicas', 'Mejores prácticas del sistema', 'Guía de mejores prácticas para uso del sistema: filtros recomendados, optimización de consultas, mantenimiento preventivo.', 'Desarrollo, mantenimiento, optimización, training de equipo', 'Ver documentación técnica completa', 'Actualizar regularmente. Compartir con todo el equipo de desarrollo.');

-- =================================================================
-- TABLA DE ARQUITECTURA DEL SISTEMA
-- =================================================================

CREATE TABLE IF NOT EXISTS `arquitectura_sistema` (
  `id_componente` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID único del componente',
  `nombre_componente` varchar(100) NOT NULL COMMENT 'Nombre del componente de arquitectura',
  `tipo_componente` enum('CAPA','MODULO','SERVICIO','INTEGRACION','HERRAMIENTA') NOT NULL COMMENT 'Tipo de componente',
  `descripcion` text NOT NULL COMMENT 'Descripción detallada del componente',
  `dependencias` json COMMENT 'Dependencias con otros componentes',
  `tecnologias` json COMMENT 'Tecnologías utilizadas',
  `responsabilidades` text COMMENT 'Responsabilidades específicas',
  `patrones_aplicados` json COMMENT 'Patrones de diseño aplicados',
  `metricas_rendimiento` json COMMENT 'Métricas de rendimiento esperadas',
  `contacto_responsable` varchar(100) COMMENT 'Responsable del componente',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `version` varchar(20) DEFAULT '1.0' COMMENT 'Versión del componente',
  PRIMARY KEY (`id_componente`),
  UNIQUE KEY `uk_componente` (`nombre_componente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Documentación de arquitectura del sistema';

-- Insertar arquitectura del sistema
INSERT INTO `arquitectura_sistema` (`nombre_componente`, `tipo_componente`, `descripcion`, `dependencias`, `tecnologias`, `responsabilidades`, `patrones_aplicados`) VALUES

('Capa de Datos', 'CAPA', 'Capa de persistencia y gestión de datos con MySQL como motor principal', 
'["Capa de Lógica de Negocio"]', 
'["MySQL 8.0+", "InnoDB Engine", "Triggers", "Stored Procedures", "Events"]',
'Almacenamiento de datos, integridad referencial, cálculos automáticos, auditoría',
'["Repository Pattern", "Unit of Work", "Domain Events"]'),

('Módulo de Movimientos', 'MODULO', 'Gestión completa de transacciones financieras con automatización de saldos',
'["Módulo de Cuentas", "Módulo de Categorización", "Capa de Datos"]',
'["Triggers Automáticos", "Stored Procedures", "Vistas Optimizadas"]',
'Registro de transacciones, actualización automática de saldos, categorización',
'["Event Sourcing", "CQRS", "Observer Pattern"]'),

('Sistema de Backup Empresarial', 'SERVICIO', 'Servicio completo de backup con compresión, verificación y rotación automática',
'["Capa de Datos", "Sistema de Monitoreo"]',
'["MySQL Dump", "Gzip Compression", "MD5 Checksum", "Scheduled Events"]',
'Backup automático, verificación de integridad, rotación de archivos, logging',
'["Strategy Pattern", "Template Method", "Command Pattern"]'),

('Framework de Migraciones', 'SERVICIO', 'Sistema de control de versiones y migraciones de esquema de base de datos',
'["Sistema de Versionado", "Capa de Datos"]',
'["Dependency Resolution", "Rollback Automation", "Schema Snapshots"]',
'Control de versiones de BD, migraciones seguras, rollback automático',
'["State Pattern", "Chain of Responsibility", "Memento Pattern"]'),

('Motor de Machine Learning', 'MODULO', 'Sistema de IA para categorización automática y detección de anomalías',
'["Módulo de Movimientos", "Sistema de Configuración"]',
'["Algoritmos ML", "Pattern Recognition", "Anomaly Detection"]',
'Categorización automática, detección de gastos anómalos, sugerencias inteligentes',
'["Strategy Pattern", "Factory Pattern", "Observer Pattern"]'),

('Sistema de Monitoreo', 'SERVICIO', 'Monitoreo en tiempo real de rendimiento, errores y métricas del sistema',
'["Todos los módulos"]',
'["Performance Metrics", "Error Tracking", "Health Checks"]',
'Monitoreo de rendimiento, alertas automáticas, métricas de negocio',
'["Observer Pattern", "Decorator Pattern", "Facade Pattern"]');

-- =================================================================
-- VISTA DE DOCUMENTACIÓN COMPLETA
-- =================================================================

CREATE OR REPLACE VIEW `v_documentacion_completa` AS
SELECT 
    ds.tipo,
    ds.nombre_objeto,
    ds.descripcion_corta,
    ds.casos_uso,
    ds.version,
    ds.fecha_creacion,
    CASE 
        WHEN ds.tipo = 'TABLA' THEN 'Base de datos'
        WHEN ds.tipo = 'VISTA' THEN 'Consultas optimizadas'
        WHEN ds.tipo = 'PROCEDIMIENTO' THEN 'Lógica de negocio'
        WHEN ds.tipo = 'FUNCION' THEN 'Cálculos específicos'
        WHEN ds.tipo = 'TRIGGER' THEN 'Automatización'
        WHEN ds.tipo = 'EVENTO' THEN 'Mantenimiento automático'
        WHEN ds.tipo = 'SISTEMA' THEN 'Funcionalidad empresarial'
        ELSE 'General'
    END AS categoria_funcional,
    CASE 
        WHEN ds.nombre_objeto LIKE '%saldo%' OR ds.nombre_objeto IN ('movimiento', 'cuenta', 'tarjeta_credito') THEN 'Crítico'
        WHEN ds.nombre_objeto LIKE '%backup%' OR ds.nombre_objeto LIKE '%migration%' THEN 'Empresarial'
        ELSE 'Normal'
    END AS nivel_criticidad
FROM documentacion_sistema ds
ORDER BY 
    FIELD(ds.tipo, 'TABLA', 'VISTA', 'PROCEDIMIENTO', 'FUNCION', 'TRIGGER', 'EVENTO', 'SISTEMA'),
    ds.nombre_objeto;

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
-- FINALIZACIÓN Y VERIFICACIÓN
-- =================================================================

-- Actualizar fecha de última documentación en constantes
INSERT INTO constantes (categoria, nombre, valor, tipo_dato, descripcion, es_editable)
VALUES ('SISTEMA', 'FECHA_ULTIMA_DOCUMENTACION', NOW(), 'DATE', 'Fecha de la última actualización de documentación', 0)
ON DUPLICATE KEY UPDATE 
    valor = NOW(),
    fecha_actualizacion = NOW();

-- Verificar documentación completa
SELECT 
    'DOCUMENTACIÓN ACTUALIZADA EXITOSAMENTE' AS resultado,
    COUNT(*) AS total_elementos_documentados,
    COUNT(DISTINCT tipo) AS tipos_componentes,
    NOW() AS fecha_actualizacion
FROM documentacion_sistema;

-- Generar reporte inicial
CALL sp_generar_reporte_documentacion(NULL, 'COMPLETO');

-- Script completado exitosamente
SELECT 
    '📚 DOCUMENTACIÓN COMPLETA ACTUALIZADA' AS resultado,
    'Sistema completamente documentado para desarrollo y mantenimiento' AS estado,
    'Usar: CALL sp_generar_reporte_documentacion() para reportes detallados' AS instruccion;
