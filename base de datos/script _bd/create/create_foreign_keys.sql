-- Foreign keys para producto
ALTER TABLE producto
ADD CONSTRAINT fk_producto_tipo FOREIGN KEY (id_tipo) REFERENCES tipo_producto (id_tipo);

-- Foreign keys para movimiento
ALTER TABLE movimiento
ADD CONSTRAINT fk_movimiento_producto FOREIGN KEY (id_producto) REFERENCES producto (id_producto),
ADD CONSTRAINT fk_movimiento_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona),
ADD CONSTRAINT fk_movimiento_categoria FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria),
ADD CONSTRAINT fk_movimiento_beneficiario FOREIGN KEY (id_beneficiario) REFERENCES beneficiario (id_beneficiario),
ADD CONSTRAINT fk_movimiento_tipo FOREIGN KEY (id_tipo) REFERENCES tipo_movimiento (id_tipo),
ADD CONSTRAINT fk_movimiento_estado FOREIGN KEY (id_estado) REFERENCES estado_movimiento (id_estado);

-- Foreign keys para transaccion_programada
ALTER TABLE transaccion_programada
ADD CONSTRAINT fk_tp_categoria FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria),
ADD CONSTRAINT fk_tp_beneficiario FOREIGN KEY (id_beneficiario) REFERENCES beneficiario (id_beneficiario),
ADD CONSTRAINT fk_tp_tipo FOREIGN KEY (id_tipo) REFERENCES tipo_movimiento (id_tipo),
ADD CONSTRAINT fk_tp_frecuencia FOREIGN KEY (id_frecuencia) REFERENCES frecuencia_transaccion (id_frecuencia);

-- Foreign keys para prestamo
ALTER TABLE prestamo
ADD CONSTRAINT fk_prestamo_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona),
ADD CONSTRAINT fk_prestamo_estado FOREIGN KEY (id_estado) REFERENCES estado_prestamo (id_estado);

-- Foreign keys para activo
ALTER TABLE activo
ADD CONSTRAINT fk_activo_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona);

-- Foreign keys para presupuesto
ALTER TABLE presupuesto
ADD CONSTRAINT fk_presupuesto_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona);

-- Foreign keys para presupuesto_categoria
ALTER TABLE presupuesto_categoria
ADD CONSTRAINT fk_presupuesto_categoria_presupuesto FOREIGN KEY (id_presupuesto) REFERENCES presupuesto (id_presupuesto),
ADD CONSTRAINT fk_presupuesto_categoria_categoria FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria);

-- Foreign keys para tarjeta_credito
ALTER TABLE tarjeta_credito
ADD CONSTRAINT fk_tc_producto FOREIGN KEY (id_producto) REFERENCES producto (id_producto),
ADD CONSTRAINT fk_tc_estado FOREIGN KEY (id_estado) REFERENCES estado_tarjeta (id_estado);

-- Foreign keys para pago_tarjeta
ALTER TABLE pago_tarjeta
ADD CONSTRAINT fk_pt_tarjeta FOREIGN KEY (id_tarjeta) REFERENCES tarjeta_credito (id_tarjeta),
ADD CONSTRAINT fk_pt_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona);

-- Foreign keys para accion y fondo
ALTER TABLE accion
ADD CONSTRAINT fk_accion_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona);

ALTER TABLE fondo
ADD CONSTRAINT fk_fondo_persona FOREIGN KEY (id_persona) REFERENCES persona (id_persona);