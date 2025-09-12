-- Elimina la clave foránea si existe antes de crearla para evitar duplicados
ALTER TABLE `app_presupuesto`.`accion`
  DROP FOREIGN KEY IF EXISTS `fk_accion_persona`;
ALTER TABLE `app_presupuesto`.`accion`
  ADD INDEX `fk_accion_persona` (`id_persona`),
  ADD CONSTRAINT `fk_accion_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`);

ALTER TABLE `app_presupuesto`.`activo`
  DROP FOREIGN KEY IF EXISTS `fk_activo_persona`;
ALTER TABLE `app_presupuesto`.`activo`
  ADD CONSTRAINT `fk_activo_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`);

ALTER TABLE `app_presupuesto`.`beneficiario`
  ADD INDEX `idx_beneficiario` (`id_beneficiario`);

ALTER TABLE `app_presupuesto`.`categoria`
  ADD INDEX `idx_categoria` (`id_categoria`);

ALTER TABLE `app_presupuesto`.`deuda_financiada`
  DROP FOREIGN KEY IF EXISTS `fk_deuda_persona`;
ALTER TABLE `app_presupuesto`.`deuda_financiada`
  ADD INDEX `fk_deuda_persona` (`id_persona`),
  ADD CONSTRAINT `fk_deuda_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`);

ALTER TABLE `app_presupuesto`.`tipo_movimiento`
  ADD INDEX `nombre` (`nombre`);

ALTER TABLE `app_presupuesto`.`cuenta`
  DROP FOREIGN KEY IF EXISTS `fk_cuenta_persona`;
ALTER TABLE `app_presupuesto`.`cuenta`
  ADD INDEX `fk_cuenta_persona` (`id_persona`),
  ADD CONSTRAINT `fk_cuenta_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`);

ALTER TABLE `app_presupuesto`.`movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_movimiento_beneficiario`;
ALTER TABLE `app_presupuesto`.`movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_movimiento_categoria`;
ALTER TABLE `app_presupuesto`.`movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_movimiento_tipo`;
ALTER TABLE `app_presupuesto`.`movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_movimiento_estado`;
ALTER TABLE `app_presupuesto`.`movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_movimiento_cuenta`;
ALTER TABLE `app_presupuesto`.`movimiento`
  ADD INDEX `fk_movimiento_categoria` (`id_categoria`),
  ADD INDEX `fk_movimiento_beneficiario` (`id_beneficiario`),
  ADD INDEX `fk_movimiento_tipo` (`id_tipo`),
  ADD INDEX `fk_movimiento_estado` (`id_estado`),
  ADD INDEX `fk_movimiento_cuenta_idx` (`id_cuenta`),
  ADD CONSTRAINT `fk_movimiento_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `app_presupuesto`.`beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `fk_movimiento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_movimiento_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `app_presupuesto`.`tipo_movimiento` (`id_tipo`),
  ADD CONSTRAINT `fk_movimiento_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_movimiento` (`id_estado`),
  ADD CONSTRAINT `fk_movimiento_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `app_presupuesto`.`cuenta` (`id_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `app_presupuesto`.`prestamo`
  DROP FOREIGN KEY IF EXISTS `fk_prestamo_persona`;
ALTER TABLE `app_presupuesto`.`prestamo`
  DROP FOREIGN KEY IF EXISTS `fk_prestamo_estado`;
ALTER TABLE `app_presupuesto`.`prestamo`
  ADD INDEX `fk_prestamo_persona` (`id_persona`),
  ADD INDEX `fk_prestamo_estado` (`id_estado`),
  ADD CONSTRAINT `fk_prestamo_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`),
  ADD CONSTRAINT `fk_prestamo_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_prestamo` (`id_estado`);

ALTER TABLE `app_presupuesto`.`presupuesto`
  DROP FOREIGN KEY IF EXISTS `fk_presupuesto_persona`;
ALTER TABLE `app_presupuesto`.`presupuesto`
  ADD INDEX `idx_presupuesto_persona` (`id_persona`),
  ADD CONSTRAINT `fk_presupuesto_persona` FOREIGN KEY (`id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`);

ALTER TABLE `app_presupuesto`.`presupuesto_categoria`
  DROP FOREIGN KEY IF EXISTS `fk_presupuesto_categoria_categoria`;
ALTER TABLE `app_presupuesto`.`presupuesto_categoria`
  DROP FOREIGN KEY IF EXISTS `fk_presupuesto_categoria_presupuesto`;
ALTER TABLE `app_presupuesto`.`presupuesto_categoria`
  ADD INDEX `fk_presupuesto_categoria_categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_presupuesto_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_presupuesto_categoria_presupuesto` FOREIGN KEY (`id_presupuesto`) REFERENCES `app_presupuesto`.`presupuesto` (`id_presupuesto`);

ALTER TABLE `app_presupuesto`.`tarjeta_credito`
  DROP FOREIGN KEY IF EXISTS `fk_tc_estado`;
ALTER TABLE `app_presupuesto`.`tarjeta_credito`
  ADD INDEX `fk_tc_estado` (`id_estado`),
  ADD CONSTRAINT `fk_tc_estado` FOREIGN KEY (`id_estado`) REFERENCES `app_presupuesto`.`estado_tarjeta` (`id_estado`);

ALTER TABLE `app_presupuesto`.`transaccion_programada`
  DROP FOREIGN KEY IF EXISTS `fk_tp_beneficiario`;
ALTER TABLE `app_presupuesto`.`transaccion_programada`
  DROP FOREIGN KEY IF EXISTS `fk_tp_categoria`;
ALTER TABLE `app_presupuesto`.`transaccion_programada`
  DROP FOREIGN KEY IF EXISTS `fk_tp_tipo`;
ALTER TABLE `app_presupuesto`.`transaccion_programada`
  ADD INDEX `fk_tp_categoria` (`id_categoria`),
  ADD INDEX `fk_tp_beneficiario` (`id_beneficiario`),
  ADD INDEX `fk_tp_tipo` (`id_tipo`),
  ADD CONSTRAINT `fk_tp_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `app_presupuesto`.`beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `fk_tp_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `app_presupuesto`.`categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_tp_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `app_presupuesto`.`tipo_movimiento` (`id_tipo`);

ALTER TABLE `app_presupuesto`.`prestamo_movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_persona_has_prestamo_persona1`;
ALTER TABLE `app_presupuesto`.`prestamo_movimiento`
  DROP FOREIGN KEY IF EXISTS `fk_persona_has_prestamo_prestamo1`;
ALTER TABLE `app_presupuesto`.`prestamo_movimiento`
  ADD INDEX `fk_persona_has_prestamo_prestamo1_idx` (`prestamo_id_prestamo`),
  ADD INDEX `fk_persona_has_prestamo_persona1_idx` (`persona_id_persona`),
  ADD CONSTRAINT `fk_persona_has_prestamo_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `app_presupuesto`.`persona` (`id_persona`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_persona_has_prestamo_prestamo1` FOREIGN KEY (`prestamo_id_prestamo`) REFERENCES `app_presupuesto`.`prestamo` (`id_prestamo`) ON DELETE NO ACTION ON UPDATE NO ACTION;