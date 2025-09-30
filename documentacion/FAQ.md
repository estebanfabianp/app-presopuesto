# Preguntas Frecuentes (FAQ) — App Presupuesto

Respuestas a las preguntas más comunes sobre la aplicación de escritorio de gestión financiera personal desarrollada con Flet.

---

## 🖥️ General y Tecnología

### ¿Qué tipo de aplicación es App Presupuesto?
**App Presupuesto** es una **aplicación de escritorio** desarrollada con Python y Flet. No es una aplicación web ni API REST. Se ejecuta nativamente en tu computadora sin necesidad de navegador web.

### ¿Qué tecnologías utiliza el proyecto?
- **Lenguaje Principal**: Python 3.8+
- **Framework UI**: Flet (interfaz gráfica moderna)
- **Base de Datos**: MySQL 8.0+ o MariaDB 10.6+
- **Conector BD**: mysql-connector-python
- **Seguridad**: bcrypt para hash de contraseñas
- **Arquitectura**: MVC (Modelo-Vista-Controlador)
- **Testing**: pytest + coverage
- **Validación**: Validadores personalizados con sanitización

### ¿Puedo usar otra base de datos que no sea MySQL?
Actualmente la aplicación está optimizada específicamente para **MySQL/MariaDB**. Aunque técnicamente es posible adaptar el código para otros motores como PostgreSQL o SQLite, requeriría modificaciones significativas en:
- Scripts SQL de inicialización
- Pool de conexiones en `src/database/connection.py`
- Consultas específicas en `src/database/queries.py`

---

## 🛠️ Instalación y Configuración

### ¿Cómo instalo la aplicación?
Sigue estos pasos detallados:

1. **Prerrequisitos**:
   ```bash
   # Verificar Python 3.8+
   python --version
   
   # Verificar MySQL
   mysql --version
   ```

2. **Instalación**:
   ```bash
   git clone https://github.com/usuario/app-presopuesto.git
   cd app-presupuesto
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configuración**:
   ```bash
   copy .env.example .env
   # Editar .env con tus credenciales MySQL
   database\scripts\init_db.bat
   ```

4. **Ejecutar**:
   ```bash
   python src/views/user_view.py
   ```

Para detalles completos, consulta la [Guía de Usuario](../docs/USER_GUIDE.md).

### ¿Qué sistemas operativos soporta?
- ✅ **Windows 10/11**
- ✅ **macOS 10.14+** (Mojave o superior)
- ✅ **Linux** (Ubuntu 18.04+, Debian 10+, CentOS 7+)

### ¿Necesito conexión a internet para usarla?
**No.** La aplicación funciona completamente **offline**. Todos los datos se almacenan localmente en tu computadora usando MySQL local.

---

## 🔐 Seguridad y Datos

### ¿Mis datos están seguros?
**Absolutamente sí.** La aplicación implementa múltiples capas de seguridad:

- ✅ **Hash bcrypt**: Contraseñas con salt automático
- ✅ **Datos locales únicamente**: Sin envío a servidores externos
- ✅ **Validación exhaustiva**: Prevención de inyección SQL
- ✅ **Sanitización automática**: Limpieza de entrada maliciosa
- ✅ **Logs de auditoría**: Registro completo de eventos de seguridad
- ✅ **Pool de conexiones seguro**: Timeouts y reconexión automática

### ¿Quién puede acceder a mis datos?
**Solo tú.** No hay servidores remotos, clouds o terceros involucrados. Tienes control total sobre tus datos financieros.

### ¿Cómo hago backup de mis datos?
```bash
# Backup automático (incluido en la aplicación)
database\scripts\backup_db.bat  # Windows
bash database/scripts/backup_db.sh  # Linux/macOS

# Los backups se guardan en: database/backups/
# Con timestamp: backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 🚀 Funcionalidades Actuales y Futuras

