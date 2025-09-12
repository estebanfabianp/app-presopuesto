ALTER TABLE `mydb`.`accion`
ADD INDEX `fk_accion_persona` (`id_persona`),
ADD CONSTRAINT `fk_accion_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`);

ALTER TABLE `mydb`.`activo`
ADD INDEX `idx_activo_persona` (`id_persona`),
ADD CONSTRAINT `fk_activo_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`);

ALTER TABLE `mydb`.`beneficiario`
ADD INDEX `idx_beneficiario` (`id_beneficiario`);

ALTER TABLE `mydb`.`categoria`
ADD INDEX `idx_categoria` (`id_categoria`);

ALTER TABLE `mydb`.`deuda_financiada`
ADD INDEX `fk_deuda_persona` (`id_persona`),
ADD CONSTRAINT `fk_deuda_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`);

ALTER TABLE `mydb`.`tipo_movimiento` ADD INDEX `nombre` (`nombre`);

ALTER TABLE `mydb`.`cuenta`
ADD INDEX `fk_cuenta_persona` (`id_persona`),
ADD CONSTRAINT `fk_cuenta_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`);

ALTER TABLE `mydb`.`movimiento`
ADD INDEX `fk_movimiento_categoria` (`id_categoria`),
ADD INDEX `fk_movimiento_beneficiario` (`id_beneficiario`),
ADD INDEX `fk_movimiento_tipo` (`id_tipo`),
ADD INDEX `fk_movimiento_estado` (`id_estado`),
ADD INDEX `fk_movimiento_cuenta_idx` (`id_cuenta`),
ADD CONSTRAINT `fk_movimiento_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `mydb`.`beneficiario` (`id_beneficiario`),
ADD CONSTRAINT `fk_movimiento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
ADD CONSTRAINT `fk_movimiento_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `mydb`.`tipo_movimiento` (`id_tipo`),
ADD CONSTRAINT `fk_movimiento_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_movimiento` (`id_estado`),
ADD CONSTRAINT `fk_movimiento_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `mydb`.`cuenta` (`id_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `mydb`.`prestamo`
ADD INDEX `fk_prestamo_persona` (`id_persona`),
ADD INDEX `fk_prestamo_estado` (`id_estado`),
ADD CONSTRAINT `fk_prestamo_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`),
ADD CONSTRAINT `fk_prestamo_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_prestamo` (`id_estado`);

ALTER TABLE `mydb`.`presupuesto`
ADD INDEX `idx_presupuesto_persona` (`id_persona`),
ADD CONSTRAINT `fk_presupuesto_persona` FOREIGN KEY (`id_persona`) REFERENCES `mydb`.`persona` (`id_persona`);

ALTER TABLE `mydb`.`presupuesto_categoria`
ADD INDEX `fk_presupuesto_categoria_categoria` (`id_categoria`),
ADD CONSTRAINT `fk_presupuesto_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
ADD CONSTRAINT `fk_presupuesto_categoria_presupuesto` FOREIGN KEY (`id_presupuesto`) REFERENCES `mydb`.`presupuesto` (`id_presupuesto`);

ALTER TABLE `mydb`.`tarjeta_credito`
ADD INDEX `fk_tc_estado` (`id_estado`),
ADD CONSTRAINT `fk_tc_estado` FOREIGN KEY (`id_estado`) REFERENCES `mydb`.`estado_tarjeta` (`id_estado`);

ALTER TABLE `mydb`.`transaccion_programada`
ADD INDEX `fk_tp_categoria` (`id_categoria`),
ADD INDEX `fk_tp_beneficiario` (`id_beneficiario`),
ADD INDEX `fk_tp_tipo` (`id_tipo`),
ADD CONSTRAINT `fk_tp_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `mydb`.`beneficiario` (`id_beneficiario`),
ADD CONSTRAINT `fk_tp_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `mydb`.`categoria` (`id_categoria`),
ADD CONSTRAINT `fk_tp_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `mydb`.`tipo_movimiento` (`id_tipo`);

ALTER TABLE `mydb`.`prestamo_movimiento`
ADD INDEX `fk_persona_has_prestamo_prestamo1_idx` (`prestamo_id_prestamo`),
ADD INDEX `fk_persona_has_prestamo_persona1_idx` (`persona_id_persona`),
ADD CONSTRAINT `fk_persona_has_prestamo_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `mydb`.`persona` (`id_persona`) ON DELETE NO ACTION ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_persona_has_prestamo_prestamo1` FOREIGN KEY (`prestamo_id_prestamo`) REFERENCES `mydb`.`prestamo` (`id_prestamo`) ON DELETE NO ACTION ON UPDATE NO ACTION;