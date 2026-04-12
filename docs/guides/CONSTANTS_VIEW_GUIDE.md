# Constantes del Sistema - Guía de Vista

## Archivo principal

```text
src/views/constante.py
```

## Alcance

La vista permite gestionar constantes globales del sistema desde la interfaz Flet.

## Capacidades

- carga de datos desde base de datos,
- filtrado por texto y categoría,
- validación por tipo,
- edición en formularios de la propia vista,
- creación de nuevas constantes,
- eliminación lógica.

## Consideraciones de mantenimiento

- la vista contiene bastante lógica UI y conviene mantenerla separada de cambios web,
- cualquier ajuste al tipo de dato debe respetar el formato esperado por la base,
- si se añaden nuevos tipos, deben actualizarse validación, renderizado y persistencia.

## Uso esperado

1. abrir la vista de constantes,
2. buscar o filtrar,
3. editar o crear,
4. refrescar para confirmar persistencia.