### ¿Qué puedo hacer con la versión actual (v0.5.0)?
**Funcionalidades implementadas:**
- ✅ **Sistema de Login**: Autenticación robusta con validación en tiempo real
- ✅ **Interfaz Gráfica Moderna**: UI desarrollada con Flet (400x500px optimizada)
- ✅ **Seguridad Avanzada**: Hash bcrypt, sanitización, prevención SQL injection
- ✅ **Base de Datos Optimizada**: Pool de conexiones MySQL con scripts automatizados
- ✅ **Validación Completa**: Try-catch comprehensivo con feedback visual
- ✅ **Logging y Auditoría**: Sistema completo de logs de seguridad
- ✅ **Arquitectura MVC**: Separación clara de responsabilidades

### ¿Cuándo estará disponible el dashboard principal?
**Versión 0.6.0** (Q1 2025 - Febrero-Abril) incluirá:
- 📈 Dashboard interactivo con métricas financieras
- 💳 CRUD completo de cuentas bancarias
- 💰 Registro de transacciones (ingresos/gastos/transferencias)
- 📂 Sistema de categorización personalizable
- 📊 Gráficos básicos de distribución de gastos

### ¿Habrá funciones de inteligencia artificial?
**Sí.** **Versión 0.7.0** (Q2 2025 - Mayo-Julio) incluirá:
- 🤖 **Categorización automática** con Machine Learning
- 📊 **Análisis predictivo** de patrones de gasto
- 💡 **Recomendaciones personalizadas** para optimizar finanzas
- 📥 **Importación inteligente** de extractos bancarios (CSV/Excel)
- 🧠 **Aprendizaje continuo** que mejora con tu feedback

### ¿Cuál es el roadmap completo?
Consulta el [Roadmap detallado](roadmap.md) para información completa sobre:
- **v0.8.0**: Reportes avanzados y exportación PDF/Excel
- **v0.9.0**: Gestión de inversiones y portafolios
- **v1.0.0**: Aplicación móvil companion y sincronización

---

## 🐛 Problemas y Soluciones

### La aplicación no inicia, ¿qué hago?
**Diagnóstico paso a paso:**

1. **Verificar Python**:
   ```bash
   python --version  # Debe mostrar 3.8+
   ```

2. **Verificar entorno virtual**:
   ```bash
   # Debe estar activado
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

3. **Verificar Flet**:
   ```bash
   python -c "import flet as ft; print('✅ Flet OK')"
   ```

4. **Verificar MySQL**:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

5. **Revisar logs**:
   ```bash
   # Consultar logs/error.log para detalles
   cat logs/error.log  # Linux/macOS
   type logs\error.log  # Windows
   ```

### Error "No se puede conectar a la base de datos"
**Soluciones ordenadas por probabilidad:**

1. **Verificar MySQL activo**:
   ```bash
   # Windows
   net start mysql
   
   # Linux
   sudo systemctl start mysql
   
   # macOS
   brew services start mysql
   ```

2. **Verificar configuración `.env`**:
   ```bash
   # Revisar credenciales
   cat .env
   
   # Probar conexión manual
   mysql -h localhost -u app_user -p presupuesto_db
   ```

3. **Probar conexión desde Python**:
   ```bash
   python -c "
   from src.database.connection import get_db_connection
   try:
       conn = get_db_connection()
       print('✅ Conexión exitosa')
       conn.close()
   except Exception as e:
       print(f'❌ Error: {e}')
   "
   ```

4. **Reinicializar base de datos**:
   ```bash
   database\scripts\reset_db.bat  # Windows
   bash database/scripts/reset_db.sh  # Linux/macOS
   ```

### Error "Módulo flet no encontrado"
```bash
# Verificar entorno virtual activo
which python  # Linux/macOS
where python  # Windows

# Reinstalar Flet
pip uninstall flet -y
pip install flet

# Verificar instalación
pip list | grep flet
```

### Error "Credenciales inválidas"
```bash
# Verificar usuarios en BD
mysql -u root -p presupuesto_db -e "SELECT username, nombre FROM usuarios LIMIT 5;"

# Crear usuario de prueba
mysql -u root -p presupuesto_db < database/scripts/create/create_data.sql

