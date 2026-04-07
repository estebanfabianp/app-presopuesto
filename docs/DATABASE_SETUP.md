# 🗄️ Configuración de Base de Datos - App Presupuesto v0.7.1
**Sistema Empresarial Automatizado**

Esta guía explica en detalle la configuración de la base de datos MySQL con sistema de instalación automatizado, funciones empresariales y documentación integrada.

---

## 📋 Tabla de Contenidos

1. [Introducción](#-introducción)
2. [Métodos de Instalación](#-métodos-de-instalación)
3. [Instalación Automatizada (Recomendada)](#-instalación-automatizada-recomendada)
4. [Instalación Manual](#-instalación-manual)
5. [Verificación y Validación](#-verificación-y-validación)
6. [Funcionalidades Empresariales](#-funcionalidades-empresariales)
7. [Mantenimiento y Respaldo](#-mantenimiento-y-respaldo)
8. [Solución de Problemas](#-solución-de-problemas)

---

## 🎯 Introducción

El sistema de base de datos v0.7.1 incluye:

- **✅ Instalación Automatizada**: Scripts maestros con logging y rollback
- **🔧 Funciones Empresariales**: Cálculo de días hábiles, fechas de Colombia
- **📊 Sistema de Documentación**: Auto-documentación y reportes arquitectónicos
- **⚡ Triggers Inteligentes**: Automatización de cálculos financieros
- **🕐 Eventos Programados**: Mantenimiento automático del sistema
- **🛡️ Validación Completa**: Verificación de integridad en instalación

---

## 🚀 Métodos de Instalación

### Método 1: Script Maestro (RECOMENDADO)
```bash
# Navegar a la carpeta de scripts
cd base_de_datos/db/01_core/create

# Ejecutar instalación completa con logging
mysql -u root -p < 09_master_script.sql
```
**✅ Incluye**: Logging completo, rollback automático, validación, reportes

### Método 2: Instalación Batch (Windows)
```cmd
# Desde la raíz del proyecto
cd base_de_datos\db
init_db.bat
```
**✅ Incluye**: Instalación paso a paso, pausas para verificación, logging

### Método 3: Instalación Manual
```bash
# Paso a paso para máximo control
mysql -u root -p < 01_create_database.sql
mysql -u root -p < 02_create_tables.sql
# ... continuar con archivos en orden
```

---

## 🎯 Instalación Automatizada (Recomendada)

### Paso 1: Preparación
```bash
# Verificar MySQL está ejecutándose
systemctl status mysql  # Linux
# o 
net start MySQL80       # Windows

# Verificar credenciales de acceso
mysql -u root -p -e "SELECT VERSION();"
```

### Paso 2: Ejecutar Script Maestro
```bash
cd base_de_datos/db/01_core/create
mysql -u root -p < 09_master_script.sql
```

### Paso 3: Verificar Instalación
El script automáticamente mostrará:
```
📊 INSTALACIÓN COMPLETADA EXITOSAMENTE
🔧 COMPONENTES INSTALADOS:
  - Tablas creadas: 18
  - Funciones creadas: 4
  - Procedimientos: 8
  - Triggers: 6
  - Vistas: 3
  - Usuarios sistema: 2
  - Categorías base: 15
  - Constantes: 12
  - Días festivos Colombia: 18

🎯 PRÓXIMOS PASOS:
  1. Ejecutar: python main.py
  2. Usar: CALL sp_generar_reporte_documentacion();
  3. Configurar constantes según necesidades
```

---

## 🔧 Instalación Manual Detallada

### Orden de Ejecución (CRÍTICO)
```bash
# 1. Base de datos
mysql -u root -p < 01_create_database.sql

# 2. Estructura base
mysql -u root -p app_presupuesto < 02_create_tables.sql
mysql -u root -p app_presupuesto < 03_create_indexes.sql
mysql -u root -p app_presupuesto < 04_foreign_keys.sql

# 3. Lógica de negocio
mysql -u root -p app_presupuesto < 05_stored_procedures.sql
mysql -u root -p app_presupuesto < 06_functions.sql
mysql -u root -p app_presupuesto < 07_triggers.sql

# 4. Mantenimiento y eventos
mysql -u root -p app_presupuesto < 08_events_jobs.sql

# 5. Documentación
mysql -u root -p app_presupuesto < 10_add_comments.sql
mysql -u root -p app_presupuesto < 11_create_view.sql
mysql -u root -p app_presupuesto < 13_create_documentation_tables.sql
mysql -u root -p app_presupuesto < 14_documentation_procedures.sql

# 6. Datos iniciales
mysql -u root -p app_presupuesto < insert_initial_data.sql
```

---

## ✅ Verificación y Validación

### Verificar Instalación Básica
```sql
-- Conectar a la base de datos
USE app_presupuesto;

-- Verificar tablas principales
SHOW TABLES;

-- Verificar datos iniciales
SELECT COUNT(*) as usuarios FROM persona;
SELECT COUNT(*) as categorias FROM categoria;
SELECT COUNT(*) as constantes FROM constantes;
SELECT COUNT(*) as dias_festivos FROM dias_festivos;
```

### Verificar Funcionalidades Avanzadas
```sql
-- Probar función de días hábiles
SELECT fn_dias_habiles('2024-01-01', '2024-01-31') as dias_habiles_enero;

-- Probar siguiente día hábil
SELECT fn_siguiente_dia_habil('2024-12-24') as siguiente_dia_habil;

-- Generar reporte de documentación
CALL sp_generar_reporte_documentacion();

-- Generar reporte de arquitectura
CALL sp_generar_reporte_arquitectura();
```

### Verificar Triggers y Automatización
```sql
-- Insertar movimiento de prueba para verificar triggers
INSERT INTO cuenta (id_persona, nombre_cuenta, tipo_cuenta, saldo_inicial) 
VALUES (1, 'Cuenta Prueba', 'AHORRO', 1000.00);

-- El trigger debería actualizar automáticamente campos calculados
SELECT * FROM cuenta WHERE nombre_cuenta = 'Cuenta Prueba';
```

---

## 🏢 Funcionalidades Empresariales

### Cálculo de Días Hábiles
```sql
-- Días hábiles entre dos fechas (excluyendo festivos Colombia)
SELECT fn_dias_habiles('2024-01-01', '2024-12-31') as dias_habiles_2024;

-- Siguiente día hábil desde una fecha específica
SELECT fn_siguiente_dia_habil(CURDATE()) as proximo_dia_habil;
```

### Sistema de Constantes Configurables
```sql
-- Ver todas las constantes del sistema
SELECT * FROM constantes ORDER BY categoria, clave;

-- Actualizar configuración específica
UPDATE constantes 
SET valor = '18%' 
WHERE categoria = 'FINANCIERO' AND clave = 'TASA_INTERES_PRESTAMO';
```

### Reportes Automáticos
```sql
-- Reporte completo del sistema
CALL sp_generar_reporte_documentacion();

-- Arquitectura y métricas
CALL sp_generar_reporte_arquitectura();

-- Ver documentación integrada
SELECT * FROM v_documentacion_completa;
```

---

## 🔧 Mantenimiento y Respaldo

### Eventos Automáticos Configurados
El sistema incluye eventos programados que se ejecutan automáticamente:

- **Mantenimiento Diario**: Optimización de tablas y limpieza de logs
- **Respaldo Semanal**: Backup automático de datos críticos  
- **Limpieza Mensual**: Eliminación de datos obsoletos

```sql
-- Ver eventos programados
SHOW EVENTS;

-- Verificar estado de eventos
SELECT EVENT_NAME, STATUS, EXECUTE_AT, INTERVAL_VALUE, INTERVAL_FIELD 
FROM information_schema.EVENTS 
WHERE EVENT_SCHEMA = 'app_presupuesto';
```

### Respaldo Manual
```bash
# Respaldo completo
mysqldump -u root -p app_presupuesto > backup_app_presupuesto_$(date +%Y%m%d).sql

# Respaldo solo estructura
mysqldump -u root -p --no-data app_presupuesto > estructura_app_presupuesto.sql

# Respaldo solo datos
mysqldump -u root -p --no-create-info app_presupuesto > datos_app_presupuesto.sql
```

---

## 🚨 Solución de Problemas

### Error: "Database app_presupuesto already exists"
```sql
-- Opción 1: Usar el script de eliminación
USE mysql;
SOURCE base_de_datos/db/01_core/drop/99_drop_all_objects.sql;

-- Opción 2: Eliminación manual (¡CUIDADO!)
DROP DATABASE IF EXISTS app_presupuesto;
```

### Error: "Function fn_dias_habiles does not exist"
```bash
# Reinstalar solo las funciones
mysql -u root -p app_presupuesto < 06_functions.sql
```

### Error: "Event scheduler is not running"
```sql
-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- Verificar estado
SHOW VARIABLES LIKE 'event_scheduler';
```

### Problemas de Permisos
```sql
-- Crear usuario específico para la aplicación
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password_seguro';
GRANT ALL PRIVILEGES ON app_presupuesto.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### Verificar Logs de Instalación
```sql
-- Si se usó el script maestro, revisar logs de instalación
SELECT * FROM install_log ORDER BY timestamp DESC;

-- Ver errores específicos
SELECT * FROM install_log WHERE status = 'ERROR';
```

---

## 📊 Métricas de Instalación Exitosa

Una instalación correcta debe mostrar:

| Componente | Cantidad Esperada |
|------------|-------------------|
| Tablas | 18 |
| Funciones | 4 |
| Procedimientos | 8+ |
| Triggers | 6+ |
| Vistas | 3+ |
| Eventos | 3+ |
| Índices | 25+ |
| Usuarios Demo | 2 |
| Categorías | 15+ |
| Constantes | 12+ |
| Días Festivos | 18+ |

### Comando de Verificación Rápida
```sql
-- Ejecutar para obtener resumen completo
CALL sp_generar_reporte_documentacion();
```

---

## 📚 Documentación Adicional

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Arquitectura del sistema
- **[DATA_MODEL.md](DATA_MODEL.md)**: Modelo de datos detallado
- **[API_REFERENCE.md](API_REFERENCE.md)**: Referencia de API
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Solución de problemas específicos

---

## ✅ Checklist de Instalación

- [ ] MySQL 8.0+ instalado y ejecutándose
- [ ] Credenciales de acceso configuradas
- [ ] Scripts descargados y en la carpeta correcta
- [ ] Script maestro ejecutado exitosamente
- [ ] Verificación de componentes completada
- [ ] Reportes de documentación funcionando
- [ ] Funciones de días hábiles operativas
- [ ] Eventos programados activados
- [ ] Datos de prueba cargados correctamente
- [ ] Aplicación Python conecta exitosamente

**¡Instalación Completa!** 🎉

El sistema está listo para usar con `python main.py`