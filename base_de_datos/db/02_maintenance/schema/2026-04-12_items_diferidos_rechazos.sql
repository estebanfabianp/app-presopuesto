-- =================================================================
-- MIGRACIÓN: Items Desglosados, Relación Diferidos y Rechazos
-- Fecha: 2026-04-12
-- Propósito: Mejorar modelo de datos con:
--   1. Tabla de items desglosados de movimientos (consultas mejores)
--   2. Relación clara diferido ↔ movimiento (reportes de cuotas)
--   3. Registro de movimientos rechazados (auditoría)
-- =================================================================

-- =================================================================
-- TABLA 1: movimiento_tarjeta_item
-- Descripción: Items individuales de un movimiento desglosado
-- Propósito: Permitir desglose granular de gastos (comida $20 + clase $20)
-- Relaciones: movimiento_tarjeta (N:1)
-- =================================================================

CREATE TABLE IF NOT EXISTS movimiento_tarjeta_item (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_movimiento_tarjeta INT NOT NULL,
    numero_item INT NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    id_categoria INT NULL,
    monto DECIMAL(15,2) NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_mti_movimiento FOREIGN KEY (id_movimiento_tarjeta)
        REFERENCES movimiento_tarjeta(id_movimiento_tarjeta)
        ON DELETE CASCADE,
    CONSTRAINT fk_mti_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria)
        ON DELETE SET NULL,
    
    INDEX idx_mti_movimiento (id_movimiento_tarjeta),
    INDEX idx_mti_categoria (id_categoria),
    UNIQUE KEY uq_mti_item (id_movimiento_tarjeta, numero_item)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- TABLA 2: detalle_diferido_movimiento
-- Descripción: Relaciona diferidos con sus movimientos de cuota
-- Propósito: Rastrear cuáles movimientos corresponden a cada diferido
-- Relaciones: tarjeta_diferido (1:N), movimiento_tarjeta (1:1)
-- =================================================================

