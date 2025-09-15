# Arquitectura del Proyecto: Sistema de Gestión de Presupuestos

## Visión General

El sistema está diseñado como una aplicación modular para la gestión de finanzas personales y familiares, priorizando escalabilidad, seguridad, extensibilidad y facilidad de integración. Utiliza una arquitectura basada en API RESTful, separación clara entre backend, base de datos y lógica de negocio, y está preparado para futuras integraciones de inteligencia artificial y analítica avanzada.

---

## Componentes Principales

### 1. Backend (Flask API)
- **Framework:** Flask
- **ORM:** SQLAlchemy
- **Conector BD:** PyMySQL
- **Gestión de migraciones:** Flask-Migrate
- **Seguridad:** bcrypt para contraseñas, validación de entradas, uso de sentencias preparadas, autenticación JWT.
- **Estructura:**  
  - `/presupuesto/controllers/`: Lógica de negocio y endpoints.
  - `/presupuesto/models/`: Modelos de datos (ORM).
  - `/presupuesto/views/`: Definición de rutas y vistas Flask.
  - `/presupuesto/services/`: Servicios auxiliares y utilidades.
  - `/presupuesto/api/`: Endpoints RESTful.
  - `/presupuesto/notificaciones/`: Módulo de notificaciones.
  - `/presupuesto/auditoria/`: Logs y auditoría de acciones.
  - `/presupuesto/inversiones/`: Gestión de inversiones y activos.
- **Características adicionales:**
  - Soporte para paginación y filtrado en endpoints de listados.
  - Control de acceso por roles (usuario, admin).
  - Gestión de sesiones y cierre de sesión (`/api/logout`).
  - Endpoints versionados para facilitar futuras actualizaciones.
  - Documentación de endpoints y parámetros en archivos `.md`.

### 2. Base de Datos (MySQL/MariaDB)
- **Scripts SQL:**  
  - Creación de tablas, llaves foráneas, vistas, funciones, procedimientos almacenados y triggers.
- **Modelo relacional:**  
  - Tablas normalizadas para personas, cuentas, movimientos, presupuestos, préstamos, tarjetas, activos, categorías, notificaciones, configuración de usuario, etc.
  - Uso de claves primarias y foráneas para integridad referencial.
  - Tablas de catálogo para mayor flexibilidad.
  - Restricciones y comentarios descriptivos.
  - Automatización de saldos mediante triggers y procedimientos.
  - Vistas para reportes y análisis.
  - Datos de prueba incluidos.
  - Soporte para auditoría de cambios y logs de actividad.

### 3. Lógica de Negocio
- **Controladores:** Encapsulan la lógica de operaciones CRUD y reglas de negocio.
- **Servicios:** Para tareas auxiliares, integración con IA, categorización automática y recomendaciones.
- **Validaciones:** Validación robusta de datos y manejo de errores.
- **Manejo de excepciones:** Respuestas estandarizadas para errores de negocio y validación.

### 4. Automatización y Seguridad
- **Procedimientos y triggers:** Automatización de tareas recurrentes (ej. recálculo de saldos, reclasificación de categorías).
- **Hash de contraseñas:** Almacenamiento seguro usando bcrypt.
- **Prevención de ataques:** Uso de sentencias preparadas y validación de entradas.
- **Autenticación:** Implementación de JWT para proteger los endpoints.
- **Control de acceso:** Roles y permisos definidos en base de datos y backend.

### 5. Inteligencia Artificial y Analítica (Futuro)
- **Categorización automática:** Reglas simples y modelos de machine learning (scikit-learn).
- **Análisis de datos:** Uso de pandas y matplotlib para reportes y visualizaciones.
- **Recomendaciones:** Estrategias de pago, ahorro e inversión.
- **Alertas inteligentes:** Notificaciones automáticas basadas en patrones de gasto.

---

## Flujo General

1. **Usuario** interactúa con la API (por ejemplo, desde una app web o móvil).
2. **API Flask** recibe la solicitud, valida los datos y delega la lógica al controlador correspondiente.
3. **Controlador** procesa la lógica de negocio y accede a los modelos para interactuar con la base de datos.
4. **Modelos SQLAlchemy** traducen las operaciones a consultas SQL seguras.
5. **Base de datos** almacena y recupera la información solicitada.
6. **API** responde al usuario con los datos o el resultado de la operación.

---

## Diagrama Simplificado

```
[Usuario] ⇄ [API Flask (views/controllers)] ⇄ [Modelos SQLAlchemy] ⇄ [MySQL/MariaDB]
```

---

## Extensibilidad

- **Nuevos módulos:** Fácil de agregar nuevas entidades (por ejemplo, inversiones, notificaciones, configuración de usuario, auditoría).
- **IA y analítica:** Arquitectura preparada para integrar módulos de machine learning y visualización.
- **Integración externa:** Posibilidad de conectar con APIs bancarias y servicios de terceros.
- **Soporte para nuevas versiones:** Endpoints versionados y documentación actualizada.
- **Internacionalización:** Preparado para soportar múltiples idiomas en el futuro.

---

## Buenas Prácticas y Notas

- El proyecto sigue buenas prácticas de seguridad, modularidad y documentación.
- La estructura facilita el mantenimiento y la colaboración en equipo.
- La API soporta paginación y filtrado en la mayoría de los listados.
- El sistema implementa control de acceso por roles (usuario, admin).
- Se recomienda el uso de entornos virtuales y archivos `.env` para variables sensibles.
- Para más detalles, consulta la documentación técnica en `/documentacion/`.

---