# Modelo de Datos — App Presupuesto (Flet Desktop)

Este documento describe la estructura de datos, relaciones y automatización para la aplicación de escritorio desarrollada con Flet y MySQL.

---

## 📊 Diagrama Entidad-Relación

### Diagrama Conceptual

```
┌─────────────────────────────────────────────────────────────────┐
│                    APP PRESUPUESTO - MODELO DE DATOS           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 USUARIOS (Personas)                                        │
│       │                                                         │
│       ├── 🏦 CUENTAS ──── 💰 TRANSACCIONES ──── 📂 CATEGORÍAS │
│       │      │                    │                            │
│       │      └── 💳 TARJETAS      └── 👥 BENEFICIARIOS         │
│       │                                                         │
│       ├── 📊 PRESUPUESTOS ────── 📂 CATEGORÍAS (M:N)          │
│       │                                                         │
│       ├── 🏠 PRÉSTAMOS ──── 💸 MOVIMIENTOS_PRÉSTAMO           │
│       │                                                         │
│       ├── 💎 ACTIVOS                                           │
│       │                                                         │
│       ├── 📈 INVERSIONES                                       │
│       │                                                         │
│       ├── 🔔 NOTIFICACIONES                                    │
│       │                                                         │
│       ├── ⚙️ CONFIGURACIÓN_USUARIO                            │
│       │                                                         │
│       └── 📝 LOGS_SEGURIDAD (Auditoría)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Estructura por Módulos de la Aplicación

### Módulo de Autenticación (v0.5.0 - Implementado ✅)

#### `usuarios` (tabla principal)
```sql
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL,
    rol ENUM('usuario', 'admin') DEFAULT 'usuario',
    
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_ultimo_login (ultimo_login)
);
```

#### `sesiones` (gestión de sesiones Flet)
```sql
CREATE TABLE sesiones (
    id_sesion VARCHAR(255) PRIMARY KEY,
    id_usuario INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    device_info TEXT,
    activa BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_expiracion (fecha_expiracion)
);
```

#### `logs_seguridad` (auditoría completa)
```sql
CREATE TABLE logs_seguridad (
    id_log BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    accion VARCHAR(100) NOT NULL,
    detalle TEXT,
    ip_address VARCHAR(45),
    device_info TEXT,
    resultado ENUM('EXITOSO', 'FALLIDO', 'BLOQUEADO') NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    INDEX idx_usuario (id_usuario),
    INDEX idx_fecha (fecha),
    INDEX idx_accion (accion),
    INDEX idx_resultado (resultado)
);
```

---

### Módulo de Gestión Financiera (v0.6.0 - Próximo)

#### `cuentas` (cuentas bancarias)
```sql
CREATE TABLE cuentas (
    id_cuenta INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('corriente', 'ahorros', 'efectivo', 'inversion') NOT NULL,
    saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    moneda VARCHAR(3) DEFAULT 'COP',
    numero_cuenta VARCHAR(50),
    banco VARCHAR(100),
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo),
    INDEX idx_activa (activa),
    INDEX idx_banco (banco)
);
```

#### `categorias` (categorización para IA)
```sql
CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo ENUM('ingreso', 'gasto', 'transferencia') NOT NULL,
    color VARCHAR(7) DEFAULT '#2196F3',  -- Color hex para UI Flet
    icono VARCHAR(50) DEFAULT 'category', -- Iconos Flet
    padre_id INT NULL,  -- Para subcategorías jerárquicas
    keywords TEXT,  -- Palabras clave para IA (v0.7.0)
    activa BOOLEAN DEFAULT TRUE,
    orden INT DEFAULT 0,
    
    FOREIGN KEY (padre_id) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    INDEX idx_tipo (tipo),
    INDEX idx_padre (padre_id),
    INDEX idx_activa (activa),
    FULLTEXT idx_keywords (keywords)  -- Para búsqueda IA
);
```

#### `transacciones` (movimientos financieros)
```sql
CREATE TABLE transacciones (
    id_transaccion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_cuenta INT NOT NULL,
    id_categoria INT NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    beneficiario VARCHAR(150),
    numero_referencia VARCHAR(100),
    notas TEXT,
    origen ENUM('manual', 'importado', 'automatico') DEFAULT 'manual',
    etiquetas JSON,  -- Tags flexibles para filtrado
    ubicacion_gps POINT,  -- Geolocalización (futuro)
    adjuntos JSON,  -- Referencias a archivos (futuro)
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_cuenta) REFERENCES cuentas(id_cuenta) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    INDEX idx_cuenta (id_cuenta),
    INDEX idx_fecha (fecha),
    INDEX idx_categoria (id_categoria),
    INDEX idx_monto (monto),
    INDEX idx_origen (origen),
    INDEX idx_beneficiario (beneficiario),
    FULLTEXT idx_descripcion (descripcion)  -- Para búsqueda de texto
);
```

#### `beneficiarios` (terceros frecuentes)
```sql
CREATE TABLE beneficiarios (
    id_beneficiario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM('persona', 'empresa', 'institucion') DEFAULT 'empresa',
    contacto JSON,  -- {email, telefono, direccion}
    categoria_preferida INT,
    activo BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (categoria_preferida) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
    INDEX idx_tipo (tipo),
    INDEX idx_nombre (nombre)
);
```

---

### Módulo de Presupuestos (v0.6.0)

#### `presupuestos`
```sql
CREATE TABLE presupuestos (
    id_presupuesto INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    monto_total DECIMAL(15,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    tipo ENUM('mensual', 'trimestral', 'anual', 'personalizado') DEFAULT 'mensual',
    estado ENUM('activo', 'pausado', 'completado') DEFAULT 'activo',
    alertas JSON,  -- Configuración de alertas {50%, 75%, 90%, 100%}
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_fechas (fecha_inicio, fecha_fin),
    INDEX idx_estado (estado)
);
```

#### `presupuesto_categorias` (relación M:N)
```sql
CREATE TABLE presupuesto_categorias (
    id_presupuesto INT,
    id_categoria INT,
    monto_asignado DECIMAL(15,2) NOT NULL,
    monto_gastado DECIMAL(15,2) DEFAULT 0.00,
    porcentaje_usado DECIMAL(5,2) AS (
        CASE 
            WHEN monto_asignado > 0 THEN (monto_gastado / monto_asignado) * 100 
            ELSE 0 
        END
    ) STORED,
    
    PRIMARY KEY (id_presupuesto, id_categoria),
    FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id_presupuesto) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE,
    INDEX idx_porcentaje (porcentaje_usado)
);
```

---

### Módulo de Crédito y Deudas (v0.7.0)

#### `tarjetas_credito`
```sql
CREATE TABLE tarjetas_credito (
    id_tarjeta INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    banco VARCHAR(100),
    numero_enmascarado VARCHAR(19),  -- **** **** **** 1234
    limite_credito DECIMAL(15,2) NOT NULL,
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    tasa_interes DECIMAL(5,2),
    fecha_corte INT,  -- Día del mes (1-31)
    fecha_pago INT,   -- Día del mes (1-31)
    estado ENUM('activa', 'bloqueada', 'cancelada') DEFAULT 'activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_estado (estado)
);
```

#### `prestamos`
```sql
CREATE TABLE prestamos (
    id_prestamo INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    entidad VARCHAR(150) NOT NULL,
    tipo ENUM('vivienda', 'vehiculo', 'personal', 'educativo', 'comercial') NOT NULL,
    monto_inicial DECIMAL(15,2) NOT NULL,
    saldo_actual DECIMAL(15,2) NOT NULL,
    tasa_interes DECIMAL(5,2),
    plazo_meses INT,
    cuota_mensual DECIMAL(15,2),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado ENUM('activo', 'pausado', 'pagado', 'mora') DEFAULT 'activo',
    descripcion TEXT,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo),
    INDEX idx_estado (estado)
);
```

---

### Módulo de Inversiones (v0.9.0)

#### `inversiones`
```sql
CREATE TABLE inversiones (
    id_inversion INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    tipo_inversion ENUM('accion', 'bono', 'fondo', 'etf', 'criptomoneda', 'inmueble') NOT NULL,
    simbolo VARCHAR(20),  -- Ticker symbol
    nombre VARCHAR(150) NOT NULL,
    cantidad DECIMAL(18,8),
    precio_compra DECIMAL(15,2),
    precio_actual DECIMAL(15,2),
    valor_total AS (cantidad * precio_actual) STORED,
    ganancia_perdida AS (valor_total - (cantidad * precio_compra)) STORED,
    porcentaje_cambio AS (
        CASE 
            WHEN precio_compra > 0 THEN ((precio_actual - precio_compra) / precio_compra) * 100 
            ELSE 0 
        END
    ) STORED,
    fecha_compra DATE,
    fecha_actualizacion_precio TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    broker VARCHAR(100),
    notas TEXT,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo_inversion),
    INDEX idx_simbolo (simbolo)
);
```

#### `activos_fisicos`
```sql
CREATE TABLE activos_fisicos (
    id_activo INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM('inmueble', 'vehiculo', 'maquinaria', 'electronico', 'joyeria', 'otro') NOT NULL,
    valor_compra DECIMAL(15,2),
    valor_actual DECIMAL(15,2),
    depreciacion_anual DECIMAL(5,2),
    fecha_compra DATE,
    ubicacion VARCHAR(255),
    estado ENUM('excelente', 'bueno', 'regular', 'malo') DEFAULT 'bueno',
    asegurado BOOLEAN DEFAULT FALSE,
    descripcion TEXT,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo)
);
```

---

### Módulo de Notificaciones y Configuración

#### `notificaciones`
```sql
CREATE TABLE notificaciones (
    id_notificacion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('info', 'warning', 'error', 'success') DEFAULT 'info',
    categoria ENUM('presupuesto', 'pago', 'inversion', 'seguridad', 'sistema') NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_programada TIMESTAMP NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_adicionales JSON,  -- Contexto adicional
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_tipo (tipo),
    INDEX idx_leida (leida),
    INDEX idx_fecha_programada (fecha_programada)
);
```

#### `configuracion_usuario`
```sql
CREATE TABLE configuracion_usuario (
    id_usuario INT PRIMARY KEY,
    moneda_principal VARCHAR(3) DEFAULT 'COP',
    zona_horaria VARCHAR(50) DEFAULT 'America/Bogota',
    formato_fecha ENUM('dd/mm/yyyy', 'mm/dd/yyyy', 'yyyy-mm-dd') DEFAULT 'dd/mm/yyyy',
    idioma VARCHAR(5) DEFAULT 'es_CO',
    tema ENUM('claro', 'oscuro', 'auto') DEFAULT 'claro',
    notificaciones JSON,  -- Preferencias de notificaciones
    privacidad JSON,      -- Configuración de privacidad
    backup_automatico BOOLEAN DEFAULT TRUE,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);
