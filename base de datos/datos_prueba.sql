
-- Datos de prueba para persona
INSERT INTO `mydb`.`persona` (`nombre`, `correo_electronico`, `usuario`, `contrasena`, `fecha_creacion`, `activo`)
VALUES
('Juan Pérez', 'juan.perez@email.com', 'juanp', '123456', NOW(), 1),
('Ana Gómez', 'ana.gomez@email.com', 'anag', 'abcdef', NOW(), 1);

-- Datos de prueba para producto
INSERT INTO `mydb`.`producto` (`nombre`, `monto_maximo`, `monto_minimo`, `porcentaje_interes`, `tipo_producto`)
VALUES
('Tarjeta Visa', 10000, 500, 15.5, 'TARJETA'),
('Préstamo Personal', 50000, 1000, 12.0, 'PRESTAMO');

-- Datos de prueba para categoria
INSERT INTO `mydb`.`categoria` (`nombre`)
VALUES
('Alimentación'),
('Transporte'),
('Educación');

-- Datos de prueba para beneficiario
INSERT INTO `mydb`.`beneficiario` (`nombre`)
VALUES
('Supermercado ABC'),
('Universidad XYZ');

-- Datos de prueba para movimiento
INSERT INTO `mydb`.`movimiento` (`codigo`, `monto`, `tipo`, `cuotas`, `estado`, `id_producto`, `id_persona`, `id_categoria`, `id_beneficiario`)
VALUES
('MOV001', 150.00, 'CARGO', NULL, 'PENDIENTE', 1, 1, 1, 1),
('MOV002', 2000.00, 'ABONO', 12, 'PAGADO', 2, 2, 3, 2);

-- Datos de prueba para transaccion_programada
INSERT INTO `mydb`.`transaccion_programada` (`fecha`, `tipo`, `monto`, `frecuencia`, `repeticion`, `id_categoria`, `id_beneficiario`)
VALUES
('2025-09-01', 'CARGO', 100.00, 'MENSUAL', 12, 1, 1),
('2025-09-05', 'ABONO', 500.00, 'ANUAL', 1, 3, 2);

-- Datos de prueba para prestamo
INSERT INTO `mydb`.`prestamo` (`fecha`, `estado`, `moneda`, `saldo_inicial`, `limite_credito`, `id_persona`)
VALUES
('2025-08-01', 'ACTIVO', 'MXN', 10000.00, 50000.00, 1),
('2025-08-15', 'CANCELADO', 'USD', 2000.00, 10000.00, 2);

-- Datos de prueba para activo
INSERT INTO `mydb`.`activo` (`nombre_activo`, `valor`, `depreciacion`, `id_persona`, `fecha_creacion`)
VALUES
('Laptop', 15000.00, 2000.00, 1, NOW()),
('Bicicleta', 3000.00, 500.00, 2, NOW());

-- Datos de prueba para presupuesto 
INSERT INTO `mydb`.`presupuesto` (`nombre`, `descripcion`, `monto_total`, `fecha_inicio`, `fecha_fin`, `id_persona`)
VALUES
('Presupuesto Mensual', 'Gastos y ahorros mensuales', 10000.00, '2025-09-01', '2025-09-30', 1),
('Presupuesto Escolar', 'Gastos educativos', 5000.00, '2025-09-01', '2025-12-31', 2);

-- Datos de prueba para tarjeta_credito
INSERT INTO `mydb`.`tarjeta_credito` (`id_producto`, `numero_tarjeta`, `limite_credito`, `saldo_actual`, `fecha_corte`, `fecha_pago`, `fecha_creacion`, `estado`)
VALUES
(1, '4111111111111111', 10000.00, 5000.00, '2025-09-15', '2025-09-25', NOW(), 'ACTIVA'),
(1, '4222222222222222', 8000.00, 2000.00, '2025-09-10', '2025-09-20', NOW(), 'ACTIVA');

-- Datos de prueba para pago_tarjeta
INSERT INTO `mydb`.`pago_tarjeta` (`id_tarjeta`, `fecha_pago`, `monto_pago`, `referencia`, `id_persona`)
VALUES
(1, '2025-09-20', 1000.00, 'Pago septiembre', 1),
(2, '2025-09-21', 500.00, 'Pago parcial', 2);
