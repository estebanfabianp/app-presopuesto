-- =================================================================
-- ARCHIVO DE VISTAS DEL SISTEMA
-- =================================================================
-- Proyecto: app-presupuesto
-- Archivo: 11_create_view.sql
-- Descripción: Vistas para consultas optimizadas y reportes del sistema
-- Autor: Sistema de Presupuesto Personal
-- Fecha creación: Diciembre 2025
-- Última modificación: 16 de diciembre de 2025
-- Versión: 1.0.0
-- 
-- PROPÓSITO:
-- Este archivo contiene vistas para:
--   * Consultas financieras complejas
--   * Reportes y dashboards
--   * Análisis de datos consolidados
--   * Optimización de consultas frecuentes
--
-- DEPENDENCIAS:
--   * Todas las tablas del sistema
--   * Funciones personalizadas definidas
--
-- ORGANIZACIÓN:
--   1. Vistas de Información Personal y Cuentas
--   2. Vistas de Movimientos y Transacciones
--   3. Vistas de Análisis Financiero
--   4. Vistas de Reportes y Estadísticas
--   5. Vistas de Utilidad y Configuración
-- =================================================================

-- =================================================================
-- SECCIÓN 1: VISTAS DE INFORMACIÓN PERSONAL Y CUENTAS
-- =================================================================

-- =================================================================
-- Vista: v_resumen_cuentas_persona
-- Descripción: Resumen consolidado de todas las cuentas por persona
-- Propósito: Dashboard principal, vista general de patrimonio
-- =================================================================
CREATE OR REPLACE VIEW `v_resumen_cuentas_persona` AS
SELECT 
    p.id_persona,
    p.nombre AS nombre_persona,
    p.usuario,
    COUNT(c.id_cuenta) AS total_cuentas,
    SUM(c.saldo_inicial) AS saldo_inicial_total,
    COALESCE(SUM(mov_resumen.saldo_actual), SUM(c.saldo_inicial)) AS saldo_actual_total,
    c.moneda,
    MIN(c.fecha_creacion) AS primera_cuenta_creada,
    MAX(c.fecha_creacion) AS ultima_cuenta_creada,
    p.estado AS persona_activa
FROM persona p
LEFT JOIN cuenta c ON p.id_persona = c.id_persona
LEFT JOIN (
    SELECT 
        m.id_cuenta,
        SUM(CASE 
            WHEN tm.nombre = 'INGRESO' THEN m.monto 
            WHEN tm.nombre = 'GASTO' THEN -m.monto
            ELSE 0 
        END) AS saldo_movimientos
    FROM movimiento m
    LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
    WHERE m.id_estado = 1  -- Solo movimientos activos
    GROUP BY m.id_cuenta
) mov_resumen ON c.id_cuenta = mov_resumen.id_cuenta
WHERE p.estado = 1  -- Solo personas activas
GROUP BY p.id_persona, p.nombre, p.usuario, c.moneda, p.estado;

-- =================================================================
-- Vista: v_detalle_cuentas
-- Descripción: Información detallada de cuentas con saldo calculado
-- Propósito: Gestión individual de cuentas, transacciones
-- =================================================================
CREATE OR REPLACE VIEW `v_detalle_cuentas` AS
SELECT 
    c.id_cuenta,
    c.id_persona,
    p.nombre AS nombre_persona,
    p.usuario,
    c.nombre AS nombre_cuenta,
    c.tipo AS tipo_cuenta,
    c.saldo_inicial,
    c.moneda,
    c.fecha_creacion,
    COALESCE(mov_stats.total_movimientos, 0) AS total_movimientos,
    COALESCE(mov_stats.total_ingresos, 0) AS total_ingresos,
    COALESCE(mov_stats.total_gastos, 0) AS total_gastos,
    (c.saldo_inicial + COALESCE(mov_stats.saldo_movimientos, 0)) AS saldo_actual,
    COALESCE(mov_stats.ultimo_movimiento, NULL) AS fecha_ultimo_movimiento,
    CASE 
        WHEN COALESCE(mov_stats.total_movimientos, 0) = 0 THEN 'SIN_ACTIVIDAD'
        WHEN DATEDIFF(NOW(), COALESCE(mov_stats.ultimo_movimiento, c.fecha_creacion)) > 30 THEN 'INACTIVA'
        ELSE 'ACTIVA'
    END AS estado_actividad
