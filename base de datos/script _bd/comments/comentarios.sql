ALTER TABLE `activo` COMMENT = 'Activos físicos o financieros registrados por una persona';

ALTER TABLE `activo`
MODIFY `nombre_activo` varchar(100) COMMENT 'Nombre descriptivo del activo';

ALTER TABLE `activo`
MODIFY `valor` decimal(15, 2) COMMENT 'Valor monetario del activo';

ALTER TABLE `activo`
MODIFY `depreciacion` decimal(15, 2) COMMENT 'Depreciación acumulada del activo';

ALTER TABLE `activo`
MODIFY `id_persona` int(11) COMMENT 'Referencia a la persona propietaria';

ALTER TABLE `beneficiario` COMMENT = 'Entidad o persona que recibe un pago o beneficio';

ALTER TABLE `beneficiario`
MODIFY `nombre` varchar(100) COMMENT 'Nombre del beneficiario';

ALTER TABLE `categoria` COMMENT = 'Categoría para clasificar movimientos, activos, etc.';

ALTER TABLE `categoria`
MODIFY `nombre` varchar(100) COMMENT 'Nombre de la categoría';

ALTER TABLE `estado_movimiento` COMMENT = 'Estados posibles para los movimientos financieros';

ALTER TABLE `estado_movimiento`
MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado del movimiento';

ALTER TABLE `estado_prestamo` COMMENT = 'Estados posibles para préstamos';

ALTER TABLE `estado_prestamo`
MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado del préstamo';

ALTER TABLE `estado_tarjeta` COMMENT = 'Estados posibles para tarjetas de crédito';

ALTER TABLE `estado_tarjeta`
MODIFY `nombre` varchar(20) COMMENT 'Nombre del estado de la tarjeta';

ALTER TABLE `frecuencia_transaccion` COMMENT = 'Frecuencia de ejecución para transacciones programadas';

ALTER TABLE `frecuencia_transaccion`
MODIFY `nombre` varchar(20) COMMENT 'Nombre de la frecuencia';

ALTER TABLE `movimiento` COMMENT = 'Registro de movimientos financieros realizados';

ALTER TABLE `movimiento`
MODIFY `codigo` varchar(45) COMMENT 'Código externo o identificador del movimiento';

ALTER TABLE `movimiento`
MODIFY `monto` decimal(15, 2) COMMENT 'Monto del movimiento';

ALTER TABLE `movimiento`
MODIFY `id_tipo` int(11) COMMENT 'Tipo de movimiento (cargo/abono)';

ALTER TABLE `movimiento`
MODIFY `cuotas` int(11) COMMENT 'Número de cuotas si aplica';

ALTER TABLE `movimiento`
MODIFY `id_estado` int(11) COMMENT 'Estado del movimiento';

ALTER TABLE `movimiento`
MODIFY `id_producto` int(11) COMMENT 'Producto asociado al movimiento';

ALTER TABLE `movimiento`
MODIFY `id_persona` int(11) COMMENT 'Persona que realiza el movimiento';

ALTER TABLE `movimiento`
MODIFY `id_categoria` int(11) COMMENT 'Categoría del movimiento';

ALTER TABLE `movimiento`
MODIFY `id_beneficiario` int(11) COMMENT 'Beneficiario del movimiento';

ALTER TABLE `movimiento`
MODIFY `nota` text COMMENT 'Nota o descripción adicional';

ALTER TABLE `pago_tarjeta` COMMENT = 'Pagos realizados a tarjetas de crédito';

ALTER TABLE `pago_tarjeta`
MODIFY `id_tarjeta` int(11) COMMENT 'Tarjeta de crédito pagada';

ALTER TABLE `pago_tarjeta`
MODIFY `fecha_pago` date COMMENT 'Fecha en que se realizó el pago';

ALTER TABLE `pago_tarjeta`
MODIFY `monto_pago` decimal(15, 2) COMMENT 'Monto pagado';

ALTER TABLE `pago_tarjeta`
MODIFY `referencia` varchar(100) COMMENT 'Referencia o descripción del pago';

ALTER TABLE `pago_tarjeta`
MODIFY `id_persona` int(11) COMMENT 'Persona que realizó el pago';

ALTER TABLE `persona` COMMENT = 'Usuarios registrados en el sistema';

ALTER TABLE `persona`
MODIFY `nombre` varchar(100) COMMENT 'Nombre completo del usuario';

ALTER TABLE `persona`
MODIFY `correo_electronico` varchar(100) COMMENT 'Correo electrónico único del usuario';

ALTER TABLE `persona`
MODIFY `usuario` varchar(45) COMMENT 'Nombre de usuario único';

