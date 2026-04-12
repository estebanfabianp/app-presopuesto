@echo off
REM ============================================================================
REM 🚀 SCRIPT DE INICIALIZACIÓN COMPLETA DE LA BASE DE DATOS
REM ============================================================================
REM Proyecto: app-presupuesto
REM Autor: Esteban Fabián Patiño Montealegre
REM Fecha: Diciembre 2025
REM Descripción: Inicializa la base de datos completa con todas las estructuras
REM              tablas, vistas, funciones, procedimientos y datos iniciales
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuración de la base de datos
set DB_USER=root
set DB_PASS=
set DB_NAME=app_presupuesto
set DB_HOST=localhost
set DB_PORT=3306

REM Configuración de rutas
set BASE_DIR=%~dp0
set CREATE_DIR=%BASE_DIR%01_core\create
set SEED_DIR=%BASE_DIR%01_core\seed
set DROP_DIR=%BASE_DIR%01_core\drop
set MAINT_DIR=%BASE_DIR%02_maintenance
set HASH_MIGRATION_FILE=%MAINT_DIR%\2026-04-12_hash_legacy_persona_passwords.sql

REM Construir comando MySQL sin forzar prompt cuando DB_PASS está vacío
set MYSQL_BASE=mysql -u %DB_USER% -h %DB_HOST% -P %DB_PORT%
if not "%DB_PASS%"=="" (
    set MYSQL_BASE=%MYSQL_BASE% -p%DB_PASS%
)

REM Variables de control
set ERROR_COUNT=0
set SUCCESS_COUNT=0
set EXISTING_TABLE_COUNT=0
set INSTALL_MODE=full

echo ============================================================================
echo  🏗️  INICIALIZADOR DE BASE DE DATOS - APP PRESUPUESTO
echo ============================================================================
echo  📅 Fecha: %DATE% %TIME%
echo  🗄️  Base de datos: %DB_NAME%
echo  🖥️  Servidor: %DB_HOST%:%DB_PORT%
echo  👤 Usuario: %DB_USER%
echo ============================================================================

REM Verificar que MySQL esté disponible
echo 🔍 Verificando conexión a MySQL...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: MySQL no está disponible en el PATH del sistema
    echo    Asegúrate de tener MySQL instalado y agregado al PATH
    pause
    exit /b 1
)

REM Probar conexión a la base de datos
echo 🔐 Probando conexión a MySQL...
%MYSQL_BASE% -e "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: No se puede conectar a MySQL
    echo    Verifica las credenciales y que el servidor esté ejecutándose
    pause
    exit /b 1
)
echo ✅ Conexión a MySQL establecida correctamente

REM Crear la base de datos si no existe
echo 🏗️  Creando base de datos '%DB_NAME%'...
%MYSQL_BASE% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8 COLLATE utf8_general_ci;"
if errorlevel 1 (
    echo ❌ ERROR: No se pudo crear la base de datos
    set /a ERROR_COUNT+=1
) else (
    echo ✅ Base de datos '%DB_NAME%' creada/verificada correctamente
    set /a SUCCESS_COUNT+=1
)

REM Detectar si la base ya contiene estructura; si existe, evitar scripts no idempotentes
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='%DB_NAME%' AND table_type='BASE TABLE';"') do set EXISTING_TABLE_COUNT=%%i
if %EXISTING_TABLE_COUNT% gtr 0 (
    set INSTALL_MODE=maintenance
    echo ℹ️  Base existente detectada con %EXISTING_TABLE_COUNT% tablas.
    echo ℹ️  Se activará modo mantenimiento para evitar errores por re-ejecución.
) else (
    echo ℹ️  Base vacía detectada. Se ejecutará instalación completa.
)

if /I "%INSTALL_MODE%"=="maintenance" goto MAINTENANCE_ONLY

echo ============================================================================
echo  📋 EJECUTANDO SCRIPTS DE CREACIÓN DE ESTRUCTURA
echo ============================================================================