```

---

## 🔄 Automatización y Triggers

### Triggers para Integridad de Datos

#### 1. Actualización Automática de Saldos
```sql
-- Trigger para actualizar saldo_actual al insertar transacción
DELIMITER //
CREATE TRIGGER tr_actualizar_saldo_insert
    AFTER INSERT ON transacciones
    FOR EACH ROW
BEGIN
    UPDATE cuentas 
    SET saldo_actual = saldo_actual + NEW.monto
    WHERE id_cuenta = NEW.id_cuenta;
END //
DELIMITER ;

-- Trigger para actualizar saldo al modificar transacción
DELIMITER //
CREATE TRIGGER tr_actualizar_saldo_update
    AFTER UPDATE ON transacciones
    FOR EACH ROW
BEGIN
    UPDATE cuentas 
    SET saldo_actual = saldo_actual - OLD.monto + NEW.monto
    WHERE id_cuenta = NEW.id_cuenta;
END //
DELIMITER ;
```

#### 2. Actualización de Presupuestos
```sql
-- Trigger para actualizar gastos en presupuestos
DELIMITER //
CREATE TRIGGER tr_actualizar_presupuesto
    AFTER INSERT ON transacciones
    FOR EACH ROW
BEGIN
    IF NEW.monto < 0 THEN  -- Solo gastos
        UPDATE presupuesto_categorias pc
        JOIN presupuestos p ON pc.id_presupuesto = p.id_presupuesto
        JOIN cuentas c ON NEW.id_cuenta = c.id_cuenta
        SET pc.monto_gastado = pc.monto_gastado + ABS(NEW.monto)
        WHERE pc.id_categoria = NEW.id_categoria
        AND c.id_usuario = p.id_usuario
        AND p.fecha_inicio <= NEW.fecha 
        AND p.fecha_fin >= NEW.fecha
        AND p.estado = 'activo';
    END IF;
