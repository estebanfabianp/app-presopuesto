-- Configuraciones financieras
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('FINANCIERO', 'TASA_INTERES_DEFAULT', '0.15', 'DECIMAL', 'Tasa de interés por defecto para préstamos y tarjetas de crédito', 1),
('FINANCIERO', 'LIMITE_CREDITO_MINIMO', '100000', 'DECIMAL', 'Límite mínimo de crédito para productos financieros', 1),
('FINANCIERO', 'LIMITE_CREDITO_MAXIMO', '50000000', 'DECIMAL', 'Límite máximo de crédito para productos financieros', 1),
('FINANCIERO', 'MONEDA_PRINCIPAL', 'COP', 'STRING', 'Moneda principal del sistema', 1),
('FINANCIERO', 'DIAS_ALERTA_VENCIMIENTO', '7', 'INTEGER', 'Días de anticipación para alertas de vencimiento', 1);

-- Configuraciones del sistema
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('SISTEMA', 'VERSION_APP', '0.7.0', 'STRING', 'Versión actual de la aplicación', 0),
('SISTEMA', 'NOMBRE_APP', 'App Presupuesto', 'STRING', 'Nombre de la aplicación', 0),
('SISTEMA', 'MAX_INTENTOS_LOGIN', '3', 'INTEGER', 'Máximo número de intentos de login fallidos', 1),
('SISTEMA', 'TIEMPO_SESION_MINUTOS', '60', 'INTEGER', 'Tiempo de duración de la sesión en minutos', 1),
('SISTEMA', 'BACKUP_AUTOMATICO', 'true', 'BOOLEAN', 'Indica si el backup automático está habilitado', 1);

-- Configuraciones de interfaz de usuario
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('UI', 'REGISTROS_POR_PAGINA', '20', 'INTEGER', 'Número de registros por página en tablas', 1),
('UI', 'TEMA_DEFAULT', 'light', 'STRING', 'Tema visual por defecto de la aplicación', 1),
('UI', 'IDIOMA_DEFAULT', 'es', 'STRING', 'Idioma por defecto de la aplicación', 1),
('UI', 'FORMATO_FECHA', 'DD/MM/YYYY', 'STRING', 'Formato de fecha por defecto', 1),
('UI', 'FORMATO_MONEDA', '$ #,##0.00', 'STRING', 'Formato de visualización de moneda', 1);

-- Configuraciones de Machine Learning e IA
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('ML', 'PRECISION_MINIMA_CATEGORIA', '0.8', 'DECIMAL', 'Precisión mínima requerida para categorización automática', 1),
('ML', 'DIAS_ENTRENAMIENTO_MODELO', '90', 'INTEGER', 'Días de datos históricos para entrenar modelos ML', 1),
('ML', 'UMBRAL_GASTO_ANOMALO', '3.0', 'DECIMAL', 'Múltiplo de desviación estándar para detectar gastos anómalos', 1),
('ML', 'MAX_CATEGORIAS_SUGERIDAS', '3', 'INTEGER', 'Número máximo de categorías sugeridas por el modelo', 1);

-- Configuraciones de alertas y notificaciones
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('ALERTAS', 'PORCENTAJE_ALERTA_PRESUPUESTO', '80', 'INTEGER', 'Porcentaje del presupuesto para generar alerta', 1),
('ALERTAS', 'DIAS_RECORDATORIO_CATEGORIA', '30', 'INTEGER', 'Días sin categorizar para enviar recordatorio', 1),
('ALERTAS', 'HABILITADO_NOTIFICACIONES', 'true', 'BOOLEAN', 'Indica si las notificaciones están habilitadas', 1);

-- Configuraciones de seguridad
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('SEGURIDAD', 'LONGITUD_MINIMA_PASSWORD', '8', 'INTEGER', 'Longitud mínima requerida para contraseñas', 1),
('SEGURIDAD', 'REQUIERE_MAYUSCULAS', 'true', 'BOOLEAN', 'Indica si las contraseñas requieren mayúsculas', 1),
('SEGURIDAD', 'REQUIERE_NUMEROS', 'true', 'BOOLEAN', 'Indica si las contraseñas requieren números', 1),
('SEGURIDAD', 'REQUIERE_SIMBOLOS', 'false', 'BOOLEAN', 'Indica si las contraseñas requieren símbolos especiales', 1);

