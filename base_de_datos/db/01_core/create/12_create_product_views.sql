-- =================================================================
-- VISTAS DE PRODUCTO UNIFICADO
-- Estrategia: vista unificada por tipo de producto
-- =================================================================

USE app_presupuesto;

-- -----------------------------------------------------------------
-- Vista principal de productos financieros por persona
-- Estandariza cuenta, tarjeta, prestamo y fondo (activo)
-- -----------------------------------------------------------------
CREATE OR REPLACE VIEW v_producto_unificado AS
SELECT
    c.id_persona,
    c.id_cuenta AS id_producto,
    'cuenta_bancaria' AS tipo_producto,
    c.nombre,
    CAST(
        COALESCE(c.saldo_inicial, 0) + 
        COALESCE(ms.total_ingresos, 0) - 
        COALESCE(ms.total_gastos, 0) 
    AS DECIMAL(15,2)) AS saldo_actual,
    CAST(
        COALESCE(c.saldo_inicial, 0) + 
        COALESCE(ms.total_ingresos, 0) - 
        COALESCE(ms.total_gastos, 0)
    AS DECIMAL(15,2)) AS saldo_disponible,
    CAST(0 AS DECIMAL(15,2)) AS limite_credito,
    CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
    c.fecha_creacion AS fecha_apertura,
    'ACTIVO' AS estado,
    'Cuenta Bancaria' AS tipo_display,
    CAST(
        COALESCE(c.saldo_inicial, 0) + 
        COALESCE(ms.total_ingresos, 0) - 
        COALESCE(ms.total_gastos, 0)
    AS DECIMAL(15,2)) AS valor_efectivo,
    'cuenta' AS origen_tabla
FROM cuenta c
LEFT JOIN (
    SELECT
        m.id_cuenta,
        COALESCE(SUM(
            CASE
                WHEN LOWER(TRIM(tm.nombre)) = 'ingreso' THEN COALESCE(m.monto, 0)
                ELSE 0
            END
        ), 0) AS total_ingresos,
        COALESCE(SUM(
            CASE
                WHEN LOWER(TRIM(tm.nombre)) = 'gasto' THEN COALESCE(m.monto, 0)
                ELSE 0
            END
        ), 0) AS total_gastos
    FROM movimiento m
    LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
    WHERE m.monto IS NOT NULL AND m.monto > 0
    GROUP BY m.id_cuenta
) ms ON ms.id_cuenta = c.id_cuenta

UNION ALL

SELECT
    mtp.id_persona,
    tc.id_tarjeta AS id_producto,
    'tarjeta_credito' AS tipo_producto,
    CONCAT('Tarjeta ', RIGHT(tc.numero_tarjeta, 4)) AS nombre,
    CAST(COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS saldo_actual,
    CAST(COALESCE(tc.limite_credito, 0) - COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS saldo_disponible,
    CAST(COALESCE(tc.limite_credito, 0) AS DECIMAL(15,2)) AS limite_credito,
    CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
    tc.fecha_creacion AS fecha_apertura,
    UPPER(COALESCE(et.nombre, 'ACTIVA')) AS estado,
    'Tarjeta de Credito' AS tipo_display,
    CAST(COALESCE(tc.saldo_actual, 0) AS DECIMAL(15,2)) AS valor_efectivo,
    'tarjeta_credito' AS origen_tabla
FROM tarjeta_credito tc
LEFT JOIN estado_tarjeta et ON et.id_estado = tc.id_estado
LEFT JOIN (
    SELECT id_tarjeta, MIN(id_persona) AS id_persona
    FROM movimiento_tarjeta
    GROUP BY id_tarjeta
) mtp ON mtp.id_tarjeta = tc.id_tarjeta

UNION ALL

SELECT
    p.id_persona,
    p.id_prestamo AS id_producto,
    'prestamo' AS tipo_producto,
    CONCAT('Prestamo #', p.id_prestamo) AS nombre,
    CAST(COALESCE(p.saldo_pendiente, p.saldo_inicial, 0) AS DECIMAL(15,2)) AS saldo_actual,
    CAST(0 AS DECIMAL(15,2)) AS saldo_disponible,
    CAST(0 AS DECIMAL(15,2)) AS limite_credito,
    CAST(0 AS DECIMAL(10,2)) AS tasa_interes,
    p.fecha_creacion AS fecha_apertura,
    UPPER(COALESCE(ep.nombre, 'ACTIVO')) AS estado,
    'Prestamo' AS tipo_display,
    CAST(-ABS(COALESCE(p.saldo_pendiente, p.saldo_inicial, 0)) AS DECIMAL(15,2)) AS valor_efectivo,
    'prestamo' AS origen_tabla
FROM prestamo p
LEFT JOIN estado_prestamo ep ON ep.id_estado = p.id_estado

UNION ALL

SELECT
    a.id_persona,
    a.id_activo AS id_producto,
    'fondo_inversion' AS tipo_producto,
    a.nombre_activo AS nombre,
    CAST(COALESCE(a.valor, 0) AS DECIMAL(15,2)) AS saldo_actual,
    CAST(COALESCE(a.valor, 0) AS DECIMAL(15,2)) AS saldo_disponible,
    CAST(0 AS DECIMAL(15,2)) AS limite_credito,
    CAST(0.80 AS DECIMAL(10,2)) AS tasa_interes,
    a.fecha_creacion AS fecha_apertura,
    'ACTIVO' AS estado,
    'Fondo de Inversion' AS tipo_display,
    CAST(COALESCE(a.valor, 0) AS DECIMAL(15,2)) AS valor_efectivo,
    'activo' AS origen_tabla
FROM activo a;

-- -----------------------------------------------------------------
-- Vista mensual para graficos de Ingresos vs Gastos
-- -----------------------------------------------------------------
CREATE OR REPLACE VIEW v_ingresos_vs_gastos_mensual AS
SELECT
    c.id_persona,
    DATE_FORMAT(m.fecha_creacion, '%Y-%m-01') AS periodo,
    SUM(CASE WHEN LOWER(tm.nombre) = 'ingreso' THEN COALESCE(m.monto, 0) ELSE 0 END) AS ingresos,
    SUM(CASE WHEN LOWER(tm.nombre) = 'gasto' THEN COALESCE(m.monto, 0) ELSE 0 END) AS gastos,
    SUM(CASE
        WHEN LOWER(tm.nombre) = 'ingreso' THEN COALESCE(m.monto, 0)
        WHEN LOWER(tm.nombre) = 'gasto' THEN -COALESCE(m.monto, 0)
        ELSE 0
    END) AS balance_neto
FROM movimiento m
JOIN cuenta c ON c.id_cuenta = m.id_cuenta
LEFT JOIN tipo_movimiento tm ON tm.id_tipo = m.id_tipo
GROUP BY c.id_persona, DATE_FORMAT(m.fecha_creacion, '%Y-%m-01');