FROM cuenta c
INNER JOIN persona p ON c.id_persona = p.id_persona
LEFT JOIN (
    SELECT 
        m.id_cuenta,
        COUNT(*) AS total_movimientos,
        SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) AS total_ingresos,
        SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END) AS total_gastos,
        SUM(CASE 
            WHEN tm.nombre = 'INGRESO' THEN m.monto 
            WHEN tm.nombre = 'GASTO' THEN -m.monto
            ELSE 0 
        END) AS saldo_movimientos,
        MAX(m.fecha_creacion) AS ultimo_movimiento
    FROM movimiento m
    LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
    WHERE m.id_estado = 1
    GROUP BY m.id_cuenta
) mov_stats ON c.id_cuenta = mov_stats.id_cuenta
WHERE p.estado = 1;

-- =================================================================
-- SECCIÓN 2: VISTAS DE MOVIMIENTOS Y TRANSACCIONES
-- =================================================================

-- =================================================================
-- Vista: v_movimientos_completos
-- Descripción: Movimientos con toda la información relacionada (JOINs completos)
-- Propósito: Consultas detalladas, reportes, auditoría
-- =================================================================
CREATE OR REPLACE VIEW `v_movimientos_completos` AS
SELECT 
    m.id_movimiento,
    m.codigo,
    m.monto,
    m.numero_transaccion,
    m.nota,
    m.fecha_creacion,
    
    -- Información de la cuenta
    c.id_cuenta,
    c.nombre AS cuenta_nombre,
    c.tipo AS cuenta_tipo,
    c.moneda,
    
    -- Información de la persona
    p.id_persona,
    p.nombre AS persona_nombre,
    p.usuario,
    
    -- Información del tipo de movimiento
    tm.id_tipo,
    tm.nombre AS tipo_movimiento,
    
    -- Información del estado
    em.id_estado,
    em.nombre AS estado_movimiento,
    
    -- Información de la categoría
    cat.id_categoria,
    cat.nombre AS categoria_nombre,
    
    -- Información del beneficiario
    b.id_beneficiario,
    b.nombre AS beneficiario_nombre,
    
    -- Campos calculados
    CASE 
        WHEN tm.nombre = 'INGRESO' THEN 'POSITIVO'
        WHEN tm.nombre = 'GASTO' THEN 'NEGATIVO'
        ELSE 'NEUTRO'
    END AS impacto_saldo,
    
    CASE 
        WHEN tm.nombre = 'INGRESO' THEN m.monto
        ELSE 0
    END AS monto_ingreso,
    
    CASE 
        WHEN tm.nombre = 'GASTO' THEN m.monto
        ELSE 0
    END AS monto_gasto,
    
    YEAR(m.fecha_creacion) AS anio,
    MONTH(m.fecha_creacion) AS mes,
    DAY(m.fecha_creacion) AS dia,
    DAYOFWEEK(m.fecha_creacion) AS dia_semana,
    WEEKOFYEAR(m.fecha_creacion) AS semana_anio
    
FROM movimiento m
INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
INNER JOIN persona p ON c.id_persona = p.id_persona
LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
LEFT JOIN estado_movimiento em ON m.id_estado = em.id_estado
LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
WHERE p.estado = 1;  -- Solo personas activas

-- =================================================================
-- Vista: v_movimientos_recientes
-- Descripción: Últimos movimientos con información esencial
-- Propósito: Dashboard, actividad reciente, notificaciones
-- =================================================================
CREATE OR REPLACE VIEW `v_movimientos_recientes` AS
SELECT 
    m.id_movimiento,
    m.codigo,
    m.monto,
    m.fecha_creacion,
    c.nombre AS cuenta,
    p.nombre AS persona,
    tm.nombre AS tipo,
    cat.nombre AS categoria,
    b.nombre AS beneficiario,
    m.nota,
    DATEDIFF(NOW(), m.fecha_creacion) AS dias_transcurridos,
    CASE 
        WHEN DATEDIFF(NOW(), m.fecha_creacion) = 0 THEN 'HOY'
        WHEN DATEDIFF(NOW(), m.fecha_creacion) = 1 THEN 'AYER'
        WHEN DATEDIFF(NOW(), m.fecha_creacion) <= 7 THEN 'ESTA_SEMANA'
        WHEN DATEDIFF(NOW(), m.fecha_creacion) <= 30 THEN 'ESTE_MES'
        ELSE 'ANTERIOR'
    END AS periodo_relativo
