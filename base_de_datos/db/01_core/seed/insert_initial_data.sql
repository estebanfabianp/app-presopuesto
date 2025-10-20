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
('Combustible'),
('Préstamos y Deudas'),
('Impuestos');

-- CATEGORÍAS DE GASTOS VARIABLES (NECESARIOS)
INSERT INTO `app_presupuesto`.`categoria` (`nombre`) VALUES
('Alimentación'),
('Mercado y Supermercado'),
('Medicamentos'),
('Ropa y Calzado'),
('Cuidado Personal'),
('Mantenimiento del Hogar'),
('Reparaciones'),
('Transporte - Taxi/Uber');

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

-- Agrega las claves foráneas después de la creación de las tablas
