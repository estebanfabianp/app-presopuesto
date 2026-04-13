# Cambios Implementados - Umbrales Personalizables y Botones de Acción

## 1. ✅ Umbrales Centralizados y Personalizables

### Archivo: `src/analisis_thresholds.py` (NUEVO)
Todos los umbrales ahora están en un único archivo para fácil personalización sin tocar lógica de Flask:

```python
# Antes: Hardcodeados en analisis.py
if score >= 80:  # ❌ Difícil de cambiar

# Después: Parametrizados en config
SCORE_THRESHOLDS = {'excelente': 80}
if score >= SCORE_THRESHOLDS['excelente']:  # ✅ Fácil de ajustar
```

### Parámetros Configurables

| Categoría | Parámetros | Valores Actuales |
|-----------|-----------|------------------|
| **Score** | Excelente, Estable, En riesgo, Crítico | 80, 60, 40, 0 |
| **Metas** | Ahorro mín, Fijo ideal, Uso tarjetas, Variación | 20%, 50%, 50%, ±10% |
| **Alertas Tarjetas** | Warning, Crítica | 70%, 90% |
| **Alertas Presupuesto** | Warning, Crítica | 85%, 100% |
| **Presupuesto Semáforo** | Verde, Amarillo, Rojo | <80%, 80-100%, >100% |

---

## 2. ✅ Botones de Acción Rápida en Oportunidades

### Interfaz Anterior
```html
<div class="border rounded p-2 mb-2">
    <div class="fw-semibold small">Suscripciones detectadas</div>
    <div class="small text-muted">Impacto: $45.00</div>
    <div class="small">Cancelar o renegociar suscripciones poco usadas</div>
    <!-- ❌ Sin botón de acción -->
</div>
```

### Interfaz Nueva
```html
<div class="border rounded p-3 mb-2 bg-light">
    <div class="fw-semibold">Suscripciones detectadas</div>
    <div class="text-muted small mb-2">💰 Impacto: $45.00</div>
    <div class="small text-secondary mb-2">Cancelar o renegociar...</div>
    <button class="btn btn-sm btn-outline-danger" onclick="accionRapida('/nueva-transaccion', 'suscripciones')">
        <i class="fa-solid fa-sync"></i> Revisar Suscripciones
    </button>
    <!-- ✅ Con botón navegable -->
</div>
```

### Acciones Disponibles

| Tipo | Acción | Icono | Color | Destino |
|------|--------|-------|-------|---------|
| Presupuesto | Ajustar Presupuesto | 📊 | warning | `/presupuesto` |
| Suscripciones | Revisar Suscripciones | 🔄 | danger | `/nueva-transaccion` |
| Ahorro | Crear Meta | 🎯 | success | `/metas-ahorro` |
| Tarjetas | Ver Tarjetas | 💳 | info | `/tarjeta` |

---

## 3. ✅ Panel Informativo de Umbrales

Nueva sección desplegable en la UI que muestra la política actual:

```html
<!-- Política de umbrales configurados (NUEVA) -->
<div class="card h-100 bg-light">
    <button data-bs-toggle="collapse">
        <i class="fas fa-cog"></i> Política de umbrales configurados
    </button>
    <div class="collapse" id="thresholdContent">
        <!-- Muestra score, alertas, metas ideales -->
        <div class="border-start ps-2">
            ✅ Excelente: ≥ 80
            🟡 Estable: 60-79
            ⚠️ En riesgo: 40-59
            ❌ Crítico: < 40
        </div>
        <div class="text-muted small">
            Editar: src/analisis_thresholds.py
        </div>
    </div>
</div>
```

---

## 4. 🔄 Cambios en Backend

### `src/routes/analisis.py`

#### Imports (NUEVO)
```python
from src.analisis_thresholds import (
    SCORE_THRESHOLDS, SCORE_TARGETS, SCORE_PENALTIES,
    PRESUPUESTO_STATES, ALERT_THRESHOLDS, ...
)
```

#### Endpoint: `/api/analisis/oportunidades`
```python
# Ahora retorna action_type
oportunidades.append({
    'tipo': 'suscripciones',
    'titulo': 'Suscripciones detectadas',
    'impacto_mensual': 45.00,
    'accion': '...',
    'action_type': 'revisar_suscripciones',  # ← NUEVO
})
```