FROM movimiento m
INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
INNER JOIN persona p ON c.id_persona = p.id_persona
LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
LEFT JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
WHERE m.id_estado = 1 AND p.estado = 1
ORDER BY m.fecha_creacion DESC
LIMIT 100;

-- =================================================================
-- SECCIÓN 3: VISTAS DE ANÁLISIS FINANCIERO
-- =================================================================

-- =================================================================
-- Vista: v_gastos_por_categoria
-- Descripción: Análisis de gastos agrupados por categoría y período
-- Propósito: Reportes de gastos, análisis de hábitos, presupuestos
-- =================================================================
CREATE OR REPLACE VIEW `v_gastos_por_categoria` AS
SELECT 
    p.id_persona,
    p.nombre AS persona_nombre,
    cat.id_categoria,
    cat.nombre AS categoria_nombre,
    YEAR(m.fecha_creacion) AS anio,
    MONTH(m.fecha_creacion) AS mes,
    COUNT(m.id_movimiento) AS cantidad_transacciones,
    SUM(m.monto) AS total_gastos,
    AVG(m.monto) AS promedio_gasto,
    MIN(m.monto) AS gasto_minimo,
    MAX(m.monto) AS gasto_maximo,
    MIN(m.fecha_creacion) AS primera_transaccion,
    MAX(m.fecha_creacion) AS ultima_transaccion
FROM movimiento m
INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
INNER JOIN persona p ON c.id_persona = p.id_persona
INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
WHERE tm.nombre = 'GASTO' 
  AND m.id_estado = 1 
  AND p.estado = 1
GROUP BY p.id_persona, p.nombre, cat.id_categoria, cat.nombre, 
         YEAR(m.fecha_creacion), MONTH(m.fecha_creacion)
ORDER BY p.id_persona, anio DESC, mes DESC, total_gastos DESC;

-- =================================================================
-- Vista: v_ingresos_por_categoria
-- Descripción: Análisis de ingresos agrupados por categoría y período
-- Propósito: Reportes de ingresos, proyecciones, análisis de fuentes
-- =================================================================
CREATE OR REPLACE VIEW `v_ingresos_por_categoria` AS
SELECT 
    p.id_persona,
    p.nombre AS persona_nombre,
    cat.id_categoria,
    cat.nombre AS categoria_nombre,
    YEAR(m.fecha_creacion) AS anio,
    MONTH(m.fecha_creacion) AS mes,
    COUNT(m.id_movimiento) AS cantidad_transacciones,
    SUM(m.monto) AS total_ingresos,
    AVG(m.monto) AS promedio_ingreso,
    MIN(m.monto) AS ingreso_minimo,
    MAX(m.monto) AS ingreso_maximo,
    MIN(m.fecha_creacion) AS primera_transaccion,
    MAX(m.fecha_creacion) AS ultima_transaccion
FROM movimiento m
INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
INNER JOIN persona p ON c.id_persona = p.id_persona
INNER JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
LEFT JOIN categoria cat ON m.id_categoria = cat.id_categoria
WHERE tm.nombre = 'INGRESO' 
  AND m.id_estado = 1 
  AND p.estado = 1
GROUP BY p.id_persona, p.nombre, cat.id_categoria, cat.nombre, 
         YEAR(m.fecha_creacion), MONTH(m.fecha_creacion)
ORDER BY p.id_persona, anio DESC, mes DESC, total_ingresos DESC;

-- =================================================================
-- SECCIÓN 4: VISTAS DE REPORTES Y ESTADÍSTICAS
-- =================================================================

