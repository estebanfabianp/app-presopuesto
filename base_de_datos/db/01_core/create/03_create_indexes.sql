-- =================================================================
-- CREACIÓN DE ÍNDICES
-- Proyecto: app-presupuesto
-- Descripción: Índices para optimización de consultas
-- =================================================================

-- Índices para tabla accion
ALTER TABLE `accion`
  ADD PRIMARY KEY (`id_accion`),
  ADD KEY `fk_accion_persona` (`id_persona`);

-- Índices para tabla activo
ALTER TABLE `activo`
  ADD PRIMARY KEY (`id_activo`),
  ADD KEY `idx_activo_persona` (`id_persona`);

-- Índices para tabla beneficiario
ALTER TABLE `beneficiario`
  ADD PRIMARY KEY (`id_beneficiario`),
  ADD KEY `idx_beneficiario` (`id_beneficiario`);

-- Índices para tabla categoria
ALTER TABLE `categoria`
  ADD PRIMARY KEY (`id_categoria`),
  ADD KEY `idx_categoria` (`id_categoria`);

-- Índices para tabla constantes
ALTER TABLE `constantes`
  ADD UNIQUE KEY `uk_constante_nombre` (`categoria`,`nombre`),
  ADD KEY `idx_constante_categoria` (`categoria`),
  ADD KEY `idx_constante_estado` (`estado`);

-- Índices para tabla cuenta
ALTER TABLE `cuenta`
  ADD PRIMARY KEY (`id_cuenta`),
  ADD KEY `fk_cuenta_persona` (`id_persona`);

-- Índices para tabla deuda_financiada
ALTER TABLE `deuda_financiada`
  ADD PRIMARY KEY (`id_deuda`),
  ADD KEY `fk_deuda_persona` (`id_persona`);

-- Índices para tablas de estado
ALTER TABLE `estado_movimiento`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

ALTER TABLE `estado_prestamo`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

ALTER TABLE `estado_tarjeta`
  ADD PRIMARY KEY (`id_estado`),
  ADD UNIQUE KEY `nombre` (`nombre`);

-- Índices para tabla moneda
ALTER TABLE `moneda`
  ADD PRIMARY KEY (`codigo`);

-- Índices para tabla movimiento
ALTER TABLE `movimiento`
  ADD KEY `fk_movimiento_categoria` (`id_categoria`),
  ADD KEY `fk_movimiento_beneficiario` (`id_beneficiario`),
  ADD KEY `fk_movimiento_tipo` (`id_tipo`),
  ADD KEY `fk_movimiento_estado` (`id_estado`),
  ADD KEY `fk_movimiento_cuenta_idx` (`id_cuenta`);

-- Índices para tabla tarjeta_credito
ALTER TABLE `tarjeta_credito`
  ADD UNIQUE KEY `numero_tarjeta` (`numero_tarjeta`),
  ADD KEY `idx_tc_numero` (`numero_tarjeta`),
  ADD KEY `fk_tc_estado` (`id_estado`);

-- Índices para tabla prestamo
ALTER TABLE `prestamo`
  ADD KEY `fk_prestamo_persona` (`id_persona`),
  ADD KEY `fk_prestamo_estado` (`id_estado`),
  ADD KEY `idx_prestamo_persona` (`id_persona`);

-- Índices para tabla movimiento_tarjeta
ALTER TABLE `movimiento_tarjeta`
  ADD KEY `fk_mt_tarjeta` (`id_tarjeta`),
  ADD KEY `fk_mt_persona` (`id_persona`),
  ADD KEY `fk_mt_categoria` (`id_categoria`),
  ADD KEY `fk_mt_beneficiario` (`id_beneficiario`);

-- AUTO_INCREMENT configuración
ALTER TABLE `accion`
  MODIFY `id_accion` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `activo`
  MODIFY `id_activo` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `beneficiario`
  MODIFY `id_beneficiario` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `categoria`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `constantes`
  MODIFY `id_constante` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `cuenta`
  MODIFY `id_cuenta` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `deuda_financiada`
  MODIFY `id_deuda` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `estado_movimiento`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `estado_prestamo`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `estado_tarjeta`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `moneda`
  MODIFY `codigo` char(3) NOT NULL;

-- =================================================================
-- ÍNDICES PARA TABLA DIAS_FESTIVOS
-- Descripción: Índices optimizados para consultas de días festivos
-- =================================================================

-- Índices para tabla dias_festivos
ALTER TABLE `dias_festivos`
  ADD KEY `idx_fecha` (`fecha`),
  ADD KEY `idx_tipo_pais` (`tipo_festivo`, `pais`),
  ADD KEY `idx_mes_dia` (`mes`, `dia`),
  ADD KEY `idx_estado_fecha` (`estado`, `fecha`),
  ADD UNIQUE KEY `uk_festivo_fecha_tipo` (`fecha`, `tipo_festivo`, `pais`, `region`);

-- AUTO_INCREMENT para tabla dias_festivos
ALTER TABLE `dias_festivos`
  MODIFY `id_festivo` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `movimiento`
  MODIFY `id_movimiento` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `tarjeta_credito`
  MODIFY `id_tarjeta` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `prestamo`
  MODIFY `id_prestamo` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `movimiento_tarjeta`
  MODIFY `id_movimiento_tarjeta` int(11) NOT NULL AUTO_INCREMENT;
