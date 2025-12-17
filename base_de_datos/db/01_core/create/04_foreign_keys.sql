-- =================================================================
-- CLAVES FORÁNEAS E ÍNDICES
-- Proyecto: app-presupuesto
-- Descripción: Definición de relaciones entre tablas e índices de rendimiento
-- =================================================================

-- Relaciones de tabla accion
ALTER TABLE `accion`
  ADD CONSTRAINT `fk_accion_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Relaciones de tabla activo
ALTER TABLE `activo`
  ADD CONSTRAINT `fk_activo_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Relaciones de tabla cuenta
ALTER TABLE `cuenta`
  ADD CONSTRAINT `fk_cuenta_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Relaciones de tabla movimiento
ALTER TABLE `movimiento`
  ADD CONSTRAINT `fk_movimiento_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `fk_movimiento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_movimiento_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`),
  ADD CONSTRAINT `fk_movimiento_estado` FOREIGN KEY (`id_estado`) REFERENCES `estado_movimiento` (`id_estado`),
  ADD CONSTRAINT `fk_movimiento_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `cuenta` (`id_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- Relaciones de tabla prestamo
ALTER TABLE `prestamo`
  ADD CONSTRAINT `fk_prestamo_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  ADD CONSTRAINT `fk_prestamo_estado` FOREIGN KEY (`id_estado`) REFERENCES `estado_prestamo` (`id_estado`);

-- Relaciones de tabla tarjeta_credito
ALTER TABLE `tarjeta_credito`
  ADD CONSTRAINT `fk_tc_estado` FOREIGN KEY (`id_estado`) REFERENCES `estado_tarjeta` (`id_estado`);

-- Relaciones de tabla movimiento_tarjeta
ALTER TABLE `movimiento_tarjeta`
  ADD CONSTRAINT `fk_mt_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `fk_mt_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_mt_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
  ADD CONSTRAINT `fk_mt_tarjeta` FOREIGN KEY (`id_tarjeta`) REFERENCES `tarjeta_credito` (`id_tarjeta`);

-- Relaciones de tabla prestamo_movimiento
ALTER TABLE `prestamo_movimiento`
  ADD CONSTRAINT `fk_persona_has_prestamo_persona1` FOREIGN KEY (`persona_id_persona`) REFERENCES `persona` (`id_persona`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_persona_has_prestamo_prestamo1` FOREIGN KEY (`prestamo_id_prestamo`) REFERENCES `prestamo` (`id_prestamo`) ON DELETE NO ACTION ON UPDATE NO ACTION;

-- Relaciones de tabla presupuesto
ALTER TABLE `presupuesto`
  ADD CONSTRAINT `fk_presupuesto_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Relaciones de tabla presupuesto_categoria
ALTER TABLE `presupuesto_categoria`
  ADD CONSTRAINT `fk_presupuesto_categoria_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_presupuesto_categoria_presupuesto` FOREIGN KEY (`id_presupuesto`) REFERENCES `presupuesto` (`id_presupuesto`);

-- Relaciones de tabla transaccion_programada
ALTER TABLE `transaccion_programada`
  ADD CONSTRAINT `fk_tp_beneficiario` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
  ADD CONSTRAINT `fk_tp_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
  ADD CONSTRAINT `fk_tp_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`);
