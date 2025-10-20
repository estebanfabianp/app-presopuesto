# 💡 Roadmap de Ideas y Mejoras Futuras - App Presupuesto

Este documento centraliza las **ideas, sugerencias y mejoras planificadas** para **app-presupuesto**.  
Se organiza por **prioridad estratégica** y **categorías** para optimizar el desarrollo iterativo con enfoque en **fintech moderno** y **experiencia de usuario excepcional**.

---

## 📋 Tabla de Contenido

1. [🎯 Metodología de Priorización](#-metodología-de-priorización-actualizada-2024)
2. [📊 Resumen Ejecutivo](#-resumen-ejecutivo)
3. [🔴 Crítico - Fundamentos MVP](#-crítico---fundamentos-mvp-y-seguridad)
4. [🟡 Alto - Diferenciación Competitiva](#-alto---diferenciación-competitiva-y-ux)
5. [🔵 Medio - Funcionalidades Avanzadas](#-medio---funcionalidades-avanzadas)
6. [🟢 Bajo - Optimización Premium](#-bajo---optimización-y-funcionalidades-premium)
7. [🚀 Futuro - Disrupción e Innovación](#-futuro---disrupción-e-innovación)
8. [🌍 Escalabilidad Global](#-escalabilidad-global)
9. [📊 Métricas y KPIs](#-métricas-de-éxito-y-kpis-críticos)
10. [💰 Análisis de Costo-Beneficio](#-análisis-de-costo-beneficio)
11. [⚠️ Riesgos y Mitigación](#️-riesgos-y-mitigación)
12. [🔧 Stack Tecnológico](#-stack-tecnológico-actualizado-2024)
13. [🎯 Roadmap Ejecutivo](#-roadmap-ejecutivo-2024-2025)

---

## 📊 Resumen Ejecutivo

### 🎯 Objetivo Principal
Convertir **app-presupuesto** en la **super-app financiera personal #1 en LATAM** para 2025, democratizando herramientas financieras inteligentes mediante IA y automatización.

### 📈 Métricas de Éxito Clave
- **50,000 usuarios activos** para Q4 2024
- **$2M+ en transacciones mensuales** para 2025
- **4.5+ estrellas** en app stores
- **<5% churn rate** mensual

### 💰 Inversión vs ROI Proyectado
| Período | Inversión | ROI Esperado | Break-even |
|---------|-----------|--------------|------------|
| 2024 | $150K | 200% | Q3 2024 |
| 2025 | $300K | 400% | Q1 2025 |

---

## 🎯 Metodología de Priorización Actualizada 2024

### Matriz de Evaluación (Puntuación 1-5)

| Criterio | Descripción | Peso | Fórmula |
|----------|-------------|------|---------|
| **📊 Business Impact** | Impacto en adopción y retención | 25% | (Users Affected × Revenue Impact) / 10 |
| **🔒 Security & Compliance** | Criticidad para seguridad financiera | 25% | (Risk Level × Regulatory Impact) / 10 |
| **⚡ Time to Market** | Velocidad vs. valor | 20% | (Value Score / Development Weeks) × 10 |
| **🔄 Technical Debt** | Impacto en mantenibilidad | 15% | (Complexity Reduction × Future Savings) / 10 |
| **👥 User Experience** | Mejora en satisfacción | 10% | (UX Score Improvement × User Feedback) / 10 |
| **💰 Revenue Potential** | Potencial de monetización | 5% | (Revenue Increase × Market Size) / 100 |

### Scoring Final
**Prioridad = Σ(Criterio × Peso)**
- **🔴 Crítico**: Score 4.0-5.0 (0-3 meses)
- **🟡 Alto**: Score 3.0-3.9 (3-6 meses)
- **🔵 Medio**: Score 2.0-2.9 (6-12 meses)
- **🟢 Bajo**: Score 1.0-1.9 (12-18 meses)
- **🚀 Futuro**: Score 0.5-0.9 (18+ meses)

---

## 🔴 CRÍTICO - Fundamentos MVP y Seguridad

### 📦 Estado Actual del Proyecto

#### ✅ Funcionalidades Completadas
- [x] **Migración de base de datos**: Columna 'activo' → 'estado' con referencia a estado_persona
- [x] **Sistema de estados**: Para personas (ACTIVO, INACTIVO, SUSPENDIDO, BLOQUEADO)
- [x] **Validaciones de seguridad**: Persona activa antes de operaciones

### 🚨 Automatización Financiera Crítica

#### 1. Sistema de Deudas Financiadas
- [ ] **🔥 URGENTE**: Trigger inteligente para movimientos con cuotas → tabla *deudas_financiadas*
  - **Score**: 4.8/5.0 ⭐⭐⭐⭐⭐
  - **Effort**: 3 semanas | **Cost**: $15K | **ROI**: 300%
  - **Auto-cálculo**: Intereses compuestos con múltiples métodos
  - **Gestión de comisiones**: Por cuota con escalamiento automático
  - **Alertas predictivas**: Vencimientos (7, 3, 1 días, vencido)
  - **Reestructuración automática**: Deudas con workflow de aprobación
  - **🎯 KPI**: Reducir 80% el tiempo de gestión manual de cuotas
  - **💡 Quick Win**: Implementar MVP en 1 semana con interés simple

#### 2. Sistema Multi-Moneda Empresarial
- [ ] **🔥 URGENTE**: Soporte completo para COP/USD/EUR
  - **API en tiempo real**: Tasas de cambio (múltiples proveedores)
  - **Cupos dinámicos**: Conversión automática y límites inteligentes
  - **Análisis histórico**: Tendencias para optimización
  - **Protección cambiaria**: Hedging básico
  - **🎯 KPI**: Soporte 95% de transacciones internacionales sin intervención manual

#### 3. Motor de Conciliación Bancaria
- [ ] **🔥 URGENTE**: Automatización completa de conciliación
  - **Matching inteligente**: Algoritmos de similitud (80%+ precisión)
  - **Machine Learning**: Mejora continua de categorización
  - **Gestión de excepciones**: Workflow de aprobación
  - **🎯 KPI**: 90% de transacciones conciliadas automáticamente

### ⚡ Performance y Escalabilidad

#### Optimización de Base de Datos
- [ ] **⚡ CRÍTICO**: Preparación para 100K+ usuarios
  - **Índices optimizados**: Análisis de consultas frecuentes
  - **Particionamiento horizontal**: Por fechas con retención automática
  - **Connection pooling**: Con circuit breaker pattern
  - **🎯 KPI**: Respuesta <200ms para 95% de consultas

### 🔒 Seguridad Financiera de Grado Bancario

#### 1. Autenticación Multi-Factor
- [ ] **🔒 CRÍTICO**: MFA obligatorio para operaciones críticas
  - **JWT avanzado**: Rotación automática cada 15 minutos
  - **Biometría nativa**: Face ID, Touch ID, reconocimiento de voz
  - **Device fingerprinting**: Análisis de riesgo por dispositivo
  - **🎯 KPI**: 0 incidentes de seguridad críticos

#### 2. Encriptación End-to-End
- [ ] **🔒 CRÍTICO**: Protección completa de datos financieros
  - **AES-256**: Key rotation automática mensual
  - **Vault Enterprise**: Gestión centralizada de secretos
  - **PCI DSS Level 1**: Preparación para compliance
  - **🎯 KPI**: 100% de datos sensibles encriptados

#### 3. Auditoría Blockchain
- [ ] **🔒 CRÍTICO**: Trazabilidad inmutable
  - **Blockchain privado**: Audit trail inmutable
  - **SIEM Integration**: Alertas en tiempo real
  - **Compliance automático**: GDPR, CCPA, LGPD
  - **🎯 KPI**: Audit trail completo para 100% de transacciones críticas

---

## 🟡 ALTO - Diferenciación Competitiva y UX

### 🤖 Inteligencia Artificial Financiera

#### 1. Asistente Financiero Personal con IA
- [ ] **🤖 IA PREMIUM**: Copilot financiero conversacional
  - **Procesamiento de lenguaje natural**: Análisis de patrones de gasto
  - **Recomendaciones proactivas**: Basadas en comportamiento y metas
  - **Predicción de flujo de caja**: 85%+ precisión (modelo LSTM)
  - **Detección automática**: Oportunidades de ahorro
  - **🎯 KPI**: 40% mejora en hábitos financieros de usuarios activos

#### 2. Categorización Inteligente Avanzada
- [ ] **🧠 ML CATEGORIZATION**: Aprendizaje automático
  - **Modelo de clasificación**: >95% precisión
  - **Aprendizaje continuo**: Basado en correcciones de usuario
  - **Detección de anomalías**: Alertas automáticas de patrones extraños
  - **Sugerencias inteligentes**: Presupuesto basado en histórico
  - **🎯 KPI**: 95% de transacciones categorizadas automáticamente

### 💰 Gestión Financiera Inteligente

#### 1. Presupuestos Dinámicos 3.0
- [ ] **💰 SMART BUDGETS**: Presupuestos adaptativos con IA
  - **Ajuste automático**: Según ingresos variables
  - **Alertas predictivas**: Machine learning para límites
  - **Presupuestos compartidos**: Familias con permisos granulares
  - **Simulador de escenarios**: "¿Qué pasaría si?" con Monte Carlo
  - **Eventos inteligentes**: Gastos por categoría para eventos específicos
    - *Ejemplo*: Evento "Cerveza" → botones automáticos: Licor, Comida, Transporte
  - **🎯 KPI**: 60% reducción en sobregiros de presupuesto

#### 2. Dashboard Financiero Ejecutivo
- [ ] **📊 EXECUTIVE DASHBOARD**: Visualización avanzada
  - **Widgets personalizables**: Drag-and-drop intuitivo
  - **Gráficos interactivos**: Drill-down hasta transacción individual
  - **Reportes automatizados**: Programables (diario, semanal, mensual)
  - **Exportación multi-formato**: Templates personalizables
  - **🎯 KPI**: 80% de usuarios utilizan dashboards personalizados semanalmente

### 🔌 API-First Architecture

#### 1. API Pública para Desarrolladores
- [ ] **🔌 DEVELOPER API**: Ecosistema abierto
  - **Documentación interactiva**: Swagger/OpenAPI 3.0
  - **SDKs oficiales**: Python, JavaScript, React Native
  - **Webhooks robustos**: Retry automático y circuit breaker
  - **Rate limiting inteligente**: Tiers de suscripción
  - **🎯 KPI**: 100+ integraciones de terceros en primer año

#### 2. Integraciones Bancarias Nativas
- [ ] **🏦 OPEN BANKING**: Agregación multi-banco
  - **APIs PSD2 compliant**: Múltiples proveedores bancarios
  - **Sincronización en tiempo real**: Transacciones automáticas
  - **Reconciliación inteligente**: Matching automático
  - **Cobertura amplia**: 20+ bancos principales en Colombia
  - **🎯 KPI**: 70% de usuarios conectan al menos una cuenta bancaria

---

## 🔵 MEDIO - Funcionalidades Avanzadas

### 📈 Fintech Avanzado

#### 1. Gestión de Inversiones Básica
- [ ] **📈 INVESTMENT TRACKING**: Seguimiento de portafolios
  - **Integración con brokers**: Alianza Valores, BTG Pactual
  - **Cálculo automático**: Rendimientos ajustados por riesgo
  - **Análisis de diversificación**: Recomendaciones automáticas
  - **Alertas de rebalanceo**: Basadas en tolerancia al riesgo
  - **🎯 KPI**: 30% de usuarios premium utilizan tracking de inversiones

#### 2. Planificación Financiera Automatizada
- [ ] **🎯 FINANCIAL PLANNING**: Metas financieras inteligentes
  - **Calculadora de metas**: Múltiples escenarios
  - **Plan de ahorro automático**: Optimización de rendimientos
  - **Simulación de jubilación**: Variables económicas
  - **Recomendaciones de productos**: Basadas en perfil financiero
  - **🎯 KPI**: 50% de usuarios establecen y siguen metas financieras

### 📱 Experiencia Premium

#### 1. Aplicación Móvil Nativa
- [ ] **📱 MOBILE APP**: iOS/Android con React Native
  - **Offline-first**: Sincronización automática
  - **Push notifications**: Timing óptimo e inteligente
  - **Widget nativo**: Entrada rápida de gastos
  - **Asistentes de voz**: Siri Shortcuts y Google Assistant
  - **🎯 KPI**: 4.5+ estrellas en app stores con 10K+ descargas

#### 2. Gamificación Financiera
- [ ] **🎮 GAMIFICATION**: Sistema de logros y recompensas
  - **Challenges mensuales**: Personalizados según perfil financiero
  - **Leaderboards anónimos**: Benchmarking social
  - **Badges y achievements**: Hitos financieros
  - **Programa de recompensas**: Partners comerciales
  - **🎯 KPI**: 35% aumento en engagement de usuarios gamificados

### 📊 Analytics y Business Intelligence

#### Reportes Avanzados
- [ ] **📊 ADVANCED ANALYTICS**: Suite completa de análisis
  - **Cash flow forecasting**: Modelos predictivos
  - **Análisis de sensibilidad**: Decisiones financieras
  - **Benchmarking anónimo**: Usuarios similares
  - **Exportación automática**: Para contadores/asesores
  - **🎯 KPI**: 25% de usuarios utilizan reportes avanzados mensualmente

---

## 🟢 BAJO - Optimización y Funcionalidades Premium

### 🚀 Tecnologías Emergentes

#### 1. Blockchain para Auditoría
- [ ] **₿ BLOCKCHAIN AUDIT**: Trazabilidad inmutable
  - **Smart contracts**: Reglas de negocio automáticas
  - **Tokenización**: Achievements y recompensas
  - **DeFi integration básica**: Yield farming
  - **🎯 KPI**: 100% de transacciones críticas en blockchain

#### 2. IoT Financial Tracking
- [ ] **🏠 IOT INTEGRATION**: Internet de las cosas financiero
  - **Smart home**: Tracking automático de gastos del hogar
  - **Wearables integration**: Micro-pagos
  - **Geolocalización**: Categorización automática por ubicación
  - **🎯 KPI**: 15% de usuarios conectan dispositivos IoT

### 🎨 Experiencia de Usuario Avanzada

#### 1. Personalización Extrema
- [ ] **🎨 HYPER PERSONALIZATION**: UX adaptativa con IA
  - **Interfaz adaptativa**: Patrones de uso individual
  - **Themes dinámicos**: Basados en estado financiero
  - **Onboarding personalizado**: Perfil psicográfico
  - **🎯 KPI**: 90% de usuarios completan onboarding personalizado

#### 2. Accesibilidad Universal
- [ ] **♿ ACCESSIBILITY**: WCAG 2.1 AAA compliance
  - **Screen reader optimization**: Navegación completa por voz
  - **Voice navigation**: Comandos naturales
  - **High contrast modes**: Personalización visual
  - **🎯 KPI**: 5% de usuarios utilizan features de accesibilidad

---

## 🚀 FUTURO - Disrupción e Innovación

### 🧠 Inteligencia Artificial Avanzada

#### 1. GPT Financiero Personalizado
- [ ] **🧠 CUSTOM LLM**: Modelo de lenguaje financiero especializado
  - **Fine-tuning**: Datos financieros colombianos
  - **Asesoría conversacional**: Avanzada y personalizada
  - **Análisis de sentimiento**: Patrones de gasto emocional
  - **🎯 KPI**: 90% de precisión en recomendaciones financieras

#### 2. Computer Vision Financiero
- [ ] **👁️ COMPUTER VISION**: Reconocimiento automático de documentos
  - **OCR avanzado**: Facturas y recibos
  - **Reconocimiento de productos**: Categorización automática
  - **Análisis de documentos**: Financieros complejos
  - **🎯 KPI**: 95% precisión en extracción de datos de documentos

### 🏦 Fintech de Siguiente Generación

#### 1. Neobank Features
- [ ] **🏦 NEOBANK EVOLUTION**: Evolución hacia servicios bancarios
  - **Cuenta de ahorros digital**: Rendimientos competitivos
  - **Tarjeta de débito virtual**: Controles avanzados
  - **Préstamos P2P**: Scoring alternativo
  - **🎯 KPI**: $1M+ en assets under management

#### 2. Crypto y DeFi Integration
- [ ] **₿ DEFI ECOSYSTEM**: Ecosistema DeFi completo
  - **Multi-chain wallet**: Bitcoin, Ethereum, Solana
  - **DeFi protocols**: Yield farming automático
  - **NFT portfolio**: Valuación en tiempo real
  - **🎯 KPI**: 20% de usuarios premium utilizan crypto features

### 🕶️ Realidad Aumentada y Virtual

#### AR Financial Experience
- [ ] **🕶️ AR/VR FINTECH**: Experiencia financiera inmersiva
  - **AR receipt scanning**: Reconocimiento instantáneo
  - **VR financial planning**: Sesiones con asesores
  - **Visualización holográfica**: Analytics complejos
  - **🎯 KPI**: 5% early adopters utilizan AR/VR features

---

## 🌍 Escalabilidad Global

### 🌎 Expansión Internacional
- [ ] **🌎 GLOBAL EXPANSION**: Mercados internacionales
  - **Localización completa**: Mercados LATAM
  - **Multi-currency nativa**: 50+ monedas
  - **Compliance automático**: Regulaciones locales
  - **🎯 KPI**: Expansión a 3 países LATAM en 24 meses

### 🏢 Enterprise B2B
- [ ] **🏢 B2B ENTERPRISE**: Soluciones empresariales
  - **Multi-tenant architecture**: White-labeling
  - **Enterprise SSO**: Active Directory integration
  - **Advanced analytics**: Para CFOs y controllers
  - **🎯 KPI**: 100+ empresas clientes en 18 meses

---

## 📊 Métricas de Éxito y KPIs Críticos

### 👥 User Engagement

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **DAU/MAU Ratio** | >25% | Indicador de stickiness |
| **Session Duration** | >5 minutos | Tiempo promedio por sesión |
| **Feature Adoption** | >60% | Adopción de funcionalidades core |
| **Churn Rate** | <5% mensual | Tasa de abandono |

### 💰 Business Metrics

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Revenue per User** | $5-15 USD/mes | Modelo freemium |
| **Customer Acquisition Cost** | <$10 USD | Costo de adquisición |
| **Lifetime Value** | >$200 USD | Valor de vida del cliente |
| **Time to Value** | <7 días | Tiempo hasta primeros insights |

### ⚡ Technical Performance

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **API Response Time** | <200ms p95 | Tiempo de respuesta |
| **Uptime** | >99.9% SLA | Disponibilidad del servicio |
| **Mobile App Performance** | >90 score | Puntuación de performance |
| **Security Score** | 0 críticas | Vulnerabilidades críticas |

---

## 💰 Análisis de Costo-Beneficio

### 🔴 Prioridad Crítica - ROI Analysis

| Feature | Costo | Tiempo | ROI 6 meses | Impacto Usuario |
|---------|-------|--------|-------------|-----------------|
| Sistema Multi-Moneda | $25K | 4 sem | 400% | ⭐⭐⭐⭐⭐ |
| MFA + Seguridad | $20K | 3 sem | 300% | ⭐⭐⭐⭐⭐ |
| Deudas Financiadas | $15K | 3 sem | 350% | ⭐⭐⭐⭐ |
| DB Optimization | $10K | 2 sem | 200% | ⭐⭐⭐ |

### 🟡 Prioridad Alta - Investment Planning

| Feature | Costo | Tiempo | ROI 12 meses | Market Demand |
|---------|-------|--------|--------------|---------------|
| IA Categorización | $40K | 8 sem | 500% | ⭐⭐⭐⭐⭐ |
| Open Banking | $35K | 6 sem | 300% | ⭐⭐⭐⭐ |
| Mobile App | $30K | 10 sem | 400% | ⭐⭐⭐⭐⭐ |
| API Pública | $25K | 6 sem | 250% | ⭐⭐⭐ |

---

## ⚠️ Riesgos y Mitigación

### 🚨 Riesgos Críticos

#### 1. Seguridad y Compliance
- **Riesgo**: Brecha de seguridad financiera
- **Probabilidad**: Media | **Impacto**: Crítico
- **Mitigación**: 
  - Auditorías de seguridad mensuales
  - Penetration testing trimestral
  - Compliance automático con frameworks

#### 2. Competencia Agresiva
- **Riesgo**: Entrada de big tech (Google, Apple)
- **Probabilidad**: Alta | **Impacto**: Alto
- **Mitigación**:
  - Diferenciación por IA local
  - Partnerships bancarios exclusivos
  - Time-to-market acelerado

#### 3. Regulación Financiera
- **Riesgo**: Cambios regulatorios LATAM
- **Probabilidad**: Media | **Impacto**: Alto
- **Mitigación**:
  - Legal advisory board
  - Compliance framework modular
  - Relationships con reguladores

### 🛡️ Plan de Contingencia

| Escenario | Trigger | Acción Inmediata | Plan 30-60-90 días |
|-----------|---------|------------------|-------------------|
| Breach Seguridad | Detección anomalía | Freeze + audit | Refactor completo |
| Competitor Launch | Market intel | Feature acceleration | Pivoting strategy |
| Funding Gap | Burn rate >150% | Cost optimization | Revenue acceleration |

---

## 🎯 Roadmap Ejecutivo 2024-2025

### 📅 Cronograma Detallado con Hitos

#### Q1 2024: Fundación MVP ✅ (Completado 85%)
- ✅ **Core MVP** con seguridad empresarial
- ✅ **API básica** con documentación completa
- ✅ **Aplicación web** responsive optimizada
- 🔄 **Pending**: Testing automatizado (15% restante)

#### Q2 2024: Intelligence Layer 🔄 (En progreso 40%)
- 🔄 **IA categorización** automática (60% completado)
- 🔄 **Presupuestos dinámicos** adaptativos (30% completado)
- 🔄 **App móvil nativa** iOS/Android (20% completado)
- **Milestone**: 1,000 usuarios activos

#### Q3 2024: Integration & Scale 📋 (Planificado)
- 📋 **Open Banking** con bancos principales
- 📋 **Dashboard ejecutivo** avanzado
- 📋 **API pública** para desarrolladores
- **Milestone**: 5,000 usuarios activos

#### Q4 2024: Premium Features 📋 (Diseño)
- 📋 **Investment tracking** básico
- 📋 **Gamificación** y engagement
- 📋 **Analytics predictivos** avanzados
- **Milestone**: 15,000 usuarios activos

#### 2025: Market Leadership 🚀 (Visión)
- 🚀 **Neobank features** (Q1)
- 🚀 **Expansión LATAM** México/Brasil (Q2-Q3)
- 🚀 **AI copilot avanzado** (Q4)
- **Milestone**: 50,000 usuarios activos

### 🎯 Success Metrics por Quarter

| Quarter | MAU Target | Revenue Target | Feature Releases | Team Size |
|---------|------------|----------------|-------------------|-----------|
| Q1 2024 | 500 | $0 | 3 core | 3 devs |
| Q2 2024 | 1,500 | $2K | 4 premium | 5 devs |
| Q3 2024 | 5,000 | $15K | 3 integration | 7 devs |
| Q4 2024 | 15,000 | $75K | 5 advanced | 10 devs |
| Q1 2025 | 25,000 | $200K | 3 fintech | 12 devs |

---

## 💡 Conclusión Estratégica

**app-presupuesto** está posicionado para convertirse en la **super-app financiera personal líder en LATAM**, combinando:

### 🏆 Ventajas Competitivas Únicas

1. **🇨🇴 Local-First Approach**
   - Entendimiento profundo del mercado colombiano
   - Integración nativa con bancos locales
   - Compliance automático con regulaciones LATAM

2. **🤖 AI-Powered desde el Core**
   - No retrofit de IA, sino diseño AI-first
   - Modelos entrenados con datos financieros locales
   - Personalización extrema basada en comportamiento

3. **🔓 Open Ecosystem Strategy**
   - API-first para crear marketplace de servicios
   - Partnerships estratégicos vs. competencia directa
   - Developer-friendly para adopción viral

4. **⚡ Execution Excellence**
   - Time-to-market superior vs. competencia
   - Team técnico experimentado
   - Funding strategy clara y ejecutable

### 🎯 Visión 2025 Actualizada

> **"La plataforma financiera más inteligente de América Latina que democratiza la libertad financiera a través de IA y automatización"**

**Misión**: Empoderar a 10 millones de latinoamericanos con herramientas financieras inteligentes para tomar mejores decisiones de dinero y construir riqueza a largo plazo.

### 📈 Path to $10M ARR

| Año | Usuarios | ARPU | Revenue | Valuation |
|-----|---------|------|---------|-----------|
| 2024 | 15K | $6 | $1.1M | $15M |
| 2025 | 50K | $12 | $7.2M | $75M |
| 2026 | 150K | $18 | $32.4M | $300M |

---

**📅 Última Actualización**: Enero 2024  
**✍️ Autor**: Esteban Fabián Patiño Montealegre  
**📧 Contacto**: estebanfabianp@gmail.com  
**🚀 Estado**: Documento Vivo - Actualización Quincenal  
**🔄 Próxima Revisión**: 15 Febrero 2024