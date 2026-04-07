# Modelo de Datos — App Presupuesto v0.7.1 (Sistema Empresarial)
**Actualizado: Diciembre 2024**

Este documento describe la estructura de datos empresarial, relaciones, automatización y sistema de documentación para la aplicación de escritorio desarrollada con Flet y MySQL 8.0+ con funcionalidades empresariales.

---

## 📊 Diagrama Entidad-Relación Empresarial

### Diagrama Conceptual Actualizado v0.7.1

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              APP PRESUPUESTO - MODELO DE DATOS EMPRESARIAL v0.7.1      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 USUARIOS (Personas) ──── ⚙️ CONSTANTES (Configuración Global)  │
│       │                                                         │
│       ├── 🏦 CUENTAS ──── 💰 TRANSACCIONES ──── 📂 CATEGORÍAS │
│       │      │                    │                   │        │
│       │      └── 💳 TARJETAS      │                   └── 🤖 IA_REGLAS
│       │                          │                             │
│       │                          ├── 👥 BENEFICIARIOS         │
│       │                          └── 📎 ARCHIVOS_ADJUNTOS     │
│       │                                                         │
│       ├── 📊 PRESUPUESTOS ────── 📂 CATEGORÍAS (M:N)          │
│       │      │                                                 │
│       │      └── 🚨 ALERTAS_PRESUPUESTO                       │
│       │                                                         │
│       ├── 🏠 PRÉSTAMOS ──── 💸 PAGOS_PRÉSTAMO                 │
│       │                                                         │
│       ├── 💎 ACTIVOS ──── 📈 VALUACIONES_ACTIVOS              │
│       │                                                         │
│       ├── 📈 INVERSIONES ──── 💹 MOVIMIENTOS_INVERSIÓN         │
│       │                                                         │
│       ├── 🔔 NOTIFICACIONES                                    │
│       │                                                         │
│       ├── ⚙️ CONFIGURACIÓN_USUARIO                            │
│       │                                                         │
│       ├── 📝 LOGS_SEGURIDAD (Auditoría)                       │
│       │                                                         │
│       ├── 📊 REPORTES_GENERADOS                               │
│       │                                                         │
│       ├── 🔐 TOKENS_API (Integraciones)                       │
│       │                                                         │
│       ├── 🇴🇩 DÍAS_FESTIVOS (Colombia - Automatización)           │
│       │                                                         │
│       ├── 📚 DOCUMENTACION_SISTEMA (Auto-documentación)        │
│       │                                                         │
│       └── 🏗️ ARQUITECTURA_SISTEMA (Componentes & Métricas)      │
│                                                                 │
│  🔄 FUNCIONES EMPRESARIALES:                                   │
│    • fn_dias_habiles() - Cálculo automático días laborales      │
│    • fn_siguiente_dia_habil() - Automatización de fechas        │
│    • fn_calcular_interes() - Cálculos financieros              │
│                                                                 │
│  ⚡ TRIGGERS AUTOMÁTICOS:                                       │
│    • Actualización automática de saldos                       │
│    • Validación de límites y restricciones                   │
│    • Log automático de cambios críticos                        │
│                                                                 │
│  ⏰ EVENTOS PROGRAMADOS:                                        │
│    • Mantenimiento automático diario                           │
│    • Respaldo de seguridad semanal                             │
│    • Limpieza de datos obsoletos                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Estructura por Módulos de la Aplicación

### Módulo de Autenticación (v0.5.2 - Implementado ✅)

#### `usuarios` (tabla principal con seguridad mejorada)
```sql
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash con salt rounds=12
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    
    -- Seguridad
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    email_verificado BOOLEAN DEFAULT FALSE,
    telefono_verificado BOOLEAN DEFAULT FALSE,
    
    -- Roles y permisos
    rol ENUM('usuario', 'premium', 'admin') DEFAULT 'usuario',
    permisos JSON,  -- Permisos específicos en formato JSON
    
    -- Configuración de seguridad
    doble_factor_activo BOOLEAN DEFAULT FALSE,
    secret_2fa VARCHAR(32),  -- Secreto para TOTP
    codigos_backup JSON,     -- Códigos de backup encriptados
    
    -- Metadata
    ip_registro VARCHAR(45),
    timezone VARCHAR(50) DEFAULT 'America/Bogota',
    idioma VARCHAR(5) DEFAULT 'es_CO',
    
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_ultimo_login (ultimo_login),
    INDEX idx_activo (activo),
    FULLTEXT KEY ft_nombre_completo (nombre, apellido)
);
```

