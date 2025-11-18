-- =================================================================
-- CREACIÓN DE TABLAS
-- Proyecto: app-presupuesto
-- Descripción: Definición de estructura de tablas sin claves foráneas
-- =================================================================

-- Tabla: moneda
DROP TABLE IF EXISTS `moneda`;
CREATE TABLE `moneda` (
  `codigo` varchar(10) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: estado_movimiento
DROP TABLE IF EXISTS `estado_movimiento`;
CREATE TABLE `estado_movimiento` (
  `id_estado` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: estado_prestamo
DROP TABLE IF EXISTS `estado_prestamo`;
CREATE TABLE `estado_prestamo` (
  `id_estado` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: estado_tarjeta
DROP TABLE IF EXISTS `estado_tarjeta`;
CREATE TABLE `estado_tarjeta` (
  `id_estado` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: persona
DROP TABLE IF EXISTS `persona`;
CREATE TABLE `persona` (
  `id_persona` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `correo_electronico` varchar(100) DEFAULT NULL,
  `usuario` varchar(45) DEFAULT NULL,
  `clave` varchar(255) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `estado` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: tipo_movimiento
DROP TABLE IF EXISTS `tipo_movimiento`;
CREATE TABLE `tipo_movimiento` (
  `id_tipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- =================================================================
-- Tabla: accion
-- Descripción: Almacena información sobre acciones/inversiones en bolsa
-- Propósito: Gestión de portafolio de inversiones
-- Relaciones: persona (FK)
-- =================================================================
DROP TABLE IF EXISTS `accion`;
CREATE TABLE `accion` (
  `id_accion` int(11) NOT NULL,
  `simbolo` varchar(10) DEFAULT NULL,
  `empresa` varchar(100) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_compra` decimal(15,2) DEFAULT NULL,
  `fecha_compra` date DEFAULT NULL,
  `precio_actual` decimal(15,2) DEFAULT NULL,
  `mercado` varchar(50) DEFAULT NULL,
  `id_persona` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- =================================================================
-- Tabla: activo
-- Descripción: Registro de bienes y activos fijos
-- Propósito: Control de patrimonio y depreciación
-- Relaciones: persona (FK)
-- =================================================================
DROP TABLE IF EXISTS `activo`;
CREATE TABLE `activo` (
  `id_activo` int(11) NOT NULL,
  `nombre_activo` varchar(100) DEFAULT NULL,
  `valor` decimal(15,2) DEFAULT NULL,
  `depreciacion` decimal(15,2) DEFAULT NULL,
  `id_persona` int(11) DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: beneficiario
DROP TABLE IF EXISTS `beneficiario`;
CREATE TABLE `beneficiario` (
  `id_beneficiario` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Tabla: categoria
DROP TABLE IF EXISTS `categoria`;
CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- =================================================================
-- Tabla: constantes
-- Descripción: Configuración dinámica del sistema
-- Propósito: Almacenar parámetros configurables sin modificar código
-- Categorías: FINANCIERO, SISTEMA, UI, ML, ALERTAS, SEGURIDAD, REPORTES
-- Uso: Tasas de interés, límites, configuraciones de ML, etc.
-- =================================================================
DROP TABLE IF EXISTS `constantes`;
CREATE TABLE `constantes` (
  `id_constante` int(11) NOT NULL AUTO_INCREMENT,
  `categoria` varchar(50) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `valor` text NOT NULL,
  `tipo_dato` enum('STRING','INTEGER','DECIMAL','BOOLEAN','JSON','DATE') NOT NULL DEFAULT 'STRING',
  `descripcion` text DEFAULT NULL,
  `es_editable` tinyint(1) NOT NULL DEFAULT 1,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `creado_por` varchar(50) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_constante`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;

-- =================================================================
-- Tabla: cuenta
-- Descripción: Cuentas bancarias y productos financieros
-- Propósito: Gestión de cuentas de ahorro, corrientes, etc.
-- Características: Saldo automático calculado por triggers
-- Relaciones: persona (FK), movimiento (1:N)
-- =================================================================
DROP TABLE IF EXISTS `cuenta`;
CREATE TABLE `cuenta` (
  `id_cuenta` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `saldo_inicial` decimal(15,2) NOT NULL DEFAULT 0.00,
  `moneda` varchar(10) NOT NULL DEFAULT 'COP',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- =================================================================
-- Tabla: movimiento
-- Descripción: Registro principal de transacciones financieras
-- Propósito: Control de todos los ingresos y gastos
-- Características: 
--   * Triggers automáticos para actualizar saldos
--   * Soporte para categorización y notas
--   * Vinculación con cuentas, beneficiarios y categorías
-- Tipos: Ingreso, Gasto, Transferencia
-- =================================================================
DROP TABLE IF EXISTS `movimiento`;
CREATE TABLE `movimiento` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(45) DEFAULT NULL,
  `monto` decimal(15,2) DEFAULT NULL,
  `id_tipo` int(11) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_beneficiario` int(11) DEFAULT NULL,
  `numero_transaccion` varchar(45) DEFAULT NULL,
  `nota` text DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `id_cuenta` int(11) NOT NULL,
  PRIMARY KEY (`id_movimiento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- ...existing code for remaining tables...
