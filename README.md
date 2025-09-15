# Sistema de Gestión Financiera Personal

Este proyecto es una aplicación integral para la gestión de finanzas personales, permitiendo el control de cuentas, movimientos, presupuestos, préstamos, tarjetas de crédito, inversiones y más. Incluye automatización de saldos mediante triggers y procedimientos, vistas para reportes y análisis, y un módulo avanzado de análisis y visualización de movimientos financieros en Python.

## 🆕 Actualizaciones recientes

- Nuevas tablas y relaciones para inversiones y activos.
- Endpoints RESTful ampliados para gestión de presupuestos, préstamos, tarjetas, inversiones y activos.
- Scripts SQL actualizados con triggers y procedimientos mejorados.
- Módulo Python para análisis financiero con nuevas funciones de agrupación y visualización.
- Documentación técnica ampliada en `/documentacion/`.
- Ejemplos de uso y consultas SQL actualizados.
- Control de acceso por roles y auditoría de acciones.
- Notificaciones y configuración de usuario.
- Exportación de reportes y datos en diferentes formatos.

---

## 📦 Estructura del Proyecto

```text
/base_de_datos/
  └── script_bd/
      └── create/
          ├── create_tables.sql         # Definición de tablas principales (estructura y relaciones)
          ├── create_triggers.sql       # Triggers para actualización automática de saldos
          ├── create_views.sql          # Vistas para reportes y consultas
          ├── create_functions.sql      # Funciones y procedimientos almacenados
          ├── create_investments.sql    # Tablas y lógica para inversiones
/presupuesto/                           # Backend y análisis Python
    ├── excel_csv_analysis.py           # Análisis y visualización de movimientos financieros
    ├── api/                            # Endpoints RESTful
    ├── models/                         # Modelos de datos (ORM)
    ├── controllers/                    # Lógica de negocio
    ├── services/                       # Servicios auxiliares y utilidades
    ├── notificaciones/                 # Módulo de notificaciones
    ├── auditoria/                      # Logs y auditoría de acciones
    ├── inversiones/                    # Gestión de inversiones y activos
/documentacion/                         # Documentación técnica y sugerencias
    ├── roadmap.md
    ├── sugerencia_IA.md
    ├── ...otros archivos...
/docs/                                  # Documentos de referencia y guías
    ├── README.md
    ├── ARCHITECTURE.md
    ├── USER_GUIDE.md
    ├── API_REFERENCE.md
    ├── DATA_MODEL.md
    ├── CHANGELOG.md
    ├── SECURITY.md
    ├── CODE_OF_CONDUCT.md
    ├── FAQ.md
requirements.txt                        # Dependencias del proyecto
config.yaml                             # Configuración general y parámetros
```

---

## 🗄️ Base de Datos

- **Tablas principales:** moneda, estado_movimiento, estado_prestamo, estado_tarjeta, persona, accion, activo, beneficiario, categoria, deuda_financiada, tipo_movimiento, cuenta, movimiento, prestamo, presupuesto, presupuesto_categoria, tarjeta_credito, transaccion_programada, prestamo_movimiento, movimiento_tarjeta, **inversion** (nuevo).
- **Llaves foráneas:** Integridad referencial entre movimientos, cuentas, personas, tarjetas, préstamos, inversiones, etc.
- **Triggers:** Actualización automática de saldos en cuenta, tarjeta_credito, prestamo e inversión tras operaciones en sus movimientos asociados.
- **Procedimientos y funciones:** Recalculo y reclasificación de saldos y categorías.
- **Vistas:** Resúmenes y detalles de saldos y movimientos para facilitar reportes y análisis.
- **Datos de prueba:** Incluidos en los scripts para facilitar pruebas y desarrollo.

---

## 📝 Funcionalidades implementadas

- **Gestión de cuentas, movimientos y activos:** Registro y actualización automática de saldos.
- **Gestión de tarjetas de crédito y préstamos:** Movimientos y saldo actualizado automáticamente.
- **Gestión de inversiones:** Registro y seguimiento de activos e inversiones.
- **Catálogos:** Monedas y estados normalizados.
- **Presupuestos y categorías:** Relación y control de presupuestos por categoría.
- **Triggers y procedimientos:** Automatización de lógica de negocio en la base de datos.
- **Vistas SQL:** Consultas para reportes de saldos y movimientos detallados.
- **Funciones:** Reclasificación de categorías de movimientos por rango de fecha.
- **Módulo de análisis en Python:** Limpieza, agrupación y visualización de movimientos financieros.
- **API RESTful:** Endpoints para operaciones CRUD sobre cuentas, movimientos, presupuestos, préstamos, tarjetas e inversiones.

