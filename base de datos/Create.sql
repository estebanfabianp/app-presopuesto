-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 03-09-2025 a las 21:50:56
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `mydb`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activo`
--

CREATE TABLE `activo` (
  `id_activo` int(11) NOT NULL,
  `nombre_activo` varchar(100) NOT NULL,
  `valor` decimal(15,2) NOT NULL CHECK (`valor` >= 0),
  `depreciacion` decimal(15,2) DEFAULT NULL CHECK (`depreciacion` >= 0),
  `id_persona` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `beneficiario`
--

CREATE TABLE `beneficiario` (
  `id_beneficiario` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria`
--

CREATE TABLE `categoria` (
  `id_categoria` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_movimiento`
--

CREATE TABLE `estado_movimiento` (
  `id_estado` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_prestamo`
--

CREATE TABLE `estado_prestamo` (
  `id_estado` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_tarjeta`
--

CREATE TABLE `estado_tarjeta` (
  `id_estado` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `frecuencia_transaccion`
--

CREATE TABLE `frecuencia_transaccion` (
  `id_frecuencia` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimiento`
--

CREATE TABLE `movimiento` (
  `id_movimiento` int(11) NOT NULL,
  `codigo` varchar(45) DEFAULT NULL,
  `monto` decimal(15,2) NOT NULL CHECK (`monto` >= 0),
  `id_tipo` int(11) NOT NULL,
  `cuotas` int(11) DEFAULT NULL,
  `id_estado` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL,
  `id_beneficiario` int(11) NOT NULL,
  `nota` text DEFAULT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pago_tarjeta`
--

CREATE TABLE `pago_tarjeta` (
  `id_pago` int(11) NOT NULL,
  `id_tarjeta` int(11) NOT NULL,
  `fecha_pago` date NOT NULL,
  `monto_pago` decimal(15,2) NOT NULL CHECK (`monto_pago` >= 0),
  `referencia` varchar(100) DEFAULT NULL,
  `id_persona` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `id_persona` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo_electronico` varchar(100) NOT NULL,
  `usuario` varchar(45) NOT NULL,
  `hash_contrasena` varchar(255) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `activo` tinyint(4) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prestamo`
--

CREATE TABLE `prestamo` (
  `id_prestamo` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `id_estado` int(11) NOT NULL,
  `moneda` varchar(10) NOT NULL,
  `saldo_inicial` decimal(15,2) NOT NULL CHECK (`saldo_inicial` >= 0),
  `limite_credito` decimal(15,2) NOT NULL CHECK (`limite_credito` >= 0),
  `id_persona` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `presupuesto`
--

CREATE TABLE `presupuesto` (
  `id_presupuesto` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `monto_total` decimal(15,2) NOT NULL CHECK (`monto_total` >= 0),
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `id_persona` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `presupuesto_categoria`
--

CREATE TABLE `presupuesto_categoria` (
  `id_presupuesto` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id_producto` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `monto_maximo` decimal(15,2) DEFAULT NULL CHECK (`monto_maximo` >= 0),
  `monto_minimo` decimal(15,2) DEFAULT NULL CHECK (`monto_minimo` >= 0),
  `porcentaje_interes` decimal(5,2) DEFAULT NULL CHECK (`porcentaje_interes` >= 0),
  `id_tipo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarjeta_credito`
--

CREATE TABLE `tarjeta_credito` (
  `id_tarjeta` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `numero_tarjeta` char(16) NOT NULL,
  `limite_credito` decimal(15,2) NOT NULL CHECK (`limite_credito` >= 0),
  `saldo_actual` decimal(15,2) NOT NULL CHECK (`saldo_actual` >= 0),
  `fecha_corte` date NOT NULL,
  `fecha_pago` date NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `id_estado` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_movimiento`
--

CREATE TABLE `tipo_movimiento` (
  `id_tipo` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_producto`
--

CREATE TABLE `tipo_producto` (
  `id_tipo` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transaccion_programada`
--

CREATE TABLE `transaccion_programada` (
  `id_transaccion` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `id_tipo` int(11) NOT NULL,
  `monto` decimal(15,2) NOT NULL CHECK (`monto` >= 0),
  `id_frecuencia` int(11) NOT NULL,
  `repeticion` int(11) DEFAULT NULL,
  `id_categoria` int(11) NOT NULL,
  `id_beneficiario` int(11) NOT NULL,
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activo`
--
ALTER TABLE `activo`
  ADD PRIMARY KEY (`id_activo`),
  ADD KEY `id_persona` (`id_persona`);

--
-- Indices de la tabla `beneficiario`
--
ALTER TABLE `beneficiario`
  ADD PRIMARY KEY (`id_beneficiario`);

--
-- Indices de la tabla `categoria`
--
ALTER TABLE `categoria`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `estado_movimiento`
--
ALTER TABLE `estado_movimiento`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `estado_prestamo`
--
ALTER TABLE `estado_prestamo`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `estado_tarjeta`
--
ALTER TABLE `estado_tarjeta`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `frecuencia_transaccion`
--
ALTER TABLE `frecuencia_transaccion`
  ADD PRIMARY KEY (`id_frecuencia`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `movimiento`
--
ALTER TABLE `movimiento`
  ADD PRIMARY KEY (`id_movimiento`),
  ADD KEY `id_producto` (`id_producto`),
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_beneficiario` (`id_beneficiario`),
  ADD KEY `id_tipo` (`id_tipo`),
  ADD KEY `id_estado` (`id_estado`),
  ADD KEY `idx_mov_persona_fecha` (`id_persona`,`id_producto`,`id_estado`,`fecha_creacion`);

--
-- Indices de la tabla `pago_tarjeta`
--
ALTER TABLE `pago_tarjeta`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `id_tarjeta` (`id_tarjeta`),
  ADD KEY `id_persona` (`id_persona`);

--
-- Indices de la tabla `persona`
--
ALTER TABLE `persona`
  ADD PRIMARY KEY (`id_persona`),
  ADD UNIQUE KEY `correo_electronico` (`correo_electronico`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- Indices de la tabla `prestamo`
--
ALTER TABLE `prestamo`
  ADD PRIMARY KEY (`id_prestamo`),
  ADD KEY `id_persona` (`id_persona`),
  ADD KEY `id_estado` (`id_estado`);

--
-- Indices de la tabla `presupuesto`
--
ALTER TABLE `presupuesto`
  ADD PRIMARY KEY (`id_presupuesto`),
  ADD KEY `id_persona` (`id_persona`);

--
-- Indices de la tabla `presupuesto_categoria`
--
ALTER TABLE `presupuesto_categoria`
  ADD PRIMARY KEY (`id_presupuesto`,`id_categoria`),
  ADD KEY `id_categoria` (`id_categoria`);

--
-- Indices de la tabla `producto`
--
ALTER TABLE `producto`
  ADD PRIMARY KEY (`id_producto`),
  ADD UNIQUE KEY `nombre` (`nombre`),
  ADD KEY `id_tipo` (`id_tipo`);

--
-- Indices de la tabla `tarjeta_credito`
--
ALTER TABLE `tarjeta_credito`
  ADD PRIMARY KEY (`id_tarjeta`),
  ADD UNIQUE KEY `numero_tarjeta` (`numero_tarjeta`),
  ADD KEY `id_producto` (`id_producto`),
  ADD KEY `id_estado` (`id_estado`);

--
-- Indices de la tabla `tipo_movimiento`
--
ALTER TABLE `tipo_movimiento`
  ADD PRIMARY KEY (`id_tipo`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `tipo_producto`
--
ALTER TABLE `tipo_producto`
  ADD PRIMARY KEY (`id_tipo`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `transaccion_programada`
--
ALTER TABLE `transaccion_programada`
  ADD PRIMARY KEY (`id_transaccion`),
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_beneficiario` (`id_beneficiario`),
  ADD KEY `id_tipo` (`id_tipo`),
  ADD KEY `id_frecuencia` (`id_frecuencia`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activo`
--
ALTER TABLE `activo`
  MODIFY `id_activo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `beneficiario`
--
ALTER TABLE `beneficiario`
  MODIFY `id_beneficiario` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `categoria`
--
ALTER TABLE `categoria`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estado_movimiento`
--
ALTER TABLE `estado_movimiento`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estado_prestamo`
--
ALTER TABLE `estado_prestamo`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estado_tarjeta`
--
ALTER TABLE `estado_tarjeta`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `frecuencia_transaccion`
--
ALTER TABLE `frecuencia_transaccion`
  MODIFY `id_frecuencia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `movimiento`
--
ALTER TABLE `movimiento`
  MODIFY `id_movimiento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pago_tarjeta`
--
ALTER TABLE `pago_tarjeta`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prestamo`
--
ALTER TABLE `prestamo`
  MODIFY `id_prestamo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `presupuesto`
--
ALTER TABLE `presupuesto`
  MODIFY `id_presupuesto` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `producto`
--
ALTER TABLE `producto`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tarjeta_credito`
--
ALTER TABLE `tarjeta_credito`
  MODIFY `id_tarjeta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipo_movimiento`
--
ALTER TABLE `tipo_movimiento`
  MODIFY `id_tipo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipo_producto`
--
ALTER TABLE `tipo_producto`
  MODIFY `id_tipo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `transaccion_programada`
--
ALTER TABLE `transaccion_programada`
  MODIFY `id_transaccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `activo`
--
ALTER TABLE `activo`
  ADD CONSTRAINT `activo_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `movimiento`
--
ALTER TABLE `movimiento`
  ADD CONSTRAINT `movimiento_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `movimiento_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  ADD CONSTRAINT `movimiento_ibfk_3` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `movimiento_ibfk_4` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `movimiento_ibfk_5` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`),
  ADD CONSTRAINT `movimiento_ibfk_6` FOREIGN KEY (`id_estado`) REFERENCES `estado_movimiento` (`id_estado`);

--
-- Filtros para la tabla `pago_tarjeta`
--
ALTER TABLE `pago_tarjeta`
  ADD CONSTRAINT `pago_tarjeta_ibfk_1` FOREIGN KEY (`id_tarjeta`) REFERENCES `tarjeta_credito` (`id_tarjeta`),
  ADD CONSTRAINT `pago_tarjeta_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `prestamo`
--
ALTER TABLE `prestamo`
  ADD CONSTRAINT `prestamo_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  ADD CONSTRAINT `prestamo_ibfk_2` FOREIGN KEY (`id_estado`) REFERENCES `estado_prestamo` (`id_estado`);

--
-- Filtros para la tabla `presupuesto`
--
ALTER TABLE `presupuesto`
  ADD CONSTRAINT `presupuesto_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `presupuesto_categoria`
--
ALTER TABLE `presupuesto_categoria`
  ADD CONSTRAINT `presupuesto_categoria_ibfk_1` FOREIGN KEY (`id_presupuesto`) REFERENCES `presupuesto` (`id_presupuesto`),
  ADD CONSTRAINT `presupuesto_categoria_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`);

--
-- Filtros para la tabla `producto`
--
ALTER TABLE `producto`
  ADD CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_producto` (`id_tipo`);

--
-- Filtros para la tabla `tarjeta_credito`
--
ALTER TABLE `tarjeta_credito`
  ADD CONSTRAINT `tarjeta_credito_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
  ADD CONSTRAINT `tarjeta_credito_ibfk_2` FOREIGN KEY (`id_estado`) REFERENCES `estado_tarjeta` (`id_estado`);

--
-- Filtros para la tabla `transaccion_programada`
--
ALTER TABLE `transaccion_programada`
  ADD CONSTRAINT `transaccion_programada_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `transaccion_programada_ibfk_2` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `transaccion_programada_ibfk_3` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`),
  ADD CONSTRAINT `transaccion_programada_ibfk_4` FOREIGN KEY (`id_frecuencia`) REFERENCES `frecuencia_transaccion` (`id_frecuencia`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- SUGERENCIAS DE MEJORA

-- 1. Agregar ON DELETE/ON UPDATE CASCADE en las claves foráneas donde tenga sentido para evitar datos huérfanos.
-- Ejemplo para la tabla movimiento:
ALTER TABLE `movimiento`
  DROP FOREIGN KEY `movimiento_ibfk_1`,
  ADD CONSTRAINT `movimiento_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE;
-- Repetir para otras claves foráneas según la lógica de negocio.

-- 2. Agregar comentarios descriptivos a las tablas y columnas importantes.
-- Ejemplo:
ALTER TABLE `persona` COMMENT = 'Tabla que almacena los usuarios del sistema';

-- 3. Validar que los campos de contraseña siempre sean hash y nunca texto plano.

-- 4. Si usas MariaDB/MySQL 8+, puedes usar tipos de datos más específicos (por ejemplo, `JSON` para notas si lo requieres).

-- 5. Si alguna tabla requiere auditoría, agregar campos como `fecha_eliminacion`, `usuario_creacion`, etc.

-- Comentarios para tablas y columnas principales

ALTER TABLE `activo` COMMENT = 'Activos físicos o financieros registrados por una persona';
ALTER TABLE `activo` MODIFY `nombre_activo` varchar(100) COMMENT 'Nombre descriptivo del activo';
ALTER TABLE `activo` MODIFY `valor` decimal(15,2) COMMENT 'Valor monetario del activo';
ALTER TABLE `activo` MODIFY `depreciacion` decimal(15,2) COMMENT 'Depreciación acumulada del activo';
ALTER TABLE `activo` MODIFY `id_persona` int(11) COMMENT 'Referencia a la persona propietaria';

ALTER TABLE `beneficiario` COMMENT = 'Entidad o persona que recibe un pago o beneficio';
ALTER TABLE `beneficiario` MODIFY `nombre` varchar(100) COMMENT 'Nombre del beneficiario';

ALTER TABLE `categoria` COMMENT = 'Categoría para clasificar movimientos, activos, etc.';
ALTER TABLE `categoria` MODIFY `nombre` varchar(100) COMMENT 'Nombre de la categoría';

ALTER TABLE `estado_movimiento` COMMENT = 'Estados posibles para los movimientos financieros';
ALTER TABLE `estado_movimiento` MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado del movimiento';

ALTER TABLE `estado_prestamo` COMMENT = 'Estados posibles para préstamos';
ALTER TABLE `estado_prestamo` MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado del préstamo';

ALTER TABLE `estado_tarjeta` COMMENT = 'Estados posibles para tarjetas de crédito';
ALTER TABLE `estado_tarjeta` MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado de la tarjeta';

ALTER TABLE `frecuencia_transaccion` COMMENT = 'Frecuencia de ejecución para transacciones programadas';
ALTER TABLE `frecuencia_transaccion` MODIFY `nombre` varchar(20) COMMENT 'Nombre de la frecuencia';

ALTER TABLE `movimiento` COMMENT = 'Registro de movimientos financieros realizados';
ALTER TABLE `movimiento` MODIFY `codigo` varchar(45) COMMENT 'Código externo o identificador del movimiento';
ALTER TABLE `movimiento` MODIFY `monto` decimal(15,2) COMMENT 'Monto del movimiento';
ALTER TABLE `movimiento` MODIFY `id_tipo` int(11) COMMENT 'Tipo de movimiento (cargo/abono)';
ALTER TABLE `movimiento` MODIFY `cuotas` int(11) COMMENT 'Número de cuotas si aplica';
ALTER TABLE `movimiento` MODIFY `id_estado` int(11) COMMENT 'Estado del movimiento';
ALTER TABLE `movimiento` MODIFY `id_producto` int(11) COMMENT 'Producto asociado al movimiento';
ALTER TABLE `movimiento` MODIFY `id_persona` int(11) COMMENT 'Persona que realiza el movimiento';
ALTER TABLE `movimiento` MODIFY `id_categoria` int(11) COMMENT 'Categoría del movimiento';
ALTER TABLE `movimiento` MODIFY `id_beneficiario` int(11) COMMENT 'Beneficiario del movimiento';
ALTER TABLE `movimiento` MODIFY `nota` text COMMENT 'Nota o descripción adicional';

ALTER TABLE `pago_tarjeta` COMMENT = 'Pagos realizados a tarjetas de crédito';
ALTER TABLE `pago_tarjeta` MODIFY `id_tarjeta` int(11) COMMENT 'Tarjeta de crédito pagada';
ALTER TABLE `pago_tarjeta` MODIFY `fecha_pago` date COMMENT 'Fecha en que se realizó el pago';
ALTER TABLE `pago_tarjeta` MODIFY `monto_pago` decimal(15,2) COMMENT 'Monto pagado';
ALTER TABLE `pago_tarjeta` MODIFY `referencia` varchar(100) COMMENT 'Referencia o descripción del pago';
ALTER TABLE `pago_tarjeta` MODIFY `id_persona` int(11) COMMENT 'Persona que realizó el pago';

ALTER TABLE `persona` COMMENT = 'Usuarios registrados en el sistema';
ALTER TABLE `persona` MODIFY `nombre` varchar(100) COMMENT 'Nombre completo del usuario';
ALTER TABLE `persona` MODIFY `correo_electronico` varchar(100) COMMENT 'Correo electrónico único del usuario';
ALTER TABLE `persona` MODIFY `usuario` varchar(45) COMMENT 'Nombre de usuario único';
ALTER TABLE `persona` MODIFY `hash_contrasena` varchar(255) COMMENT 'Contraseña en formato hash';
ALTER TABLE `persona` MODIFY `fecha_creacion` datetime COMMENT 'Fecha de creación del usuario';
ALTER TABLE `persona` MODIFY `fecha_actualizacion` datetime COMMENT 'Fecha de última actualización';
ALTER TABLE `persona` MODIFY `activo` tinyint(4) COMMENT 'Indica si el usuario está activo';

ALTER TABLE `prestamo` COMMENT = 'Préstamos otorgados a personas';
ALTER TABLE `prestamo` MODIFY `fecha` date COMMENT 'Fecha de inicio del préstamo';
ALTER TABLE `prestamo` MODIFY `id_estado` int(11) COMMENT 'Estado actual del préstamo';
ALTER TABLE `prestamo` MODIFY `moneda` varchar(10) COMMENT 'Moneda del préstamo';
ALTER TABLE `prestamo` MODIFY `saldo_inicial` decimal(15,2) COMMENT 'Saldo inicial del préstamo';
ALTER TABLE `prestamo` MODIFY `limite_credito` decimal(15,2) COMMENT 'Límite de crédito del préstamo';
ALTER TABLE `prestamo` MODIFY `id_persona` int(11) COMMENT 'Persona que recibe el préstamo';

ALTER TABLE `presupuesto` COMMENT = 'Presupuestos definidos por los usuarios';
ALTER TABLE `presupuesto` MODIFY `nombre` varchar(100) COMMENT 'Nombre del presupuesto';
ALTER TABLE `presupuesto` MODIFY `descripcion` text COMMENT 'Descripción del presupuesto';
ALTER TABLE `presupuesto` MODIFY `monto_total` decimal(15,2) COMMENT 'Monto total asignado al presupuesto';
ALTER TABLE `presupuesto` MODIFY `fecha_inicio` date COMMENT 'Fecha de inicio del presupuesto';
ALTER TABLE `presupuesto` MODIFY `fecha_fin` date COMMENT 'Fecha de fin del presupuesto';
ALTER TABLE `presupuesto` MODIFY `id_persona` int(11) COMMENT 'Persona propietaria del presupuesto';

ALTER TABLE `presupuesto_categoria` COMMENT = 'Relación entre presupuestos y categorías';

ALTER TABLE `producto` COMMENT = 'Productos financieros disponibles';
ALTER TABLE `producto` MODIFY `nombre` varchar(100) COMMENT 'Nombre del producto';
ALTER TABLE `producto` MODIFY `monto_maximo` decimal(15,2) COMMENT 'Monto máximo permitido para el producto';
ALTER TABLE `producto` MODIFY `monto_minimo` decimal(15,2) COMMENT 'Monto mínimo permitido para el producto';
ALTER TABLE `producto` MODIFY `porcentaje_interes` decimal(5,2) COMMENT 'Porcentaje de interés aplicado';
ALTER TABLE `producto` MODIFY `id_tipo` int(11) COMMENT 'Tipo de producto';

ALTER TABLE `tarjeta_credito` COMMENT = 'Tarjetas de crédito asociadas a productos';
ALTER TABLE `tarjeta_credito` MODIFY `id_producto` int(11) COMMENT 'Producto asociado a la tarjeta';
ALTER TABLE `tarjeta_credito` MODIFY `numero_tarjeta` char(16) COMMENT 'Número único de la tarjeta de crédito';
ALTER TABLE `tarjeta_credito` MODIFY `limite_credito` decimal(15,2) COMMENT 'Límite de crédito de la tarjeta';
ALTER TABLE `tarjeta_credito` MODIFY `saldo_actual` decimal(15,2) COMMENT 'Saldo actual de la tarjeta';
ALTER TABLE `tarjeta_credito` MODIFY `fecha_corte` date COMMENT 'Fecha de corte de la tarjeta';
ALTER TABLE `tarjeta_credito` MODIFY `fecha_pago` date COMMENT 'Fecha límite de pago de la tarjeta';
ALTER TABLE `tarjeta_credito` MODIFY `id_estado` int(11) COMMENT 'Estado actual de la tarjeta';

ALTER TABLE `tipo_movimiento` COMMENT = 'Tipos de movimientos financieros';
ALTER TABLE `tipo_movimiento` MODIFY `nombre` varchar(20) COMMENT 'Nombre del tipo de movimiento';

ALTER TABLE `tipo_producto` COMMENT = 'Tipos de productos financieros';
ALTER TABLE `tipo_producto` MODIFY `nombre` varchar(50) COMMENT 'Nombre del tipo de producto';

ALTER TABLE `transaccion_programada` COMMENT = 'Transacciones programadas por los usuarios';
ALTER TABLE `transaccion_programada` MODIFY `fecha` date COMMENT 'Fecha de ejecución de la transacción';
ALTER TABLE `transaccion_programada` MODIFY `id_tipo` int(11) COMMENT 'Tipo de movimiento programado';
ALTER TABLE `transaccion_programada` MODIFY `monto` decimal(15,2) COMMENT 'Monto de la transacción programada';
ALTER TABLE `transaccion_programada` MODIFY `id_frecuencia` int(11) COMMENT 'Frecuencia de la transacción';
ALTER TABLE `transaccion_programada` MODIFY `repeticion` int(11) COMMENT 'Cantidad de repeticiones';
ALTER TABLE `transaccion_programada` MODIFY `id_categoria` int(11) COMMENT 'Categoría de la transacción';
ALTER TABLE `transaccion_programada` MODIFY `id_beneficiario` int(11) COMMENT 'Beneficiario de la transacción';