REM PASO 1: Crear tablas base
echo 📊 [1/7] Creando tablas base...
if exist "%CREATE_DIR%\02_create_tables.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\02_create_tables.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de tablas
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Tablas creadas correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de tablas no encontrado: %CREATE_DIR%\02_create_tables.sql
)

REM PASO 2: Crear claves foráneas
echo 🔗 [2/10] Creando claves foráneas...
if exist "%CREATE_DIR%\04_foreign_keys.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\04_foreign_keys.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de claves foráneas
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Claves foráneas creadas correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de claves foráneas no encontrado
)

REM PASO 3: Crear índices
echo 📇 [3/11] Creando índices...
if exist "%CREATE_DIR%\03_create_indexes.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\03_create_indexes.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de índices
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Índices creados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de índices no encontrado
)

REM PASO 4: Crear funciones
echo ⚙️  [4/11] Creando funciones personalizadas...
if exist "%CREATE_DIR%\06_functions.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\06_functions.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de funciones
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Funciones creadas correctamente (días hábiles, cálculos financieros)
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de funciones no encontrado
)

REM PASO 5: Crear procedimientos
echo 🔧 [5/11] Creando procedimientos almacenados...
if exist "%CREATE_DIR%\05_stored_procedures.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\05_stored_procedures.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de procedimientos
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Procedimientos creados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de procedimientos no encontrado
)

REM PASO 6: Crear triggers
echo ⚡ [6/11] Creando triggers...
if exist "%CREATE_DIR%\07_triggers.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\07_triggers.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de triggers
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Triggers creados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de triggers no encontrado
)

REM PASO 7: Agregar comentarios
echo 📝 [7/11] Agregando comentarios de documentación...
if exist "%CREATE_DIR%\10_add_comments.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\10_add_comments.sql"
    if errorlevel 1 (
        echo ❌ ERROR al agregar comentarios
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Comentarios agregados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de comentarios no encontrado
)

REM PASO 8: Crear vistas
echo 👁️  [8/11] Creando vistas consolidadas...
if exist "%CREATE_DIR%\11_create_view.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\11_create_view.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de vistas
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Vistas creadas correctamente (productos, balances, reportes)
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de vistas no encontrado
)

REM PASO 9: Crear tablas de documentación
echo 📚 [9/11] Creando sistema de documentación...
if exist "%CREATE_DIR%\13_create_documentation_tables.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\13_create_documentation_tables.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de tablas de documentación
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Tablas de documentación creadas correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de tablas de documentación no encontrado
)

REM PASO 10: Crear procedimientos de documentación
echo 🔧 [10/11] Creando procedimientos de documentación...
if exist "%CREATE_DIR%\14_documentation_procedures.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\14_documentation_procedures.sql"
    if errorlevel 1 (
        echo ❌ ERROR en procedimientos de documentación
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Procedimientos de documentación creados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de procedimientos de documentación no encontrado
)

