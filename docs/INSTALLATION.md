# Guía de Instalación

Esta guía deja el proyecto listo para usar tanto en modo escritorio Flet como en modo web Flask.

## Requisitos

- Python 3.10 o superior.
- MySQL 8.0+ o MariaDB 10.6+.
- Git opcional para clonar el repositorio.
- PowerShell en Windows.

## 1. Preparar el entorno Python

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configurar la base de datos

El proyecto usa por defecto MySQL/MariaDB. El flujo recomendado es el batch oficial:

```powershell
$env:Path = "C:\xampp\mysql\bin;" + $env:Path
.\base_de_datos\db\init_db.bat
```

Comportamiento del batch:

- Crea la base `app_presupuesto` si no existe.
- Ejecuta instalación completa si la base está vacía.
- Entra en modo mantenimiento si detecta tablas existentes.
- Ejecuta la migración de contraseñas legacy a SHA-256.

## 3. Configurar variables de entorno para la versión web

La capa web usa `app.py` y un archivo `.env` local. Si ya existe, revísalo antes de arrancar.

Variables comunes:

```env
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_presupuesto
DB_USER=root
DB_PASSWORD=
```

## 4. Ejecutar la aplicación

### Modo escritorio

```powershell
python main.py
```

### Modo web

```powershell
python app.py
```

## 5. Verificación

Versión web:

```powershell
curl http://127.0.0.1:5000/health
```

Respuesta esperada:

```json
{"status":"ok","app":"presopuesto-flask"}
```

Versión escritorio:

- La ventana principal debe abrir sin errores de importación.
- Si falla el login, revisa la conectividad con la tabla `persona`.

## Problemas frecuentes de instalación

### MySQL no está en PATH

```powershell
$env:Path = "C:\xampp\mysql\bin;" + $env:Path
```

### Dependencias faltantes

```powershell
pip install -r requirements.txt
```

### Error de conexión a BD

- Verifica host, puerto, usuario y contraseña.
- Confirma que el servidor MySQL/MariaDB esté iniciado.
- Revisa `docs/DATABASE_SETUP.md` para el flujo de diagnóstico.
