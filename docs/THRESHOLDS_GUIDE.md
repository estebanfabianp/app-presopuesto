# Política de Umbrales - Análisis de Consumo

## Resumen Rápido

Los umbrales están centralizados en **[src/analisis_thresholds.py](src/analisis_thresholds.py)** para facilitar ajustes sin modificar lógica de Flask.

## Umbrales Actuales (Por Defecto)

### 📊 Score de Salud (0-100)
| Nivel | Rango | Significado |
|-------|-------|-------------|
| ✅ Excelente | ≥ 80 | Excelente control financiero |
| 🟡 Estable | 60-79 | Situación equilibrada |
| ⚠️ En riesgo | 40-59 | Requiere atención |
| ❌ Crítico | < 40 | Necesita intervención urgente |

**Metas ideales:**
- Ahorro: ≥ 20% de ingresos
- Gasto fijo: ~50% ideal
- Variación mes-a-mes: ±10%

### 💳 Alertas (Tarjetas de Crédito)
- **🟡 Aviso**: Uso ≥ **70%** del cupo
- **❌ Crítica**: Uso ≥ **90%** del cupo

### 🎯 Alertas (Presupuesto Mensual)
- **🟡 Aviso**: Gasto ≥ **85%** del presupuesto
- **❌ Crítica**: Gasto ≥ **100%** (sobrepresupuesto)

### 📈 Presupuesto por Categoría (Semáforo)
- **🟢 Verde**: < 80% ejecutado
- **🟡 Amarillo**: 80-100% ejecutado
- **🔴 Rojo**: > 100% ejecutado

## Cómo Personalizar

### Ejemplo: Bajar tarjetas a 60%
[src/analisis_thresholds.py](src/analisis_thresholds.py) línea ~45:
```python
ALERT_THRESHOLDS = {
    'tarjeta_warning': 0.60,  # Cambiar de 0.70 a 0.60
    ...
}
```

### Ejemplo: Ajustar meta de ahorro a 25%
[src/analisis_thresholds.py](src/analisis_thresholds.py) línea ~15:
```python
SCORE_TARGETS = {
    'tasa_ahorro_min': 25.0,  # Cambiar de 20.0 a 25.0
    ...
}
```

## Botones de Acción Rápida

Las oportunidades incluyen botones que navegan a:

| Acción | Ruta | Caso de uso |
|--------|------|------------|
| Ajustar Presupuesto | `/presupuesto` | Categoría con gasto alto |
| Revisar Suscripciones | `/nueva-transaccion` | Suscripciones detectadas |
| Crear Meta | `/metas-ahorro` | Objetivo de ahorro (futuro) |
| Ver Tarjetas | `/tarjeta` | Alerta de tarjeta (futuro) |

## Archivos Relacionados

- **Backend**: [src/routes/analisis.py](src/routes/analisis.py) - Endpoints que usan los thresholds
- **Frontend**: [src/templates/analisis/index.html](src/templates/analisis/index.html) - UI con botones de acción
- **Config**: [src/analisis_thresholds.py](src/analisis_thresholds.py) - **← Edita aquí**

## Notas

- Los umbrales se aplican en **tiempo de ejecución** (sin reiniciar app necesariamente)
- Cambios se reflejan inmediatamente en el próximo request / reload
- Todos los valores en porcentaje se usan como decimales (0.70 = 70%)
