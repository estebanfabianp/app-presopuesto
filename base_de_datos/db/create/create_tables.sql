# tablas para la base de datos de gestión financiera personal
CREATE TABLE IF NOT EXISTS `app_presupuesto`.`moneda` (
    `codigo` VARCHAR(10) NOT NULL,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`codigo`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`estado_movimiento` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`estado_prestamo` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`estado_tarjeta` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`persona` (
    `id_persona` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    `correo_electronico` VARCHAR(100) NULL DEFAULT NULL,
    `usuario` VARCHAR(45) NULL DEFAULT NULL,
    `hash_contrasena` VARCHAR(255) NULL DEFAULT NULL,
    `fecha_creacion` DATETIME NULL DEFAULT NULL,
    `fecha_actualizacion` DATETIME NULL DEFAULT NULL,
    `estado` TINYINT(1) NULL DEFAULT NULL,
    PRIMARY KEY (`id_persona`),
    UNIQUE KEY `correo_electronico` (`correo_electronico`),
    UNIQUE KEY `usuario` (`usuario`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`accion` (
    `id_accion` INT(11) NOT NULL AUTO_INCREMENT,
    `simbolo` VARCHAR(10) NULL DEFAULT NULL,
    `empresa` VARCHAR(100) NULL DEFAULT NULL,
    `cantidad` INT(11) NULL DEFAULT NULL,
    `precio_compra` DECIMAL(15, 2) NULL DEFAULT NULL,
    `fecha_compra` DATE NULL DEFAULT NULL,
    `precio_actual` DECIMAL(15, 2) NULL DEFAULT NULL,
    `mercado` VARCHAR(50) NULL DEFAULT NULL,
    `id_persona` INT(11) NULL DEFAULT NULL,
    PRIMARY KEY (`id_accion`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`activo` (
    `id_activo` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre_activo` VARCHAR(100) NULL DEFAULT NULL,
    `valor` DECIMAL(15, 2) NULL DEFAULT NULL,
    `depreciacion` DECIMAL(15, 2) NULL DEFAULT NULL,
    `id_persona` INT(11) NULL DEFAULT NULL,
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id_activo`),
    KEY `idx_activo_persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`beneficiario` (
    `id_beneficiario` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    PRIMARY KEY (`id_beneficiario`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`categoria` (
    `id_categoria` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    PRIMARY KEY (`id_categoria`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`deuda_financiada` (
    `id_deuda` INT(11) NOT NULL AUTO_INCREMENT,
    `entidad` VARCHAR(100) NOT NULL,
    `monto_inicial` DECIMAL(15, 2) NOT NULL,
    `saldo_actual` DECIMAL(15, 2) NOT NULL,
    `numero_transaccion` VARCHAR(45) NULL,
    `tasa_interes` DECIMAL(5, 2) NOT NULL,
    `fecha_inicio` DATE NOT NULL,
    `fecha_fin` DATE NOT NULL,
    `id_persona` INT(11) NULL DEFAULT NULL,
    PRIMARY KEY (`id_deuda`),
    INDEX `fk_deuda_persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`tipo_movimiento` (
    `id_tipo` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(20) NULL DEFAULT NULL,
    PRIMARY KEY (`id_tipo`),
    UNIQUE INDEX `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`cuenta` (
    `id_cuenta` INT(11) NOT NULL AUTO_INCREMENT,
    `id_persona` INT(11) NOT NULL,
    `nombre` VARCHAR(100) NOT NULL,
    `tipo` VARCHAR(50) NOT NULL,
    `saldo_inicial` DECIMAL(15, 2) NOT NULL DEFAULT 0,
    `moneda` VARCHAR(10) NOT NULL DEFAULT 'COP',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id_cuenta`),
    INDEX `fk_cuenta_persona` (`id_persona`),
    CONSTRAINT `fk_cuenta_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`movimiento` (
    `id_movimiento` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del movimiento',
    `codigo` VARCHAR(45) NULL DEFAULT NULL COMMENT 'Código externo o identificador del movimiento',
    `monto` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Monto del movimiento',
    `id_tipo` INT(11) NULL DEFAULT NULL COMMENT 'Tipo de movimiento (cargo/abono)',
    `id_estado` INT(11) NULL DEFAULT NULL COMMENT 'Estado del movimiento',
    `id_producto` INT(11) NULL DEFAULT NULL COMMENT 'Producto asociado al movimiento',
    `id_categoria` INT(11) NULL DEFAULT NULL COMMENT 'Categoría del movimiento',
    `id_beneficiario` INT(11) NULL DEFAULT NULL COMMENT 'Beneficiario del movimiento',
    `numero_transaccion` VARCHAR(45) NULL COMMENT 'Número de transacción asociada',
    `nota` TEXT NULL DEFAULT NULL COMMENT 'Nota o descripción adicional',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación del movimiento',
    `id_cuenta` INT(11) NOT NULL COMMENT 'Cuenta asociada al movimiento',
    PRIMARY KEY (`id_movimiento`),
    INDEX `fk_movimiento_categoria` (`id_categoria`),
    INDEX `fk_movimiento_beneficiario` (`id_beneficiario`),
    INDEX `fk_movimiento_tipo` (`id_tipo`),
    INDEX `fk_movimiento_estado` (`id_estado`),
    INDEX `fk_movimiento_cuenta_idx` (`id_cuenta`),
    CONSTRAINT `fk_movimiento_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `app_presupuesto`.`beneficiario` (`id_beneficiario`),
    CONSTRAINT `fk_movimiento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_movimiento_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `app_presupuesto`.`tipo_movimiento` (`id_tipo`),
    CONSTRAINT `fk_movimiento_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_movimiento` (`id_estado`),
    CONSTRAINT `fk_movimiento_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `app_presupuesto`.`cuenta` (`id_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Registro de movimientos financieros realizados';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`prestamo` (
    `id_prestamo` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del préstamo',
    `fecha` DATE NULL DEFAULT NULL COMMENT 'Fecha de inicio del préstamo',
    `id_estado` INT(11) NULL DEFAULT NULL COMMENT 'Estado actual del préstamo',
    `moneda` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Moneda del préstamo',
    `saldo_inicial` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Saldo inicial del préstamo',
    `limite_credito` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Límite de crédito del préstamo',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación del préstamo',
    `id_persona` INT(11) NULL DEFAULT NULL COMMENT 'Referencia al usuario que recibe el préstamo',
    PRIMARY KEY (`id_prestamo`),
    INDEX `fk_prestamo_persona` (`id_persona`),
    INDEX `fk_prestamo_estado` (`id_estado`),
    CONSTRAINT `fk_prestamo_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`),
    CONSTRAINT `fk_prestamo_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_prestamo` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Préstamos otorgados a personas';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`presupuesto` (
    `id_presupuesto` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del presupuesto',
    `nombre` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Nombre del presupuesto',
    `descripcion` TEXT NULL DEFAULT NULL COMMENT 'Descripción del presupuesto',
    `monto_total` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Monto total asignado al presupuesto',
    `fecha_inicio` DATE NULL DEFAULT NULL COMMENT 'Fecha de inicio del presupuesto',
    `fecha_fin` DATE NULL DEFAULT NULL COMMENT 'Fecha de fin del presupuesto',
    `id_persona` INT(11) NULL DEFAULT NULL COMMENT 'Persona propietaria del presupuesto',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación del presupuesto',
    PRIMARY KEY (`id_presupuesto`),
    INDEX `idx_presupuesto_persona` (`id_persona`),
    CONSTRAINT `fk_presupuesto_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Presupuestos definidos por los usuarios';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`presupuesto_categoria` (
    `id_presupuesto` INT(11) NOT NULL COMMENT 'Identificador del presupuesto',
    `id_categoria` INT(11) NOT NULL COMMENT 'Identificador de la categoría',
    PRIMARY KEY (
        `id_presupuesto`,
        `id_categoria`
    ),
    INDEX `fk_presupuesto_categoria_categoria` (`id_categoria`),
    CONSTRAINT `fk_presupuesto_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_presupuesto_categoria_presupuesto` FOREIGN KEY (`id_presupuesto`) REFERENCES `app_presupuesto`.`presupuesto` (`id_presupuesto`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Relación entre presupuestos y categorías';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`tarjeta_credito` (
    `id_tarjeta` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la tarjeta',
    `id_producto` INT(11) NULL DEFAULT NULL COMMENT 'Producto asociado a la tarjeta',
    `numero_tarjeta` CHAR(16) NULL DEFAULT NULL COMMENT 'Número único de la tarjeta de crédito',
    `limite_credito` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Límite de crédito de la tarjeta',
    `saldo_actual` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Saldo actual de la tarjeta',
    `fecha_corte` DATE NULL DEFAULT NULL COMMENT 'Fecha de corte de la tarjeta',
    `fecha_pago` DATE NULL DEFAULT NULL COMMENT 'Fecha límite de pago de la tarjeta',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación de la tarjeta',
    `id_estado` INT(11) NULL DEFAULT NULL COMMENT 'Estado actual de la tarjeta',
    PRIMARY KEY (`id_tarjeta`),
    UNIQUE INDEX `numero_tarjeta` (`numero_tarjeta`),
    INDEX `idx_tc_numero` (`numero_tarjeta`),
    INDEX `fk_tc_estado` (`id_estado`),
    CONSTRAINT `fk_tc_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_tarjeta` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Tarjetas de crédito asociadas a productos';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`transaccion_programada` (
    `id_transaccion` INT(11) NOT NULL COMMENT 'Identificador único de la transacción programada',
    `fecha` DATE NULL DEFAULT NULL COMMENT 'Fecha de ejecución de la transacción',
    `id_tipo` INT(11) NULL DEFAULT NULL COMMENT 'Tipo de movimiento programado',
    `numero_transaccion` VARCHAR(45) NULL COMMENT 'Número de transacción asociada',
    `monto` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Monto de la transacción programada',
    `repeticion` INT(11) NULL DEFAULT NULL COMMENT 'Cantidad de repeticiones',
    `id_categoria` INT(11) NULL DEFAULT NULL COMMENT 'Categoría de la transacción',
    `id_beneficiario` INT(11) NULL DEFAULT NULL COMMENT 'Beneficiario de la transacción',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación de la transacción programada',
    PRIMARY KEY (`id_transaccion`),
    INDEX `fk_tp_categoria` (`id_categoria`),
    INDEX `fk_tp_beneficiario` (`id_beneficiario`),
    INDEX `fk_tp_tipo` (`id_tipo`),
    CONSTRAINT `fk_tp_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `app_presupuesto`.`beneficiario` (`id_beneficiario`),
    CONSTRAINT `fk_tp_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_tp_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `app_presupuesto`.`tipo_movimiento` (`id_tipo`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Transacciones programadas por los usuarios';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`prestamo_movimiento` (
    `persona_id_persona` INT(11) NOT NULL COMMENT 'Identificador de la persona',
    `prestamo_id_prestamo` INT(11) NOT NULL COMMENT 'Identificador del préstamo',
    `valor` DECIMAL(15, 2) NULL COMMENT 'Valor del movimiento',
    `interes` DECIMAL(5, 2) NULL COMMENT 'Interés aplicado',
    `numero_transaccion` VARCHAR(45) NULL COMMENT 'Número de transacción asociada',
    `seguro` DECIMAL(15, 2) NULL COMMENT 'Valor del seguro',
    `saldo` DECIMAL(15, 2) NULL COMMENT 'Saldo restante',
    PRIMARY KEY (
        `persona_id_persona`,
        `prestamo_id_prestamo`
    ),
    INDEX `fk_persona_has_prestamo_prestamo1_idx` (`prestamo_id_prestamo`),
    INDEX `fk_persona_has_prestamo_persona1_idx` (`persona_id_persona`),
    CONSTRAINT `fk_persona_has_prestamo_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `fk_persona_has_prestamo_prestamo1` FOREIGN KEY (`prestamo_id_prestamo`) REFERENCES `app_presupuesto`.`prestamo` (`id_prestamo`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Movimientos asociados a préstamos';

CREATE TABLE IF NOT EXISTS `app_presupuesto`.`movimiento_tarjeta` (
    `id_movimiento_tarjeta` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del movimiento de tarjeta',
    `id_tarjeta` INT(11) NOT NULL COMMENT 'Identificador de la tarjeta de crédito',
    `id_persona` INT(11) NOT NULL COMMENT 'Identificador de la persona',
    `fecha` DATE NULL COMMENT 'Fecha del movimiento',
    `valor` DECIMAL(15, 2) NULL COMMENT 'Valor del movimiento',
    `estado` VARCHAR(45) NULL COMMENT 'Estado del movimiento',
    `nota` VARCHAR(255) NULL COMMENT 'Nota o descripción adicional',
    `numero_transaccion` VARCHAR(45) NULL COMMENT 'Número de transacción asociada',
    `id_categoria` INT(11) NULL COMMENT 'Identificador de la categoría',
    `id_beneficiario` INT(11) NULL COMMENT 'Identificador del beneficiario',
    `saldo` DECIMAL(15, 2) NULL COMMENT 'Saldo restante',
    `cuotas` INT NULL COMMENT 'Número de cuotas',
    PRIMARY KEY (`id_movimiento_tarjeta`),
    INDEX `fk_mt_tarjeta` (`id_tarjeta`),
    INDEX `fk_mt_persona` (`id_persona`),
    INDEX `fk_mt_categoria` (`id_categoria`),
    INDEX `fk_mt_beneficiario` (`id_beneficiario`),
    CONSTRAINT `fk_mt_tarjeta` FOREIGN KEY (`id_tarjeta`) REFERENCES `app_presupuesto`.`tarjeta_credito` (`id_tarjeta`),
    CONSTRAINT `fk_mt_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`),
    CONSTRAINT `fk_mt_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_mt_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `app_presupuesto`.`beneficiario` (`id_beneficiario`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COMMENT = 'Movimientos asociados a tarjetas de crédito';

-- Agrega las claves foráneas después de la creación de las tablas