END //
DELIMITER ;
```

#### 3. Logs de Auditoría
```sql
-- Trigger para logging de cambios críticos
DELIMITER //
CREATE TRIGGER tr_audit_usuarios
    AFTER UPDATE ON usuarios
    FOR EACH ROW
BEGIN
    IF OLD.password_hash != NEW.password_hash THEN
        INSERT INTO logs_seguridad (id_usuario, accion, detalle, resultado)
        VALUES (NEW.id_usuario, 'CAMBIO_PASSWORD', 'Contraseña actualizada', 'EXITOSO');
    END IF;
END //
DELIMITER ;
```

---

## 📊 Vistas Optimizadas para la UI Flet

### 1. Vista Dashboard Principal
```sql
CREATE VIEW vista_dashboard_usuario AS
SELECT 
    u.id_usuario,
    u.nombre,
    COUNT(DISTINCT c.id_cuenta) as total_cuentas,
    COALESCE(SUM(CASE WHEN c.activa = TRUE THEN c.saldo_actual ELSE 0 END), 0) as patrimonio_total,
    
    -- Gastos último mes
    COALESCE((
        SELECT SUM(ABS(t.monto)) 
        FROM transacciones t 
        JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
        WHERE c2.id_usuario = u.id_usuario 
        AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        AND t.monto < 0
    ), 0) as gastos_ultimo_mes,
    
    -- Ingresos último mes
    COALESCE((
        SELECT SUM(t.monto) 
        FROM transacciones t 
        JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
        WHERE c2.id_usuario = u.id_usuario 
        AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        AND t.monto > 0
    ), 0) as ingresos_ultimo_mes,
    
    -- Transacciones recientes
    (
        SELECT COUNT(*) 
        FROM transacciones t 
        JOIN cuentas c2 ON t.id_cuenta = c2.id_cuenta 
        WHERE c2.id_usuario = u.id_usuario 
        AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    ) as transacciones_semana
    
