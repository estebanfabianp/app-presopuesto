# Arquitectura del Proyecto: Sistema de Gestión de Presupuestos

## Visión General

El sistema está diseñado como una aplicación modular para la gestión de finanzas personales, con enfoque en escalabilidad, seguridad y extensibilidad. Utiliza una arquitectura basada en API RESTful y separación clara entre backend, base de datos y lógica de negocio.

---

## Componentes Principales

### 1. Backend (Flask API)
- **Framework:** Flask
- **ORM:** SQLAlchemy
- **Conector BD:** PyMySQL
- **Gestión de migraciones:** Flask-Migrate
- **Seguridad:** bcrypt para contraseñas, validación de entradas, uso de sentencias preparadas.
- **Estructura:**  
  - `/presupuesto/controllers/`: Lógica de negocio y endpoints.
  - `/presupuesto/models/`: Modelos de datos (ORM).
  - `/presupuesto/views/`: Definición de rutas y vistas Flask.

### 2. Base de Datos (MySQL/MariaDB)
- **Scripts SQL:**  
  - Creación de tablas, llaves foráneas, vistas, funciones, procedimientos almacenados y triggers.
- **Modelo relacional:**  
  - Tablas normalizadas para personas, cuentas, movimientos, presupuestos, préstamos, tarjetas, activos, categorías, etc.
  - Uso de claves primarias y foráneas para integridad referencial.
  - Tablas de catálogo para mayor flexibilidad.
  - Restricciones y comentarios descriptivos.
  - Automatización de saldos mediante triggers y procedimientos.
  - Vistas para reportes y análisis.
  - Datos de prueba incluidos.

### 3. Lógica de Negocio
- **Controladores:** Encapsulan la lógica de operaciones CRUD y reglas de negocio.
- **Servicios:** (Futuro) Para IA, categorización automática y recomendaciones.
- **Validaciones:** Validación robusta de datos y manejo de errores.

### 4. Automatización y Seguridad
- **Procedimientos y triggers:** Automatización de tareas recurrentes (ej. recálculo de saldos, reclasificación de categorías).
- **Hash de contraseñas:** Almacenamiento seguro usando bcrypt.
- **Prevención de ataques:** Uso de sentencias preparadas y validación de entradas.

### 5. Inteligencia Artificial y Analítica (Futuro)
- **Categorización automática:** Reglas simples y modelos de machine learning (scikit-learn).
- **Análisis de datos:** Uso de pandas y matplotlib para reportes y visualizaciones.
- **Recomendaciones:** Estrategias de pago, ahorro e inversión.

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

- **Nuevos módulos:** Fácil de agregar nuevas entidades (por ejemplo, inversiones, Forex).
- **IA y analítica:** Arquitectura preparada para integrar módulos de machine learning y visualización.
- **Integración externa:** Posibilidad de conectar con APIs bancarias y servicios de terceros.

---

## Notas

- El proyecto sigue buenas prácticas de seguridad, modularidad y documentación.
- La estructura facilita el mantenimiento y la colaboración en equipo.
- Para más detalles, consulta la documentación técnica en `/documentacion/`.

---
