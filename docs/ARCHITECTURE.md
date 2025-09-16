# Arquitectura del Proyecto: Sistema de Gestión de Presupuestos

El sistema utiliza una arquitectura modular con API RESTful, backend Flask, base de datos MySQL/MariaDB y lógica de negocio separada. Está preparado para integración de IA y analítica avanzada.

## Componentes Principales

### 1. Backend (Flask API)
- **Framework:** Flask
- **ORM:** SQLAlchemy
- **Conector BD:** PyMySQL
- **Gestión de migraciones:** Flask-Migrate
- **Seguridad:** bcrypt para contraseñas, validación de entradas, uso de sentencias preparadas, autenticación JWT.
- **Estructura:**  
  - `/src/presupuesto/api/`: Endpoints RESTful y rutas
  - `/src/presupuesto/models/`: Modelos de datos (ORM)
  - `/src/presupuesto/controllers/`: Lógica de negocio
  - `/src/presupuesto/services/`: Servicios auxiliares y utilidades
  - `/src/presupuesto/notificaciones/`: Módulo de notificaciones
  - `/src/presupuesto/auditoria/`: Logs y auditoría de acciones
  - `/src/presupuesto/inversiones/`: Gestión de inversiones y activos

### 2. Base de Datos (MySQL/MariaDB)
- **Scripts organizados:**  
  - `/base_de_datos/script_bd/create/`: Creación de estructura
  - `/base_de_datos/script_bd/comments/`: Documentación
  - `/base_de_datos/script_bd/migrations/`: Migraciones
- **Herramientas:** Scripts de inicialización en `/data/db/`

### 3. Configuración y Datos
- **Configuración por entornos:** `/config/`
- **Datos de ejemplo y exportación:** `/data/`
- **Scripts de automatización:** `/scripts/`

### 4. Testing y Calidad
- **Pruebas organizadas:** `/tests/unit/` y `/tests/integration/`
- **Datos de prueba:** `/tests/fixtures/`

## Flujo General

```
[Usuario] ⇄ [API Flask] ⇄ [Modelos SQLAlchemy] ⇄ [MySQL/MariaDB]
```

## Extensibilidad

- Fácil integración de nuevos módulos y servicios.
- Preparado para IA, analítica y APIs externas.
- Endpoints versionados y documentación actualizada.

---

## Buenas Prácticas y Notas

- El proyecto sigue buenas prácticas de seguridad, modularidad y documentación.
- La estructura facilita el mantenimiento y la colaboración en equipo.
- La API soporta paginación y filtrado en la mayoría de los listados.
- El sistema implementa control de acceso por roles (usuario, admin).
- Se recomienda el uso de entornos virtuales y archivos `.env` para variables sensibles.
- Para más detalles, consulta la documentación técnica en `/documentacion/`.

- IA y analítica: `/src/presupuesto/excel_csv_analysis.py`, `/documentacion/sugerencia_IA.md`