#### `sesiones` (gestión avanzada de sesiones)
```sql
CREATE TABLE sesiones (
    id_sesion VARCHAR(255) PRIMARY KEY,
    id_usuario INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    
    -- Información de sesión
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    fecha_ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    
    -- Información del cliente
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    device_info JSON,  -- Información detallada del dispositivo
    geolocation JSON,  -- Ubicación aproximada
    
    -- Configuración de sesión
    recordar_dispositivo BOOLEAN DEFAULT FALSE,
    sesion_confiable BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_expiracion (fecha_expiracion),
    INDEX idx_token_hash (token_hash),
    INDEX idx_activa (activa)
);
```

#### `logs_seguridad` (auditoría completa mejorada)
```sql
CREATE TABLE logs_seguridad (
    id_log BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    id_sesion VARCHAR(255),
    
    -- Detalles del evento
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,  -- Ej: 'AUTH', 'TRANSACCIONES', 'CONFIGURACION'
    detalle TEXT,
    metadatos JSON,  -- Información adicional en formato JSON
    
    -- Información de contexto
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    
    -- Resultado y severidad
    resultado ENUM('EXITOSO', 'FALLIDO', 'BLOQUEADO', 'SOSPECHOSO') NOT NULL,
    nivel_severidad ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL') DEFAULT 'INFO',
    
    -- Timestamps
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado BOOLEAN DEFAULT FALSE,
    fecha_procesamiento TIMESTAMP NULL,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_sesion) REFERENCES sesiones(id_sesion) ON DELETE SET NULL,
    
    INDEX idx_usuario (id_usuario),
    INDEX idx_fecha (fecha),
    INDEX idx_accion (accion),
    INDEX idx_resultado (resultado),
    INDEX idx_severidad (nivel_severidad),
    INDEX idx_modulo (modulo),
    FULLTEXT KEY ft_detalle (detalle)
);
```

### Módulo Financiero Básico (v0.6.0 - En Desarrollo 🚧)

#### `cuentas` (cuentas financieras)
```sql
CREATE TABLE cuentas (
    id_cuenta INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    
    -- Información básica
    nombre VARCHAR(100) NOT NULL,
    tipo_cuenta ENUM('EFECTIVO', 'AHORRO', 'CORRIENTE', 'CREDITO', 'INVERSION') NOT NULL,
    numero_cuenta VARCHAR(50),
    entidad_financiera VARCHAR(100),
    
    -- Saldos
    saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    limite_credito DECIMAL(15,2) DEFAULT 0.00,
    
    -- Configuración
    moneda VARCHAR(3) DEFAULT 'COP',
    activa BOOLEAN DEFAULT TRUE,
    incluir_en_total BOOLEAN DEFAULT TRUE,
    color VARCHAR(7) DEFAULT '#2196F3',  -- Color hex para UI
    icono VARCHAR(50) DEFAULT 'account_balance',
    
    -- Automatización
    auto_categorizacion BOOLEAN DEFAULT TRUE,
    notificaciones BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_cierre DATE NULL,  -- Para cuentas cerradas
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo_cuenta),
    INDEX idx_activa (activa),
    INDEX idx_fecha_creacion (fecha_creacion)
);
```

#### `categorias` (categorías mejoradas con IA)
```sql
CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_categoria_padre INT NULL,  -- Para subcategorías
    
    -- Información básica
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo ENUM('INGRESO', 'GASTO', 'TRANSFERENCIA') NOT NULL,
    
    -- Configuración visual
    color VARCHAR(7) NOT NULL DEFAULT '#757575',
    icono VARCHAR(50) NOT NULL DEFAULT 'category',
    orden_visualizacion INT DEFAULT 0,
    
    -- Configuración de comportamiento
    activa BOOLEAN DEFAULT TRUE,
    predeterminada BOOLEAN DEFAULT FALSE,
    sistema BOOLEAN DEFAULT FALSE,  -- Categorías del sistema (no editables)
    
    -- IA y automatización
    palabras_clave JSON,  -- Palabras clave para categorización automática
    patrones_regex JSON,  -- Patrones regex para detección automática
    confianza_ia DECIMAL(3,2) DEFAULT 0.00,  -- Nivel de confianza de la IA
    
    -- Presupuesto
    limite_mensual DECIMAL(15,2) DEFAULT 0.00,
    alerta_porcentaje INT DEFAULT 80,  -- % para generar alerta
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria_padre) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo),
    INDEX idx_activa (activa),
    INDEX idx_padre (id_categoria_padre),
    FULLTEXT KEY ft_nombre_desc (nombre, descripcion)
);
```