---

## ⚙️ Automatización y lógica en SQL

- **Triggers:**  
  - `tr_update_saldo_cuenta_after_insert/update/delete`  
  - `tr_update_saldo_tarjeta_after_insert/update/delete`  
  - `tr_update_saldo_prestamo_after_insert/update/delete`  
  - `tr_update_saldo_inversion_after_insert/update/delete` (nuevo)  
  Actualizan los saldos automáticamente tras cambios en movimientos.

- **Procedimientos y funciones:**  
  - `sp_recalcular_saldo_cuenta`
  - `sp_recalcular_saldo_tarjeta`
  - `sp_recalcular_saldo_prestamo`
  - `sp_recalcular_saldo_inversion` (nuevo)
  - `reclasificar_categoria_movimientos`
  Permiten recalcular manualmente los saldos y reclasificar categorías de movimientos.

- **Vistas:**  
  - `v_cuenta_saldos`: Resumen de saldos por cuenta.
  - `v_movimientos_detalle`: Detalle de movimientos con información relacionada.
  - `v_tarjeta_saldos`: Resumen de saldos de tarjetas de crédito.
  - `v_prestamo_saldos`: Resumen de préstamos y su saldo.
  - `v_inversion_saldos`: Resumen de inversiones y su saldo (nuevo).

---

## 🚀 Instalación rápida

1. Crea la base de datos y ejecuta los scripts en este orden:
   ```bash
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_tables.sql
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_triggers.sql
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_views.sql
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_investments.sql
   ```
2. (Opcional) Agrega datos iniciales según tus necesidades (ya incluidos algunos datos de prueba).

---

## 📊 Ejemplo de consulta

```sql
-- Consulta de saldo actual de todas las cuentas:
SELECT * FROM v_cuenta_saldos;

-- Consulta de movimientos detallados:
SELECT * FROM v_movimientos_detalle WHERE id_cuenta = 1;

-- Consulta de saldo de inversiones:
SELECT * FROM v_inversion_saldos;
```

---

## 📚 Documentación adicional

- Los scripts están comentados y organizados por funcionalidad.
- Puedes modificar los triggers, procedimientos y funciones para adaptarlos a tus reglas de negocio.
- Para más detalles sobre la estructura, revisa los archivos SQL en `/base de datos/script_bd/create/`.
- Documentación técnica ampliada en `/documentacion/`.

---

## 👨‍💻 Autor

Desarrollado por Esteban Fabián Patiño Montealegre

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera personal.

```bash
flask run
```

---

## 🚀 Uso

Accede a los endpoints para realizar operaciones como:
- Registro y consulta de transacciones
- Gestión de presupuestos, movimientos, préstamos, tarjetas e inversiones
- Visualización de resúmenes y reportes financieros

---

## 📝 Buenas Prácticas Implementadas

- Integridad referencial con claves primarias y foráneas.
- Tablas de catálogo en lugar de ENUMs para mayor flexibilidad.
- Comentarios descriptivos en tablas y columnas.
- Restricciones `CHECK` para asegurar datos válidos.
- Contraseñas almacenadas de forma segura (hash + salt).
- Automatización con procedimientos y jobs (event scheduler de MySQL).
- Separación de lógica de negocio, modelos y vistas en el backend.
- Uso de sentencias preparadas para prevenir inyección SQL.
- Validación robusta de entradas de usuario.
- Modularización y documentación clara en el código Python.

---

## 📊 Ejemplo de Consulta SQL

```sql
-- Resumen de gastos por categoría para un usuario:
SELECT m.categoria, SUM(m.monto) AS total_gastado
FROM movimiento m
JOIN cuenta c ON m.cuenta_id = c.id_cuenta
WHERE c.usuario_id = 1 AND m.tipo = 'gasto'
GROUP BY m.categoria;

-- Resumen de inversiones por tipo:
SELECT tipo_inversion, SUM(monto) AS total_invertido
FROM inversion
GROUP BY tipo_inversion;
```

---

## 📁 Archivos clave del proyecto