FROM usuarios u
LEFT JOIN cuentas c ON u.id_usuario = c.id_usuario
WHERE u.activo = TRUE
GROUP BY u.id_usuario, u.nombre;
```

### 2. Vista Resumen de Categorías
```sql
CREATE VIEW vista_gastos_categoria AS
SELECT 
    c.id_usuario,
    cat.id_categoria,
    cat.nombre as categoria,
    cat.color,
    cat.icono,
    COUNT(t.id_transaccion) as num_transacciones,
    SUM(ABS(t.monto)) as total_gastado,
    AVG(ABS(t.monto)) as promedio_transaccion,
    MONTH(t.fecha) as mes,
    YEAR(t.fecha) as año
FROM usuarios c
JOIN cuentas cu ON c.id_usuario = cu.id_usuario
JOIN transacciones t ON cu.id_cuenta = t.id_cuenta
JOIN categorias cat ON t.id_categoria = cat.id_categoria
WHERE t.monto < 0  -- Solo gastos
AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY c.id_usuario, cat.id_categoria, YEAR(t.fecha), MONTH(t.fecha);
```

### 3. Vista Alertas de Presupuesto
```sql
CREATE VIEW vista_alertas_presupuesto AS
SELECT 
    p.id_usuario,
    p.nombre as presupuesto,
    pc.id_categoria,
    cat.nombre as categoria,
    pc.monto_asignado,
    pc.monto_gastado,
    pc.porcentaje_usado,
    CASE 
        WHEN pc.porcentaje_usado >= 100 THEN 'EXCEDIDO'
        WHEN pc.porcentaje_usado >= 90 THEN 'CRITICO'
        WHEN pc.porcentaje_usado >= 75 THEN 'ALTO'
        WHEN pc.porcentaje_usado >= 50 THEN 'MEDIO'
        ELSE 'BAJO'
    END as nivel_alerta,
    cat.color