#### `transacciones` (transacciones con IA y adjuntos)
```sql
CREATE TABLE transacciones (
    id_transaccion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_cuenta INT NOT NULL,
    id_categoria INT NOT NULL,
    id_beneficiario INT NULL,
    
    -- Información financiera
    monto DECIMAL(15,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'COP',
    tasa_cambio DECIMAL(10,4) DEFAULT 1.0000,  -- Para conversiones
    monto_original DECIMAL(15,2),  -- Monto en moneda original
    
    -- Detalles de la transacción
    descripcion VARCHAR(255) NOT NULL,
    notas TEXT,
    numero_referencia VARCHAR(100),
    
    -- Fechas
    fecha DATE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Clasificación y etiquetas
    tipo_transaccion ENUM('MANUAL', 'AUTOMATICA', 'IMPORTADA', 'PROGRAMADA') DEFAULT 'MANUAL',
    estado ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'ERROR') DEFAULT 'CONFIRMADA',
    etiquetas JSON,  -- Etiquetas personalizables
    
    -- IA y automatización
    categoria_sugerida_ia INT,
    confianza_categoria DECIMAL(3,2) DEFAULT 0.00,
    procesada_ia BOOLEAN DEFAULT FALSE,
    requiere_revision BOOLEAN DEFAULT FALSE,
    
    -- Geolocalización
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    ubicacion_nombre VARCHAR(200),
    
    -- Adjuntos y evidencia
    tiene_adjuntos BOOLEAN DEFAULT FALSE,
    hash_adjuntos VARCHAR(64),  -- Hash para verificar integridad
    
    FOREIGN KEY (id_cuenta) REFERENCES cuentas(id_cuenta) ON DELETE RESTRICT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE RESTRICT,
    FOREIGN KEY (id_beneficiario) REFERENCES beneficiarios(id_beneficiario) ON DELETE SET NULL,
    FOREIGN KEY (categoria_sugerida_ia) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    
    INDEX idx_cuenta (id_cuenta),
    INDEX idx_categoria (id_categoria),
    INDEX idx_fecha (fecha),
    INDEX idx_monto (monto),
    INDEX idx_estado (estado),
    INDEX idx_tipo (tipo_transaccion),
    INDEX idx_fecha_creacion (fecha_creacion),
    FULLTEXT KEY ft_descripcion_notas (descripcion, notas)
);
```

---

## 📈 Procedimientos Almacenados Optimizados

### Procedimientos para Dashboard Flet