- [`README.md`](README.md): Introducción y guía general del proyecto.
- [`ARCHITECTURE.md`](ARCHITECTURE.md): Arquitectura y componentes principales.
- [`USER_GUIDE.md`](USER_GUIDE.md): Guía de usuario paso a paso.
- [`API_REFERENCE.md`](API_REFERENCE.md): Referencia de los endpoints de la API.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): Cómo contribuir al proyecto.
- [`CHANGELOG.md`](CHANGELOG.md): Registro de cambios y versiones.
- [`SECURITY.md`](SECURITY.md): Políticas y recomendaciones de seguridad.
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md): Código de conducta para la comunidad.
- [`FAQ.md`](FAQ.md): Preguntas frecuentes.
- [`DATA_MODEL.md`](DATA_MODEL.md): Modelo de datos y relaciones.
- [`requirements.txt`](requirements.txt): Dependencias del proyecto.
- Carpeta [`/documentacion/`](documentacion/): Roadmap, sugerencias y documentación técnica.
- Carpeta [`/base de datos/`](base%20de%20datos/): Scripts SQL para la base de datos.
- Carpeta [`/presupuesto/`](presupuesto/): Código fuente del backend y análisis Python.

---

## 📚 Documentación y Sugerencias

- [Roadmap del proyecto](documentacion/roadmap.md)
- [Sugerencias de IA y mejoras](documentacion/sugerencia_IA.md)
- [Arquitectura del sistema](ARCHITECTURE.md)
- [Guía de usuario](USER_GUIDE.md)
- [Referencia de la API](API_REFERENCE.md)
- [Guía de contribución](CONTRIBUTING.md)
- [Registro de cambios](CHANGELOG.md)
- [Política de seguridad](SECURITY.md)
- [Código de conducta](CODE_OF_CONDUCT.md)
- [Preguntas frecuentes](FAQ.md)
- [Modelo de datos](DATA_MODEL.md)

---

# Análisis y Visualización de Movimientos Financieros

Este módulo permite analizar y visualizar movimientos financieros a partir de un archivo CSV, realizando limpieza de datos, agrupaciones y generación de gráficos para el análisis de gastos e inversiones.

## Requisitos

- Python 3.8+
- pandas
- matplotlib

Se recomienda usar un entorno virtual y un archivo `requirements.txt` para instalar dependencias:

```bash
pip install pandas matplotlib
```

## Uso

1. Coloca tu archivo `movimientos_simulados.csv` en la carpeta raíz del proyecto o define la variable de entorno `PRESUPUESTO_CSV_PATH` con la ruta al archivo.
2. Ejecuta el script principal:

```bash
python presupuesto/excel_csv_analysis.py
```

## Funcionalidades principales

- Limpieza de caracteres especiales en columnas y datos.
- Conversión y limpieza de columnas numéricas.
- Conversión de fechas y creación de columnas auxiliares (año, mes, trimestre, día de la semana, día del mes).
- Agrupaciones y resúmenes por:
  - Año, mes, trimestre, día de la semana, día del mes.
  - Categoría (descripción).
  - Tipo de inversión (nuevo).
  - Combinaciones de las anteriores.
- Cálculo de totales, promedios, máximos, mínimos, conteos, desviaciones estándar, medianas y porcentajes.
- Resultados exportables a CSV.
- Visualizaciones automáticas:
  - Barras, barras apiladas, líneas, boxplot, pie chart, histograma, dispersión, heatmap.
- Modularización del código en funciones.
- Uso de logging para mensajes informativos.
- Manejo de errores en la carga y procesamiento de datos.
- Uso de rutas relativas o variables de entorno.
- Guardado de resultados en archivos CSV.

## Ejemplo de gráficos generados

- Total por año, mes, categoría, tipo de inversión.
- Top 5 categorías por año.
- Evolución mensual por categoría.
- Distribución de gastos por categoría (boxplot).
- Participación por categoría (pie chart).
- Histograma de montos de gastos.
- Dispersión entre valor original y cargos/abonos.
- Heatmap año/mes vs categoría.

## Buenas prácticas aplicadas

- Modularización del código en funciones.
- Uso de logging en vez de print.
- Manejo de errores en la carga y procesamiento de datos.
- Uso de rutas relativas o variables de entorno.
- Guardado de resultados en archivos CSV.
- Documentación clara en el código.
- Corrección de nombres de columnas inconsistentes.
- Separación de lógica de limpieza, análisis y visualización.

## Estructura recomendada

```text
presupuesto/
    excel_csv_analysis.py
movimientos_simulados.csv
README.md
requirements.txt
```

## Personalización

Puedes modificar el script para agregar nuevas agrupaciones, cambiar los gráficos o exportar resultados adicionales según tus necesidades.

---

## 👨‍💻 Autor

Desarrollado por **Esteban Fabián Patiño Montealegre**

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera personal.