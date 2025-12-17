# 📚 API Reference - App Presupuesto v0.7.1
**Sistema Empresarial de Gestión Financiera**

Documentación completa de la API interna del sistema empresarial de gestión financiera personal. Esta documentación cubre todas las funciones, controladores, servicios y funciones de base de datos disponibles en la arquitectura MVC optimizada.

---

## 📋 Tabla de Contenidos

1. [Visión General](#-visión-general)
2. [Sistema de Autenticación](#-sistema-de-autenticación)
3. [Funciones de Base de Datos Empresariales](#-funciones-de-base-de-datos-empresariales)
4. [Procedimientos Almacenados](#-procedimientos-almacenados)
5. [Controladores Principales](#-controladores-principales)
6. [Modelos de Datos](#-modelos-de-datos)
7. [Sistema de Documentación](#-sistema-de-documentación)
8. [Utilidades y Helpers](#-utilidades-y-helpers)
9. [Códigos de Error](#-códigos-de-error)
10. [Ejemplos de Uso](#-ejemplos-de-uso)
11. [Best Practices](#-best-practices)

---

## 🔍 Visión General

### Arquitectura de la API

La API interna de App Presupuesto sigue el patrón **MVC (Model-View-Controller)** con las siguientes capas:

```
📊 VIEW LAYER (Presentación)
    ↓
🎮 CONTROLLER LAYER (Lógica de Negocio)  
    ↓
🗄️ DATABASE LAYER (Funciones Empresariales)
    ↓
📊 AUTOMATION LAYER (Triggers & Events)
    ↓
🗄️ MODEL LAYER (Datos y Persistencia)
```

### Convenciones Generales

#### Tipos de Retorno Estándar
```python
# Patrón de respuesta para operaciones críticas
Tuple[bool, str, Optional[Dict]] = (success, message, data)

# Patrón de respuesta para consultas
Optional[Dict] = data or None

# Patrón de respuesta para validaciones
Tuple[bool, str] = (is_valid, error_message)
```

#### Manejo de Errores
- **ValidationError**: Errores de validación de entrada
- **AuthenticationError**: Errores de autenticación
- **DatabaseError**: Errores de acceso a datos
- **BusinessLogicError**: Errores de lógica de negocio

---

## 🏢 Funciones de Base de Datos Empresariales

### 📅 Funciones de Días Hábiles

#### `fn_dias_habiles(fecha_inicio, fecha_fin)`
Calcula días hábiles entre dos fechas excluyendo festivos de Colombia.

**Sintaxis:**
```sql
SELECT fn_dias_habiles('2024-01-01', '2024-01-31') as dias_habiles;
```

**Parámetros:**
- `fecha_inicio` (DATE): Fecha inicial del período
- `fecha_fin` (DATE): Fecha final del período

**Retorna:** INT - Número de días hábiles

**Ejemplo:**
```sql
-- Días hábiles en enero 2024
SELECT fn_dias_habiles('2024-01-01', '2024-01-31') as dias_enero;
-- Resultado: 22 días hábiles
```

#### `fn_siguiente_dia_habil(fecha_referencia)`
Obtiene el siguiente día hábil después de una fecha dada.

**Sintaxis:**
```sql
SELECT fn_siguiente_dia_habil(CURDATE()) as proximo_dia_habil;
```

**Parámetros:**
- `fecha_referencia` (DATE): Fecha de referencia

**Retorna:** DATE - Siguiente día hábil

**Ejemplo:**
```sql
-- Si hoy es viernes, devuelve el lunes siguiente
SELECT fn_siguiente_dia_habil('2024-12-20') as siguiente;
-- Resultado: 2024-12-23 (lunes)
```

### 💰 Funciones de Cálculo Financiero

#### `fn_calcular_interes_simple(monto, tasa, dias)`
Calcula interés simple para un período dado.

**Sintaxis:**
```sql
SELECT fn_calcular_interes_simple(1000000, 0.18, 30) as interes;
```

**Parámetros:**
- `monto` (DECIMAL): Capital inicial
- `tasa` (DECIMAL): Tasa de interés anual (0.18 = 18%)
- `dias` (INT): Número de días

**Retorna:** DECIMAL - Valor del interés calculado

---

## 📊 Procedimientos Almacenados

### 📚 Sistema de Documentación

#### `sp_generar_reporte_documentacion()`
Genera reporte completo de documentación del sistema.

**Sintaxis:**
```sql
CALL sp_generar_reporte_documentacion();
```

**Descripción:**
Produce un reporte detallado con:
- Cobertura de documentación por tabla
- Campos sin documentar
- Métricas de calidad de documentación
- Recomendaciones de mejora

#### `sp_generar_reporte_arquitectura()`
Genera análisis de arquitectura y métricas del sistema.

**Sintaxis:**
```sql
CALL sp_generar_reporte_arquitectura();
```

---

## 🔐 Sistema de Autenticación

### PersonaController v1.4.0

Controlador principal para gestión de usuarios y autenticación con optimizaciones de performance y seguridad empresarial.

#### Funciones de Autenticación Core

##### `iniciar_sesion(username: str, password: str) -> Tuple[bool, str, Optional[Dict]]`

Inicia sesión de usuario con validación completa y creación de sesión segura.

**Parámetros:**
- `username` (str): Nombre de usuario o email
- `password` (str): Contraseña en texto plano

**Returns:**
```python
(
    success: bool,           # True si login exitoso
    message: str,           # Mensaje descriptivo del resultado
    session_data: Optional[Dict]  # Datos de sesión si exitoso
)
```

**Validaciones Implementadas:**
- ✅ Usuario existe en base de datos
- ✅ Usuario en estado ACTIVO
- ✅ Contraseña válida con bcrypt
- ✅ Rate limiting para prevenir ataques
- ✅ Logging de eventos de seguridad

**Ejemplo de Uso:**
```python
from controllers.persona_controller import iniciar_sesion

success, message, session = iniciar_sesion("usuario@email.com", "mi_password")
if success:
    print(f"Bienvenido: {session['nombre_completo']}")
    print(f"Rol: {session['rol']}")
else:
    print(f"Error de login: {message}")
```

**Estructura de session_data:**
```python
{
    'usuario_id': int,              # ID único del usuario
    'persona_id': int,              # ID de la persona asociada  
    'username': str,                # Nombre de usuario
    'nombre_completo': str,         # Nombres + Apellidos
    'email': str,                   # Email del usuario
    'rol': str,                     # Rol: admin, user, guest
    'activo': bool,                 # Estado de sesión activa
    'fecha_login': datetime,        # Timestamp del login
    'ultima_actividad': datetime,   # Última interacción
    'permisos': List[str],          # Lista de permisos específicos
    'token_seguridad': str,         # Token único de sesión
    'expira_en': datetime,          # Timestamp de expiración
    'configuracion': Dict,          # Configuraciones personalizadas
    'estadisticas': Dict            # Métricas de uso
}
```

---

##### `cerrar_sesion() -> bool`

Cierra sesión activa de forma segura con limpieza completa de datos.

**Returns:**
- `bool`: True si cierre exitoso, False si no había sesión activa

**Acciones Realizadas:**
- 🧹 Limpieza de variables globales de sesión
- 📝 Logging del evento de logout
- 🗄️ Actualización de última actividad en BD
- 🔒 Invalidación de token de seguridad

**Ejemplo:**
```python
from controllers.persona_controller import cerrar_sesion

if cerrar_sesion():
    print("Sesión cerrada exitosamente")
else:
    print("No había sesión activa")
```

---

##### `verificar_sesion_activa() -> bool`

Verifica si existe una sesión válida y activa con múltiples validaciones de seguridad.

**Returns:**
- `bool`: True si hay sesión válida activa

**Validaciones Realizadas:**
- ✅ Existencia de datos de sesión
- ✅ Validez del token de seguridad  
- ✅ Verificación de expiración
- ✅ Estado activo del usuario en BD
- ✅ Integridad de datos de sesión

**Ejemplo:**
```python
from controllers.persona_controller import verificar_sesion_activa

if verificar_sesion_activa():
    print("Usuario autenticado correctamente")
else:
    # Redirigir a login
    print("Sesión expirada o inválida")
```
