# Arquitectura del sistema

El proyecto está estructurado como una aplicación financiera web basada en Flask, con MySQL/MariaDB como sistema de persistencia y plantillas Jinja2 para la capa de presentación. El foco de desarrollo actual es la versión web, aunque sigue existiendo una capa desktop legacy basada en Flet.

## Vista general

```text
Cliente web (Navegador)
        |
        v
Flask + Jinja2
        |
        +--> src/routes/      -> endpoints y páginas
        +--> src/templates/   -> UI web
        +--> src/static/      -> CSS/JS
        |
        v
Servicios y lógica de negocio
        |
        +--> src/business/services/
        +--> src/models/
        +--> src/controllers/ (legacy)
        |
        v
MySQL / MariaDB
        |
        +--> base_de_datos/db/
        +--> scripts/migrations/
```

## Capas principales

### 1. Capa de presentación

- `app.py`: punto de entrada principal de la web.
- `src/routes/`: blueprints Flask con la lógica de endpoints y vistas.
- `src/templates/`: templates Jinja2 de la aplicación web.
- `src/static/`: estilos, scripts y recursos frontend.
- `main.py` y `src/views/`: capa heredada para la versión desktop.

### 2. Capa de lógica de negocio

- `src/business/services/`: servicios de negocio, ETL, análisis y automatización.
- `src/models/`: entidades del dominio y lógica asociada.
- `src/controllers/`: código heredado utilizado principalmente por Flet.

### 3. Capa de persistencia

- Conector de base de datos centralizado en la carpeta `src/database/`.
- Scripts SQL y mantenimiento en `base_de_datos/db/`.
- Migraciones específicas en `scripts/migrations/`.

## Módulos principales

### Autenticación

- `src/routes/auth.py`
- Usuario autenticado mediante JWT.
- Maneja login, sesión, perfil y validación de accesos.

### Dashboard y KPIs

- `src/routes/dashboard.py`
- Resumen financiero general y consolidado.
- Indicadores de patrimonio, flujo del mes, cuentas y productos.

### Cuentas y movimientos

- `src/routes/cuentas_bancarias.py`
- `src/routes/transacciones.py`
- Registro y clasificación de movimientos bancarios y transacciones.

### Tarjetas de crédito y diferidos

- `src/routes/tarjetas.py`
- Administración de tarjetas, cuotas, pagos y extractos.
- Soporta flujo de compras diferidas y cálculo asociado.

### Presupuesto y categorías

- `src/routes/presupuesto.py`
- `src/routes/categorias.py`
- Manejo del catálogo de categorías y presupuestos por concepto.

### Análisis y reportes

- `src/routes/analisis.py`
- `src/routes/reportes.py`
- Visualización de consumo, tendencias, comparativas y KPIs de operación.

### Optimización de clasificación

- `src/routes/optimizacion_categorias.py`
- `src/business/services/optimizacion_categorias.py`
- Motor para detectar conceptos repetidos, generar reglas y aplicar clasificación automática.
- La lógica soporta origen de movimiento en cuenta o tarjeta.

### ETL y carga masiva

- `src/business/services/etl_tarjeta_credito.py`
- `src/business/services/etl_cuenta_bancaria.py`
- Procesamiento de datos importados desde archivos o extractos.

## Principios de diseño

- La base de datos es la fuente de verdad del sistema.
- La capa web es la interfaz principal y preferida del producto.
- Flet queda como una compatibilidad heredada, pero no como eje de desarrollo.
- La autenticación y los permisos se gestionan con JWT y validación por persona.
- Los servicios business encapsulan la lógica no trivial y evitan acoplar la UI con la BD.

## Flujo de ejecución típico

```text
usuario -> login -> dashboard -> cuentas/movimientos -> presupuestos -> reportes -> análisis
                               \-> tarjetas
                               \-> optimizacion_categorias
```

## Consideraciones operativas

### MySQL/MariaDB

- El proyecto asume una instancia local o remota de MySQL/MariaDB.
- Los scripts de base de datos y migración deben ejecutarse en el orden correcto.
- La estructura de tablas y relaciones es crítica para la operación del sistema.

### ETL y reloader

Durante carga automática de archivos Excel o procesos ETL, debe evitarse reinicios innecesarios del servidor. Para ello se recomienda usar:

```powershell
python app.py
```

con `use_reloader=False` cuando se usa desarrollo con archivos pesados o imports de librerías que disparan watchers.

### Modo de mantenimiento

Algunos scripts de inicialización revisan si la base ya existe para entrar en mantenimiento y no recrear objetos de forma destructiva.

## Limitaciones actuales

- Parte del proyecto sigue basado en código heredado de Flet y de estructuras antiguas.
- La documentación debe mantenerse alineada con la realidad de modelos y migraciones.
- No todos los scripts de inicialización son totalmente idempotentes en entornos distintos.

## Conclusión

La arquitectura del proyecto está pensada para ser una solución financiera personal con enfoque operativo y analítico. La combinación de Flask, templates, servicios de negocio y base de datos relacional permite un flujo claro desde la captura de datos hasta la clasificación, el análisis y la toma de decisiones.
