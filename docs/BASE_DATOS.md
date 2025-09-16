# Documentación de la Base de Datos

Este documento describe la estructura, scripts y buenas prácticas para la base de datos del proyecto **app-presopuesto**.

---

## 📦 Estructura de carpetas y scripts

```text
base_de_datos/
└── script_bd/
    ├── create/
    │   ├── create_tables.sql
    │   ├── create_triggers.sql
    │   ├── create_views.sql
    │   ├── create_functions.sql
    │   ├── create_investments.sql
    │   └── create_data.sql
    └── comments/
        └── comentarios.sql
```

---

## 🗄️ Descripción de scripts principales

- **create_tables.sql**: Definición de todas las tablas principales y relaciones.
- **create_triggers.sql**: Triggers para automatización de saldos y auditoría.
- **create_views.sql**: Vistas para reportes y consultas avanzadas.
- **create_functions.sql**: Funciones y procedimientos almacenados.
- **create_investments.sql**: Tablas y lógica para inversiones y activos.
- **create_data.sql**: Datos de prueba y carga inicial.
- **comentarios.sql**: Comentarios descriptivos y documentación interna.

---

## 🚀 Inicialización rápida

Puedes inicializar la base de datos ejecutando el script batch:

```bat
data\db\init_db.bat
```

O manualmente, ejecuta los scripts en este orden:

```bash
mysql -u usuario -p < base_de_datos/script_bd/create/create_tables.sql
mysql -u usuario -p < base_de_datos/script_bd/create/create_triggers.sql
mysql -u usuario -p < base_de_datos/script_bd/create/create_views.sql
mysql -u usuario -p < base_de_datos/script_bd/create/create_functions.sql
mysql -u usuario -p < base_de_datos/script_bd/create/create_investments.sql
mysql -u usuario -p < base_de_datos/script_bd/create/create_data.sql
```

---

## 📝 Buenas prácticas

- Usa llaves foráneas para integridad referencial.
- Separa scripts por funcionalidad (tablas, triggers, vistas, funciones).
- Incluye comentarios descriptivos en los scripts.
- Mantén los scripts versionados y documentados.
- Utiliza datos de prueba para facilitar el desarrollo y testing.

---

## 📚 Referencias

- [Modelo de datos](DATA_MODEL.md)
- [Documentación técnica](../documentacion/roadmap.md)
- [Script de inicialización](../data/db/init_db.bat)

---

## 👨‍💻 Autor

Desarrollado por Esteban Fabián Patiño Montealegre

---
