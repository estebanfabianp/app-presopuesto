# Guía de Usuario — Sistema de Gestión de Presupuestos

Esta guía te ayudará a comenzar a utilizar la aplicación de gestión financiera personal desarrollada con Flet y arquitectura MVC.

## 📋 Instalación y Primeros Pasos

Sigue los pasos de instalación descritos detalladamente en el [README.md](../README.md):

1. **Requisitos del Sistema:**
   - Python 3.8+ (Recomendado: 3.11+)
   - MySQL 8.0+ o MariaDB 10.6+
   - 4GB RAM mínimo, 8GB recomendado
   - 2GB espacio libre en disco

2. **Instalación:**
   ```bash
   git clone https://github.com/usuario/app-presopuesto.git
   cd app-presopuesto
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

3. **Configuración:**
   ```bash
   copy .env.example .env
   # Editar variables de entorno en .env
   database\scripts\init_db.bat
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python src/views/user_view.py
   ```

## 🔐 Acceso y Autenticación

### Sistema de Login con Flet
La aplicación cuenta con una interfaz gráfica moderna desarrollada con Flet que incluye:

- **Ventana de Login**: Interfaz centrada de 400x500px
- **Validación en Tiempo Real**: Campos obligatorios con feedback inmediato
- **Seguridad Robusta**: Hash de contraseñas con bcrypt y validación de sesión
- **Manejo de Errores**: Try-catch comprehensivo con mensajes descriptivos

### Credenciales de Prueba

Para probar la aplicación, puedes usar estas credenciales predeterminadas:
- **Usuario**: `admin` o `test@test.com`
- **Contraseña**: `admin123` o `test123`

### Características del Login:

- **Campo Usuario**: Mínimo 3 caracteres, validación automática
- **Campo Contraseña**: Campo oculto con opción de mostrar, mínimo 6 caracteres
- **Validaciones**:
  - ✅ Campos no pueden estar vacíos
  - ✅ Sanitización automática (trim de espacios)
  - ✅ Prevención de inyección SQL
  - ✅ Límite de intentos fallidos
  - ✅ Timeout de sesión por inactividad

## 🚀 Funcionalidades Principales

### a) Interfaz Gráfica con Flet

**Vista Principal de Login:**
- Diseño moderno y responsive
- Iconos descriptivos para mejor UX
- Retroalimentación visual inmediata (verde para éxito, rojo para errores)
- Sistema de fallback para importaciones

**Características Técnicas:**
- Arquitectura MVC implementada
- Sistema de importación robusto con múltiples fallbacks
- Manejo de errores granular por tipo de excepción
- Logging detallado para debugging

### b) Gestión de Datos

**Funcionalidades Actuales (v0.5.0):**
- ✅ Sistema de autenticación completo
- ✅ Gestión segura de sesiones
- ✅ Logging y auditoría de seguridad
- ✅ Base de datos optimizada con pool de conexiones

**Próximas Funcionalidades (v0.6.0 - Q1 2025):**
- 📈 Dashboard interactivo con métricas financieras
- 💳 CRUD completo de cuentas bancarias
- 💰 Registro de transacciones (ingresos/gastos/transferencias)
- 📂 Sistema de categorización personalizable
- 📊 Gráficos básicos de distribución de gastos

### c) Base de Datos Integrada

**Sistema de Base de Datos:**
- Conexión MySQL/MariaDB optimizada
- Pool de conexiones para mejor rendimiento
- Scripts automatizados de inicialización
- Migraciones y respaldos automatizados

## 🛠️ Uso Avanzado

### Desarrollo y Testing
```bash
# Ejecutar pruebas
python -m pytest tests/ -v

# Verificar cobertura
python -m pytest tests/ --cov=src/ --cov-report=html

# Linting del código
flake8 src/
black src/
```

### Configuración Avanzada
```bash
# Variables de entorno importantes
DB_HOST=localhost
DB_PORT=3306
DB_NAME=presupuesto_db
DB_USER=app_user
DB_PASSWORD=secure_password
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## 🔒 Seguridad y Mejores Prácticas

### Medidas de Seguridad Implementadas:
- **Hash de Contraseñas**: bcrypt con salt automático
- **Validación de Entrada**: Sanitización completa contra inyección SQL
- **Variables de Entorno**: Credenciales sensibles fuera del código
- **Logs de Seguridad**: Registro completo de intentos de acceso
- **Manejo de Errores**: Sin exposición de información sensible

### Recomendaciones de Uso:
- Utiliza contraseñas seguras (mínimo 8 caracteres, combinación de letras, números y símbolos)
- No compartas credenciales de acceso
- Cierra sesión en dispositivos compartidos
- Mantén actualizada la aplicación y sus dependencias
- Realiza respaldos regulares de tus datos

## 🐛 Solución de Problemas

### Problemas Comunes y Soluciones:

**Error de Importación:**
```bash
# Verificar estructura del proyecto
python -c "import sys; print('\n'.join(sys.path))"

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

**Error de Conexión a BD:**
```bash
# Verificar MySQL
mysql -u root -p -e "SHOW DATABASES;"

# Probar conexión
python -c "
from src.database.connection import get_connection
try:
    conn = get_connection()
    print('✅ Conexión exitosa')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Problemas de Interfaz:**
- Verificar que Flet esté correctamente instalado: `pip install flet`
- Comprobar resolución de pantalla (mínimo 800x600)
- Asegurar que Python 3.8+ esté siendo utilizado

## 📚 Próximas Funcionalidades

### Versión 0.6.0 - Dashboard Principal (Q1 2025):
- [ ] Dashboard interactivo con métricas financieras
- [ ] CRUD completo de presupuestos
- [ ] Gestión avanzada de categorías
- [ ] Gráficos y reportes básicos

### Versión 0.7.0 - Análisis Avanzado (Q2 2025):
- [ ] Reportes con exportación PDF/Excel
- [ ] Análisis predictivo básico con IA
- [ ] Sistema de notificaciones
- [ ] Importación automática de extractos bancarios

### Versión 0.8.0 - Reportes Avanzados (Q3 2025):
- [ ] Gráficos interactivos avanzados
- [ ] Dashboard personalizable
- [ ] Análisis de tendencias
- [ ] Múltiples cuentas bancarias

## 📞 Soporte y Documentación

### Recursos Disponibles:
- 📖 [Documentación Técnica Completa](../README.md)
- 🗄️ [Documentación de Base de Datos](BASE_DATOS.md)
- 🏗️ [Arquitectura del Sistema](ARCHITECTURE.md)
- 🔧 [Guía de Contribución](CONTRIBUTING.md)
- ❓ [Preguntas Frecuentes](FAQ.md)

### Contacto y Soporte:
- **GitHub Issues**: Para reportar bugs o solicitar funcionalidades
- **Email**: estebanfabianp@gmail.com
- **Documentación**: Consulta los archivos MD en `/docs/` y `/documentacion/`

---

## 🎯 Consejos para Maximizar el Uso

1. **Familiarízate con la Interfaz**: Explora todas las opciones de validación y feedback
2. **Configura Correctamente**: Asegúrate de que las variables de entorno estén bien configuradas
3. **Mantén Actualizado**: Sigue el changelog para nuevas funcionalidades
4. **Contribuye**: El proyecto es open source, tus contribuciones son bienvenidas

---

**¡Disfruta gestionando tus finanzas de manera inteligente con nuestra aplicación desarrollada con tecnología moderna!**

**Versión Actual**: 0.5.0 | **Última Actualización**: Enero 2025 | **Tipo**: Aplicación de Escritorio
