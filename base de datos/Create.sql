-- --------------------------------------------------------
-- Tablas de catálogos y tipos
-- --------------------------------------------------------

CREATE TABLE `tipo_producto` (
    `id_tipo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tipo de producto',
    `nombre` varchar(50) NOT NULL COMMENT 'Nombre del tipo de producto',
    PRIMARY KEY (`id_tipo`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Tipos de productos financieros';

CREATE TABLE `tipo_movimiento` (
    `id_tipo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tipo de movimiento',
    `nombre` varchar(20) NOT NULL COMMENT 'Nombre del tipo de movimiento',
    PRIMARY KEY (`id_tipo`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Tipos de movimientos financieros';

CREATE TABLE `estado_movimiento` (
    `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
    `nombre` varchar(20) NOT NULL COMMENT 'Nombre del estado del movimiento',
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Estados posibles para los movimientos financieros';

CREATE TABLE `estado_prestamo` (
    `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
    `nombre` varchar(20) NOT NULL COMMENT 'Nombre del estado del préstamo',
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Estados posibles para préstamos';

CREATE TABLE `estado_tarjeta` (
    `id_estado` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
    `nombre` varchar(20) NOT NULL COMMENT 'Nombre del estado de la tarjeta',
    PRIMARY KEY (`id_estado`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Estados posibles para tarjetas de crédito';

CREATE TABLE `frecuencia_transaccion` (
    `id_frecuencia` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la frecuencia',
    `nombre` varchar(20) NOT NULL COMMENT 'Nombre de la frecuencia',
    PRIMARY KEY (`id_frecuencia`),
    UNIQUE KEY `nombre` (`nombre`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Frecuencia de ejecución para transacciones programadas';

-- --------------------------------------------------------
-- Tablas principales
-- --------------------------------------------------------

CREATE TABLE `persona` (
    `id_persona` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la persona',
    `nombre` varchar(100) NOT NULL COMMENT 'Nombre completo del usuario',
    `correo_electronico` varchar(100) NOT NULL COMMENT 'Correo electrónico único del usuario',
    `usuario` varchar(45) NOT NULL COMMENT 'Nombre de usuario único',
    `hash_contrasena` varchar(255) NOT NULL COMMENT 'Contraseña en formato hash',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del usuario',
    `fecha_actualizacion` datetime DEFAULT NULL ON UPDATE current_timestamp() COMMENT 'Fecha de última actualización',
    `activo` tinyint(4) NOT NULL DEFAULT 1 COMMENT 'Indica si el usuario está activo',
    PRIMARY KEY (`id_persona`),
    UNIQUE KEY `correo_electronico` (`correo_electronico`),
    UNIQUE KEY `usuario` (`usuario`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Usuarios registrados en el sistema';

CREATE TABLE `producto` (
    `id_producto` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del producto',
    `nombre` varchar(100) NOT NULL COMMENT 'Nombre del producto',
    `monto_maximo` decimal(15, 2) DEFAULT NULL COMMENT 'Monto máximo permitido para el producto' CHECK (`monto_maximo` >= 0),
    `monto_minimo` decimal(15, 2) DEFAULT NULL COMMENT 'Monto mínimo permitido para el producto' CHECK (`monto_minimo` >= 0),
    `porcentaje_interes` decimal(5, 2) DEFAULT NULL COMMENT 'Porcentaje de interés aplicado' CHECK (`porcentaje_interes` >= 0),
    `id_tipo` int(11) NOT NULL COMMENT 'Tipo de producto',
    PRIMARY KEY (`id_producto`),
    UNIQUE KEY `nombre` (`nombre`),
    KEY `id_tipo` (`id_tipo`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Productos financieros disponibles';

CREATE TABLE `categoria` (
    `id_categoria` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la categoría',
    `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la categoría',
    PRIMARY KEY (`id_categoria`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Categoría para clasificar movimientos, activos, etc.';

CREATE TABLE `beneficiario` (
    `id_beneficiario` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del beneficiario',
    `nombre` varchar(100) NOT NULL COMMENT 'Nombre del beneficiario',
    PRIMARY KEY (`id_beneficiario`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Entidad o persona que recibe un pago o beneficio';

-- --------------------------------------------------------
-- Tablas de operaciones y relaciones
-- --------------------------------------------------------

CREATE TABLE `movimiento` (
    `id_movimiento` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del movimiento',
    `codigo` varchar(45) DEFAULT NULL COMMENT 'Código externo o identificador del movimiento',
    `monto` decimal(15, 2) NOT NULL COMMENT 'Monto del movimiento' CHECK (`monto` >= 0),
    `id_tipo` int(11) NOT NULL COMMENT 'Tipo de movimiento (cargo/abono)',
    `cuotas` int(11) DEFAULT NULL COMMENT 'Número de cuotas si aplica',
    `id_estado` int(11) NOT NULL COMMENT 'Estado del movimiento',
    `id_producto` int(11) NOT NULL COMMENT 'Producto asociado al movimiento',
    `id_persona` int(11) NOT NULL COMMENT 'Persona que realiza el movimiento',
    `id_categoria` int(11) NOT NULL COMMENT 'Categoría del movimiento',
    `id_beneficiario` int(11) NOT NULL COMMENT 'Beneficiario del movimiento',
    `nota` text DEFAULT NULL COMMENT 'Nota o descripción adicional',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del movimiento',
    PRIMARY KEY (`id_movimiento`),
    KEY `id_producto` (`id_producto`),
    KEY `id_categoria` (`id_categoria`),
    KEY `id_beneficiario` (`id_beneficiario`),
    KEY `id_tipo` (`id_tipo`),
    KEY `id_estado` (`id_estado`),
    KEY `idx_mov_persona_fecha` (
        `id_persona`,
        `id_producto`,
        `id_estado`,
        `fecha_creacion`
    )
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Registro de movimientos financieros realizados';

CREATE TABLE `transaccion_programada` (
    `id_transaccion` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la transacción programada',
    `fecha` date NOT NULL COMMENT 'Fecha de ejecución de la transacción',
    `id_tipo` int(11) NOT NULL COMMENT 'Tipo de movimiento programado',
    `monto` decimal(15, 2) NOT NULL COMMENT 'Monto de la transacción programada' CHECK (`monto` >= 0),
    `id_frecuencia` int(11) NOT NULL COMMENT 'Frecuencia de la transacción',
    `repeticion` int(11) DEFAULT NULL COMMENT 'Cantidad de repeticiones',
    `id_categoria` int(11) NOT NULL COMMENT 'Categoría de la transacción',
    `id_beneficiario` int(11) NOT NULL COMMENT 'Beneficiario de la transacción',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación de la transacción',
    PRIMARY KEY (`id_transaccion`),
    KEY `id_categoria` (`id_categoria`),
    KEY `id_beneficiario` (`id_beneficiario`),
    KEY `id_tipo` (`id_tipo`),
    KEY `id_frecuencia` (`id_frecuencia`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Transacciones programadas por los usuarios';

CREATE TABLE `prestamo` (
    `id_prestamo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del préstamo',
    `fecha` date NOT NULL COMMENT 'Fecha de inicio del préstamo',
    `id_estado` int(11) NOT NULL COMMENT 'Estado actual del préstamo',
    `moneda` varchar(10) NOT NULL COMMENT 'Moneda del préstamo',
    `saldo_inicial` decimal(15, 2) NOT NULL COMMENT 'Saldo inicial del préstamo' CHECK (`saldo_inicial` >= 0),
    `limite_credito` decimal(15, 2) NOT NULL COMMENT 'Límite de crédito del préstamo' CHECK (`limite_credito` >= 0),
    `id_persona` int(11) NOT NULL COMMENT 'Persona que recibe el préstamo',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del préstamo',
    PRIMARY KEY (`id_prestamo`),
    KEY `id_persona` (`id_persona`),
    KEY `id_estado` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Préstamos otorgados a personas';

CREATE TABLE `activo` (
    `id_activo` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del activo',
    `nombre_activo` varchar(100) NOT NULL COMMENT 'Nombre descriptivo del activo',
    `valor` decimal(15, 2) NOT NULL COMMENT 'Valor monetario del activo' CHECK (`valor` >= 0),
    `depreciacion` decimal(15, 2) DEFAULT NULL COMMENT 'Depreciación acumulada del activo' CHECK (`depreciacion` >= 0),
    `id_persona` int(11) NOT NULL COMMENT 'Referencia a la persona propietaria',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del activo',
    PRIMARY KEY (`id_activo`),
    KEY `id_persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Activos físicos o financieros registrados por una persona';

CREATE TABLE `presupuesto` (
    `id_presupuesto` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del presupuesto',
    `nombre` varchar(100) NOT NULL COMMENT 'Nombre del presupuesto',
    `descripcion` text DEFAULT NULL COMMENT 'Descripción del presupuesto',
    `monto_total` decimal(15, 2) NOT NULL COMMENT 'Monto total asignado al presupuesto' CHECK (`monto_total` >= 0),
    `fecha_inicio` date NOT NULL COMMENT 'Fecha de inicio del presupuesto',
    `fecha_fin` date NOT NULL COMMENT 'Fecha de fin del presupuesto',
    `id_persona` int(11) NOT NULL COMMENT 'Persona propietaria del presupuesto',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del presupuesto',
    PRIMARY KEY (`id_presupuesto`),
    KEY `id_persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Presupuestos definidos por los usuarios';

CREATE TABLE `presupuesto_categoria` (
    `id_presupuesto` int(11) NOT NULL COMMENT 'Identificador del presupuesto',
    `id_categoria` int(11) NOT NULL COMMENT 'Identificador de la categoría',
    PRIMARY KEY (
        `id_presupuesto`,
        `id_categoria`
    ),
    KEY `id_categoria` (`id_categoria`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Relación entre presupuestos y categorías';

CREATE TABLE `tarjeta_credito` (
    `id_tarjeta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la tarjeta de crédito',
    `id_producto` int(11) NOT NULL COMMENT 'Producto asociado a la tarjeta',
    `numero_tarjeta` char(16) NOT NULL COMMENT 'Número único de la tarjeta de crédito',
    `limite_credito` decimal(15, 2) NOT NULL COMMENT 'Límite de crédito de la tarjeta' CHECK (`limite_credito` >= 0),
    `saldo_actual` decimal(15, 2) NOT NULL COMMENT 'Saldo actual de la tarjeta' CHECK (`saldo_actual` >= 0),
    `fecha_corte` date NOT NULL COMMENT 'Fecha de corte de la tarjeta',
    `fecha_pago` date NOT NULL COMMENT 'Fecha límite de pago de la tarjeta',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación de la tarjeta',
    `id_estado` int(11) NOT NULL COMMENT 'Estado actual de la tarjeta',
    PRIMARY KEY (`id_tarjeta`),
    UNIQUE KEY `numero_tarjeta` (`numero_tarjeta`),
    KEY `id_producto` (`id_producto`),
    KEY `id_estado` (`id_estado`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Tarjetas de crédito asociadas a productos';

CREATE TABLE `pago_tarjeta` (
    `id_pago` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del pago',
    `id_tarjeta` int(11) NOT NULL COMMENT 'Tarjeta de crédito pagada',
    `fecha_pago` date NOT NULL COMMENT 'Fecha en que se realizó el pago',
    `monto_pago` decimal(15, 2) NOT NULL COMMENT 'Monto pagado' CHECK (`monto_pago` >= 0),
    `referencia` varchar(100) DEFAULT NULL COMMENT 'Referencia o descripción del pago',
    `id_persona` int(11) NOT NULL COMMENT 'Persona que realizó el pago',
    `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del pago',
    PRIMARY KEY (`id_pago`),
    KEY `id_tarjeta` (`id_tarjeta`),
    KEY `id_persona` (`id_persona`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8 COLLATE = utf8_general_ci COMMENT = 'Pagos realizados a tarjetas de crédito';

-- --------------------------------------------------------
-- Tablas adicionales
-- --------------------------------------------------------

CREATE TABLE parametro_dian (
    id_parametro INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL,
    concepto VARCHAR(150) NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    unidad VARCHAR(50) DEFAULT 'COP',
    descripcion TEXT
);

CREATE TABLE accion (
    id_accion INT AUTO_INCREMENT PRIMARY KEY,
    simbolo VARCHAR(10) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio_compra DECIMAL(15, 2) NOT NULL,
    fecha_compra DATE NOT NULL,
    precio_actual DECIMAL(15, 2),
    mercado VARCHAR(50) DEFAULT 'BVC',
    id_persona INT
);

CREATE TABLE fondo (
    id_fondo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM(
        'Mutuo',
        'ETF',
        'Pensión',
        'Otro'
    ) NOT NULL,
    entidad VARCHAR(100) NOT NULL,
    monto_invertido DECIMAL(15, 2) NOT NULL,
    fecha_inversion DATE NOT NULL,
    valor_actual DECIMAL(15, 2),
    rentabilidad DECIMAL(6, 2),
    id_persona INT
);