# Probar credenciales por defecto:
# Usuario: admin, Contraseña: admin123
# Usuario: test@test.com, Contraseña: test123
```

---

## 🔄 Desarrollo y Contribución

### ¿Cómo reporto un bug?
1. **GitHub Issues**: [Crear nuevo issue](https://github.com/tu-usuario/app-presopuesto/issues)
2. **Información a incluir**:
   - Versión de la aplicación (v0.5.0 actual)
   - Sistema operativo y versión
   - Pasos para reproducir el error
   - Logs relevantes (sin información sensible)
   - Screenshots si es aplicable

3. **Email directo**: estebanfabianp@gmail.com para problemas críticos

### ¿Cómo contribuyo al proyecto?
El proyecto es **open source** bajo licencia MIT. Para contribuir:

1. **Fork** del repositorio
2. **Crear rama** para tu feature: `git checkout -b feature/mi-funcionalidad`
3. **Seguir estándares**:
   - Código Python siguiendo PEP 8
   - Docstrings en formato Google
   - Tests para nuevas funcionalidades
4. **Crear Pull Request** con descripción detallada

Consulta la [Guía de Contribución](CONTRIBUTING.md) para detalles completos.

### ¿Puedo usar la aplicación en producción para mi negocio?
**Consideraciones importantes:**

✅ **Para uso personal**: Completamente recomendado
⚠️ **Para uso empresarial**: Evaluar cuidadosamente

**Recomendaciones**:
- Revisar la licencia MIT
- Realizar pruebas exhaustivas con tus datos
- Implementar backups automáticos regulares
- Considerar que las APIs internas pueden cambiar entre versiones
- Para consultas empresariales: estebanfabianp@gmail.com

---

## 📊 Datos y Exportación

### ¿Puedo exportar mis datos?
**Actualmente**: Acceso directo a MySQL para exportación manual

**Próximas versiones**:
- **v0.8.0**: Exportación nativa a PDF, Excel, CSV
- **v1.0.0**: APIs de exportación para integración con otras herramientas

### ¿Qué formatos de importación soportará?
**Planificado para v0.7.0**:
- ✅ CSV de extractos bancarios
- ✅ Excel con formato estándar
- ✅ QIF (Quicken Interchange Format)
- ✅ OFX (Open Financial Exchange)
- ✅ Mapeo automático de columnas con IA

### ¿Soportará múltiples monedas?
**Sí.** **Versión 1.0.0** incluirá:
- 💱 Soporte para múltiples monedas simultáneas
- 🔄 Tasas de cambio automáticas (APIs financieras)
- 📊 Conversión en tiempo real
- 📈 Reportes multi-moneda unificados

---

## 🎯 Mejores Prácticas y Consejos

### ¿Con qué frecuencia debo hacer backup?
**Estrategia recomendada**:
- **Automático**: Scripts incluidos hacen backup diario
- **Manual semanal**: Backup adicional para mayor seguridad
- **Antes de actualizaciones**: Siempre backup antes de cambiar versiones
- **Prueba de restauración**: Verificar backups mensualmente

### ¿Cómo organizo mejor mis datos financieros?
**Tips para maximizar el uso**:

1. **Nomenclatura consistente**:
   - Cuentas: "Banco_Tipo_Descripcion" (ej: "Bancolombia_Corriente_Principal")
   - Categorías: Mantener lista simple y consistente

2. **Entrada regular**:
   - Transacciones: Registrar diariamente
   - Revisión: Semanal de saldos
   - Presupuestos: Actualizar mensualmente

3. **Preparación para IA** (v0.7.0):
   - Descripciones detalladas para mejor categorización automática
   - Recopilar extractos bancarios para entrenamiento
   - Mantener categorías organizadas desde ahora

### ¿Debo preocuparme por el rendimiento?
**No.** La aplicación está optimizada para:
- **Pool de conexiones**: 20 conexiones simultáneas
- **Queries optimizadas**: Índices y consultas eficientes
- **UI responsiva**: Interfaz Flet con feedback inmediato
- **Uso de memoria**: Mínimo consumo de recursos

**Para volúmenes grandes** (>100,000 transacciones):
- Implementar paginación en consultas
- Usar filtros de fecha para limitar resultados
- Considerar archivado de datos antiguos

---

## 📞 Soporte y Comunidad

### ¿Dónde encuentro más documentación?
**Documentación técnica completa**:
- 📖 **Principal**: [README.md](../README.md)
- 🏗️ **Arquitectura**: [ARCHITECTURE.md](ARCHITECTURE.md)
- 🗄️ **Base de Datos**: [BASE_DATOS.md](../docs/BASE_DATOS.md)
- 👤 **Guía de Usuario**: [USER_GUIDE.md](../docs/USER_GUIDE.md)
- 🔒 **Seguridad**: [SECURITY.md](SECURITY.md)
- 🚀 **Roadmap**: [roadmap.md](roadmap.md)

### ¿Cómo me mantengo actualizado?
**Métodos recomendados**:
1. **GitHub Watch**: Suscribirse a notificaciones del repositorio
2. **GitHub Releases**: Seguir página de releases para nuevas versiones
3. **Changelog**: Revisar [CHANGELOG.md](CHANGELOG.md) regularmente
4. **Issues**: Seguir discusiones activas

### ¿Hay alguna comunidad de usuarios?
**En desarrollo**:
- **GitHub Discussions**: Para preguntas y discusiones técnicas
- **Discord Server**: Planificado para v1.0.0
- **Newsletter**: En evaluación para notificaciones de updates

### Contacto directo del desarrollador
- **Email**: estebanfabianp@gmail.com
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)
- **Issues técnicos**: [GitHub Issues](https://github.com/tu-usuario/app-presopuesto/issues)

---

## 🏆 Proyecto Open Source

### ¿Puedo contribuir económicamente?
Por el momento no hay sistema de donaciones configurado. **Las mejores formas de apoyar**:
- ⭐ **Star en GitHub**: Dar estrella al repositorio
- 🐛 **Reportar bugs**: Ayudar a mejorar la calidad
- 💻 **Contribuir código**: Pull requests con mejoras
- 📢 **Compartir**: Recomendar a otros usuarios
- 📝 **Documentación**: Mejorar guías y tutoriales

### ¿Quién desarrolla la aplicación?
**Desarrollador Principal**: Esteban Fabián Patiño Montealegre
- **Especialización**: Arquitectura MVC, seguridad, bases de datos
- **Visión**: Democratizar la gestión financiera personal con tecnología moderna
- **Contacto**: estebanfabianp@gmail.com

### ¿Cuál es la licencia del proyecto?
**Licencia MIT** - Código abierto que permite:
- ✅ Uso comercial y personal
- ✅ Modificación y distribución
- ✅ Uso privado sin restricciones
- ✅ Sublicenciar si es necesario

**Obligaciones**: Incluir aviso de copyright y licencia

---

## 🔮 Futuro del Proyecto

### ¿Habrá versión móvil?
**Sí.** **Versión 1.0.0** incluirá:
- 📱 Aplicación móvil companion (iOS/Android)
- 🔄 Sincronización bidireccional con desktop
- 📊 Dashboard móvil optimizado
- 🔔 Notificaciones push

### ¿Se convertirá en aplicación web?
**No está planificado.** El enfoque es mantener la **privacidad y control local** de datos. Sin embargo, **v1.0.0** incluirá:
- 🌐 APIs opcionales para integraciones
- ☁️ Backup en la nube (encriptado)
- 🔗 Conectores para servicios bancarios

### ¿Habrá soporte comercial?
**Evaluación en curso** para v1.0.0:
- Soporte técnico prioritario
- Implementación empresarial
- Consultoría en gestión financiera
- Contacto: estebanfabianp@gmail.com

---

**💫 ¿Tu pregunta no está aquí?**

**¡No dudes en contactarnos!**
- 📧 **Email**: estebanfabianp@gmail.com  
- 🐛 **Bug Report**: [GitHub Issues](https://github.com/tu-usuario/app-presopuesto/issues)
- 💬 **Discusión**: [GitHub Discussions](https://github.com/tu-usuario/app-presopuesto/discussions)

---

**Última actualización**: Enero 2025 | **Versión**: 0.5.0 | **Tipo**: Aplicación de Escritorio con Flet

**¡Gracias por usar App Presupuesto! 💰✨**