# tablas para la base de datos de gestión financiera personal
CREATE TABLE IF NOT EXISTS `mydb`.`moneda` (
    `codigo` VARCHAR(10) NOT NULL,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`codigo`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`estado_movimiento` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`estado_prestamo` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`estado_tarjeta` (
    `id_estado` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`persona` (
    `id_persona` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    `correo_electronico` VARCHAR(100) NULL DEFAULT NULL,
    `usuario` VARCHAR(45) NULL DEFAULT NULL,
    `hash_contrasena` VARCHAR(255) NULL DEFAULT NULL,
    `fecha_creacion` DATETIME NULL DEFAULT NULL,
    `fecha_actualizacion` DATETIME NULL DEFAULT NULL,
    `activo` TINYINT(4) NULL DEFAULT NULL,
    PRIMARY KEY (`id_persona`),
    UNIQUE INDEX `correo_electronico` (`correo_electronico` ASC) VISIBLE,
    UNIQUE INDEX `usuario` (`usuario` ASC) VISIBLE
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`accion` (
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

CREATE TABLE IF NOT EXISTS `mydb`.`activo` (
    `id_activo` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre_activo` VARCHAR(100) NULL DEFAULT NULL,
    `valor` DECIMAL(15, 2) NULL DEFAULT NULL,
    `depreciacion` DECIMAL(15, 2) NULL DEFAULT NULL,
    `id_persona` INT(11) NULL DEFAULT NULL,
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id_activo`),
    INDEX `idx_activo_persona` (`id_persona` ASC) VISIBLE,
    CONSTRAINT `fk_activo_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`beneficiario` (
    `id_beneficiario` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    PRIMARY KEY (`id_beneficiario`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`categoria` (
    `id_categoria` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(100) NULL DEFAULT NULL,
    PRIMARY KEY (`id_categoria`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`deuda_financiada` (
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
    INDEX `fk_deuda_persona` (`id_persona` ASC) VISIBLE,
    CONSTRAINT `fk_deuda_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`tipo_movimiento` (
    `id_tipo` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(20) NULL DEFAULT NULL,
    PRIMARY KEY (`id_tipo`),
    UNIQUE INDEX `nombre` (`nombre` ASC) VISIBLE
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`cuenta` (
    `id_cuenta` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `id_persona` INT UNSIGNED NOT NULL,
    `nombre` VARCHAR(100) NOT NULL,
    `tipo` VARCHAR(50) NOT NULL,
    `saldo_inicial` DECIMAL(15, 2) NOT NULL DEFAULT 0,
    `moneda` VARCHAR(10) NOT NULL DEFAULT 'COP',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id_cuenta`),
    INDEX `fk_cuenta_persona` (`id_persona` ASC) VISIBLE,
    CONSTRAINT `fk_cuenta_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `mydb`.`movimiento` (
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
    `id_cuenta` INT UNSIGNED NOT NULL COMMENT 'Cuenta asociada al movimiento',
    PRIMARY KEY (`id_movimiento`),
    INDEX `fk_movimiento_categoria` (`id_categoria` ASC),
    INDEX `fk_movimiento_beneficiario` (`id_beneficiario` ASC),
    INDEX `fk_movimiento_tipo` (`id_tipo` ASC),
    INDEX `fk_movimiento_estado` (`id_estado` ASC),
    INDEX `fk_movimiento_cuenta_idx` (`id_cuenta` ASC),
    CONSTRAINT `fk_movimiento_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `mydb`.`beneficiario` (`id_beneficiario`),
    CONSTRAINT `fk_movimiento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_movimiento_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `mydb`.`tipo_movimiento` (`id_tipo`),
    CONSTRAINT `fk_movimiento_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_movimiento` (`id_estado`),
    CONSTRAINT `fk_movimiento_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `mydb`.`cuenta` (`id_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Registro de movimientos financieros realizados';

CREATE TABLE IF NOT EXISTS `mydb`.`prestamo` (
    `id_prestamo` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del préstamo',
    `fecha` DATE NULL DEFAULT NULL COMMENT 'Fecha de inicio del préstamo',
    `id_estado` INT(11) NULL DEFAULT NULL COMMENT 'Estado actual del préstamo',
    `moneda` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Moneda del préstamo',
    `saldo_inicial` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Saldo inicial del préstamo',
    `limite_credito` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Límite de crédito del préstamo',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación del préstamo',
    `id_persona` INT(11) NULL DEFAULT NULL COMMENT 'Referencia al usuario que recibe el préstamo',
    PRIMARY KEY (`id_prestamo`),
    INDEX `fk_prestamo_persona` (`id_persona` ASC),
    INDEX `fk_prestamo_estado` (`id_estado` ASC),
    CONSTRAINT `fk_prestamo_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`),
    CONSTRAINT `fk_prestamo_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_prestamo` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Préstamos otorgados a personas';

CREATE TABLE IF NOT EXISTS `mydb`.`presupuesto` (
    `id_presupuesto` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del presupuesto',
    `nombre` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Nombre del presupuesto',
    `descripcion` TEXT NULL DEFAULT NULL COMMENT 'Descripción del presupuesto',
    `monto_total` DECIMAL(15, 2) NULL DEFAULT NULL COMMENT 'Monto total asignado al presupuesto',
    `fecha_inicio` DATE NULL DEFAULT NULL COMMENT 'Fecha de inicio del presupuesto',
    `fecha_fin` DATE NULL DEFAULT NULL COMMENT 'Fecha de fin del presupuesto',
    `id_persona` INT(11) NULL DEFAULT NULL COMMENT 'Persona propietaria del presupuesto',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Fecha de creación del presupuesto',
    PRIMARY KEY (`id_presupuesto`),
    INDEX `idx_presupuesto_persona` (`id_persona` ASC) VISIBLE,
    CONSTRAINT `fk_presupuesto_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Presupuestos definidos por los usuarios';

CREATE TABLE IF NOT EXISTS `mydb`.`presupuesto_categoria` (
    `id_presupuesto` INT(11) NOT NULL COMMENT 'Identificador del presupuesto',
    `id_categoria` INT(11) NOT NULL COMMENT 'Identificador de la categoría',
    PRIMARY KEY (
        `id_presupuesto`,
        `id_categoria`
    ),
    INDEX `fk_presupuesto_categoria_categoria` (`id_categoria` ASC) VISIBLE,
    CONSTRAINT `fk_presupuesto_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_presupuesto_categoria_presupuesto` FOREIGN KEY (`id_presupuesto`) REFERENCES `mydb`.`presupuesto` (`id_presupuesto`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Relación entre presupuestos y categorías';

CREATE TABLE IF NOT EXISTS `mydb`.`tarjeta_credito` (
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
    UNIQUE INDEX `numero_tarjeta` (`numero_tarjeta` ASC) VISIBLE,
    INDEX `idx_tc_numero` (`numero_tarjeta` ASC) VISIBLE,
    INDEX `fk_tc_estado` (`id_estado` ASC),
    CONSTRAINT `fk_tc_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_tarjeta` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Tarjetas de crédito asociadas a productos';

CREATE TABLE IF NOT EXISTS `mydb`.`transaccion_programada` (
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
    INDEX `fk_tp_categoria` (`id_categoria` ASC) VISIBLE,
    INDEX `fk_tp_beneficiario` (`id_beneficiario` ASC) VISIBLE,
    INDEX `fk_tp_tipo` (`id_tipo` ASC) VISIBLE,
    CONSTRAINT `fk_tp_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `mydb`.`beneficiario` (`id_beneficiario`),
    CONSTRAINT `fk_tp_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_tp_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `mydb`.`tipo_movimiento` (`id_tipo`)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Transacciones programadas por los usuarios';

CREATE TABLE IF NOT EXISTS `mydb`.`prestamo_movimiento` (
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
    INDEX `fk_persona_has_prestamo_prestamo1_idx` (`prestamo_id_prestamo` ASC) VISIBLE,
    INDEX `fk_persona_has_prestamo_persona1_idx` (`persona_id_persona` ASC) VISIBLE,
    CONSTRAINT `fk_persona_has_prestamo_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `mydb`.`persona` (`id_persona`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `fk_persona_has_prestamo_prestamo1` FOREIGN KEY (`prestamo_id_prestamo`) REFERENCES `mydb`.`prestamo` (`id_prestamo`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COMMENT = 'Movimientos asociados a préstamos';

CREATE TABLE IF NOT EXISTS `mydb`.`movimiento_tarjeta` (
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
    CONSTRAINT `fk_mt_tarjeta` FOREIGN KEY (`id_tarjeta`) REFERENCES `mydb`.`tarjeta_credito` (`id_tarjeta`),
    CONSTRAINT `fk_mt_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`),
    CONSTRAINT `fk_mt_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
    CONSTRAINT `fk_mt_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `mydb`.`beneficiario` (`id_beneficiario`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COMMENT = 'Movimientos asociados a tarjetas de crédito';

-- ===========================
-- DATOS DE PRUEBA (INSERTS)
-- ===========================

-- Monedas
INSERT INTO moneda (codigo, nombre) VALUES
  ('COP', 'Peso Colombiano'),
  ('USD', 'Dólar Estadounidense'),
  ('EUR', 'Euro');

-- Estados
INSERT INTO estado_movimiento (nombre) VALUES ('pendiente'), ('realizado'), ('anulado');
INSERT INTO estado_prestamo (nombre) VALUES ('activo'), ('pagado'), ('vencido');
INSERT INTO estado_tarjeta (nombre) VALUES ('activa'), ('bloqueada'), ('cancelada');

-- Personas
INSERT INTO persona (nombre, correo_electronico, usuario, hash_contrasena, fecha_creacion, activo)
VALUES
  ('Juan Pérez', 'juan@example.com', 'juanp', 'hash1', NOW(), 1),
  ('Ana Gómez', 'ana@example.com', 'anag', 'hash2', NOW(), 1);

-- Cuentas
INSERT INTO cuenta (id_persona, nombre, tipo, saldo_inicial, moneda, fecha_creacion)
VALUES
  (1, 'Cuenta Ahorros', 'ahorro', 1000000, 'COP', NOW()),
  (2, 'Cuenta Corriente', 'corriente', 500000, 'COP', NOW());

-- Categorías
INSERT INTO categoria (nombre) VALUES ('Alimentación'), ('Transporte'), ('Salud'), ('Entretenimiento');

-- Beneficiarios
INSERT INTO beneficiario (nombre) VALUES ('Supermercado XYZ'), ('Clínica ABC'), ('Cine 123');

-- Tipos de movimiento
INSERT INTO tipo_movimiento (nombre) VALUES ('ingreso'), ('gasto');

-- Movimientos
INSERT INTO movimiento (codigo, monto, id_tipo, id_estado, id_categoria, id_beneficiario, fecha_creacion, id_cuenta, nota)
VALUES
  ('M001', 200000, 2, 2, 1, 1, NOW(), 1, 'Compra supermercado'),
  ('M002', 150000, 2, 2, 2, NULL, NOW(), 1, 'Taxi'),
  ('M003', 50000, 1, 2, 1, NULL, NOW(), 2, 'Ingreso extra');

-- Presupuestos
INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
VALUES
  ('Presupuesto Mensual Juan', 'Presupuesto de gastos mensuales', 1200000, '2024-06-01', '2024-06-30', 1, NOW());

-- Presupuesto-Categoría
INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (1, 1), (1, 2);

-- Préstamos
INSERT INTO prestamo (fecha, id_estado, moneda, saldo_inicial, limite_credito, fecha_creacion, id_persona)
VALUES
  ('2024-01-01', 1, 'COP', 500000, 500000, NOW(), 1);

-- Préstamo-Movimiento
INSERT INTO prestamo_movimiento (persona_id_persona, prestamo_id_prestamo, valor, interes, numero_transaccion, seguro, saldo)
VALUES
  (1, 1, 100000, 2.5, 'TRX001', 1000, 400000);

-- Tarjetas de crédito
INSERT INTO tarjeta_credito (id_producto, numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, fecha_creacion, id_estado)
VALUES
  (NULL, '1234567890123456', 2000000, 500000, '2024-06-20', '2024-07-05', NOW(), 1);

-- Movimiento Tarjeta
INSERT INTO movimiento_tarjeta (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, saldo, cuotas)
VALUES
  (1, 1, NOW(), 100000, 'compra', 'Compra en tienda', 'MT001', 1, 1, 400000, 1),
  (1, 1, NOW(), 50000, 'abono', 'Pago tarjeta', 'MT002', NULL, NULL, 350000, 1);

-- Activos
INSERT INTO activo (nombre_activo, valor, depreciacion, id_persona, fecha_creacion)
VALUES
  ('Laptop', 3000000, 500000, 1, NOW()),
  ('Bicicleta', 800000, 100000, 2, NOW());

-- Acciones
INSERT INTO accion (simbolo, empresa, cantidad, precio_compra, fecha_compra, precio_actual, mercado, id_persona)
VALUES
  ('AAPL', 'Apple Inc.', 10, 150, '2024-01-15', 180, 'NASDAQ', 1),
  ('ECOPETROL', 'Ecopetrol S.A.', 50, 2500, '2024-02-10', 2700, 'BVC', 2);

-- Deuda financiada
INSERT INTO deuda_financiada (entidad, monto_inicial, saldo_actual, numero_transaccion, tasa_interes, fecha_inicio, fecha_fin, id_persona)
VALUES
  ('Banco ABC', 1000000, 800000, 'DF001', 1.5, '2024-01-01', '2025-01-01', 1);
