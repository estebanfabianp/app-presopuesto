# 🎯 SystemConstantsView - Guía Rápida

## ✅ Status Actual

- **Tabla constantes**: ✅ Creada con 17 datos de prueba
- **Interfaz**: ✅ Mejorada y corregida
- **Carga de datos**: ✅ Funcionando correctamente

## 📊 Datos de Prueba Cargados

Se han insertado **17 constantes** organizadas en 5 categorías:

### FINANCIERO (4 constantes)
- `IVA` = 0.19 (DECIMAL) - No editable
- `TASA_INTERES_AHORRO` = 0.04 (DECIMAL)
- `TASA_INTERES_PLAZO` = 0.05 (DECIMAL)
- `TASA_COMISION_TRANSFERENCIA` = 0.001 (DECIMAL)

### GENERAL (4 constantes)
- `MONEDA_PRINCIPAL` = COP (STRING) - No editable
- `PAIS` = Colombia (STRING) - No editable
- `IDIOMA_DEFECTO` = es (STRING)
- `TEMA_MODO_OSCURO` = false (BOOLEAN)

### LIMITES (3 constantes)
- `MAX_TARJETA_CREDITO` = 10000000 (INTEGER)
- `MIN_DEPOSITO` = 50000 (INTEGER)
- `MAX_TRANSFERENCIA_DIARIA` = 50000000 (INTEGER)

### NOTIFICACIONES (2 constantes)
- `NOTIFICACIONES_HABILITADAS` = true (BOOLEAN)
- `EMAIL_NOTIFICACIONES` = app@empresa.com (STRING)

### SISTEMA (3 constantes)
- `VERSION_APP` = 1.0.0 (STRING) - No editable
- `MODO_MANTENIMIENTO` = false (BOOLEAN)
- `CONFIG_BACKUP` = {...} (JSON)
- `FECHA_ULTIMO_BACKUP` = 2026-04-07 (DATE)

---

## 🚀 Cómo Usar

### **1. Acceder a la vista**
1. Abre la app
2. Ve al sidebar izquierdo
3. Sección **CONFIGURACIÓN**
4. Haz clic en **"Constantes"**

### **2. Ver todas las constantes**
- La tabla mostrará automáticamente todas las 17 constantes
- Organizadas por categoría y nombre

### **3. Buscar**
- Campo "Buscar constante..." en la parte superior
- Busca por nombre o descripción (búsqueda completa)

### **4. Filtrar por categoría**
- Dropdown "Filtrar por categoría"
- Selecciona una categoría para ver solo esas constantes

### **5. Editar una constante**
- Haz clic en el ✏️ (lápiz) al lado de la constante
- Se abre un formulario en BottomSheet
- Edita el **Valor** y/o **Descripción**
- Validación en tiempo real muestra ✓ o ✗
- Haz clic en **Guardar**

**Nota**: Algunas constantes tienen `es_editable=false`, en esas el botón edit mostrará una validación.

### **6. Crear nueva constante**
- Haz clic en el botón **+** (FAB) en la esquina inferior derecha
- Completa el formulario:
  - **Nombre**: Identificador único (requerido)
  - **Categoría**: Selecciona o crea nueva
  - **Tipo de dato**: STRING, INTEGER, DECIMAL, BOOLEAN, JSON, DATE
  - **Valor**: Debe cumplir el formato del tipo
  - **Descripción**: Opcional
- La validación muestra si el valor es válido para el tipo seleccionado
- Haz clic en **Crear**

### **7. Eliminar una constante**
- Haz clic en el 🗑️ (basura) al lado de la constante
- Se muestra confirmación
- Confirma para eliminar (soft delete - no se borra de verdad)

### **8. Refrescar datos**
- Icono 🔄 en la barra de herramientas
- Recarga los datos desde BD

---

## 🎨 Interface Mejorada

### **Estructura**
```
┌─ Header ─────────────────────────────────────────┐
│ Constantes del Sistema                            │
│ Gestión de variables globales...                 │
└─────────────────────────────────────────────────┘
┌─ Toolbar ────────────────────────────────────────┐
│ [🔍 Buscar...] [📁 Categoría ▼] [🔄]            │
└─────────────────────────────────────────────────┘
┌─ Tabla ──────────────────────────────────────────┐
│ Nombre      │ Valor      │ Tipo    │ Desc │ Act  │
├─────────────┼────────────┼─────────┼──────┼──────┤
│ IVA         │ 0.19       │ DECIMAL │ ...  │ ✏️🗑️ │
│ MONEDA_... │ COP        │ STRING  │ ...  │ ✏️🗑️ │
│ ...         │ ...        │ ...     │ ...  │ ... │
└─────────────────────────────────────────────────┘
                    [+] (crear nueva)
```

