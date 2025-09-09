-- Índices adicionales para optimizar consultas

CREATE INDEX idx_mov_persona_fecha ON movimiento (id_persona, id_producto, id_estado, fecha_creacion);
CREATE INDEX idx_tc_numero ON tarjeta_credito (numero_tarjeta);
CREATE INDEX idx_presupuesto_persona ON presupuesto (id_persona);
CREATE INDEX idx_prestamo_persona ON prestamo (id_persona);
CREATE INDEX idx_activo_persona ON activo (id_persona);