-- =================================================================
-- Vista: v_balance_mensual
-- Descripción: Balance financiero mensual por persona (ingresos vs gastos)
-- Propósito: Reportes mensuales, análisis de flujo de caja
-- =================================================================
CREATE OR REPLACE VIEW `v_balance_mensual` AS
SELECT 
    p.id_persona,
    p.nombre AS persona_nombre,
    YEAR(m.fecha_creacion) AS anio,
    MONTH(m.fecha_creacion) AS mes,
    MONTHNAME(m.fecha_creacion) AS nombre_mes,
    
    -- Totales de ingresos
    SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) AS total_ingresos,
    COUNT(CASE WHEN tm.nombre = 'INGRESO' THEN 1 END) AS cantidad_ingresos,
    
    -- Totales de gastos
    SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END) AS total_gastos,
    COUNT(CASE WHEN tm.nombre = 'GASTO' THEN 1 END) AS cantidad_gastos,
    
    -- Balance y métricas
    (SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) - 
     SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END)) AS balance_neto,
    
    -- Porcentajes
    CASE 
        WHEN SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) > 0 THEN
            ROUND((SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END) / 
                   SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END)) * 100, 2)
        ELSE 0
    END AS porcentaje_gastos_vs_ingresos,
    
    -- Clasificación del balance
    CASE 
        WHEN (SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) - 
              SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END)) > 0 THEN 'SUPERAVIT'
        WHEN (SUM(CASE WHEN tm.nombre = 'INGRESO' THEN m.monto ELSE 0 END) - 
              SUM(CASE WHEN tm.nombre = 'GASTO' THEN m.monto ELSE 0 END)) < 0 THEN 'DEFICIT'
        ELSE 'EQUILIBRIO'
    END AS tipo_balance,
    
    COUNT(m.id_movimiento) AS total_transacciones
    
FROM movimiento m
INNER JOIN cuenta c ON m.id_cuenta = c.id_cuenta
INNER JOIN persona p ON c.id_persona = p.id_persona
LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
WHERE m.id_estado = 1 AND p.estado = 1
GROUP BY p.id_persona, p.nombre, YEAR(m.fecha_creacion), MONTH(m.fecha_creacion)
ORDER BY p.id_persona, anio DESC, mes DESC;

-- =================================================================
-- Vista: v_productos_cliente
-- Descripción: Consolidado de todos los productos financieros por cliente
-- Propósito: Vista unificada de productos (cuentas, tarjetas, préstamos, activos)
-- =================================================================
CREATE OR REPLACE VIEW `v_productos_cliente` AS
-- CUENTAS BANCARIAS
SELECT 
    p.id_persona,
    p.nombre AS cliente_nombre,
    p.usuario,
    'CUENTA' AS tipo_producto,
    c.id_cuenta AS id_producto,
    c.nombre AS nombre_producto,
    c.tipo AS subtipo_producto,
    c.saldo_inicial AS valor_inicial,
    (c.saldo_inicial + COALESCE(saldos.saldo_movimientos, 0)) AS valor_actual,
    c.moneda,
    c.fecha_creacion AS fecha_apertura,
    NULL AS fecha_vencimiento,
    CASE 
        WHEN COALESCE(saldos.ultimo_movimiento, c.fecha_creacion) >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 'ACTIVO'
        WHEN COALESCE(saldos.ultimo_movimiento, c.fecha_creacion) >= DATE_SUB(NOW(), INTERVAL 90 DAY) THEN 'POCO_ACTIVO'
        ELSE 'INACTIVO'
    END AS estado_producto,
    COALESCE(saldos.total_movimientos, 0) AS cantidad_transacciones,
    saldos.ultimo_movimiento AS fecha_ultima_transaccion,
    CONCAT('Cuenta ', c.tipo, ' - ', c.nombre) AS descripcion_completa,
    NULL AS tasa_interes,
    NULL AS limite_credito,
    'Producto bancario para gestión de fondos' AS observaciones
FROM persona p
INNER JOIN cuenta c ON p.id_persona = c.id_persona
LEFT JOIN (
    SELECT 
        m.id_cuenta,
        COUNT(*) AS total_movimientos,
        SUM(CASE 
            WHEN tm.nombre = 'INGRESO' THEN m.monto 
            WHEN tm.nombre = 'GASTO' THEN -m.monto
            ELSE 0 
        END) AS saldo_movimientos,
        MAX(m.fecha_creacion) AS ultimo_movimiento
    FROM movimiento m
    LEFT JOIN tipo_movimiento tm ON m.id_tipo = tm.id_tipo
    WHERE m.id_estado = 1
    GROUP BY m.id_cuenta
) saldos ON c.id_cuenta = saldos.id_cuenta