### **Colores por Tipo**
- 🔵 **STRING**: Azul (#2196F3)
- 🟢 **INTEGER**: Verde (#4CAF50)
- 🟠 **DECIMAL**: Naranja (#FF9800)
- 🟣 **BOOLEAN**: Púrpura (#9C27B0)
- 🔴 **JSON**: Rojo (#F44336)
- 🔵 **DATE**: Cian (#00BCD4)

---

## 📝 Ejemplos de Uso

### **Crear constante de tipo DECIMAL**
```
Nombre: TAX_RATE
Categoría: FINANCIERO
Tipo: DECIMAL
Valor: 0.25  ✓ Válido
Descripción: Tasa impositiva general
```

### **Crear constante de tipo BOOLEAN**
```
Nombre: FEATURE_BETA
Categoría: SISTEMA
Tipo: BOOLEAN
Valor: true  ✓ Válido (también acepta: false, yes, no, 1, 0, si)
Descripción: Habilitar características beta
```

### **Crear constante de tipo JSON**
```
Nombre: API_CONFIG
Categoría: SISTEMA
Tipo: JSON
Valor: {"host":"api.example.com","port":8080}  ✓ Válido
Descripción: Configuración de conexión API
```

### **Crear constante de tipo DATE**
```
Nombre: LAUNCH_DATE
Categoría: GENERAL
Tipo: DATE
Valor: 2026-04-07  ✓ Válido (formato: YYYY-MM-DD)
Descripción: Fecha de lanzamiento del producto
```

---

## ⚙️ Validaciones por Tipo

| Tipo | Acepta | Ejemplo | Rechaza |
|------|--------|---------|---------|
| **STRING** | Cualquier texto | "Hello" | (siempre válido) |
| **INTEGER** | Números enteros | 123, -50 | 12.34, "abc" |
| **DECIMAL** | Números con decimales | 0.19, -100.5, 1,000.50 | "abc", "12.34.56" |
| **BOOLEAN** | true/false, si/no, 1/0, yes/no | true, false, 1, si, yes | "maybe", 2 |
| **JSON** | JSON válido | {"key":"value"} | {invalid json} |
| **DATE** | Formato YYYY-MM-DD | 2026-04-07 | 07/04/2026, 2026-4-7 |

---

## 🔧 Troubleshooting

### **❌ La tabla está vacía**
1. Abre DevTools (F12)
2. Ve a la consola
3. Busca mensajes de error
4. Ejecuta: `python verify_data.py` para verificar BD
5. Si dice "0 constantes", ejecuta: `python insert_test_data.py`

### **❌ Cambios no se guardan**
1. Verifica que la constante tiene `es_editable=true`
2. Revisa que la validación muestra ✓ (no ✗)
3. Mira los logs: `logging.debug("...")`

### **❌ Icono de creación no funciona**
1. Verifica que el FAB (+) es visible en la esquina inferior derecha
2. Intenta hacer scroll si está cubierto
3. Si no aparece, verifica que el `build()` tiene el Stack con Column

### **❌ Búsqueda no funciona**
1. Escribe algo en el campo "Buscar constante..."
2. Presiona Enter o espera ~500ms
3. Debería filtrar por nombre o descripción

---

## 📚 Archivos Relacionados

```
📁 Proyecto
├── src/views/constante.py ...................... Vista principal (700+ líneas)
├── insert_test_data.py ......................... Script para cargar datos
├── verify_data.py ............................. Script para verificar BD
├── db/01_core/create/constantes_init.sql ...... SQL para crear tabla
├── CONSTANTS_VIEW_GUIDE.md ..................... Guía detallada (500+ líneas)
└── CONSTANTS_INTEGRATION_GUIDE.py ............. Guía de integración
```

---

## 🎓 Tips Pro

1. **Búsqueda global**: Busca en nombre Y descripción
2. **Filtros combinados**: Puedes buscar Y filtrar por categoría
3. **Edición rápida**: Haz clic edit, cambia valor, haz clic guardar (2 clics)
4. **Soft delete**: Las constantes eliminadas pueden "recuperarse" directamente en BD
5. **Valores formateados**: Los decimales se muestran con separador de miles (1,000.50)
6. **Tipos seguros**: No puedes guardar un valor que no cumpla el tipo

---

## 🚀 Status de Implementación

| Feature | Status | Notas |
|---------|--------|-------|
| Leer constantes | ✅ Completo | Carga desde BD automáticamente |
| Crear constantes | ✅ Completo | Con validación de tipo |
| Editar constantes | ✅ Completo | Respeta flag es_editable |
| Eliminar constantes | ✅ Completo | Soft delete (estado=0) |
| Búsqueda | ✅ Completo | Full-text en nombre+descripción |
| Filtrado | ✅ Completo | Por categoría dinámica |
| Validación tipos | ✅ Completo | 6 tipos soportados |
| Formateo valores | ✅ Completo | Decimales e integers con separadores |
| Colores por tipo | ✅ Completo | 6 colores diferentes |
| Datos de prueba | ✅ Completo | 17 constantes listas |

---

**¡Listo para usar en producción! 🎉**
