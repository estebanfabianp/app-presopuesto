# Política de Umbrales - Análisis de Consumo

## Resumen Rápido

Algunos umbrales de endpoints están definidos en [analisis_thresholds.py](../src/analisis_thresholds.py). La vista principal también contiene valores propios en el backend y en JavaScript; no todos se actualizan automáticamente al modificar ese archivo.

## Umbrales Actuales (Por Defecto)

### 📊 Score de Salud (0-100)
| Nivel | Rango | Significado |
|-------|-------|-------------|
| ✅ Excelente | ≥ 80 | Excelente control financiero |
| 🟡 Estable | 60-79 | Situación equilibrada |
| ⚠️ En riesgo | 40-59 | Requiere atención |
| ❌ Crítico | < 40 | Necesita intervención urgente |

El score orientativo es del mes hasta hoy, parte de 100 y resta puntos por ahorro inferior al 20%, gasto fijo superior al 50% y uso promedio de tarjetas activas superior al 50%. Clasifica gastos reales según la hoja mensual y no aplica variación mes a mes. Sin ingresos, gastos o clasificación suficiente devuelve «Sin datos suficientes». La fórmula y las limitaciones están en [la referencia API](API_REFERENCE.md#análisis-de-consumo-apianalisis).

### 💳 Alertas (Tarjetas de Crédito)
Estos umbrales corresponden al endpoint heredado de alertas, no al indicador principal actual.
- **🟡 Aviso**: Uso ≥ **70%** del cupo
- **❌ Crítica**: Uso ≥ **90%** del cupo

### 🎯 Alertas (Presupuesto Mensual)
La pantalla principal muestra atención desde el **85%** del presupuesto mensual, siempre que haya movimientos. El endpoint heredado distingue aviso desde 85% y nivel crítico desde 100%.

### 📈 Presupuesto por Categoría (Semáforo)
- **🟢 Verde**: < 80% ejecutado
- **🟡 Amarillo**: 80-100% ejecutado
- **🔴 Rojo**: > 100% ejecutado
- **Sin datos**: no hay movimientos de ingreso o gasto en el mes.

## Cómo Personalizar

### Ejemplo: Bajar tarjetas a 60%
[analisis_thresholds.py](../src/analisis_thresholds.py):
```python
ALERT_THRESHOLDS = {
    'tarjeta_warning': 0.60,  # Cambiar de 0.70 a 0.60
    ...
}
```

### Ejemplo: Ajustar meta de ahorro a 25%
[analisis_thresholds.py](../src/analisis_thresholds.py):
```python
SCORE_TARGETS = {
    'tasa_ahorro_min': 25.0,  # Cambiar de 20.0 a 25.0
    ...
}
```

## Acciones rápidas

La configuración define las siguientes rutas de acciones. Su disponibilidad y destino deben comprobarse en cada instalación: algunas acciones de la pantalla heredada conservan rutas antiguas.

| Acción | Ruta | Caso de uso |
|--------|------|------------|
| Ajustar Presupuesto | `/presupuesto` | Categoría con gasto alto |
| Revisar Suscripciones | `/nueva-transaccion` | Suscripciones detectadas |
| Crear Meta | `/metas` | Objetivo de ahorro |
| Ver Tarjetas | `/tarjeta` | Alerta de tarjeta (futuro) |

## Archivos Relacionados

- **Backend**: [analisis.py](../src/routes/analisis.py) - endpoints y vista de consumo
- **Frontend**: [index.html](../src/templates/analisis/index.html) - pantalla de análisis
- **Config**: [analisis_thresholds.py](../src/analisis_thresholds.py)

## Notas

- Reinicia el servidor tras modificar configuración Python y recarga el navegador. Revisa también textos y valores independientes de la interfaz para mantenerlos coherentes.
- Algunos umbrales son porcentajes (`20.0` = 20%) y otros son proporciones (`0.70` = 70%); consulta cada campo antes de cambiarlo.