FROM presupuestos p
JOIN presupuesto_categorias pc ON p.id_presupuesto = pc.id_presupuesto
JOIN categorias cat ON pc.id_categoria = cat.id_categoria
WHERE p.estado = 'activo'
AND CURDATE() BETWEEN p.fecha_inicio AND p.fecha_fin
ORDER BY pc.porcentaje_usado DESC;
```

---

## 🤖 Preparación para IA (v0.7.0)

### Campos para Machine Learning
```sql
-- Tabla para entrenamiento de categorización
CREATE TABLE ml_training_data (
    id_training BIGINT PRIMARY KEY AUTO_INCREMENT,
    descripcion_original TEXT NOT NULL,
    descripcion_normalizada TEXT,
    id_categoria INT NOT NULL,
    beneficiario VARCHAR(150),
    monto DECIMAL(15,2),
    usuario_confirmado BOOLEAN DEFAULT FALSE,
    accuracy_score DECIMAL(5,4),
    fecha_entrenamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FULLTEXT idx_descripcion (descripcion_original, descripcion_normalizada),
    INDEX idx_categoria (id_categoria)
);

-- Tabla para reglas de categorización
CREATE TABLE reglas_categorizacion (
    id_regla INT PRIMARY KEY AUTO_INCREMENT,
    patron VARCHAR(255) NOT NULL,
    id_categoria INT NOT NULL,
    prioridad INT DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    confianza DECIMAL(5,4) DEFAULT 1.0000,
    
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    INDEX idx_patron (patron),
    INDEX idx_prioridad (prioridad)
);
```

---

## 📈 Funciones y Procedimientos Almacenados

### Procedimientos para la Aplicación Flet

#### 1. Autenticación Segura
```sql
DELIMITER //
CREATE PROCEDURE sp_autenticar_usuario(
    IN p_username VARCHAR(150),
    OUT p_user_id INT,
    OUT p_password_hash VARCHAR(255),
    OUT p_intentos_fallidos INT,
    OUT p_bloqueado_hasta TIMESTAMP,
    OUT p_usuario_data JSON
)
BEGIN
    SELECT 
        id_usuario,
        password_hash,
        intentos_fallidos,
        bloqueado_hasta,
        JSON_OBJECT(
            'id', id_usuario,
            'nombre', nombre,
            'email', email,
            'rol', rol,
            'ultimo_login', ultimo_login
        )
    INTO p_user_id, p_password_hash, p_intentos_fallidos, p_bloqueado_hasta, p_usuario_data
    FROM usuarios 
    WHERE (username = p_username OR email = p_username) 
    AND activo = TRUE;
