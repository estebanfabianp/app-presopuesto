# Guía de Usuario — Sistema de Gestión de Presupuestos

Esta guía te ayudará a comenzar a utilizar la aplicación para gestionar tus finanzas personales y familiares.

## Instalación y Primeros Pasos

Sigue los pasos de instalación descritos en el [README.md](../README.md).

## Acceso y Autenticación

- Registro y login con JWT.
- Control de acceso por roles (usuario, admin).

## Funcionalidades Principales

- Registro de movimientos en `/presupuesto/api/movimientos/`.
- Gestión de presupuestos en `/presupuesto/api/presupuestos/`.
- Control de préstamos y tarjetas en `/presupuesto/api/prestamos/` y `/presupuesto/api/tarjetas/`.
- Gestión de inversiones y activos en `/presupuesto/api/inversiones/` y `/presupuesto/api/activos/`.
- Reportes y visualización en `/presupuesto/api/reportes/`.
- Notificaciones y configuración en `/presupuesto/api/notificaciones/` y `/presupuesto/api/configuracion/`.

## Automatización e Inteligencia

- Categorización automática de movimientos (reglas e IA).
- Sugerencias y aprendizaje de hábitos.

## Seguridad

- Contraseñas seguras, cierre de sesión, actualización de dependencias.
- Consulta la [política de seguridad](SECURITY.md).

## Soporte y Documentación

- [Documentación técnica](../documentacion/roadmap.md)
- [Preguntas Frecuentes (FAQ.md)](FAQ.md)

---

¡Disfruta gestionando tus finanzas de manera inteligente!
- Gestiona activos físicos y su depreciación.

### e) Reportes y Visualización

- Accede a reportes visuales: flujo de caja, resumen mensual, gastos por categoría, desempeño del presupuesto, evolución de inversiones, etc. desde `/presupuesto/api/reportes/`.
- Exporta reportes en diferentes formatos (Excel, PDF, CSV).

### f) Notificaciones y Configuración

- Recibe notificaciones sobre vencimientos, alertas de presupuesto y recomendaciones en `/presupuesto/api/notificaciones/`.
- Personaliza tus preferencias y configuración de usuario en `/presupuesto/api/configuracion/`.

## 4. Automatización e Inteligencia

- Categorización automática de movimientos usando reglas e IA (ver `/presupuesto/services/` y [sugerencia_IA.md](../documentacion/sugerencia_IA.md)).
- Sugerencias para optimizar gastos y estrategias de pago.
- Aprendizaje de hábitos para mejorar recomendaciones.

## 5. Consejos de Seguridad

- Utiliza contraseñas seguras y no las compartas.
- Cierra sesión después de usar la aplicación en dispositivos compartidos.
- Mantén tu aplicación y dependencias actualizadas.
- Consulta la [política de seguridad](SECURITY.md) para más recomendaciones.

---

## 6. Soporte y Documentación

- Consulta la [documentación técnica](../documentacion/roadmap.md) y los archivos de referencia para detalles avanzados.
- Si tienes dudas o encuentras errores, abre un issue en el repositorio o contacta al autor.
- Revisa la sección de [Preguntas Frecuentes (FAQ.md)](FAQ.md) para resolver dudas comunes.

---

¡Disfruta gestionando tus finanzas de manera inteligente!