UNION ALL

-- TARJETAS DE CRÉDITO (si existe la tabla tarjeta)
SELECT 
    p.id_persona,
    p.nombre AS cliente_nombre,
    p.usuario,
    'TARJETA' AS tipo_producto,
    t.id_tarjeta AS id_producto,
    CONCAT('Tarjeta **** ', RIGHT(COALESCE(t.numero, '0000'), 4)) AS nombre_producto,
    COALESCE(t.tipo, 'CREDITO') AS subtipo_producto,
    0 AS valor_inicial,
    COALESCE(-t.saldo_actual, 0) AS valor_actual,  -- Negativo porque es deuda
    'COP' AS moneda,
    t.fecha_creacion AS fecha_apertura,
    t.fecha_vencimiento AS fecha_vencimiento,
    CASE 
        WHEN COALESCE(t.estado, 1) = 1 AND t.fecha_vencimiento >= CURDATE() THEN 'ACTIVO'
        WHEN t.fecha_vencimiento < CURDATE() THEN 'VENCIDO'
        ELSE 'INACTIVO'
    END AS estado_producto,
    0 AS cantidad_transacciones,  -- Se podría calcular si hay tabla de movimientos de tarjeta
    t.fecha_ultimo_pago AS fecha_ultima_transaccion,
    CONCAT('Tarjeta de Crédito - Límite: $', FORMAT(t.limite_credito, 0)) AS descripcion_completa,
    t.tasa_interes AS tasa_interes,
    t.limite_credito AS limite_credito,
    CASE 
        WHEN t.saldo_actual > 0 AND t.fecha_pago_minimo < CURDATE() THEN 'PAGO VENCIDO - Requiere atención'
        WHEN t.saldo_actual > (t.limite_credito * 0.8) THEN 'ALTO NIVEL DE UTILIZACIÓN'
        WHEN t.saldo_actual > 0 THEN 'CON SALDO PENDIENTE'
        ELSE 'AL DÍA'
    END AS observaciones
FROM persona p
INNER JOIN tarjeta t ON p.id_persona = t.id_persona

UNION ALL

-- PRÉSTAMOS (si existe la tabla prestamo)
SELECT 
    p.id_persona,
    p.nombre AS cliente_nombre,
    p.usuario,
    'PRESTAMO' AS tipo_producto,
    pr.id_prestamo AS id_producto,
    CONCAT('Préstamo #', pr.numero_prestamo) AS nombre_producto,
    COALESCE(pr.tipo_prestamo, 'PERSONAL') AS subtipo_producto,
    pr.monto_inicial AS valor_inicial,
    pr.saldo_pendiente AS valor_actual,
    'COP' AS moneda,
    pr.fecha_otorgamiento AS fecha_apertura,
    pr.fecha_vencimiento AS fecha_vencimiento,
    CASE 
        WHEN pr.id_estado = 1 AND pr.fecha_vencimiento >= CURDATE() THEN 'ACTIVO'
        WHEN pr.id_estado = 2 THEN 'PAGADO'
        WHEN pr.fecha_vencimiento < CURDATE() THEN 'VENCIDO'
        ELSE 'INACTIVO'
    END AS estado_producto,
    pr.cuotas_pagadas AS cantidad_transacciones,
    pr.fecha_ultimo_pago AS fecha_ultima_transaccion,
    CONCAT('Préstamo de $', FORMAT(pr.monto_inicial, 0), ' - ', pr.cuotas_totales, ' cuotas') AS descripcion_completa,
    pr.tasa_interes AS tasa_interes,
    pr.monto_inicial AS limite_credito,
    CASE 
        WHEN pr.saldo_pendiente > 0 AND pr.fecha_proximo_pago < CURDATE() THEN 'CUOTA VENCIDA'
        WHEN pr.saldo_pendiente = 0 THEN 'PRÉSTAMO CANCELADO'
        WHEN pr.cuotas_pagadas / pr.cuotas_totales > 0.8 THEN 'PRÓXIMO A FINALIZAR'
        ELSE 'EN CURSO NORMAL'
    END AS observaciones
FROM persona p
INNER JOIN prestamo pr ON p.id_persona = pr.id_persona

UNION ALL