ALTER TABLE `persona`
MODIFY `hash_contrasena` varchar(255) COMMENT 'Contraseña en formato hash';

ALTER TABLE `persona`
MODIFY `fecha_creacion` datetime COMMENT 'Fecha de creación del usuario';

ALTER TABLE `persona`
MODIFY `fecha_actualizacion` datetime COMMENT 'Fecha de última actualización';

ALTER TABLE `persona`
MODIFY `activo` tinyint(4) COMMENT 'Indica si el usuario está activo';

ALTER TABLE `prestamo` COMMENT = 'Préstamos otorgados a personas';

ALTER TABLE `prestamo`
MODIFY `fecha` date COMMENT 'Fecha de inicio del préstamo';

ALTER TABLE `prestamo`
MODIFY `id_estado` int(11) COMMENT 'Estado actual del préstamo';

ALTER TABLE `prestamo`
MODIFY `moneda` varchar(10) COMMENT 'Moneda del préstamo';

ALTER TABLE `prestamo`
MODIFY `saldo_inicial` decimal(15, 2) COMMENT 'Saldo inicial del préstamo';

ALTER TABLE `prestamo`
MODIFY `limite_credito` decimal(15, 2) COMMENT 'Límite de crédito del préstamo';

ALTER TABLE `prestamo`
MODIFY `id_persona` int(11) COMMENT 'Persona que recibe el préstamo';

ALTER TABLE `presupuesto` COMMENT = 'Presupuestos definidos por los usuarios';

ALTER TABLE `presupuesto`
MODIFY `nombre` varchar(100) COMMENT 'Nombre del presupuesto';

ALTER TABLE `presupuesto`
MODIFY `descripcion` text COMMENT 'Descripción del presupuesto';

ALTER TABLE `presupuesto`
MODIFY `monto_total` decimal(15, 2) COMMENT 'Monto total asignado al presupuesto';

ALTER TABLE `presupuesto`
MODIFY `fecha_inicio` date COMMENT 'Fecha de inicio del presupuesto';

ALTER TABLE `presupuesto`
MODIFY `fecha_fin` date COMMENT 'Fecha de fin del presupuesto';

ALTER TABLE `presupuesto`
MODIFY `id_persona` int(11) COMMENT 'Persona propietaria del presupuesto';

ALTER TABLE `presupuesto_categoria` COMMENT = 'Relación entre presupuestos y categorías';

ALTER TABLE `producto` COMMENT = 'Productos financieros disponibles';

ALTER TABLE `producto`
MODIFY `nombre` varchar(100) COMMENT 'Nombre del producto';

ALTER TABLE `producto`
MODIFY `monto_maximo` decimal(15, 2) COMMENT 'Monto máximo permitido para el producto';

ALTER TABLE `producto`
MODIFY `monto_minimo` decimal(15, 2) COMMENT 'Monto mínimo permitido para el producto';

ALTER TABLE `producto`
MODIFY `porcentaje_interes` decimal(5, 2) COMMENT 'Porcentaje de interés aplicado';

ALTER TABLE `producto`
MODIFY `id_tipo` int(11) COMMENT 'Tipo de producto';

ALTER TABLE `tarjeta_credito` COMMENT = 'Tarjetas de crédito asociadas a productos';

ALTER TABLE `tarjeta_credito`
MODIFY `id_producto` int(11) COMMENT 'Producto asociado a la tarjeta';

ALTER TABLE `tarjeta_credito`
MODIFY `numero_tarjeta` char(16) COMMENT 'Número único de la tarjeta de crédito';

ALTER TABLE `tarjeta_credito`
MODIFY `limite_credito` decimal(15, 2) COMMENT 'Límite de crédito de la tarjeta';

ALTER TABLE `tarjeta_credito`
MODIFY `saldo_actual` decimal(15, 2) COMMENT 'Saldo actual de la tarjeta';

ALTER TABLE `tarjeta_credito`
MODIFY `fecha_corte` date COMMENT 'Fecha de corte de la tarjeta';

ALTER TABLE `tarjeta_credito`
MODIFY `fecha_pago` date COMMENT 'Fecha límite de pago de la tarjeta';

ALTER TABLE `tarjeta_credito`
MODIFY `id_estado` int(11) COMMENT 'Estado actual de la tarjeta';

ALTER TABLE `tipo_movimiento` COMMENT = 'Tipos de movimientos financieros';

ALTER TABLE `tipo_movimiento`
MODIFY `nombre` varchar(20) COMMENT 'Nombre del tipo de movimiento';

ALTER TABLE `tipo_producto` COMMENT = 'Tipos de productos financieros';