CREATE TABLE IF NOT EXISTS detalle_diferido_movimiento (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_diferido INT NOT NULL,
    id_movimiento_tarjeta INT NULL,
    numero_cuota INT NOT NULL,
    tipo_cuota ENUM('CAPITAL','INTERES','TOTAL') NOT NULL DEFAULT 'TOTAL',
    estado ENUM('PENDIENTE','PAGADA','VENCIDA') NOT NULL DEFAULT 'PENDIENTE',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_dim_diferido FOREIGN KEY (id_diferido)
        REFERENCES tarjeta_diferido(id_diferido)
        ON DELETE CASCADE,
    CONSTRAINT fk_dim_movimiento FOREIGN KEY (id_movimiento_tarjeta)
        REFERENCES movimiento_tarjeta(id_movimiento_tarjeta)
        ON DELETE SET NULL,
    
    INDEX idx_dim_diferido (id_diferido),
    INDEX idx_dim_movimiento (id_movimiento_tarjeta),
    INDEX idx_dim_estado (estado),
    UNIQUE KEY uq_dim_cuota (id_diferido, numero_cuota)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- TABLA 3: movimiento_rechazo
-- Descripción: Registro de transacciones rechazadas
-- Propósito: Auditoría, debugging, análisis de patrones de rechazo
-- Relaciones: movimiento_tarjeta (1:1 optional), persona (1:N)
-- =================================================================

CREATE TABLE IF NOT EXISTS movimiento_rechazo (
    id_rechazo INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT NOT NULL,
    id_tarjeta INT NULL,
    id_movimiento_tarjeta INT NULL COMMENT 'Si se creó parcialmente antes del rechazo',
    motivo ENUM(
        'LIMITE_EXCEDIDO',
        'TARJETA_BLOQUEADA',
        'FONDOS_INSUFICIENTES',
        'TARJETA_EXPIRADA',
        'TARJETA_NO_VALIDA',
        'FRAUDE_DETECTADO',
        'CUENTA_CERRADA',
        'TRANSACCION_PENDIENTE',
        'ERROR_PROCESAMIENTO',
        'OTRO'
    ) NOT NULL,
    descripcion VARCHAR(500) NULL,
    intento_valor DECIMAL(15,2) NOT NULL,
    intento_fecha DATETIME NOT NULL,
    intento_categoria VARCHAR(100) NULL,
    respuesta_sistema VARCHAR(500) NULL COMMENT 'Mensaje del sistema cuando rechazó',
    codigo_error VARCHAR(50) NULL,
    ip_origen VARCHAR(45) NULL,
    user_agent VARCHAR(500) NULL,
    intentos_consecutivos INT DEFAULT 1,
    fecha_rechazo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion DATETIME NULL COMMENT 'Cuándo se resolvió (si aplica)',
    resolucion_nota TEXT NULL,
    
    CONSTRAINT fk_mr_persona FOREIGN KEY (id_persona)
        REFERENCES persona(id_persona)
        ON DELETE CASCADE,
    CONSTRAINT fk_mr_tarjeta FOREIGN KEY (id_tarjeta)
        REFERENCES tarjeta_credito(id_tarjeta)
        ON DELETE SET NULL,
    CONSTRAINT fk_mr_movimiento FOREIGN KEY (id_movimiento_tarjeta)
        REFERENCES movimiento_tarjeta(id_movimiento_tarjeta)
        ON DELETE SET NULL,
    
    INDEX idx_mr_persona (id_persona),
    INDEX idx_mr_tarjeta (id_tarjeta),
    INDEX idx_mr_motivo (motivo),
    INDEX idx_mr_fecha (fecha_rechazo),
    INDEX idx_mr_resuelto (fecha_resolucion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- PROCEDIMIENTO: sp_registrar_rechazo
-- Descripción: Helper para registrar rechazos de forma consistente
-- =================================================================

DELIMITER //

CREATE PROCEDURE IF NOT EXISTS sp_registrar_rechazo(
    IN p_id_persona INT,
    IN p_id_tarjeta INT,
    IN p_motivo VARCHAR(50),
    IN p_valor DECIMAL(15,2),
    IN p_descripcion VARCHAR(500),
    OUT p_id_rechazo INT
)
READS SQL DATA
BEGIN
    DECLARE v_intentos INT DEFAULT 1;
    
    -- Contar intentos consecutivos recientes (últimas 2 horas)
    SELECT COUNT(*) INTO v_intentos
    FROM movimiento_rechazo
    WHERE id_persona = p_id_persona
      AND id_tarjeta = p_id_tarjeta
      AND motivo = p_motivo
      AND fecha_rechazo > DATE_SUB(NOW(), INTERVAL 2 HOUR)
      AND fecha_resolucion IS NULL;
    
    SET v_intentos = COALESCE(v_intentos, 0) + 1;
    
    -- Insertar registro de rechazo
    INSERT INTO movimiento_rechazo (
        id_persona, id_tarjeta, motivo, estatus_sistema,
        intento_valor, intento_fecha, intentos_consecutivos, descripcion
    ) VALUES (
        p_id_persona, p_id_tarjeta, p_motivo, p_descripcion,
        p_valor, NOW(), v_intentos, p_descripcion
    );
    
    SET p_id_rechazo = LAST_INSERT_ID();
END //

DELIMITER ;

-- =================================================================
-- VISTA: v_items_por_movimiento
-- Descripción: Resumen de items agrupados por movimiento
-- =================================================================

CREATE OR REPLACE VIEW v_items_por_movimiento AS
SELECT
    m.id_movimiento_tarjeta,
    m.id_tarjeta,
    m.id_persona,
    m.valor,
    m.fecha,
    COUNT(i.id_item) AS cantidad_items,
    GROUP_CONCAT(
        CONCAT(i.descripcion, ' (', IFNULL(c.nombre, 'Sin cat'), '): $', 
               FORMAT(i.monto, 2))
        SEPARATOR ' | '
    ) AS resumen_items,
    SUM(i.monto) AS total_items
FROM movimiento_tarjeta m
LEFT JOIN movimiento_tarjeta_item i ON m.id_movimiento_tarjeta = i.id_movimiento_tarjeta
LEFT JOIN categoria c ON i.id_categoria = c.id_categoria
GROUP BY m.id_movimiento_tarjeta, m.id_tarjeta, m.id_persona, m.valor, m.fecha;

-- =================================================================
-- VISTA: v_diferidos_con_movimientos
-- Descripción: Diferidos con seguimiento de cuotas
-- =================================================================

CREATE OR REPLACE VIEW v_diferidos_con_movimientos AS
SELECT
    d.id_diferido,
    d.descripcion,
    d.valor_total,
    d.numero_cuotas,
    d.cuotas_pagadas,
    d.saldo_pendiente,
    d.estado,
    COUNT(dm.id_movimiento_tarjeta) AS movimientos_registrados,
    SUM(CASE WHEN dm.estado = 'PAGADA' THEN 1 ELSE 0 END) AS cuotas_pagadas_sistema,
    SUM(CASE WHEN dm.estado = 'PENDIENTE' THEN 1 ELSE 0 END) AS cuotas_pendientes,
    SUM(CASE WHEN dm.estado = 'VENCIDA' THEN 1 ELSE 0 END) AS cuotas_vencidas
FROM tarjeta_diferido d
LEFT JOIN detalle_diferido_movimiento dm ON d.id_diferido = dm.id_diferido
GROUP BY d.id_diferido, d.descripcion, d.valor_total, d.numero_cuotas,
         d.cuotas_pagadas, d.saldo_pendiente, d.estado;

-- =================================================================
-- COMENTARIOS
-- =================================================================

ALTER TABLE movimiento_tarjeta_item 
    COMMENT = 'Items individuales de movimientos desglosados - Permite análisis granular de gastos';

ALTER TABLE detalle_diferido_movimiento 
    COMMENT = 'Relación entre diferidos y sus movimientos de cuota - Auditoría de pagos';

ALTER TABLE movimiento_rechazo 
    COMMENT = 'Registro de transacciones rechazadas - Debugging y análisis de patrones';

-- =================================================================
-- DATOS INICIALES: Ejemplo de estructura de items
-- (Descomentar si necesita datos de prueba)
-- =================================================================

-- INSERT INTO movimiento_tarjeta_item (id_movimiento_tarjeta, numero_item, descripcion, id_categoria, monto)
-- VALUES (1, 1, 'Comida', 5, 20000.00),
--        (1, 2, 'Clases de baile', 8, 20000.00);