REM PASO 11: Crear eventos programados (opcional)
echo ⏰ [11/11] Creando eventos programados...
if exist "%CREATE_DIR%\08_events_jobs.sql" (
    %MYSQL_BASE% %DB_NAME% < "%CREATE_DIR%\08_events_jobs.sql"
    if errorlevel 1 (
        echo ❌ ERROR en creación de eventos (continuando...)
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Eventos programados creados correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de eventos no encontrado (opcional)
)

echo ============================================================================
echo  🌱 INSERTANDO DATOS INICIALES
echo ============================================================================

REM Insertar datos de configuración y catálogos
echo 📄 Insertando datos iniciales y configuración...
if exist "%SEED_DIR%\insert_initial_data.sql" (
    %MYSQL_BASE% %DB_NAME% < "%SEED_DIR%\insert_initial_data.sql"
    if errorlevel 1 (
        echo ❌ ERROR en inserción de datos iniciales
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Datos iniciales insertados correctamente
        echo   • Constantes del sistema
        echo   • Categorías predefinidas  
        echo   • Días festivos de Colombia
        echo   • Documentación técnica completa
        echo   • Datos de arquitectura del sistema
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de datos iniciales no encontrado
)

:MAINTENANCE_ONLY

if /I "%INSTALL_MODE%"=="maintenance" (
    echo ============================================================================
    echo  🛠️  MODO MANTENIMIENTO SEGURO
    echo ============================================================================
    echo ℹ️  Se omite recreación de tablas, índices, claves foráneas, vistas y seed.
    echo ℹ️  Solo se ejecutan tareas seguras sobre una base existente.
    set /a SUCCESS_COUNT+=1
)

echo ============================================================================
echo  🔐 MIGRANDO CONTRASEÑAS LEGACY
echo ============================================================================

if exist "%HASH_MIGRATION_FILE%" (
    echo 🔒 Ejecutando migración de contraseñas legacy a SHA-256...
    %MYSQL_BASE% < "%HASH_MIGRATION_FILE%"
    if errorlevel 1 (
        echo ❌ ERROR en migración de contraseñas legacy
        set /a ERROR_COUNT+=1
    ) else (
        echo ✅ Migración de contraseñas legacy ejecutada correctamente
        set /a SUCCESS_COUNT+=1
    )
) else (
    echo ⚠️  Archivo de migración de contraseñas no encontrado
)

echo ============================================================================
echo  📊 RESUMEN DE LA INSTALACIÓN
echo ============================================================================

REM Verificar objetos creados
echo 🔍 Verificando objetos creados en la base de datos...

REM Contar tablas
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='%DB_NAME%' AND table_type='BASE TABLE';"') do set TABLE_COUNT=%%i

REM Contar vistas
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.views WHERE table_schema='%DB_NAME%';"') do set VIEW_COUNT=%%i

REM Contar funciones
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema='%DB_NAME%' AND routine_type='FUNCTION';"') do set FUNCTION_COUNT=%%i

REM Contar procedimientos
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema='%DB_NAME%' AND routine_type='PROCEDURE';"') do set PROCEDURE_COUNT=%%i

REM Contar triggers
for /f %%i in ('%MYSQL_BASE% %DB_NAME% -se "SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema='%DB_NAME%';"') do set TRIGGER_COUNT=%%i

echo 📈 ESTADÍSTICAS DE LA BASE DE DATOS:
echo   • Tablas creadas: %TABLE_COUNT%
echo   • Vistas creadas: %VIEW_COUNT%  
echo   • Funciones creadas: %FUNCTION_COUNT%
echo   • Procedimientos creados: %PROCEDURE_COUNT%
echo   • Triggers creados: %TRIGGER_COUNT%

echo ============================================================================
echo 📋 RESULTADO FINAL:
echo   ✅ Operaciones exitosas: %SUCCESS_COUNT%
echo   ❌ Errores encontrados: %ERROR_COUNT%
echo   ℹ️  Modo ejecutado: %INSTALL_MODE%
echo ============================================================================

if %ERROR_COUNT% equ 0 (
    echo 🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!
    echo 📱 La base de datos '%DB_NAME%' está lista para usar
    echo 🚀 Puedes iniciar la aplicación app-presupuesto
) else (
    echo ⚠️  INSTALACIÓN COMPLETADA CON ADVERTENCIAS
    echo 🔧 Revisa los errores anteriores y ejecuta manualmente los scripts fallidos
    echo 📝 Consulta los logs para más detalles
)

echo ============================================================================
echo 💡 PRÓXIMOS PASOS:
echo   1. Verificar la configuración de conexión en la aplicación
echo   2. Crear usuarios de prueba si es necesario  
echo   3. Configurar backups automáticos
echo   4. Revisar configuraciones en la tabla 'constantes'
echo ============================================================================

echo Presiona cualquier tecla para salir...
pause > nul
exit /b %ERROR_COUNT%
