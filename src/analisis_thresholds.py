"""
Configuración de umbrales y políticas para módulo de análisis.
Facilita ajustes rápidos sin editar rutas de Flask.
"""

# ──────────────────────────────────────────────────────────────
# SCORE DE SALUD (0-100)
# ──────────────────────────────────────────────────────────────
SCORE_THRESHOLDS = {
    'excelente': 80,      # score >= 80
    'estable': 60,        # 60 <= score < 80
    'en_riesgo': 40,      # 40 <= score < 60
    'critico': 0,         # score < 40
}

# Metas ideales por componente del score
SCORE_TARGETS = {
    'tasa_ahorro_min': 20.0,           # Ahorrar mínimo 20% de ingresos
    'pct_gasto_fijo_ideal': 50.0,      # Ideal: 50% gasto fijo
    'pct_uso_tarjetas_ideal': 50.0,    # Ideal: 50% uso tarjeta
    'variacion_gasto_max': 10.0,       # Tolerar ±10% variación mes a mes
}

# Pesos de penalización en score
SCORE_PENALTIES = {
    'ahorro_diferencia': 1.0,          # Penalización por cada % bajo en ahorro
    'fijo_exceso': 0.5,                # Penalización por % sobre ideal de fijo
    'tarjeta_exceso': 0.6,             # Penalización por % sobre ideal tarjeta
    'variacion_exceso': 0.5,           # Penalización por % variación sobre límite
}

# ──────────────────────────────────────────────────────────────
# PRESUPUESTO POR CATEGORÍA (Semáforo)
# ──────────────────────────────────────────────────────────────
PRESUPUESTO_STATES = {
    'verde': 80,          # < 80% → Verde
    'amarillo': 100,      # 80-100% → Amarillo
    'rojo': 100.1,        # > 100% → Rojo
    # sin-presupuesto: Sin límite definido
}

# ──────────────────────────────────────────────────────────────
# ALERTAS INTELIGENTES
# ──────────────────────────────────────────────────────────────
ALERT_THRESHOLDS = {
    'presupuesto_warning': 85.0,       # Alerta si gasto_mes >= 85%
    'presupuesto_critical': 100.0,     # Crítica si >= 100%
    'tarjeta_warning': 0.70,           # Alerta si uso >= 70%
    'tarjeta_critical': 0.90,          # Crítica si uso >= 90%
}

# ──────────────────────────────────────────────────────────────
# ANOMALÍAS Y OUTLIERS
# ──────────────────────────────────────────────────────────────
ANOMALY_DETECTION = {
    'std_dev_multiplier': 2.0,         # Flags monto > (promedio + 2*sigma)
    'avg_multiplier': 1.5,             # AND monto > (promedio * 1.5)
}

# ──────────────────────────────────────────────────────────────
# OPORTUNIDADES DE AHORRO
# ──────────────────────────────────────────────────────────────
OPPORTUNITIES = {
    'gasto_aumento_threshold': 0.15,   # Alerta si categoría sube > 15%
    'subscription_categories': [
        'suscripción', 'netflix', 'spotify', 'hbo', 'disney', 'prime', 'gym',
        'membresía', 'afiliación', 'plan', 'servicio digital', 'cloud'
    ],
    'suspicious_patterns': [
        'transferencia repetida',
        'mismo monto varias veces',
        'categoría inactiva con gasto',
    ],
}

# ──────────────────────────────────────────────────────────────
# PERFIL Y METAS PERSONALIZADAS (Expandible)
# ──────────────────────────────────────────────────────────────
USER_PROFILES = {
    'default': {
        'nombre': 'Equilibrio General',
        'tasa_ahorro_meta': 20.0,      # 20% de los ingresos
        'fijo_ideal': 50.0,             # 50% gasto fijo
    },
    'ahorrista': {
        'nombre': 'Ahorrista Agresivo',
        'tasa_ahorro_meta': 35.0,      # 35% de ingresos
        'fijo_ideal': 40.0,             # Reducir fijos a 40%
    },
    'deudor': {
        'nombre': 'Pago de Deudas',
        'tasa_ahorro_meta': 10.0,      # 10% mínimo
        'fijo_ideal': 60.0,             # Fijos pueden subir a 60%
    },
    'freelancer': {
        'nombre': 'Ingreso Variable',
        'tasa_ahorro_meta': 25.0,      # 25% para buffer
        'fijo_ideal': 45.0,
    },
}

# ──────────────────────────────────────────────────────────────
# ACCIONES RÁPIDAS EN OPORTUNIDADES
# ──────────────────────────────────────────────────────────────
QUICK_ACTIONS = {
    'crear_meta_ahorro': {
        'label': 'Crear Meta',
        'icon': 'fa-bullseye',
        'color': 'success',
        'destination': '/metas-ahorro',  # Ruta navegable
    },
    'ajustar_presupuesto': {
        'label': 'Ajustar Presupuesto',
        'icon': 'fa-chart-line',
        'color': 'warning',
        'destination': '/presupuesto',
    },
    'ver_tarjetas': {
        'label': 'Ver Tarjetas',
        'icon': 'fa-credit-card',
        'color': 'info',
        'destination': '/tarjeta',
    },
    'revisar_suscripciones': {
        'label': 'Revisar Suscripciones',
        'icon': 'fa-sync',
        'color': 'danger',
        'destination': '/nueva-transaccion',  # O modal
    },
}
