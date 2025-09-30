# Guía de Usuario — App Presupuesto (Aplicación de Escritorio)

Esta guía te ayudará a utilizar la aplicación de escritorio para gestión financiera personal desarrollada con Flet y Python.

---

## 📋 Introducción

**App Presupuesto** es una aplicación de escritorio moderna que te permite gestionar tus finanzas personales de manera intuitiva y segura. Desarrollada con tecnología Python y Flet, ofrece una interfaz gráfica nativa que funciona en Windows, macOS y Linux.

### ✨ Características Principales:
- 🖥️ **Aplicación de Escritorio**: No requiere navegador web
- 🔐 **Seguridad Avanzada**: Datos almacenados localmente con encriptación
- 📊 **Interfaz Moderna**: Diseño limpio y fácil de usar
- 💾 **Base de Datos Local**: MySQL para máximo rendimiento
- 🚀 **Rápida y Eficiente**: Sin dependencia de internet para funcionar

---

## 🛠️ Instalación y Configuración

### Requisitos del Sistema:
- **Sistema Operativo**: Windows 10+, macOS 10.14+, o Linux (Ubuntu 18.04+)
- **Memoria RAM**: 4GB mínimo, 8GB recomendado
- **Espacio en Disco**: 2GB libres para instalación
- **MySQL**: Servidor MySQL 8.0+ instalado y funcionando

### Pasos de Instalación:

#### 1. Preparar el Entorno
```bash
# Clonar el repositorio
git clone https://github.com/usuario/app-presopuesto.git
cd app-presupuesto

# Crear entorno virtual de Python
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

#### 2. Instalar Dependencias
```bash
# Instalar paquetes de Python
pip install -r requirements.txt

# Verificar instalación de Flet
python -c "import flet as ft; print('✅ Flet instalado correctamente')"
```

#### 3. Configurar Base de Datos
```bash
# Crear archivo de configuración
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS

# Editar .env con tus credenciales de MySQL:
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=presupuesto_db
# DB_USER=tu_usuario_mysql
# DB_PASSWORD=tu_password_mysql
```

#### 4. Inicializar Base de Datos
```bash
# Ejecutar scripts de inicialización
# En Windows:
database\scripts\init_db.bat