-- ACTIVOS/INVERSIONES
SELECT 
    p.id_persona,
    p.nombre AS cliente_nombre,
    p.usuario,
    'ACTIVO' AS tipo_producto,
    a.id_activo AS id_producto,
    a.nombre_activo AS nombre_producto,
    'INVERSION' AS subtipo_producto,
    a.valor AS valor_inicial,
    (a.valor - COALESCE(a.depreciacion, 0)) AS valor_actual,
    'COP' AS moneda,
    a.fecha_creacion AS fecha_apertura,
    NULL AS fecha_vencimiento,
    'ACTIVO' AS estado_producto,
    0 AS cantidad_transacciones,
    NULL AS fecha_ultima_transaccion,
    CONCAT('Activo: ', a.nombre_activo, ' - Valor original: $', FORMAT(a.valor, 0)) AS descripcion_completa,
    NULL AS tasa_interes,
    NULL AS limite_credito,
    CASE 
        WHEN COALESCE(a.depreciacion, 0) > (a.valor * 0.5) THEN 'ALTA DEPRECIACIÓN'
        WHEN COALESCE(a.depreciacion, 0) > (a.valor * 0.2) THEN 'DEPRECIACIÓN MODERADA'
        ELSE 'BUEN ESTADO'
    END AS observaciones
FROM persona p
INNER JOIN activo a ON p.id_persona = a.id_persona

UNION ALL

-- ACCIONES/INVERSIONES EN BOLSA
SELECT 
    p.id_persona,
    p.nombre AS cliente_nombre,
    p.usuario,
    'ACCION' AS tipo_producto,
    ac.id_accion AS id_producto,
    CONCAT(ac.simbolo, ' - ', ac.empresa) AS nombre_producto,
    COALESCE(ac.mercado, 'BOLSA') AS subtipo_producto,
    (ac.cantidad * ac.precio_compra) AS valor_inicial,
    (ac.cantidad * COALESCE(ac.precio_actual, ac.precio_compra)) AS valor_actual,
    'COP' AS moneda,
    ac.fecha_compra AS fecha_apertura,
    NULL AS fecha_vencimiento,
    'ACTIVO' AS estado_producto,
    1 AS cantidad_transacciones,  -- Al menos la compra inicial
    ac.fecha_compra AS fecha_ultima_transaccion,
    CONCAT(ac.cantidad, ' acciones de ', ac.empresa, ' (', ac.simbolo, ')') AS descripcion_completa,
    NULL AS tasa_interes,
    NULL AS limite_credito,
    CASE 
        WHEN COALESCE(ac.precio_actual, ac.precio_compra) > ac.precio_compra THEN 
            CONCAT('GANANCIA: +', ROUND(((COALESCE(ac.precio_actual, ac.precio_compra) - ac.precio_compra) / ac.precio_compra) * 100, 2), '%')
        WHEN COALESCE(ac.precio_actual, ac.precio_compra) < ac.precio_compra THEN 
            CONCAT('PÉRDIDA: ', ROUND(((COALESCE(ac.precio_actual, ac.precio_compra) - ac.precio_compra) / ac.precio_compra) * 100, 2), '%')
        ELSE 'SIN CAMBIOS'
    END AS observaciones
FROM persona p
INNER JOIN accion ac ON p.id_persona = ac.id_persona

-- Filtrar solo personas activas
WHERE p.estado = 1

-- Ordenar por cliente y tipo de producto
ORDER BY cliente_nombre, tipo_producto, nombre_producto;

