-- Vista: resumen de saldos por cuenta
CREATE OR REPLACE VIEW v_cuenta_saldos AS
SELECT
    c.id_cuenta,
    c.nombre AS nombre_cuenta,
    c.tipo AS tipo_cuenta,
    c.moneda,
    c.saldo_inicial AS saldo_actual,
    p.nombre AS titular
FROM cuenta c
    JOIN persona p ON c.id_persona = p.id_persona;

-- Vista: movimientos detallados por cuenta
CREATE OR REPLACE VIEW v_movimientos_detalle AS
SELECT
    m.id_movimiento,
    m.fecha_creacion,
    m.codigo,
    m.monto,
    m.id_tipo,
    tm.nombre AS tipo_movimiento,
    m.id_estado,
    em.nombre AS estado_movimiento,
    m.id_categoria,
    cat.nombre AS categoria,
    m.id_beneficiario,
    b.nombre AS beneficiario,
    m.nota,
    m.id_cuenta,
    c.nombre AS nombre_cuenta,
    p.nombre AS titular
FROM
    movimiento m
    LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
    LEFT JOIN estado_movimiento em ON m.id_estado = em.id_estado
    LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
    LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
    LEFT JOIN cuenta c ON m.id_cuenta = c.id_cuenta
    LEFT JOIN persona p ON c.id_persona = p.id_persona;

-- Vista: resumen de saldos de tarjetas de crédito
CREATE OR REPLACE VIEW v_tarjeta_saldos AS
SELECT t.id_tarjeta, t.numero_tarjeta, t.limite_credito, t.saldo_actual, t.fecha_corte, t.fecha_pago, t.id_estado, et.nombre AS estado_tarjeta
FROM
    tarjeta_credito t
    LEFT JOIN estado_tarjeta et ON t.id_estado = et.id_estado;

-- Vista: resumen de préstamos y su saldo
CREATE OR REPLACE VIEW v_prestamo_saldos AS
SELECT
    p.id_prestamo,
    p.fecha,
    p.saldo_inicial,
    p.limite_credito,
    p.moneda,
    p.id_estado,
    ep.nombre AS estado_prestamo,
    p.id_persona,
    per.nombre AS titular
FROM
    prestamo p
    LEFT JOIN estado_prestamo ep ON p.id_estado = ep.id_estado
    LEFT JOIN persona per ON p.id_persona = per.id_persona;