#### 1. Dashboard Completo con Métricas Avanzadas
```sql
DELIMITER //
CREATE PROCEDURE sp_get_dashboard_completo(
    IN p_user_id INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Resumen financiero general
    SELECT 
        COUNT(DISTINCT c.id_cuenta) as total_cuentas,
        COALESCE(SUM(CASE WHEN c.activa = TRUE AND c.incluir_en_total = TRUE 
                         THEN c.saldo_actual ELSE 0 END), 0) as patrimonio_total,
        COALESCE(SUM(CASE WHEN c.tipo_cuenta = 'CREDITO' 
                         THEN c.limite_credito - c.saldo_actual ELSE 0 END), 0) as credito_disponible,
        
        -- Gastos e ingresos del período
        COALESCE((SELECT SUM(ABS(t.monto)) 
                 FROM transacciones t 
                 JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
                 WHERE c2.id_usuario = p_user_id 
                 AND t.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
                 AND t.monto < 0 AND t.estado = 'CONFIRMADA'), 0) as total_gastos,
        
        COALESCE((SELECT SUM(t.monto) 
                 FROM transacciones t 
                 JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
                 WHERE c2.id_usuario = p_user_id 
                 AND t.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
                 AND t.monto > 0 AND t.estado = 'CONFIRMADA'), 0) as total_ingresos,
                
        -- Transacciones del período
        (SELECT COUNT(*) 
         FROM transacciones t 
         JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
         WHERE c2.id_usuario = p_user_id 
         AND t.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
         AND t.estado = 'CONFIRMADA') as total_transacciones
         
    FROM usuarios u
    LEFT JOIN cuentas c ON u.id_usuario = c.id_usuario
    WHERE u.id_usuario = p_user_id AND u.activo = TRUE;
    
    -- Top 5 categorías de gastos
    SELECT 
        cat.id_categoria,
        cat.nombre,
        cat.color,
        cat.icono,
        SUM(ABS(t.monto)) as total_gastado,
        COUNT(t.id_transaccion) as num_transacciones,
        AVG(ABS(t.monto)) as promedio_transaccion
    FROM transacciones t
    JOIN cuentas c ON t.id_cuenta = c.id_cuenta
    JOIN categorias cat ON t.id_categoria = cat.id_categoria
    WHERE c.id_usuario = p_user_id
    AND t.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    AND t.monto < 0 AND t.estado = 'CONFIRMADA'
    GROUP BY cat.id_categoria, cat.nombre, cat.color, cat.icono
    ORDER BY total_gastado DESC
    LIMIT 5;
    
    -- Evolución diaria de saldo (últimos 30 días)
    SELECT 
        fecha,
        SUM(monto_acumulado) as saldo_del_dia
    FROM (
        SELECT 
            t.fecha,
            SUM(t.monto) as monto_acumulado
        FROM transacciones t
        JOIN cuentas c ON t.id_cuenta = c.id_cuenta
        WHERE c.id_usuario = p_user_id
        AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        AND t.estado = 'CONFIRMADA'
        GROUP BY t.fecha
    ) daily_totals
    GROUP BY fecha
    ORDER BY fecha;
    
    COMMIT;
END //
DELIMITER ;
```

#### 2. Análisis Inteligente de Gastos
```sql
DELIMITER //
CREATE PROCEDURE sp_analisis_gastos_inteligente(
    IN p_user_id INT,
    IN p_meses_analisis INT DEFAULT 6
)
BEGIN
    DECLARE v_fecha_inicio DATE DEFAULT DATE_SUB(CURDATE(), INTERVAL p_meses_analisis MONTH);
    
    -- Análisis de tendencias por categoría
    SELECT 
        cat.nombre as categoria,
        cat.color,
        
        -- Gastos por mes
        SUM(CASE WHEN MONTH(t.fecha) = MONTH(CURDATE()) 
                 THEN ABS(t.monto) ELSE 0 END) as gasto_mes_actual,
        SUM(CASE WHEN MONTH(t.fecha) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) 
                 THEN ABS(t.monto) ELSE 0 END) as gasto_mes_anterior,
        
        -- Promedio y tendencia
        AVG(ABS(t.monto)) as promedio_transaccion,
        COUNT(t.id_transaccion) as total_transacciones,
        
        -- Cálculo de tendencia (% cambio mes actual vs anterior)
        CASE 
            WHEN SUM(CASE WHEN MONTH(t.fecha) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) 
                          THEN ABS(t.monto) ELSE 0 END) > 0 
            THEN ROUND(
                ((SUM(CASE WHEN MONTH(t.fecha) = MONTH(CURDATE()) 
                           THEN ABS(t.monto) ELSE 0 END) - 
                  SUM(CASE WHEN MONTH(t.fecha) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) 
                           THEN ABS(t.monto) ELSE 0 END)) / 
                 SUM(CASE WHEN MONTH(t.fecha) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) 
                          THEN ABS(t.monto) ELSE 0 END)) * 100, 2)
            ELSE NULL 
        END as tendencia_porcentual
        
    FROM transacciones t
    JOIN cuentas c ON t.id_cuenta = c.id_cuenta
    JOIN categorias cat ON t.id_categoria = cat.id_categoria
    WHERE c.id_usuario = p_user_id
    AND t.fecha >= v_fecha_inicio
    AND t.monto < 0 AND t.estado = 'CONFIRMADA'
    AND cat.tipo = 'GASTO'
    GROUP BY cat.id_categoria, cat.nombre, cat.color
    HAVING total_transacciones >= 3  -- Solo categorías con actividad significativa
    ORDER BY gasto_mes_actual DESC;
    
    -- Detectar gastos inusuales (outliers)
    SELECT 
        t.id_transaccion,
        t.descripcion,
        t.monto,
        t.fecha,
        cat.nombre as categoria,
        c.nombre as cuenta,
        
        -- Calcular si es un outlier (> 2 desviaciones estándar)
        CASE 
            WHEN ABS(t.monto) > (
                SELECT AVG(ABS(t2.monto)) + (2 * STDDEV(ABS(t2.monto)))
                FROM transacciones t2
                JOIN cuentas c2 ON t2.id_cuenta = c2.id_cuenta
                WHERE c2.id_usuario = p_user_id
                AND t2.id_categoria = t.id_categoria
                AND t2.fecha >= v_fecha_inicio
                AND t2.monto < 0 AND t2.estado = 'CONFIRMADA'
            ) THEN 'OUTLIER_ALTO'
            ELSE 'NORMAL'
        END as tipo_gasto
        
    FROM transacciones t
    JOIN cuentas c ON t.id_cuenta = c.id_cuenta
    JOIN categorias cat ON t.id_categoria = cat.id_categoria
    WHERE c.id_usuario = p_user_id
    AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    AND t.monto < 0 AND t.estado = 'CONFIRMADA'
    HAVING tipo_gasto = 'OUTLIER_ALTO'
    ORDER BY ABS(t.monto) DESC
    LIMIT 10;
    
END //
DELIMITER ;
```