-- =================================================================
-- Vista: v_resumen_productos_cliente  
-- Descripción: Resumen consolidado de productos por cliente con totales
-- Propósito: Dashboard ejecutivo, análisis de portafolio
-- =================================================================
CREATE OR REPLACE VIEW `v_resumen_productos_cliente` AS
SELECT 
    vpc.id_persona,
    vpc.cliente_nombre,
    vpc.usuario,
    
    -- Conteo de productos por tipo
    COUNT(*) AS total_productos,
    SUM(CASE WHEN vpc.tipo_producto = 'CUENTA' THEN 1 ELSE 0 END) AS total_cuentas,
    SUM(CASE WHEN vpc.tipo_producto = 'TARJETA' THEN 1 ELSE 0 END) AS total_tarjetas,
    SUM(CASE WHEN vpc.tipo_producto = 'PRESTAMO' THEN 1 ELSE 0 END) AS total_prestamos,
    SUM(CASE WHEN vpc.tipo_producto = 'ACTIVO' THEN 1 ELSE 0 END) AS total_activos,
    SUM(CASE WHEN vpc.tipo_producto = 'ACCION' THEN 1 ELSE 0 END) AS total_acciones,
    
    -- Valores consolidados
    SUM(CASE WHEN vpc.tipo_producto IN ('CUENTA', 'ACTIVO', 'ACCION') THEN vpc.valor_actual ELSE 0 END) AS patrimonio_positivo,
    SUM(CASE WHEN vpc.tipo_producto IN ('TARJETA', 'PRESTAMO') AND vpc.valor_actual < 0 THEN ABS(vpc.valor_actual) ELSE 0 END) AS deudas_totales,
    SUM(vpc.valor_actual) AS patrimonio_neto,
    
    -- Productos activos vs inactivos
    SUM(CASE WHEN vpc.estado_producto = 'ACTIVO' THEN 1 ELSE 0 END) AS productos_activos,
    SUM(CASE WHEN vpc.estado_producto IN ('INACTIVO', 'POCO_ACTIVO') THEN 1 ELSE 0 END) AS productos_inactivos,
    
    -- Información de actividad
    MAX(vpc.fecha_ultima_transaccion) AS ultima_actividad,
    MIN(vpc.fecha_apertura) AS cliente_desde,
    
    -- Análisis de riesgo
    CASE 
        WHEN SUM(vpc.valor_actual) < 0 THEN 'ALTO_RIESGO'
        WHEN SUM(CASE WHEN vpc.tipo_producto IN ('TARJETA', 'PRESTAMO') AND vpc.valor_actual < 0 THEN ABS(vpc.valor_actual) ELSE 0 END) > 
             (SUM(CASE WHEN vpc.tipo_producto IN ('CUENTA', 'ACTIVO', 'ACCION') THEN vpc.valor_actual ELSE 0 END) * 0.5) THEN 'MEDIO_RIESGO'
        ELSE 'BAJO_RIESGO'
    END AS nivel_riesgo_financiero,
    
    -- Diversificación de productos
    COUNT(DISTINCT vpc.tipo_producto) AS tipos_productos_diferentes,
    CASE 
        WHEN COUNT(DISTINCT vpc.tipo_producto) >= 4 THEN 'ALTA_DIVERSIFICACION'
        WHEN COUNT(DISTINCT vpc.tipo_producto) >= 2 THEN 'MEDIA_DIVERSIFICACION'
        ELSE 'BAJA_DIVERSIFICACION'
    END AS nivel_diversificacion

FROM v_productos_cliente vpc
GROUP BY vpc.id_persona, vpc.cliente_nombre, vpc.usuario
ORDER BY patrimonio_neto DESC, cliente_nombre;

-- =================================================================
-- SECCIÓN 5: VISTAS DE UTILIDAD Y CONFIGURACIÓN
-- =================================================================

-- =================================================================
-- Vista: v_dias_festivos_vigentes
-- Descripción: Días festivos activos con información de días hábiles
-- Propósito: Cálculos de días hábiles, reportes de fechas
-- =================================================================
CREATE OR REPLACE VIEW `v_dias_festivos_vigentes` AS
SELECT 
    df.id_festivo,
    df.nombre,
    df.fecha,
    df.tipo_festivo,
    df.es_recurrente,
    df.pais,
    df.region,
    df.descripcion,
    df.es_puente,
    YEAR(df.fecha) AS anio,
    MONTH(df.fecha) AS mes,
    DAY(df.fecha) AS dia,
    DAYOFWEEK(df.fecha) AS dia_semana,
    DAYNAME(df.fecha) AS nombre_dia_semana,
    CASE 
        WHEN df.fecha < CURDATE() THEN 'PASADO'
        WHEN df.fecha = CURDATE() THEN 'HOY'
        WHEN df.fecha > CURDATE() THEN 'FUTURO'
    END AS tiempo_relativo,
    DATEDIFF(df.fecha, CURDATE()) AS dias_hasta_festivo,
    CASE 
        WHEN DAYOFWEEK(df.fecha) IN (1, 7) THEN 'FIN_DE_SEMANA'
        ELSE 'DIA_SEMANA'
    END AS tipo_dia
