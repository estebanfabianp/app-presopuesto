# Arquitectura del Proyecto: Sistema de Gestión de Presupuestos

El sistema utiliza una arquitectura modular con API RESTful, backend Flask, base de datos MySQL/MariaDB y lógica de negocio separada. Está preparado para integración de IA y analítica avanzada.

## Componentes Principales

- Backend: `/presupuesto/` (Flask, SQLAlchemy, JWT, bcrypt)
- Base de datos: `/base_de_datos/script_bd/create/` (SQL, triggers, vistas, procedimientos)
- Lógica de negocio: controladores y servicios en `/presupuesto/controllers/` y `/presupuesto/services/`
- Seguridad: autenticación JWT, roles, validación robusta
- IA y analítica: `/presupuesto/excel_csv_analysis.py`, `/documentacion/sugerencia_IA.md`

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