---

## 🔄 Automatización y Triggers Mejorados

### Triggers para Integridad y Performance

#### 1. Sistema de Saldos con Concurrencia
```sql
-- Trigger optimizado para actualización de saldos con lock
DELIMITER //
CREATE TRIGGER tr_actualizar_saldo_insert_v2
    AFTER INSERT ON transacciones
    FOR EACH ROW
BEGIN
    -- Solo actualizar si la transacción está confirmada
    IF NEW.estado = 'CONFIRMADA' THEN
        UPDATE cuentas 
        SET saldo_actual = saldo_actual + NEW.monto,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id_cuenta = NEW.id_cuenta;
        
        -- Log para auditoría
        INSERT INTO logs_seguridad (
            id_usuario, accion, modulo, detalle, resultado, nivel_severidad
        ) SELECT 
            c.id_usuario, 'TRANSACCION_NUEVA', 'FINANZAS',
            CONCAT('Nueva transacción: ', NEW.descripcion, ' por ', NEW.monto),
            'EXITOSO', 'INFO'
        FROM cuentas c WHERE c.id_cuenta = NEW.id_cuenta;
    END IF;
END //
DELIMITER ;

-- Trigger para cambios de estado de transacciones
DELIMITER //
CREATE TRIGGER tr_cambio_estado_transaccion
    AFTER UPDATE ON transacciones
    FOR EACH ROW
BEGIN
    -- Si cambió de no confirmada a confirmada
    IF OLD.estado != 'CONFIRMADA' AND NEW.estado = 'CONFIRMADA' THEN
        UPDATE cuentas 
        SET saldo_actual = saldo_actual + NEW.monto
        WHERE id_cuenta = NEW.id_cuenta;
    
    -- Si cambió de confirmada a cancelada
    ELSEIF OLD.estado = 'CONFIRMADA' AND NEW.estado = 'CANCELADA' THEN
        UPDATE cuentas 
        SET saldo_actual = saldo_actual - NEW.monto
        WHERE id_cuenta = NEW.id_cuenta;
    
    -- Si cambió el monto en una transacción confirmada
    ELSEIF OLD.estado = 'CONFIRMADA' AND NEW.estado = 'CONFIRMADA' 
           AND OLD.monto != NEW.monto THEN
        UPDATE cuentas 
        SET saldo_actual = saldo_actual - OLD.monto + NEW.monto
        WHERE id_cuenta = NEW.id_cuenta;
    END IF;
END //
DELIMITER ;
```