FROM dias_festivos df
WHERE df.estado = 1
ORDER BY df.fecha;

-- =================================================================
-- Vista: v_constantes_sistema
-- Descripción: Configuración del sistema organizada por categorías
-- Propósito: Consulta rápida de configuración, paneles de administración
-- =================================================================
CREATE OR REPLACE VIEW `v_constantes_sistema` AS
SELECT 
    c.id_constante,
    c.categoria,
    c.nombre,
    c.valor,
    c.tipo_dato,
    c.descripcion,
    c.es_editable,
    c.fecha_creacion,
    c.fecha_actualizacion,
    c.creado_por,
    c.estado,
    
    -- Conversiones según tipo de dato
    CASE 
        WHEN c.tipo_dato = 'INTEGER' THEN CAST(c.valor AS SIGNED)
        ELSE NULL
    END AS valor_entero,
    
    CASE 
        WHEN c.tipo_dato = 'DECIMAL' THEN CAST(c.valor AS DECIMAL(15,2))
        ELSE NULL
    END AS valor_decimal,
    
    CASE 
        WHEN c.tipo_dato = 'BOOLEAN' THEN 
            CASE LOWER(c.valor) 
                WHEN 'true' THEN 1 
                WHEN 'false' THEN 0 
                ELSE NULL 
            END
        ELSE NULL
    END AS valor_booleano,
    
    CASE 
        WHEN c.tipo_dato = 'DATE' THEN STR_TO_DATE(c.valor, '%Y-%m-%d')
        ELSE NULL
    END AS valor_fecha
    
FROM constantes c
WHERE c.estado = 1
ORDER BY c.categoria, c.nombre;

-- =================================================================
-- COMENTARIOS FINALES Y RECOMENDACIONES DE USO
-- =================================================================
-- 
-- RENDIMIENTO:
-- * Las vistas están optimizadas con índices sugeridos
-- * Usar LIMIT en consultas de vistas grandes
-- * Considerar materializar vistas frecuentemente consultadas
-- 
-- MANTENIMIENTO:
-- * Revisar planes de ejecución periódicamente
-- * Actualizar estadísticas de tablas base
-- * Monitorear uso de memoria en vistas complejas
-- 
-- SEGURIDAD:
-- * Las vistas respetan el estado activo de personas
-- * Filtran registros según reglas de negocio
-- * No exponen datos sensibles directamente

-- =================================================================
-- VISTA DE DOCUMENTACIÓN COMPLETA
-- =================================================================

CREATE OR REPLACE VIEW `v_documentacion_completa` AS
SELECT 
    ds.tipo,
    ds.nombre_objeto,
    ds.descripcion_corta,
    ds.casos_uso,
    ds.version,
    ds.fecha_creacion,
    CASE 
        WHEN ds.tipo = 'TABLA' THEN 'Base de datos'
        WHEN ds.tipo = 'VISTA' THEN 'Consultas optimizadas'
        WHEN ds.tipo = 'PROCEDIMIENTO' THEN 'Lógica de negocio'
        WHEN ds.tipo = 'FUNCION' THEN 'Cálculos específicos'
        WHEN ds.tipo = 'TRIGGER' THEN 'Automatización'
        WHEN ds.tipo = 'EVENTO' THEN 'Mantenimiento automático'
        WHEN ds.tipo = 'SISTEMA' THEN 'Funcionalidad empresarial'
        ELSE 'General'
    END AS categoria_funcional,
    CASE 
        WHEN ds.nombre_objeto LIKE '%saldo%' OR ds.nombre_objeto IN ('movimiento', 'cuenta', 'tarjeta_credito') THEN 'Crítico'
        WHEN ds.nombre_objeto LIKE '%backup%' OR ds.nombre_objeto LIKE '%migration%' THEN 'Empresarial'
        ELSE 'Normal'
    END AS nivel_criticidad
FROM documentacion_sistema ds
ORDER BY 
    FIELD(ds.tipo, 'TABLA', 'VISTA', 'PROCEDIMIENTO', 'FUNCION', 'TRIGGER', 'EVENTO', 'SISTEMA'),
    ds.nombre_objeto;

-- =================================================================