-- Configuraciones de reportes
INSERT INTO `app_presupuesto`.`constantes` (`categoria`, `nombre`, `valor`, `tipo_dato`, `descripcion`, `es_editable`) VALUES
('REPORTES', 'MESES_ANALISIS_TENDENCIAS', '12', 'INTEGER', 'Meses de datos para análisis de tendencias', 1),
('REPORTES', 'CATEGORIAS_TOP_GASTOS', '5', 'INTEGER', 'Número de categorías top a mostrar en reportes', 1),
('REPORTES', 'FORMATO_EXPORTACION', 'PDF', 'STRING', 'Formato por defecto para exportar reportes', 1);

-- =================================================================
-- Datos iniciales para la tabla categoria
-- Incluye categorías comunes para gestión financiera personal
-- Organizadas por tipo: Ingresos, Gastos Fijos, Gastos Variables, etc.
-- =================================================================

-- CATEGORÍAS DE INGRESOS
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Salario'),
('Bonificaciones'),
('Freelance/Trabajos Independientes'),
('Inversiones'),
('Dividendos'),
('Intereses Bancarios'),
('Alquiler de Propiedades'),
('Ventas'),
('Subsidios'),
('Pensión'),
('Otros Ingresos');

-- CATEGORÍAS DE GASTOS FIJOS (NECESARIOS)
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Vivienda - Arriendo/Hipoteca'),
('Servicios Públicos'),
('Internet y Telefonía'),
('Seguros'),
('Educación'),
('Salud - EPS/Medicina Prepagada'),
('Transporte Público'),
('Gasolina/Combustible'),
('Moto - Gasolina, Mantenimiento, Accesorios, Seguridad'),
('Préstamos y Deudas'),
('Impuestos');

-- CATEGORÍAS DE GASTOS VARIABLES (NECESARIOS)
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Alimentación'),
('Supermercado'),
('Medicamentos'),
('Ropa y Calzado'),
('Cuidado Personal'),
('Mantenimiento del Hogar'),
('Reparaciones'),
('Taxi/Uber');

-- CATEGORÍAS DE GASTOS DISCRECIONALES (OPCIONALES)
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Entretenimiento'),
('Restaurantes'),
('Café y Snacks'),
('Deportes y Gimnasio'),
('Hobbies'),
('Viajes y Vacaciones'),
('Cine y Teatro'),
('Música y Streaming'),
('Libros y Revistas'),
('Tecnología'),
('Decoración'),
('Regalos'),
('Donaciones');

-- CATEGORÍAS DE AHORRO E INVERSIÓN
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Ahorro de Emergencia'),
('Ahorro para Objetivos'),
('Inversiones en Acciones'),
('Inversiones en Fondos'),
('CDT y Cuentas de Ahorro'),
('Pensiones Voluntarias'),
('Bienes Raíces');

-- CATEGORÍAS ESPECIALES
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Transferencias entre Cuentas'),
('Pagos de Tarjeta de Crédito'),
('Retiros en Efectivo'),
('Comisiones Bancarias'),
('Gastos Médicos de Emergencia'),
('Gastos Varios'),
('Sin Categorizar');

-- =================================================================
-- DÍAS FESTIVOS DE COLOMBIA
-- Incluye todos los días festivos oficiales según la legislación colombiana
-- Organizados por: Festivos Fijos, Trasladables al Lunes y Variables
-- =================================================================

