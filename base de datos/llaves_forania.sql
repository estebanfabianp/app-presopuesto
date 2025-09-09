-- Filtros para la tabla `activo`
ALTER TABLE `activo`
ADD CONSTRAINT `activo_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Filtros para la tabla `movimiento`
ALTER TABLE `movimiento`
ADD CONSTRAINT `movimiento_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
ADD CONSTRAINT `movimiento_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
ADD CONSTRAINT `movimiento_ibfk_3` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
ADD CONSTRAINT `movimiento_ibfk_4` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
ADD CONSTRAINT `movimiento_ibfk_5` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`),
ADD CONSTRAINT `movimiento_ibfk_6` FOREIGN KEY (`id_estado`) REFERENCES `estado_movimiento` (`id_estado`);

-- Filtros para la tabla `pago_tarjeta`
ALTER TABLE `pago_tarjeta`
ADD CONSTRAINT `pago_tarjeta_ibfk_1` FOREIGN KEY (`id_tarjeta`) REFERENCES `tarjeta_credito` (`id_tarjeta`),
ADD CONSTRAINT `pago_tarjeta_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Filtros para la tabla `prestamo`
ALTER TABLE `prestamo`
ADD CONSTRAINT `prestamo_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`),
ADD CONSTRAINT `prestamo_ibfk_2` FOREIGN KEY (`id_estado`) REFERENCES `estado_prestamo` (`id_estado`);

-- Filtros para la tabla `presupuesto`
ALTER TABLE `presupuesto`
ADD CONSTRAINT `presupuesto_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

-- Filtros para la tabla `presupuesto_categoria`
ALTER TABLE `presupuesto_categoria`
ADD CONSTRAINT `presupuesto_categoria_ibfk_1` FOREIGN KEY (`id_presupuesto`) REFERENCES `presupuesto` (`id_presupuesto`),
ADD CONSTRAINT `presupuesto_categoria_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`);

-- Filtros para la tabla `producto`
ALTER TABLE `producto`
ADD CONSTRAINT `producto_ibfk_1` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_producto` (`id_tipo`);

-- Filtros para la tabla `tarjeta_credito`
ALTER TABLE `tarjeta_credito`
ADD CONSTRAINT `tarjeta_credito_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`),
ADD CONSTRAINT `tarjeta_credito_ibfk_2` FOREIGN KEY (`id_estado`) REFERENCES `estado_tarjeta` (`id_estado`);

-- Filtros para la tabla `transaccion_programada`
ALTER TABLE `transaccion_programada`
ADD CONSTRAINT `transaccion_programada_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`),
ADD CONSTRAINT `transaccion_programada_ibfk_2` FOREIGN KEY (`id_beneficiario`) REFERENCES `beneficiario` (`id_beneficiario`),
ADD CONSTRAINT `transaccion_programada_ibfk_3` FOREIGN KEY (`id_tipo`) REFERENCES `tipo_movimiento` (`id_tipo`),
ADD CONSTRAINT `transaccion_programada_ibfk_4` FOREIGN KEY (`id_frecuencia`) REFERENCES `frecuencia_transaccion` (`id_frecuencia`);

-- Filtros para las tablas nuevas (acción, fondo)
ALTER TABLE `accion`
ADD CONSTRAINT `accion_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

ALTER TABLE `fondo`
ADD CONSTRAINT `fondo_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);