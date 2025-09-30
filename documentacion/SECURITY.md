# Política de Seguridad — App Presupuesto

La seguridad de los usuarios y la protección de datos financieros es nuestra máxima prioridad. Este documento detalla las medidas implementadas y las mejores prácticas para mantener el sistema seguro.

---

## 🛡️ Medidas de Seguridad Implementadas

### Autenticación y Autorización
- **Hash de Contraseñas**: Implementación de bcrypt con salt automático
- **Validación Robusta**: Verificación de longitud y complejidad de contraseñas
- **Sesiones Seguras**: Control de timeout y cierre automático por inactividad
- **Prevención de Fuerza Bruta**: Límite de intentos de login fallidos

### Validación de Entrada
- **Sanitización Automática**: Eliminación de espacios y caracteres especiales
- **Prevención de Inyección SQL**: Validación exhaustiva de todas las entradas
- **Validación de Tipos**: Verificación de tipos de datos en todas las interfaces
- **Escape de Caracteres**: Tratamiento seguro de caracteres especiales

### Configuración Segura
- **Variables de Entorno**: Credenciales sensibles fuera del código fuente
- **Conexiones Seguras**: Pool de conexiones con timeouts configurados
- **Logs de Seguridad**: Registro detallado de eventos de seguridad
- **Manejo de Errores**: Sin exposición de información sensible en errores

### Arquitectura de Seguridad
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  UI Layer   │ -> │ Validation   │ -> │ Controllers │
│ (Flet View) │    │ & Security   │    │ (Business)  │
└─────────────┘    └──────────────┘    └─────────────┘
                            │
                    ┌──────────────┐
                    │   Database   │
                    │ (Encrypted)  │
                    └──────────────┘
```

---

## 🚨 Reporte de Vulnerabilidades

### Proceso de Reporte Responsable

**NO divulgues vulnerabilidades públicamente.** Sigue estos pasos:

1. **Contacto Directo**: 
   - 📧 Email: estebanfabianp@gmail.com
   - 🔒 Asunto: "[SECURITY] Reporte de Vulnerabilidad"

2. **Información Requerida**:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir el problema
   - Impacto potencial estimado
   - Evidencia (screenshots, logs, etc.)
   - Versión afectada del software

3. **Proceso de Respuesta**:
   - **24 horas**: Confirmación de recepción
   - **72 horas**: Evaluación inicial
   - **7 días**: Plan de remediación
   - **30 días**: Implementación de corrección

### Política de Divulgación
- Las vulnerabilidades críticas se parchean en **máximo 7 días**
- Las vulnerabilidades altas se corrigen en **máximo 30 días**
- Se notifica a los usuarios sobre actualizaciones de seguridad
- Se otorga reconocimiento a reporteros responsables (si lo desean)

---

## 🔐 Configuración de Seguridad Recomendada

### Variables de Entorno Esenciales
```env
# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=presupuesto_db
DB_USER=app_user_secure
DB_PASSWORD=ComplexPassword123!@#

# Seguridad
SECRET_KEY=your-ultra-secure-secret-key-here-64-chars-minimum
JWT_SECRET_KEY=another-secret-for-jwt-tokens-different-from-main

# Configuración de Sesión
SESSION_TIMEOUT=3600  # 1 hora
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900  # 15 minutos
```

### Configuración de Base de Datos
```sql
-- Crear usuario dedicado con permisos limitados
CREATE USER 'app_user_secure'@'localhost' IDENTIFIED BY 'ComplexPassword123!@#';
GRANT SELECT, INSERT, UPDATE, DELETE ON presupuesto_db.* TO 'app_user_secure'@'localhost';
FLUSH PRIVILEGES;

-- Configurar SSL (recomendado para producción)
ALTER USER 'app_user_secure'@'localhost' REQUIRE SSL;
```

### Configuración del Sistema
```bash
# Permisos de archivos restrictivos
chmod 600 .env
chmod 755 src/
chmod 644 src/**/*.py

# Configuración de logs
mkdir -p logs/security
chmod 750 logs/security
```

---

## 🛠️ Mejores Prácticas para Desarrolladores

### Desarrollo Seguro
```python
# ✅ Correcto: Uso de parámetros preparados
def autenticar_usuario(username, password):
    try:
        # Sanitización de entrada
        username = username.strip()
        if len(username) < 3:
            return None, "Usuario muy corto"
        
        # Hash seguro de contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Consulta segura con parámetros
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        
    except Exception as e:
        logger.error(f"Error de autenticación: {str(e)}")
        return None, "Error interno"