#### 2. Automatización de Categorización con IA
```sql
-- Trigger para categorización automática
DELIMITER //
CREATE TRIGGER tr_categorizar_automaticamente
    BEFORE INSERT ON transacciones
    FOR EACH ROW
BEGIN
    DECLARE v_categoria_sugerida INT DEFAULT NULL;
    DECLARE v_confianza DECIMAL(3,2) DEFAULT 0.00;
    
    -- Solo si no se especificó categoría o es categoría genérica
    IF NEW.id_categoria IS NULL OR NEW.id_categoria = 1 THEN
        
        -- Buscar categoría basada en palabras clave
        SELECT 
            c.id_categoria,
            0.85 as confianza
        INTO v_categoria_sugerida, v_confianza
        FROM categorias c
        JOIN cuentas cta ON cta.id_usuario = c.id_usuario
        WHERE cta.id_cuenta = NEW.id_cuenta
        AND c.activa = TRUE
        AND JSON_LENGTH(c.palabras_clave) > 0
        AND EXISTS (
            SELECT 1 FROM JSON_TABLE(
                c.palabras_clave, '$[*]' COLUMNS (palabra VARCHAR(100) PATH '$')
            ) jt WHERE LOWER(NEW.descripcion) LIKE CONCAT('%', LOWER(jt.palabra), '%')
        )
        ORDER BY c.confianza_ia DESC
        LIMIT 1;
        
        -- Si encontró una categoría sugerida
        IF v_categoria_sugerida IS NOT NULL THEN
            SET NEW.categoria_sugerida_ia = v_categoria_sugerida;
            SET NEW.confianza_categoria = v_confianza;
            
            -- Si la confianza es alta, asignar automáticamente
            IF v_confianza >= 0.80 THEN
                SET NEW.id_categoria = v_categoria_sugerida;
                SET NEW.procesada_ia = TRUE;
            ELSE
                SET NEW.requiere_revision = TRUE;
            END IF;
        END IF;
    END IF;
END //
DELIMITER ;
```

---

## 📊 Vistas Optimizadas para Performance

### 1. Vista Materializada para Dashboard (simulada con tabla)
```sql
-- Tabla para cache de dashboard (simulando vista materializada)
CREATE TABLE cache_dashboard_usuario (
    id_usuario INT PRIMARY KEY,
    total_cuentas INT,
    patrimonio_total DECIMAL(15,2),
    gastos_mes_actual DECIMAL(15,2),
    ingresos_mes_actual DECIMAL(15,2),
    transacciones_mes INT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_fecha_actualizacion (fecha_actualizacion)
);

-- Procedimiento para actualizar cache
DELIMITER //
CREATE PROCEDURE sp_actualizar_cache_dashboard(IN p_user_id INT)
BEGIN
    INSERT INTO cache_dashboard_usuario (
        id_usuario, total_cuentas, patrimonio_total, 
        gastos_mes_actual, ingresos_mes_actual, transacciones_mes
    )
    SELECT 
        p_user_id,
        COUNT(DISTINCT c.id_cuenta),
        COALESCE(SUM(CASE WHEN c.activa = TRUE AND c.incluir_en_total = TRUE 
                         THEN c.saldo_actual ELSE 0 END), 0),
        COALESCE((SELECT SUM(ABS(t.monto)) 
                 FROM transacciones t 
                 JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
                 WHERE c2.id_usuario = p_user_id 
                 AND MONTH(t.fecha) = MONTH(CURDATE())
                 AND YEAR(t.fecha) = YEAR(CURDATE())
                 AND t.monto < 0 AND t.estado = 'CONFIRMADA'), 0),
        COALESCE((SELECT SUM(t.monto) 
                 FROM transacciones t 
                 JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
                 WHERE c2.id_usuario = p_user_id 
                 AND MONTH(t.fecha) = MONTH(CURDATE())
                 AND YEAR(t.fecha) = YEAR(CURDATE())
                 AND t.monto > 0 AND t.estado = 'CONFIRMADA'), 0),
        (SELECT COUNT(*) 
         FROM transacciones t 
         JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
         WHERE c2.id_usuario = p_user_id 
         AND MONTH(t.fecha) = MONTH(CURDATE())
         AND YEAR(t.fecha) = YEAR(CURDATE())
         AND t.estado = 'CONFIRMADA')
    FROM usuarios u
    LEFT JOIN cuentas c ON u.id_usuario = c.id_usuario
    WHERE u.id_usuario = p_user_id
    ON DUPLICATE KEY UPDATE
        total_cuentas = VALUES(total_cuentas),
        patrimonio_total = VALUES(patrimonio_total),
        gastos_mes_actual = VALUES(gastos_mes_actual),
        ingresos_mes_actual = VALUES(ingresos_mes_actual),
        transacciones_mes = VALUES(transacciones_mes),
        fecha_actualizacion = CURRENT_TIMESTAMP;
END //
DELIMITER ;
```

