-- Comentarios de tablas y columnas

ALTER TABLE `app_presupuesto`.`moneda` COMMENT = 'Catálogo de monedas soportadas';

ALTER TABLE `app_presupuesto`.`moneda`
MODIFY COLUMN `codigo` VARCHAR(10) NOT NULL COMMENT 'Código de la moneda (ej: COP, USD)';

ALTER TABLE `app_presupuesto`.`moneda`
MODIFY COLUMN `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre de la moneda';

ALTER TABLE `app_presupuesto`.`estado_movimiento` COMMENT = 'Catálogo de estados para movimientos';

ALTER TABLE `app_presupuesto`.`estado_movimiento`
MODIFY COLUMN `id_estado` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado';

ALTER TABLE `app_presupuesto`.`estado_movimiento`
MODIFY COLUMN `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre del estado';

ALTER TABLE `app_presupuesto`.`estado_prestamo` COMMENT = 'Catálogo de estados para préstamos';

ALTER TABLE `app_presupuesto`.`estado_prestamo`
MODIFY COLUMN `id_estado` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado';

ALTER TABLE `app_presupuesto`.`estado_prestamo`
MODIFY COLUMN `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre del estado';

ALTER TABLE `app_presupuesto`.`estado_tarjeta` COMMENT = 'Catálogo de estados para tarjetas de crédito';

ALTER TABLE `app_presupuesto`.`estado_tarjeta`
MODIFY COLUMN `id_estado` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado';

ALTER TABLE `app_presupuesto`.`estado_tarjeta`
MODIFY COLUMN `nombre` VARCHAR(50) NOT NULL COMMENT 'Nombre del estado';

ALTER TABLE `app_presupuesto`.`persona` COMMENT = 'Usuarios registrados en el sistema';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `id_persona` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la persona';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `nombre` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Nombre completo del usuario';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `correo_electronico` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Correo electrónico único del usuario';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `usuario` VARCHAR(45) NULL DEFAULT NULL COMMENT 'Nombre de usuario único';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `hash_contrasena` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Contraseña en formato hash';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `fecha_creacion` DATETIME NULL DEFAULT NULL COMMENT 'Fecha de creación del usuario';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `fecha_actualizacion` DATETIME NULL DEFAULT NULL COMMENT 'Fecha de última actualización';

ALTER TABLE `app_presupuesto`.`persona`
MODIFY COLUMN `activo` TINYINT(4) NULL DEFAULT NULL COMMENT 'Indica si el usuario está activo';

-- ...repite para cada tabla y columna según los comentarios originales...