# Referencia de la API — Sistema de Gestión de Presupuestos

Esta referencia describe los principales endpoints REST disponibles en la API.

## Autenticación

- `/api/login`, `/api/register`, `/api/logout`

## Usuarios

- `/api/usuarios`, `/api/usuarios/<id>`

## Cuentas

- `/api/cuentas`, `/api/cuentas/<id>`

## Movimientos

- `/api/movimientos`, `/api/movimientos/<id>`

## Presupuestos

- `/api/presupuestos`, `/api/presupuestos/<id>`

## Reportes

- `/api/reportes/resumen`, `/api/reportes/categorias`, `/api/reportes/periodos`, `/api/reportes/exportar`

## Otros recursos

- Préstamos: `/api/prestamos`
- Tarjetas: `/api/tarjetas`
- Inversiones: `/api/inversiones`
- Activos: `/api/activos`
- Notificaciones: `/api/notificaciones`
- Configuración: `/api/configuracion`
- Logs y auditoría: `/api/logs`

## Notas

- Todos los endpoints requieren autenticación JWT salvo login y registro.
- Soporte para paginación y filtrado.
- Control de acceso por roles.