END //
DELIMITER ;
```

#### 2. Dashboard Data
```sql
DELIMITER //
CREATE PROCEDURE sp_get_dashboard_data(IN p_user_id INT)
BEGIN
    -- Datos principales
    SELECT * FROM vista_dashboard_usuario WHERE id_usuario = p_user_id;
    
    -- Transacciones recientes
    SELECT t.*, cat.nombre as categoria, cat.color, c.nombre as cuenta
    FROM transacciones t
    JOIN categorias cat ON t.id_categoria = cat.id_categoria
    JOIN cuentas c ON t.id_cuenta = c.id_cuenta
    WHERE c.id_usuario = p_user_id
    ORDER BY t.fecha DESC, t.fecha_creacion DESC
    LIMIT 10;
    
    -- Alertas de presupuesto
    SELECT * FROM vista_alertas_presupuesto 
    WHERE id_usuario = p_user_id AND nivel_alerta IN ('CRITICO', 'EXCEDIDO')
    LIMIT 5;
END //
DELIMITER ;
```

---

## 🗃️ Índices Optimizados para Rendimiento

### Índices Principales
```sql
-- Índices para búsquedas frecuentes en Flet UI
CREATE INDEX idx_transacciones_usuario_fecha ON transacciones (id_cuenta, fecha DESC);
CREATE INDEX idx_transacciones_categoria_fecha ON transacciones (id_categoria, fecha DESC);
CREATE INDEX idx_notificaciones_usuario_fecha ON notificaciones (id_usuario, fecha_creacion DESC);
CREATE INDEX idx_sesiones_cleanup ON sesiones (fecha_expiracion, activa);

-- Índices compuestos para reportes
CREATE INDEX idx_transacciones_reporte ON transacciones (fecha, id_categoria, monto);
CREATE INDEX idx_presupuesto_periodo ON presupuestos (id_usuario, fecha_inicio, fecha_fin, estado);
```

---

## 📋 Resumen de Implementación por Versión

### ✅ v0.5.0 (Actual - Completado)
- **Módulo de Autenticación**: 100% implementado
  - Tabla `usuarios` con validación bcrypt
  - Tabla `sesiones` para gestión de login
  - Tabla `logs_seguridad` para auditoría
  - Triggers de auditoría
  - Procedimientos de autenticación

### 🚧 v0.6.0 (En Desarrollo - Q1 2025)
- **Módulo Financiero Básico**:
  - Tablas: `cuentas`, `transacciones`, `categorias`, `beneficiarios`
  - Tabla: `presupuestos`, `presupuesto_categorias`
  - Vistas: Dashboard y reportes básicos
  - Triggers: Actualización automática de saldos

### 📋 v0.7.0 (Planificado - Q2 2025)
- **Módulo de IA y Crédito**:
  - Tablas ML: `ml_training_data`, `reglas_categorizacion`
  - Tablas: `tarjetas_credito`, `prestamos`
  - Funciones: Categorización automática
  - Procedimientos: Análisis predictivo

### 🔮 v0.8.0+ (Futuro)
- **Módulos Avanzados**:
  - Tablas: `inversiones`, `activos_fisicos`
  - Sistema completo de reportes
  - Integración con APIs externas
  - Optimizaciones de rendimiento

---

## 📚 Referencias Técnicas

### Documentación Relacionada:
- 🏗️ [Arquitectura del Sistema](../documentacion/ARCHITECTURE.md)
- 🗄️ [Scripts de Base de Datos](../database/scripts/)
- 🔒 [Seguridad y Auditoría](../documentacion/SECURITY.md)
- 🚀 [Roadmap de Desarrollo](../documentacion/roadmap.md)

### Herramientas Recomendadas:
- **MySQL Workbench**: Modelado visual y administración
- **DBeaver**: Cliente universal para desarrollo
- **Adminer**: Interfaz web ligera para testing

---

**💾 Estado del Modelo**: Optimizado para aplicación Flet desktop con MySQL  
**🔄 Última Actualización**: Enero 2025  
**📊 Versión del Modelo**: 2.0 (Flet-based)  
**👨‍💻 Arquitecto de Datos**: Esteban Fabián Patiño Montealegre

**¡El modelo de datos está listo para soportar el crecimiento completo de la aplicación! 🚀**