```

### Validación de Entrada
```python
# ✅ Validación robusta
def validar_entrada(data):
    # Sanitización
    if isinstance(data, str):
        data = data.strip()
        data = re.sub(r'[<>"\';]', '', data)  # Remover caracteres peligrosos
    
    # Validación de longitud
    if len(data) > MAX_INPUT_LENGTH:
        raise ValueError("Entrada demasiado larga")
    
    return data
```

### Manejo de Errores Seguro
```python
# ✅ Correcto: No exponer información sensible
try:
    result = database_operation()
except DatabaseError as e:
    logger.error(f"Error de BD: {e}")
    return {"error": "Error interno del sistema"}  # Mensaje genérico
```

---

## 🔍 Auditoría y Monitoreo

### Logs de Seguridad
El sistema registra automáticamente:
- ✅ Intentos de login (exitosos y fallidos)
- ✅ Cambios de contraseña
- ✅ Accesos a datos sensibles
- ✅ Errores de validación
- ✅ Operaciones administrativas

### Métricas de Seguridad
```python
# Ejemplo de logging de seguridad
import logging

security_logger = logging.getLogger('security')
security_logger.info(f"Login exitoso: usuario={username}, ip={client_ip}")
security_logger.warning(f"Intento fallido: usuario={username}, ip={client_ip}")
security_logger.error(f"Posible ataque: múltiples intentos desde ip={client_ip}")
```

---

## 🚀 Próximas Mejoras de Seguridad

### Versión 0.6.0:
- [ ] **Autenticación de Dos Factores (2FA)**
- [ ] **Tokens JWT con refresh automático**
- [ ] **Rate limiting avanzado por IP**
- [ ] **Encriptación de datos sensibles en BD**

### Versión 0.7.0:
- [ ] **Auditoría completa de acciones**
- [ ] **Detección de anomalías en patrones de uso**
- [ ] **Backup automático encriptado**
- [ ] **Compliance con estándares PCI DSS**

### Versión 1.0.0:
- [ ] **Certificación de seguridad externa**
- [ ] **Penetration testing completo**
- [ ] **Integración con HSM para claves**
- [ ] **Zero-trust architecture**

---

## 📋 Checklist de Seguridad para Despliegue

### Antes de Producción:
- [ ] Variables de entorno configuradas correctamente
- [ ] Base de datos con usuario dedicado y permisos mínimos
- [ ] SSL/TLS habilitado para todas las conexiones
- [ ] Firewall configurado (solo puertos necesarios)
- [ ] Logs de seguridad habilitados y monitoreados
- [ ] Respaldos automáticos configurados y probados
- [ ] Pruebas de penetración básicas completadas
- [ ] Documentación de seguridad actualizada

### Mantenimiento Continuo:
- [ ] Actualizaciones de seguridad aplicadas mensualmente
- [ ] Revisión de logs de seguridad semanalmente
- [ ] Pruebas de restauración de backup trimestralmente
- [ ] Evaluación de vulnerabilidades semestralmente
- [ ] Capacitación del equipo en seguridad anualmente

---

## 📞 Contacto de Seguridad

### Equipo de Seguridad:
- **Responsable**: Esteban Fabián Patiño Montealegre
- **Email**: estebanfabianp@gmail.com
- **PGP Key**: [Disponible bajo solicitud]

### Canales de Comunicación:
- **Emergencias**: Email con [URGENT SECURITY] en el asunto
- **Reportes**: Email con [SECURITY] en el asunto
- **Consultas**: Issues en GitHub (solo para temas no sensibles)

---

## 🏆 Reconocimientos

Agradecemos a todos los investigadores de seguridad que han contribuido a mejorar la seguridad de este proyecto:

- **Hall of Fame**: [Lista de contribuidores responsables]
- **Créditos**: Se otorga reconocimiento público (opcional)
- **Recompensas**: Evaluadas caso por caso según impacto

---

**Última Revisión**: Enero 2025 | **Versión**: 0.5.0

**¡Gracias por ayudar a mantener seguro nuestro proyecto!**