-- FESTIVOS FIJOS (NO SE TRASLADAN)
-- Estos días siempre se celebran en la fecha exacta, independiente del día de la semana
INSERT INTO `app_presupuesto`.`dias_festivos` (`nombre`, `fecha`, `tipo_festivo`, `es_recurrente`, `mes`, `dia`, `pais`, `descripcion`) VALUES
-- Año 2025
('Año Nuevo', '2025-01-01', 'NACIONAL', 1, 1, 1, 'CO', 'Celebración del inicio del nuevo año'),
('Día del Trabajo', '2025-05-01', 'NACIONAL', 1, 5, 1, 'CO', 'Día Internacional del Trabajo'),
('Día de la Independencia', '2025-07-20', 'NACIONAL', 1, 7, 20, 'CO', 'Grito de Independencia de Colombia - 1810'),
('Batalla de Boyacá', '2025-08-07', 'NACIONAL', 1, 8, 7, 'CO', 'Conmemoración de la Batalla de Boyacá - 1819'),
('Inmaculada Concepción', '2025-12-08', 'RELIGIOSO', 1, 12, 8, 'CO', 'Dogma de la Inmaculada Concepción de María'),
('Navidad', '2025-12-25', 'RELIGIOSO', 1, 12, 25, 'CO', 'Celebración del nacimiento de Jesucristo');

-- FESTIVOS TRASLADABLES AL LUNES SIGUIENTE (LEY EMILIANI)
-- Si caen en domingo se celebran el lunes; si caen entre martes y sábado se trasladan al lunes siguiente
INSERT INTO `app_presupuesto`.`dias_festivos` (`nombre`, `fecha`, `tipo_festivo`, `es_recurrente`, `mes`, `dia`, `pais`, `descripcion`, `creado_por`) VALUES
-- Año 2025 (fechas ya calculadas según la Ley Emiliani)
('Reyes Magos', '2025-01-06', 'RELIGIOSO', 1, 1, 6, 'CO', 'Epifanía del Señor - Adoración de los Reyes Magos', 'SEED_DATA'),
('San José', '2025-03-24', 'RELIGIOSO', 0, NULL, NULL, 'CO', 'Día de San José - Trasladado al lunes siguiente', 'SEED_DATA'),
('San Pedro y San Pablo', '2025-06-30', 'RELIGIOSO', 0, NULL, NULL, 'CO', 'Día de San Pedro y San Pablo - Trasladado al lunes', 'SEED_DATA'),
('Asunción de la Virgen', '2025-08-18', 'RELIGIOSO', 0, NULL, NULL, 'CO', 'Asunción de la Virgen María - Trasladado al lunes', 'SEED_DATA'),
('Día de la Raza', '2025-10-13', 'NACIONAL', 0, NULL, NULL, 'CO', 'Encuentro de Dos Mundos - Trasladado al lunes', 'SEED_DATA'),
('Todos los Santos', '2025-11-03', 'RELIGIOSO', 0, NULL, NULL, 'CO', 'Día de Todos los Santos - Trasladado al lunes', 'SEED_DATA'),
('Independencia de Cartagena', '2025-11-17', 'NACIONAL', 0, NULL, NULL, 'CO', 'Independencia de Cartagena - Trasladado al lunes', 'SEED_DATA');

-- FESTIVOS VARIABLES (DEPENDEN DE LA SEMANA SANTA)
-- Estas fechas cambian cada año según el cálculo de la Pascua
INSERT INTO `app_presupuesto`.`dias_festivos` (`nombre`, `fecha`, `tipo_festivo`, `es_recurrente`, `pais`, `descripcion`, `creado_por`) VALUES
-- Año 2025 (Domingo de Pascua: 20 de abril de 2025)
('Domingo de Ramos', '2025-04-13', 'RELIGIOSO', 0, 'CO', 'Entrada triunfal de Jesús a Jerusalén', 'SEED_DATA'),
('Jueves Santo', '2025-04-17', 'RELIGIOSO', 0, 'CO', 'Última Cena de Jesús con sus apóstoles', 'SEED_DATA'),
('Viernes Santo', '2025-04-18', 'RELIGIOSO', 0, 'CO', 'Crucifixión y muerte de Jesucristo', 'SEED_DATA'),
('Domingo de Resurrección', '2025-04-20', 'RELIGIOSO', 0, 'CO', 'Resurrección de Jesucristo - Domingo de Pascua', 'SEED_DATA'),
('Ascensión del Señor', '2025-06-02', 'RELIGIOSO', 0, 'CO', 'Ascensión de Jesús al cielo - 39 días después de Pascua', 'SEED_DATA'),
('Corpus Christi', '2025-06-23', 'RELIGIOSO', 0, 'CO', 'Cuerpo y Sangre de Cristo - 60 días después de Pascua', 'SEED_DATA'),
('Sagrado Corazón de Jesús', '2025-06-30', 'RELIGIOSO', 0, 'CO', 'Devoción al Sagrado Corazón - 68 días después de Pascua', 'SEED_DATA');

