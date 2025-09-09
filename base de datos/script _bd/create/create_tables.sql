-- Tablas de catálogos y tipos
CREATE TABLE tipo_producto (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tipo_movimiento (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE estado_movimiento (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE estado_prestamo (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE estado_tarjeta (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE frecuencia_transaccion (
    id_frecuencia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

-- Tablas principales
CREATE TABLE persona (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(100) NOT NULL UNIQUE,
    usuario VARCHAR(45) NOT NULL UNIQUE,
    hash_contrasena VARCHAR(255) NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    activo TINYINT(4) NOT NULL DEFAULT 1
);

CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    monto_maximo DECIMAL(15,2) DEFAULT NULL,
    monto_minimo DECIMAL(15,2) DEFAULT NULL,
    porcentaje_interes DECIMAL(5,2) DEFAULT NULL,
    id_tipo INT NOT NULL
);

CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE beneficiario (
    id_beneficiario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE movimiento (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(45) DEFAULT NULL,
    monto DECIMAL(15,2) NOT NULL,
    id_tipo INT NOT NULL,
    cuotas INT DEFAULT NULL,
    id_estado INT NOT NULL,
    id_producto INT NOT NULL,
    id_persona INT NOT NULL,
    id_categoria INT NOT NULL,
    id_beneficiario INT NOT NULL,
    nota TEXT DEFAULT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaccion_programada (
    id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_tipo INT NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    id_frecuencia INT NOT NULL,
    repeticion INT DEFAULT NULL,
    id_categoria INT NOT NULL,
    id_beneficiario INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prestamo (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_estado INT NOT NULL,
    moneda VARCHAR(10) NOT NULL,
    saldo_inicial DECIMAL(15,2) NOT NULL,
    limite_credito DECIMAL(15,2) NOT NULL,
    id_persona INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activo (
    id_activo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_activo VARCHAR(100) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    depreciacion DECIMAL(15,2) DEFAULT NULL,
    id_persona INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE presupuesto (
    id_presupuesto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT DEFAULT NULL,
    monto_total DECIMAL(15,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    id_persona INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE presupuesto_categoria (
    id_presupuesto INT NOT NULL,
    id_categoria INT NOT NULL,
    PRIMARY KEY (id_presupuesto, id_categoria)
);

CREATE TABLE tarjeta_credito (
    id_tarjeta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    numero_tarjeta CHAR(16) NOT NULL UNIQUE,
    limite_credito DECIMAL(15,2) NOT NULL,
    saldo_actual DECIMAL(15,2) NOT NULL,
    fecha_corte DATE NOT NULL,
    fecha_pago DATE NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_estado INT NOT NULL
);

CREATE TABLE pago_tarjeta (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_tarjeta INT NOT NULL,
    fecha_pago DATE NOT NULL,
    monto_pago DECIMAL(15,2) NOT NULL,
    referencia VARCHAR(100) DEFAULT NULL,
    id_persona INT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parametro_dian (
    id_parametro INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL,
    concepto VARCHAR(150) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    unidad VARCHAR(50) DEFAULT 'COP',
    descripcion TEXT
);

CREATE TABLE accion (
    id_accion INT AUTO_INCREMENT PRIMARY KEY,
    simbolo VARCHAR(10) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio_compra DECIMAL(15,2) NOT NULL,
    fecha_compra DATE NOT NULL,
    precio_actual DECIMAL(15,2),
    mercado VARCHAR(50) DEFAULT 'BVC',
    id_persona INT
);

CREATE TABLE fondo (
    id_fondo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo ENUM('Mutuo','ETF','Pensión','Otro') NOT NULL,
    entidad VARCHAR(100) NOT NULL,
    monto_invertido DECIMAL(15,2) NOT NULL,
    fecha_inversion DATE NOT NULL,
    valor_actual DECIMAL(15,2),
    rentabilidad DECIMAL(6,2),
    id_persona INT
);