# En Linux/macOS:
bash database/scripts/init_db.sh
```

#### 5. Ejecutar la Aplicación
```bash
# Iniciar la aplicación
python src/views/user_view.py
```

---

## 🚀 Primer Uso

### Pantalla de Inicio de Sesión

Al abrir la aplicación por primera vez, verás la pantalla de login:

```
┌─────────────────────────────────────┐
│           🔑 LOGIN ICON             │
│        Inicio de Sesión             │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 👤 Nombre de Usuario            │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🔒 Contraseña          👁       │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Iniciar Sesión           │ │
│  └─────────────────────────────────┘ │
│                                     │
│        ✅ ¡Bienvenido Juan!         │
└─────────────────────────────────────┘
```

### Credenciales de Prueba

Para probar la aplicación, puedes usar estas credenciales de ejemplo:
- **Usuario**: `admin` o `test@test.com`
- **Contraseña**: `admin123` o `test123`

### Validaciones en Tiempo Real

La aplicación incluye validaciones automáticas:

✅ **Campo Usuario:**
- Mínimo 3 caracteres
- Eliminación automática de espacios
- Validación de caracteres especiales

✅ **Campo Contraseña:**
- Mínimo 6 caracteres
- Opción de mostrar/ocultar contraseña
- Validación de seguridad

✅ **Retroalimentación Visual:**
- ✅ Verde para operaciones exitosas
- ❌ Rojo para errores
- ⚠️ Amarillo para advertencias

---

## 🎮 Usando la Aplicación

### Navegación Básica

#### Ventana Principal
- **Tamaño**: 400x500 píxeles (optimizado para uso eficiente)
- **Redimensionable**: No (diseño fijo para mejor UX)
- **Tema**: Claro por defecto, con opción a tema oscuro

#### Elementos de la Interfaz

1. **Campos de Entrada:**
   - Iconos descriptivos para mejor comprensión
   - Validación en tiempo real
   - Mensajes de error contextuales

2. **Botones:**
   - Diseño moderno con colores corporativos
   - Estados visuales (normal, hover, presionado)
   - Feedback inmediato al hacer clic

3. **Mensajes de Estado:**
   - Posicionados estratégicamente
   - Colores semánticos (verde/rojo/amarillo)
   - Texto claro y descriptivo

### Funcionalidades Actuales (v0.5.0)

#### 🔐 Sistema de Autenticación
- **Login Seguro**: Validación robusta con hash bcrypt
- **Gestión de Sesiones**: Control automático de tiempo de sesión
- **Seguridad**: Protección contra ataques de fuerza bruta
- **Logging**: Registro de intentos de acceso para auditoría

#### 🛡️ Validación y Seguridad
- **Sanitización**: Limpieza automática de entrada maliciosa
- **Prevención SQL Injection**: Queries preparadas únicamente
- **Encriptación**: Contraseñas hasheadas con bcrypt
- **Auditoría**: Logs detallados de eventos de seguridad

#### 🗄️ Base de Datos
- **Conexión Optimizada**: Pool de conexiones para mejor rendimiento
- **Backup Automático**: Respaldos programados de datos
- **Integridad**: Verificación automática de datos
- **Recuperación**: Sistema de recuperación ante fallos

---

## 📊 Próximas Funcionalidades

### Versión 0.6.0 - Dashboard Principal (Febrero 2025)
- 📈 **Dashboard Interactivo**: Resumen financiero en tiempo real
- 💳 **Gestión de Cuentas**: CRUD completo de cuentas bancarias
- 💰 **Registro de Transacciones**: Ingresos, gastos y transferencias
- 📂 **Categorización**: Sistema de categorías personalizables

### Versión 0.7.0 - Inteligencia Artificial (Mayo 2025)
- 🤖 **Categorización Automática**: IA para clasificar transacciones
- 📊 **Análisis Predictivo**: Proyecciones de gastos futuros
- 💡 **Recomendaciones**: Sugerencias para optimizar finanzas
- 📥 **Importación Inteligente**: Carga automática de extractos bancarios

### Versión 0.8.0 - Reportes Avanzados (Agosto 2025)
- 📈 **Gráficos Interactivos**: Visualización avanzada de datos
- 📄 **Exportación PDF/Excel**: Reportes profesionales
- 📊 **Dashboard Personalizable**: Widgets configurables
- 🔍 **Análisis Profundo**: Métricas financieras avanzadas

---

## 🛠️ Solución de Problemas

### Problemas Comunes y Soluciones

#### ❌ Error: "No se puede conectar a la base de datos"

**Soluciones:**
1. **Verificar MySQL**:
   ```bash
   # Comprobar si MySQL está ejecutándose
   mysql -u root -p -e "SHOW DATABASES;"
   ```

2. **Verificar Configuración**:
   ```bash
   # Revisar archivo .env
   cat .env  # Linux/macOS
   type .env  # Windows
   ```

3. **Probar Conexión**:
   ```bash
   python -c "
   from src.database.connection import get_db_connection
   try:
       conn = get_db_connection()
       print('✅ Conexión exitosa')
   except Exception as e:
       print(f'❌ Error: {e}')
   "
   ```

#### ❌ Error: "Módulo flet no encontrado"

**Soluciones:**
1. **Verificar Entorno Virtual**:
   ```bash
   # Activar entorno virtual
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

2. **Reinstalar Flet**:
   ```bash
   pip uninstall flet
   pip install flet
   ```

#### ❌ Error: "Ventana no se abre"

**Soluciones:**
1. **Verificar Resolución de Pantalla**: Mínimo 800x600
2. **Cerrar Otras Instancias**: Solo una instancia por vez
3. **Verificar Python**: Debe ser 3.8 o superior

#### ❌ Error: "Credenciales inválidas"

**Soluciones:**
1. **Verificar Datos de Prueba**:
   ```bash
   # Verificar si existen usuarios de prueba
   mysql -u tu_usuario -p presupuesto_db -e "SELECT username FROM usuarios LIMIT 5;"
   ```