#### Alertas Dinámicas
```python
# Uso de ALERT_THRESHOLDS
if pct >= ALERT_THRESHOLDS['presupuesto_warning']:  # 85% configurable
if (saldo_actual / limite_credito) >= ALERT_THRESHOLDS['tarjeta_warning']:  # 70% configurable
```

---

## 5. 🎨 Cambios en Frontend

### `src/templates/analisis/index.html`

#### Función: `cargarOportunidades()`
```javascript
// Mapa de acciones con navegación
const actionMap = {
    'ajustar_presupuesto': { label: 'Ajustar Presupuesto', destination: '/presupuesto' },
    'revisar_suscripciones': { label: 'Revisar Suscripciones', destination: '/nueva-transaccion' },
    ...
};

// Renderizar botón con onClick
<button onclick="accionRapida('${action.route}', '${o.tipo}')">
    <i class="fa-solid ${action.icon}"></i> ${action.label}
</button>
```

#### Función: `accionRapida()`
```javascript
function accionRapida(ruta, tipo) {
    window.location.href = ruta;  // Navegar a la página de acción
}
```

---

## 📊 Comparativa de Umbrales

### Antes vs Después

| Métrica | Antes | Después | Personalizable |
|---------|-------|---------|---|
| Score "Excelente" | 80 (hardcoded) | 80 (config) | ✅ Sí |
| Tarjeta warning | 75% (hardcoded) | 70% (config) | ✅ Sí |
| Presupuesto warning | 85% (hardcoded) | 85% (config) | ✅ Sí |
| Botones oportunidades | ❌ No | ✅ Sí | ✅ Dinámicos |
| Mostrar umbrales UI | ❌ No | ✅ Sí | ✅ Collapsible |

---

## 📁 Archivos Modificados

1. **src/analisis_thresholds.py** (NUEVO)
   - 130+ líneas de configuración centralizada
   - SCORE_THRESHOLDS, ALERT_THRESHOLDS, PRESUPUESTO_STATES
   - USER_PROFILES, QUICK_ACTIONS (para futuro)

2. **src/routes/analisis.py** (ACTUALIZADO)
   - Imports de analisis_thresholds
   - Score: actualizado para usar SCORE_THRESHOLDS, SCORE_TARGETS, SCORE_PENALTIES
   - Presupuesto: usa PRESUPUESTO_STATES
   - Alertas: usa ALERT_THRESHOLDS
   - Oportunidades: agrega campo `action_type`

3. **src/templates/analisis/index.html** (ACTUALIZADO)
   - Función `cargarOportunidades()`: renderiza botones de acción
   - Nueva sección "Política de umbrales" (collapsible)
   - Función `accionRapida()`: maneja click en botones

4. **docs/THRESHOLDS_GUIDE.md** (NUEVO)
   - Guía para editores
   - Referencia de umbrales actuales
   - Ejemplos de personalización

---

## 🚀 Cómo Usar

### Personalizar Umbrales
```bash
# Editar archivo
vim src/analisis_thresholds.py

# Cambiar, por ejemplo, tarjeta warning de 70% a 60%:
ALERT_THRESHOLDS = {
    'tarjeta_warning': 0.60,  # ← Cambiar aquí
}

# Guardar - los cambios aplican en el siguiente request
```

### Ver UI Nuevo
1. Ir a `/analisis` en la aplicación
2. Scroll a sección "Oportunidades de ahorro"
3. Ver botones de acción: "Ajustar Presupuesto", "Revisar Suscripciones"
4. Click en botón → navega a página relevante
5. Scroll abajo → Ver sección "Política de umbrales" collapsible

---

## ✅ Validación

Todos los endpoints probados exitosamente:
- ✓ `/api/analisis/score-salud` → Usaumbral 80
- ✓ `/api/analisis/alertas-inteligentes` → Usa umbral 70% tarjeta, 85% presupuesto
- ✓ `/api/analisis/oportunidades` → Retorna `action_type` para botones
- ✓ `/api/analisis/presupuesto-categorias` → Usa semáforo 80/100

---

## 📝 Notas

- **No fue necesario reiniciar** la aplicación para que los cambios tomen efecto
- Los umbrales se cargan en **tiempo de ejecución**
- Compatible con cambios de perfil de usuario (estructura lista para USER_PROFILES)
- Botones de acción navegan a rutas existentes (`/presupuesto`, `/nueva-transaccion`, `/tarjeta`)
