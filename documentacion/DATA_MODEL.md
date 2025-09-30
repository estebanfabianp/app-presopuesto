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

#### 2. Logs de Auditoría
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
- 🏗️ [Arquitectura del Sistema](ARCHITECTURE.md)
- 🗄️ [Scripts de Base de Datos](../database/scripts/)
- 🔒 [Seguridad y Auditoría](SECURITY.md)
- 🚀 [Roadmap de Desarrollo](roadmap.md)

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