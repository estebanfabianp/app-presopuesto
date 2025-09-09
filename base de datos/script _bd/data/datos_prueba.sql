-- Datos de prueba para catálogos
INSERT INTO tipo_producto (nombre) VALUES ('TARJETA'), ('PRESTAMO'), ('OTRO');
INSERT INTO tipo_movimiento (nombre) VALUES ('CARGO'), ('ABONO');
INSERT INTO estado_movimiento (nombre) VALUES ('PENDIENTE'), ('PAGADO'), ('CANCELADO');
INSERT INTO frecuencia_transaccion (nombre) VALUES ('DIARIA'), ('SEMANAL'), ('MENSUAL'), ('ANUAL');
INSERT INTO estado_prestamo (nombre) VALUES ('ACTIVO'), ('CANCELADO'), ('MORA');
INSERT INTO estado_tarjeta (nombre) VALUES ('ACTIVA'), ('INACTIVA'), ('CANCELADA');

-- Datos de prueba para persona
INSERT INTO persona (nombre, correo_electronico, usuario, hash_contrasena, fecha_creacion, activo)
VALUES
('Juan Pérez', 'juan.perez@email.com', 'juanp', 'hash123456', NOW(), 1),
('Ana Gómez', 'ana.gomez@email.com', 'anag', 'hashabcdef', NOW(), 1);

-- Datos de prueba para producto
INSERT INTO producto (nombre, monto_maximo, monto_minimo, porcentaje_interes, id_tipo)
VALUES
('Tarjeta Visa', 10000, 500, 15.5, 1),
('Préstamo Personal', 50000, 1000, 12.0, 2);

-- Datos de prueba para categoria
INSERT INTO categoria (nombre)
VALUES
('Alimentación'),
('Transporte'),
('Educación');

-- Datos de prueba para beneficiario
INSERT INTO beneficiario (nombre)
VALUES
('Supermercado ABC'),
('Universidad XYZ');

-- Datos de prueba para movimiento
INSERT INTO movimiento (codigo, monto, id_tipo, cuotas, id_estado, id_producto, id_persona, id_categoria, id_beneficiario, nota, fecha_creacion)
VALUES
('MOV001', 150.00, 1, NULL, 1, 1, 1, 1, 1, 'Compra supermercado', NOW()),
('MOV002', 2000.00, 2, 12, 2, 2, 2, 3, 2, 'Pago colegiatura', NOW());

-- Datos de prueba para transaccion_programada
INSERT INTO transaccion_programada (fecha, id_tipo, monto, id_frecuencia, repeticion, id_categoria, id_beneficiario, fecha_creacion)
VALUES
('2025-09-01', 1, 100.00, 3, 12, 1, 1, NOW()),
('2025-09-05', 2, 500.00, 4, 1, 3, 2, NOW());

-- Datos de prueba para prestamo
INSERT INTO prestamo (fecha, id_estado, moneda, saldo_inicial, limite_credito, id_persona, fecha_creacion)
VALUES
('2025-08-01', 1, 'MXN', 10000.00, 50000.00, 1, NOW()),
('2025-08-15', 2, 'USD', 2000.00, 10000.00, 2, NOW());

-- Datos de prueba para activo
INSERT INTO activo (nombre_activo, valor, depreciacion, id_persona, fecha_creacion)
VALUES
('Laptop', 15000.00, 2000.00, 1, NOW()),
('Bicicleta', 3000.00, 500.00, 2, NOW());

-- Datos de prueba para presupuesto
INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
VALUES
('Presupuesto Mensual', 'Gastos y ahorros mensuales', 10000.00, '2025-09-01', '2025-09-30', 1, NOW()),
('Presupuesto Escolar', 'Gastos educativos', 5000.00, '2025-09-01', '2025-12-31', 2, NOW());

-- Datos de prueba para presupuesto_categoria
INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria)
VALUES
(1, 1),
(1, 2),
(2, 3);

-- Datos de prueba para tarjeta_credito
INSERT INTO tarjeta_credito (id_producto, numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, fecha_creacion, id_estado)
VALUES
(1, '4111111111111111', 10000.00, 5000.00, '2025-09-15', '2025-09-25', NOW(), 1),
(1, '4222222222222222', 8000.00, 2000.00, '2025-09-10', '2025-09-20', NOW(), 1);

-- Datos de prueba para pago_tarjeta
INSERT INTO pago_tarjeta (id_tarjeta, fecha_pago, monto_pago, referencia, id_persona, fecha_creacion)
VALUES
(1, '2025-09-20', 1000.00, 'Pago septiembre', 1, NOW()),
(2, '2025-09-21', 500.00, 'Pago parcial', 2, NOW());

-- UVT para 2025
INSERT INTO parametro_dian (anio, concepto, valor, unidad, descripcion)
VALUES (2025, 'UVT', 47065, 'COP', 'Unidad de Valor Tributario para el año 2025');

-- Tope ingresos para declarar renta 2025
INSERT INTO parametro_dian (anio, concepto, valor, unidad, descripcion)
VALUES (2025, 'Tope ingresos brutos anuales', 174000000, 'COP', 'Valor mínimo de ingresos para estar obligado a declarar renta');

-- Porcentaje de retención en la fuente
INSERT INTO parametro_dian (anio, concepto, valor, unidad, descripcion)
VALUES (2025, 'Retención en la fuente por compras', 2.50, '%', 'Aplicable a compras sujetas a retención');


-- Comprar 50 acciones de Ecopetrol
INSERT INTO accion (simbolo, empresa, cantidad, precio_compra, fecha_compra, precio_actual, mercado, usuario_id)
VALUES ('ECOPETROL', 'Ecopetrol S.A.', 50, 2800, '2025-09-07', 2900, 'BVC', 1);

-- Comprar 10 acciones de Apple
INSERT INTO accion (simbolo, empresa, cantidad, precio_compra, fecha_compra, precio_actual, mercado, usuario_id)
VALUES ('AAPL', 'Apple Inc.', 10, 175.50, '2025-09-07', 180.25, 'NASDAQ', 1);

-- Fondo mutuo de renta fija
INSERT INTO fondo (nombre, tipo, entidad, monto_invertido, fecha_inversion, valor_actual, rentabilidad, usuario_id)
VALUES ('Fondo Renta Fija Bancolombia', 'Mutuo', 'Bancolombia', 5000000, '2025-09-07', 5200000, 4.00, 1);

-- ETF en S&P500
INSERT INTO fondo (nombre, tipo, entidad, monto_invertido, fecha_inversion, valor_actual, rentabilidad, usuario_id)
VALUES ('ETF Vanguard S&P500', 'ETF', 'Vanguard', 2000, '2025-09-07', 2100, 5.00, 1);
