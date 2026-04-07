-- ========================================================================
-- Script para crear la tabla constantes e insertar datos de prueba
-- Ejecutar en MySQL/MariaDB con la BD seleccionada
-- ========================================================================

-- Crear tabla constantes si no existe
CREATE TABLE IF NOT EXISTS constantes (
    id_constante INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    tipo_dato ENUM('STRING','INTEGER','DECIMAL','BOOLEAN','JSON','DATE') NOT NULL,
    descripcion TEXT,
    es_editable TINYINT(1) DEFAULT 1,
    estado TINYINT(1) DEFAULT 1,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_categoria_estado (categoria, estado),
    INDEX idx_nombre_estado (nombre, estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar datos de prueba
INSERT INTO constantes (categoria, nombre, valor, tipo_dato, descripcion, es_editable, estado) 
VALUES 
-- Categoría FINANCIERO
('FINANCIERO', 'IVA', '0.19', 'DECIMAL', 'Impuesto al valor agregado - 19%', 0, 1),
('FINANCIERO', 'TASA_INTERES_AHORRO', '0.04', 'DECIMAL', 'Rendimiento anual para cuentas de ahorro', 1, 1),
('FINANCIERO', 'TASA_INTERES_PLAZO', '0.05', 'DECIMAL', 'Rendimiento anual para depósitos a plazo', 1, 1),
('FINANCIERO', 'TASA_COMISION_TRANSFERENCIA', '0.001', 'DECIMAL', 'Comisión por transferencia bancaria (0.1%)', 1, 1),

-- Categoría GENERAL
('GENERAL', 'MONEDA_PRINCIPAL', 'COP', 'STRING', 'Moneda principal de la aplicación', 0, 1),
('GENERAL', 'PAIS', 'Colombia', 'STRING', 'País de operación', 0, 1),
('GENERAL', 'IDIOMA_DEFECTO', 'es', 'STRING', 'Código de idioma por defecto', 1, 1),
('GENERAL', 'TEMA_MODO_OSCURO', 'false', 'BOOLEAN', 'Activar modo oscuro por defecto', 1, 1),

-- Categoría LIMITES
('LIMITES', 'MAX_TARJETA_CREDITO', '10000000', 'INTEGER', 'Límite máximo de línea de crédito (en pesos)', 1, 1),
('LIMITES', 'MIN_DEPOSITO', '50000', 'INTEGER', 'Depósito mínimo permitido (en pesos)', 1, 1),
('LIMITES', 'MAX_TRANSFERENCIA_DIARIA', '50000000', 'INTEGER', 'Límite máximo de transferencia por día', 1, 1),

-- Categoría NOTIFICACIONES
('NOTIFICACIONES', 'NOTIFICACIONES_HABILITADAS', 'true', 'BOOLEAN', 'Enviar notificaciones a usuarios', 1, 1),
('NOTIFICACIONES', 'EMAIL_NOTIFICACIONES', 'app@empresa.com', 'STRING', 'Email para enviar notificaciones', 1, 1),

-- Categoría SISTEMA
('SISTEMA', 'VERSION_APP', '1.0.0', 'STRING', 'Versión actual de la aplicación', 0, 1),
('SISTEMA', 'MODO_MANTENIMIENTO', 'false', 'BOOLEAN', 'Activar modo de mantenimiento', 1, 1),
('SISTEMA', 'CONFIG_BACKUP', '{"frecuencia": "diaria", "hora": "02:00"}', 'JSON', 'Configuración de copias de seguridad', 1, 1),
('SISTEMA', 'FECHA_ULTIMO_BACKUP', '2026-04-07', 'DATE', 'Fecha del último backup realizado', 1, 1)
ON DUPLICATE KEY UPDATE 
    valor = VALUES(valor),
    descripcion = VALUES(descripcion),
    es_editable = VALUES(es_editable),
    fecha_actualizacion = NOW();

-- Verificar datos cargados
SELECT COUNT(*) as total_constantes FROM constantes WHERE estado = 1;
SELECT * FROM constantes WHERE estado = 1 ORDER BY categoria, nombre;
