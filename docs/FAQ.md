# Preguntas Frecuentes (FAQ)

## ¿Cómo instalo el proyecto?
Sigue los pasos detallados en el [README.md](README.md) para clonar el repositorio, instalar dependencias, configurar variables de entorno y preparar la base de datos. Incluye migraciones automáticas y scripts de datos de prueba.

## ¿Qué tecnologías utiliza?
Python, Flask, SQLAlchemy, MySQL/MariaDB, PyMySQL, bcrypt, pandas, scikit-learn, JWT, Flask-Migrate, entre otras.

## ¿Puedo usar otra base de datos?
El proyecto está optimizado para MySQL/MariaDB, pero puedes adaptar los modelos para otros motores compatibles con SQLAlchemy (ej. PostgreSQL, SQLite).

## ¿Cómo reporto un bug o solicito una funcionalidad?
Abre un issue en GitHub, contacta al autor por correo o utiliza los canales de soporte definidos en la documentación.

## ¿Cómo contribuyo al proyecto?
Consulta la [guía de contribución](CONTRIBUTING.md) y sigue las recomendaciones para pull requests, pruebas y documentación.

## ¿Mis datos están seguros?
Sí, las contraseñas se almacenan con hash seguro (bcrypt), la autenticación usa JWT y se aplican buenas prácticas de seguridad y validación de entradas.

## ¿Puedo usar la app en producción?
Actualmente es un proyecto en desarrollo y aprendizaje. Úsalo bajo tu propio criterio, revisa la licencia y realiza pruebas antes de implementarlo en producción.

## ¿Dónde encuentro la documentación de la API?
En [API_REFERENCE.md](API_REFERENCE.md) y en los archivos de documentación técnica.

## ¿El sistema soporta roles y permisos?
Sí, hay control de acceso por roles (usuario, admin) y endpoints protegidos según permisos.

## ¿Se pueden exportar datos o generar reportes?
Sí, existen endpoints para reportes avanzados y exportación de datos en diferentes formatos (CSV, Excel, PDF).

## ¿Hay soporte para notificaciones y configuración de usuario?
Sí, el sistema incluye módulos para notificaciones, preferencias/configuración personalizada y auditoría de acciones.

## ¿Cómo actualizo la base de datos si hay cambios?
Utiliza los scripts de migración y sigue las instrucciones en la documentación técnica para mantener la base de datos actualizada.

---