### 2. Índices Compuestos para Consultas Frecuentes
```sql
-- Índices optimizados para consultas comunes
ALTER TABLE transacciones 
ADD INDEX idx_cuenta_fecha_estado (id_cuenta, fecha, estado),
ADD INDEX idx_cuenta_mes_tipo (id_cuenta, fecha, tipo_transaccion),
ADD INDEX idx_categoria_fecha_monto (id_categoria, fecha, monto);

-- Índice para búsquedas de texto
ALTER TABLE transacciones 
ADD FULLTEXT INDEX ft_descripcion_notas_optimized (descripcion, notas);

-- Índices para reportes
ALTER TABLE transacciones
ADD INDEX idx_reporting (fecha, estado, tipo_transaccion, id_cuenta),
ADD INDEX idx_analytics (id_categoria, fecha, estado);
```

---

## 🚀 Optimizaciones de Performance

### Configuración MySQL Recomendada
```sql
-- Configuraciones de performance para la aplicación
SET GLOBAL innodb_buffer_pool_size = 1G;  -- Ajustar según RAM disponible
SET GLOBAL innodb_log_file_size = 256M;
SET GLOBAL innodb_flush_log_at_trx_commit = 2;  -- Para mejor performance
SET GLOBAL query_cache_size = 128M;
SET GLOBAL query_cache_type = 1;

-- Para tablas con muchas escrituras
SET GLOBAL innodb_flush_method = O_DIRECT;
SET GLOBAL innodb_io_capacity = 2000;
```

### Particionado de Tablas Grandes
```sql
-- Particionado de tabla transacciones por fecha (para aplicaciones con mucho volumen)
ALTER TABLE transacciones 
PARTITION BY RANGE (YEAR(fecha)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Particionado de logs_seguridad por fecha
ALTER TABLE logs_seguridad
PARTITION BY RANGE (TO_DAYS(fecha)) (
    PARTITION p_last_month VALUES LESS THAN (TO_DAYS(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))),
    PARTITION p_current VALUES LESS THAN (TO_DAYS(DATE_ADD(CURDATE(), INTERVAL 1 MONTH))),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

---

## 📋 Roadmap de Implementación Actualizado

### ✅ v0.5.2 (Completado - Febrero 2024)
- **Módulo de Autenticación Avanzado**: 100% implementado
  - Tabla `usuarios` con 2FA y metadata de seguridad
  - Tabla `sesiones` con gestión avanzada de tokens
  - Tabla `logs_seguridad` con auditoría completa
  - Triggers de auditoría y seguridad
  - Procedimientos de autenticación con rate limiting

### 🚧 v0.6.0 (En Desarrollo - Q1 2024)
- **Módulo Financiero Core**: 80% completado
  - ✅ Tablas: `cuentas`, `transacciones`, `categorias`, `beneficiarios`
  - ✅ Vistas: Dashboard básico y reportes
  - ✅ Triggers: Actualización automática de saldos
  - 🚧 IA: Categorización automática (en desarrollo)
  - 🚧 Cache: Sistema de cache para dashboard

### 📋 v0.7.0 (Planificado - Q2 2024)
- **Módulo de IA y Análisis**:
  - Tablas ML: `ml_training_data`, `reglas_categorizacion_avanzada`
  - Sistema de detección de outliers y gastos inusuales
  - Análisis predictivo de gastos
  - Recomendaciones automáticas de ahorro
  - Dashboard de insights financieros

### 📋 v0.8.0 (Planificado - Q3 2024)
- **Módulo de Crédito y Préstamos**:
  - Tablas: `tarjetas_credito`, `prestamos`, `pagos_prestamo`
  - Calculadora de cuotas y amortizaciones
  - Alertas de vencimientos
  - Simulador de refinanciación

### 🔮 v0.9.0 (Futuro - Q4 2024)
- **Módulos Avanzados**:
  - Tablas: `inversiones`, `activos_fisicos`, `reportes_automaticos`
  - Sistema completo de reportes con scheduling
  - Integración con APIs bancarias (Open Banking)
  - Backup automático y sincronización

### 🏆 v1.0.0 (Futuro - Q1 2025)
- **Versión Production-Ready**:
  - Optimizaciones finales de performance
  - Sistema de notificaciones push
  - Módulo de importación/exportación completo
  - Compliance total con regulaciones financieras

---

## 🛠️ Herramientas y Utilidades de Desarrollo

### Scripts de Mantenimiento
```sql
-- Procedimiento de limpieza de datos antiguos
DELIMITER //
CREATE PROCEDURE sp_limpiar_datos_antiguos()
BEGIN
    -- Limpiar logs de seguridad mayores a 1 año
    DELETE FROM logs_seguridad 
    WHERE fecha < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    AND nivel_severidad = 'INFO';
    
    -- Limpiar sesiones expiradas
    DELETE FROM sesiones 
    WHERE fecha_expiracion < CURRENT_TIMESTAMP
    OR (fecha_ultimo_acceso < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 30 DAY) 
        AND recordar_dispositivo = FALSE);
    
    -- Optimizar tablas
    OPTIMIZE TABLE transacciones, logs_seguridad, sesiones;