ALTER TABLE `tipo_producto`
MODIFY `nombre` varchar(50) COMMENT 'Nombre del tipo de producto';

ALTER TABLE `transaccion_programada` COMMENT = 'Transacciones programadas por los usuarios';

ALTER TABLE `transaccion_programada`
MODIFY `fecha` date COMMENT 'Fecha de ejecución de la transacción';

ALTER TABLE `transaccion_programada`
MODIFY `id_tipo` int(11) COMMENT 'Tipo de movimiento programado';

ALTER TABLE `transaccion_programada`
MODIFY `monto` decimal(15, 2) COMMENT 'Monto de la transacción programada';

ALTER TABLE `transaccion_programada`
MODIFY `id_frecuencia` int(11) COMMENT 'Frecuencia de la transacción';

ALTER TABLE `transaccion_programada`
MODIFY `repeticion` int(11) COMMENT 'Cantidad de repeticiones';

ALTER TABLE `transaccion_programada`
MODIFY `id_categoria` int(11) COMMENT 'Categoría de la transacción';

ALTER TABLE `transaccion_programada`
MODIFY `id_beneficiario` int(11) COMMENT 'Beneficiario de la transacción';

ALTER TABLE `accion` COMMENT = 'Registro de acciones bursátiles adquiridas por los usuarios';

ALTER TABLE `accion`
MODIFY `simbolo` VARCHAR(10) COMMENT 'Símbolo bursátil de la acción (ej: AAPL, ECOPETROL)';

ALTER TABLE `accion`
MODIFY `empresa` VARCHAR(100) COMMENT 'Nombre de la empresa emisora de la acción';

ALTER TABLE `accion`
MODIFY `cantidad` INT COMMENT 'Cantidad de acciones adquiridas';

ALTER TABLE `accion`
MODIFY `precio_compra` DECIMAL(15, 2) COMMENT 'Precio unitario al momento de la compra';

ALTER TABLE `accion`
MODIFY `fecha_compra` DATE COMMENT 'Fecha en que se realizó la compra';

ALTER TABLE `accion`
MODIFY `precio_actual` DECIMAL(15, 2) COMMENT 'Precio de mercado actual de la acción';

ALTER TABLE `accion`
MODIFY `mercado` VARCHAR(50) COMMENT 'Mercado bursátil donde cotiza la acción';

ALTER TABLE `accion`
MODIFY `id_persona` INT COMMENT 'Referencia al usuario dueño de la acción';

ALTER TABLE `fondo` COMMENT = 'Fondos de inversión registrados por los usuarios';

ALTER TABLE `fondo`
MODIFY `nombre` VARCHAR(150) COMMENT 'Nombre del fondo de inversión';

ALTER TABLE `fondo`
MODIFY `tipo` ENUM(
    'Mutuo',
    'ETF',
    'Pensión',
    'Otro'
) COMMENT 'Tipo de fondo de inversión';

ALTER TABLE `fondo`
MODIFY `entidad` VARCHAR(100) COMMENT 'Entidad gestora o banco administrador del fondo';

ALTER TABLE `fondo`
MODIFY `monto_invertido` DECIMAL(15, 2) COMMENT 'Monto inicial invertido en el fondo';

ALTER TABLE `fondo`
MODIFY `fecha_inversion` DATE COMMENT 'Fecha de la inversión en el fondo';

ALTER TABLE `fondo`
MODIFY `valor_actual` DECIMAL(15, 2) COMMENT 'Valor actual del fondo';

ALTER TABLE `fondo`
MODIFY `rentabilidad` DECIMAL(6, 2) COMMENT 'Rentabilidad porcentual del fondo';

ALTER TABLE `fondo`
MODIFY `id_persona` INT COMMENT 'Referencia al usuario dueño del fondo';

ALTER TABLE `parametro_dian` COMMENT = 'Parámetros tributarios y económicos definidos por la DIAN para cada año';

ALTER TABLE `parametro_dian`
MODIFY `anio` INT COMMENT 'Año de vigencia del parámetro';

ALTER TABLE `parametro_dian`
MODIFY `concepto` VARCHAR(150) COMMENT 'Concepto del parámetro (ej: UVT, Tope renta exenta)';

ALTER TABLE `parametro_dian`
MODIFY `valor` DECIMAL(15, 2) COMMENT 'Valor numérico del parámetro';

ALTER TABLE `parametro_dian`
MODIFY `unidad` VARCHAR(50) COMMENT 'Unidad de medida del parámetro (COP, %, UVT)';

ALTER TABLE `parametro_dian`
MODIFY `descripcion` TEXT COMMENT 'Descripción o explicación adicional del parámetro';