2. **Crear Usuario de Prueba**:
   ```bash
   # Ejecutar script de datos de prueba
   mysql -u tu_usuario -p presupuesto_db < database/scripts/create/create_data.sql
   ```

### Logs y Debugging

#### Archivos de Log
```
logs/
├── app.log              # Log general de la aplicación
├── security.log         # Eventos de seguridad
├── database.log         # Operaciones de base de datos
└── error.log           # Errores críticos
```

#### Habilitar Debug Mode
```bash
# Ejecutar en modo debug
python src/views/user_view.py --debug

# O configurar variable de entorno
export DEBUG=True  # Linux/macOS
set DEBUG=True     # Windows
```

---

## 🔒 Seguridad y Privacidad

### Datos Locales
- ✅ **Almacenamiento Local**: Todos los datos se guardan en tu computadora
- ✅ **Sin Conexión a Internet**: Funciona completamente offline
- ✅ **Encriptación**: Contraseñas y datos sensibles encriptados
- ✅ **Backup Personal**: Tú controlas tus respaldos

### Mejores Prácticas de Seguridad

1. **Contraseñas Seguras**:
   - Mínimo 8 caracteres
   - Combinación de letras, números y símbolos
   - No reutilizar contraseñas de otros sistemas

2. **Respaldos Regulares**:
   ```bash
   # Crear backup manual
   database\scripts\backup_db.bat  # Windows
   bash database/scripts/backup_db.sh  # Linux/macOS
   ```

3. **Actualizaciones**:
   - Mantener la aplicación actualizada
   - Seguir el changelog para mejoras de seguridad
   - Actualizar MySQL regularmente

4. **Acceso Físico**:
   - Usar contraseña de sistema operativo
   - Cerrar aplicación al ausentarse
   - No dejar credenciales anotadas cerca del equipo

---

## 📚 Recursos Adicionales

### Documentación Técnica
- 📖 [README Principal](../README.md)
- 🏗️ [Arquitectura del Sistema](../documentacion/ARCHITECTURE.md)
- 🗄️ [Documentación de Base de Datos](BASE_DATOS.md)
- 🔒 [Política de Seguridad](../documentacion/SECURITY.md)

### Soporte y Comunidad
- 🐛 **Reportar Bugs**: [GitHub Issues](https://github.com/tu-usuario/app-presopuesto/issues)
- 💡 **Sugerir Funcionalidades**: [GitHub Discussions](https://github.com/tu-usuario/app-presopuesto/discussions)
- 📧 **Contacto Directo**: estebanfabianp@gmail.com

### Tutoriales y Videos
- 🎥 **Video Tutorial**: Instalación paso a paso (próximamente)
- 📝 **Blog**: Casos de uso y tips financieros (próximamente)
- 🎓 **Curso Online**: Gestión financiera personal (planificado)

---

## 🎯 Consejos para Maximizar el Uso

### Organización de Datos

1. **Nomenclatura Consistente**:
   - Usar nombres descriptivos para cuentas
   - Mantener categorías organizadas
   - Incluir fechas en descripciones importantes

2. **Entrada Regular de Datos**:
   - Registrar transacciones diariamente
   - Revisar saldos semanalmente
   - Actualizar presupuestos mensualmente

3. **Aprovecha las Funcionalidades**:
   - Usar la validación automática para evitar errores
   - Aprovechar el feedback visual para confirmar acciones
   - Revisar logs de seguridad periódicamente

### Preparándose para Nuevas Versiones

1. **Mantente Informado**:
   - Suscríbete a notificaciones del repositorio
   - Lee el changelog antes de actualizar
   - Prueba nuevas funcionalidades en datos de prueba

2. **Preparación de Datos**:
   - Mantén respaldos actualizados
   - Organiza tus categorías desde ahora
   - Recopila extractos bancarios para importación futura

---

**🌟 ¡Disfruta gestionando tus finanzas de manera inteligente y segura!**

**Versión de la Guía**: 1.2 | **Aplicación**: v0.5.0 | **Última Actualización**: Enero 2025

---

<div align="center">
  <p>📱 Aplicación desarrollada con ❤️ por Esteban Fabián Patiño Montealegre</p>
  <p>🔐 Tus datos están seguros y bajo tu control</p>
</div>
