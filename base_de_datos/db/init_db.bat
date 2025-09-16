@echo off
REM 🚀 Script para inicializar la base de datos del proyecto app-presopuesto
REM Autor: Esteban Fabián Patiño Montealegre

set DB_USER=root
set DB_PASS=
set DB_NAME=app_presupuesto
set DB_HOST=localhost

echo ============================================
echo  📂 Iniciando configuración de la base de datos...
echo ============================================

REM Crear la base de datos si no existe
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;"

REM Ejecutar los scripts SQL en orden
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_tables.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_foreign_keys.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\comments\comentarios.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_indexes.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_views.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_functions.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_procedures.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_jobs.sql"
mysql -u %DB_USER% -p%DB_PASS% -h %DB_HOST% %DB_NAME% < "base_de_datos\script_bd\create\create_data.sql"

echo ============================================
echo  ✅ Base de datos inicializada correctamente en %DB_NAME%
echo ============================================

pause
