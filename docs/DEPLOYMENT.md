# Guía de Despliegue

El proyecto todavía está principalmente orientado a desarrollo local, pero ya puede desplegarse en modo web Flask para pruebas internas o entornos controlados.

## Modalidades

### Escritorio Flet

Hoy se sigue ejecutando localmente con:

```powershell
python main.py
```

No hay un pipeline formal de empaquetado mantenido en esta limpieza.

### Web Flask

Se ejecuta con:

```powershell
python app.py
```

## Requisitos para despliegue web

- Python 3.10+
- MySQL/MariaDB accesible desde el host
- Variables de entorno para Flask y JWT
- Dependencias instaladas desde `requirements.txt`

## Recomendación por entorno

### Windows

Usar `waitress` como servidor WSGI.

Ejemplo:

```powershell
pip install waitress
waitress-serve --host 0.0.0.0 --port 5000 app:create_app
```

### Linux

Usar `gunicorn` detrás de `nginx`.

Ejemplo:

```bash
gunicorn "app:create_app()" --bind 0.0.0.0:5000
```

## Variables mínimas

```env
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=cambiar-en-produccion
JWT_SECRET_KEY=cambiar-en-produccion
DB_HOST=host-db
DB_PORT=3306
DB_NAME=app_presupuesto
DB_USER=usuario
DB_PASSWORD=clave
```

## Pasos recomendados

1. Instalar dependencias.
2. Verificar conectividad con la base.
3. Ejecutar `init_db.bat` o el flujo SQL equivalente.
4. Probar `GET /health`.
5. Levantar el servicio WSGI.
6. Exponerlo detrás de proxy reverso si aplica.

## Consideraciones

- No subas `.env`, `venv/` ni caches al repositorio.
- La instalación `full` de BD debe validarse antes de producción en entornos MariaDB.
- El módulo web sigue siendo una migración parcial; no todos los módulos del sistema están expuestos en HTML.
