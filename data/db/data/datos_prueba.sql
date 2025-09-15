
-- ===========================
-- DATOS DE PRUEBA (INSERTS)
-- ===========================

-- Monedas
INSERT INTO moneda (codigo, nombre) VALUES
  ('COP', 'Peso Colombiano'),
  ('USD', 'Dólar Estadounidense'),
  ('EUR', 'Euro');

-- Estados
INSERT INTO estado_movimiento (nombre) VALUES ('pendiente'), ('realizado'), ('anulado');
INSERT INTO estado_prestamo (nombre) VALUES ('activo'), ('pagado'), ('vencido');
INSERT INTO estado_tarjeta (nombre) VALUES ('activa'), ('bloqueada'), ('cancelada');

-- Personas
INSERT INTO persona (nombre, correo_electronico, usuario, hash_contrasena, fecha_creacion, activo)
VALUES
  ('Juan Pérez', 'juan@example.com', 'juanp', 'hash1', NOW(), 1),
  ('Ana Gómez', 'ana@example.com', 'anag', 'hash2', NOW(), 1);

-- Cuentas
INSERT INTO cuenta (id_persona, nombre, tipo, saldo_inicial, moneda, fecha_creacion)
VALUES
  (1, 'Cuenta Ahorros', 'ahorro', 1000000, 'COP', NOW()),
  (2, 'Cuenta Corriente', 'corriente', 500000, 'COP', NOW());

-- Categorías
INSERT INTO categoria (nombre) VALUES ('Alimentación'), ('Transporte'), ('Salud'), ('Entretenimiento');

-- Beneficiarios
INSERT INTO beneficiario (nombre) VALUES ('Supermercado XYZ'), ('Clínica ABC'), ('Cine 123');

-- Tipos de movimiento
INSERT INTO tipo_movimiento (nombre) VALUES ('ingreso'), ('gasto');

-- Movimientos
INSERT INTO movimiento (codigo, monto, id_tipo, id_estado, id_categoria, id_beneficiario, fecha_creacion, id_cuenta, nota)
VALUES
  ('M001', 200000, 2, 2, 1, 1, NOW(), 1, 'Compra supermercado'),
  ('M002', 150000, 2, 2, 2, NULL, NOW(), 1, 'Taxi'),
  ('M003', 50000, 1, 2, 1, NULL, NOW(), 2, 'Ingreso extra');

-- Presupuestos
INSERT INTO presupuesto (nombre, descripcion, monto_total, fecha_inicio, fecha_fin, id_persona, fecha_creacion)
VALUES
  ('Presupuesto Mensual Juan', 'Presupuesto de gastos mensuales', 1200000, '2024-06-01', '2024-06-30', 1, NOW());

-- Presupuesto-Categoría
INSERT INTO presupuesto_categoria (id_presupuesto, id_categoria) VALUES (1, 1), (1, 2);

-- Préstamos
INSERT INTO prestamo (fecha, id_estado, moneda, saldo_inicial, limite_credito, fecha_creacion, id_persona)
VALUES
  ('2024-01-01', 1, 'COP', 500000, 500000, NOW(), 1);

-- Préstamo-Movimiento
INSERT INTO prestamo_movimiento (persona_id_persona, prestamo_id_prestamo, valor, interes, numero_transaccion, seguro, saldo)
VALUES
  (1, 1, 100000, 2.5, 'TRX001', 1000, 400000);

-- Tarjetas de crédito
INSERT INTO tarjeta_credito (id_producto, numero_tarjeta, limite_credito, saldo_actual, fecha_corte, fecha_pago, fecha_creacion, id_estado)
VALUES
  (NULL, '1234567890123456', 2000000, 500000, '2024-06-20', '2024-07-05', NOW(), 1);

-- Movimiento Tarjeta
INSERT INTO movimiento_tarjeta (id_tarjeta, id_persona, fecha, valor, estado, nota, numero_transaccion, id_categoria, id_beneficiario, saldo, cuotas)
VALUES
  (1, 1, NOW(), 100000, 'compra', 'Compra en tienda', 'MT001', 1, 1, 400000, 1),
  (1, 1, NOW(), 50000, 'abono', 'Pago tarjeta', 'MT002', NULL, NULL, 350000, 1);

-- Activos
INSERT INTO activo (nombre_activo, valor, depreciacion, id_persona, fecha_creacion)
VALUES
  ('Laptop', 3000000, 500000, 1, NOW()),
  ('Bicicleta', 800000, 100000, 2, NOW());

-- Acciones
INSERT INTO accion (simbolo, empresa, cantidad, precio_compra, fecha_compra, precio_actual, mercado, id_persona)
VALUES
  ('AAPL', 'Apple Inc.', 10, 150, '2024-01-15', 180, 'NASDAQ', 1),
  ('ECOPETROL', 'Ecopetrol S.A.', 50, 2500, '2024-02-10', 2700, 'BVC', 2);

-- Deuda financiada
INSERT INTO deuda_financiada (entidad, monto_inicial, saldo_actual, numero_transaccion, tasa_interes, fecha_inicio, fecha_fin, id_persona)
VALUES
  ('Banco ABC', 1000000, 800000, 'DF001', 1.5, '2024-01-01', '2025-01-01', 1);