-- FESTIVOS ADICIONALES PARA AÑO 2026 (MUESTRA)
-- Festivos fijos que se repiten cada año
INSERT INTO `app_presupuesto`.`dias_festivos` (`nombre`, `fecha`, `tipo_festivo`, `es_recurrente`, `mes`, `dia`, `pais`, `descripcion`) VALUES
('Año Nuevo', '2026-01-01', 'NACIONAL', 1, 1, 1, 'CO', 'Celebración del inicio del nuevo año'),
('Día del Trabajo', '2026-05-01', 'NACIONAL', 1, 5, 1, 'CO', 'Día Internacional del Trabajo'),
('Día de la Independencia', '2026-07-20', 'NACIONAL', 1, 7, 20, 'CO', 'Grito de Independencia de Colombia - 1810'),
('Batalla de Boyacá', '2026-08-07', 'NACIONAL', 1, 8, 7, 'CO', 'Conmemoración de la Batalla de Boyacá - 1819'),
('Inmaculada Concepción', '2026-12-08', 'RELIGIOSO', 1, 12, 8, 'CO', 'Dogma de la Inmaculada Concepción de María'),
('Navidad', '2026-12-25', 'RELIGIOSO', 1, 12, 25, 'CO', 'Celebración del nacimiento de Jesucristo');

-- NOTA IMPORTANTE PARA DESARROLLADORES:
-- Los festivos trasladables y variables requieren cálculo anual
-- Se recomienda crear un procedimiento almacenado para generar automáticamente
-- las fechas de cada año nuevo basándose en:
-- 1. Ley Emiliani para festivos trasladables
-- 2. Cálculo de Pascua para festivos variables
-- 3. Considerar posibles cambios en la legislación

-- =================================================================
-- DATOS DE DOCUMENTACIÓN DEL SISTEMA
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

-- TABLA DIAS FESTIVOS
('TABLA', 'dias_festivos', 'Gestión de días festivos para cálculos de días hábiles', 'Tabla especializada en el almacenamiento y gestión de días festivos nacionales, regionales y empresariales. Soporta festivos fijos (como Navidad), trasladables (Ley Emiliani en Colombia) y variables (Semana Santa). Incluye clasificación por tipo, ámbito geográfico y funcionalidades para automatizar cálculos de días hábiles en el sistema financiero.', 'Cálculo de días hábiles, fechas de vencimiento, nóminas, reportes que excluyan festivos, automatización de pagos', 'SELECT * FROM dias_festivos WHERE pais = \"CO\" AND YEAR(fecha) = 2025; -- Festivos Colombia 2025', 'Considerar la Ley Emiliani para festivos trasladables en Colombia. Actualizar anualmente los festivos variables como Semana Santa. Los índices están optimizados para consultas por fecha y tipo.');

-- =================================================================
-- DATOS DE ARQUITECTURA DEL SISTEMA
-- =================================================================

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

-- Actualizar fecha de última documentación en constantes
INSERT INTO constantes (categoria, nombre, valor, tipo_dato, descripcion, es_editable)
VALUES ('SISTEMA', 'FECHA_ULTIMA_DOCUMENTACION', NOW(), 'DATE', 'Fecha de la última actualización de documentación', 0)
ON DUPLICATE KEY UPDATE 
    valor = NOW(),
    fecha_actualizacion = NOW();

    INSERT INTO mis_logros (logro, descripcion, icono) VALUES
('Mes Sin Excesos', 'Completaste un mes dentro del presupuesto', '🏆'),
('Ahorrador Hábil', 'Ahorraste usando cálculos de días hábiles', '📊'),
('Predictor', 'Tu predicción de gasto mensual fue 95% exacta', '🔮');

-- Agrega las claves foráneas después de la creación de las tablas