END //
DELIMITER ;

-- Evento programado para ejecutar limpieza automática
CREATE EVENT ev_limpieza_automatica
ON SCHEDULE EVERY 1 WEEK
STARTS CURRENT_TIMESTAMP
DO CALL sp_limpiar_datos_antiguos();
```

### Procedimientos de Backup y Recuperación
```sql
-- Procedimiento para generar backup selectivo
DELIMITER //
CREATE PROCEDURE sp_backup_usuario_data(IN p_user_id INT)
BEGIN
    -- Crear backup de datos de usuario específico
    CREATE TEMPORARY TABLE temp_backup_usuario AS
    SELECT 'usuarios' as tabla, JSON_OBJECT(
        'id_usuario', id_usuario,
        'nombre', nombre,
        'email', email,
        'fecha_creacion', fecha_creacion
    ) as datos
    FROM usuarios WHERE id_usuario = p_user_id
    
    UNION ALL
    
    SELECT 'cuentas' as tabla, JSON_ARRAYAGG(JSON_OBJECT(
        'id_cuenta', id_cuenta,
        'nombre', nombre,
        'tipo_cuenta', tipo_cuenta,
        'saldo_actual', saldo_actual
    )) as datos
    FROM cuentas WHERE id_usuario = p_user_id
    
    UNION ALL
    
    SELECT 'transacciones' as tabla, JSON_ARRAYAGG(JSON_OBJECT(
        'id_transaccion', id_transaccion,
        'monto', monto,
        'descripcion', descripcion,
        'fecha', fecha
    )) as datos
    FROM transacciones t
    JOIN cuentas c ON t.id_cuenta = c.id_cuenta
    WHERE c.id_usuario = p_user_id;
    
    SELECT * FROM temp_backup_usuario;
    DROP TEMPORARY TABLE temp_backup_usuario;
END //
DELIMITER ;
```

---

## 📚 Referencias y Documentación

### Documentación Relacionada:
- 🏗️ [Arquitectura del Sistema](ARCHITECTURE.md)
- 🗄️ [Scripts de Base de Datos](../database/scripts/)
- 🔒 [Seguridad y Auditoría](SECURITY.md)
- 🚀 [Roadmap de Desarrollo](roadmap.md)
- 🧪 [Testing y Calidad](TESTING.md)
- 📖 [API Documentation](API.md)

### Herramientas de Desarrollo Recomendadas:
- **MySQL Workbench**: Modelado visual y administración avanzada
- **DBeaver**: Cliente universal con soporte para debugging
- **Adminer**: Interfaz web ligera para testing rápido
- **MySQL Tuner**: Análisis y optimización de performance
- **Percona Toolkit**: Herramientas avanzadas de MySQL

### Performance Monitoring:
- **MySQL Performance Schema**: Monitoreo nativo de queries
- **Slow Query Log**: Identificación de queries lentas
- **InnoDB Metrics**: Métricas específicas del motor de almacenamiento

---

**💾 Estado del Modelo**: Optimizado para producción con Flet + MySQL  
**🔄 Última Actualización**: Febrero 2024  
**📊 Versión del Modelo**: 2.1 (Production-Ready)  
**👨‍💻 Arquitecto de Datos**: Esteban Fabián Patiño Montealegre  
**🎯 Target Performance**: <100ms queries, 99.9% uptime, 10K+ transacciones/día

**¡El modelo de datos está preparado para escalar y soportar aplicaciones financieras de nivel empresarial! 🚀💪**