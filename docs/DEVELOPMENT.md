# Guía de Desarrollo

Esta guía resume cómo trabajar en el repositorio sin mezclar la capa heredada Flet con la nueva capa web y sin ensuciar el proyecto con artefactos locales.

## Preparación local

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Flujos de arranque

### Escritorio Flet

```powershell
python main.py
```

### Web Flask

```powershell
python app.py
```

## Organización del código

- `src/views/`: vistas Flet heredadas.
- `src/routes/`: endpoints y rutas web Flask.
- `src/templates/`: vistas HTML.
- `src/static/`: JS y CSS de la versión web.
- `src/models/` y `src/database/`: lógica de acceso a datos compartida.
- `docs/status/`: resúmenes técnicos e informes de cierre.
- `tests/manual/`: pruebas exploratorias/manuales (incluye scripts Python y JS).

## Reglas prácticas

- Mantén cambios de Flet y Flask separados por archivo cuando sea posible.
- Mantén limpia la raíz del proyecto: evita dejar `.md` y `test_*` fuera de `docs/` y `tests/`.
- No agregues archivos generados al repositorio: `__pycache__`, logs, salidas debug, entornos virtuales.
- Si modificas el esquema o el flujo de inicialización, actualiza `docs/DATABASE_SETUP.md`.
- Si agregas endpoints web, actualiza `docs/API_REFERENCE.md`.
- Si cambias el flujo del usuario, actualiza `docs/USER_GUIDE.md`.

## Validación recomendada

### Verificar errores del archivo editado

Usa la integración del editor para revisar errores Python y de imports.

### Ejecutar pruebas relevantes

```powershell
pytest tests -q
```

Si vas a trabajar el ETL o pruebas manuales:

```powershell
pytest tests/manual -q
```

## Datos y base de datos

- El proyecto está pensado para MySQL/MariaDB real, no para SQLite.
- El batch `base_de_datos/db/init_db.bat` es el punto oficial de inicialización.
- Sobre una base existente, el batch entra en modo `maintenance`.

## Limpieza mínima antes de entregar cambios

- Elimina scripts de depuración temporales creados para un bug puntual.
- No dejes archivos de salida como `debug_output.txt`.
- Si generaste caches locales, bórralos antes de cerrar el trabajo.
