# Sistema de Gestión Financiera Personal

Este proyecto facilita la gestión de cuentas, movimientos, presupuestos, préstamos, tarjetas, inversiones y activos. Incluye automatización de saldos, reportes, categorización automática, exportación de datos y análisis avanzado en Python.

## 🆕 Actualizaciones

- Nuevos módulos: inversiones, activos, auditoría, notificaciones y configuración.
- Endpoints RESTful ampliados con control de acceso por roles (usuario, admin) usando JWT.
- Exportación de reportes en CSV, Excel y PDF.
- Paginación y filtrado en endpoints.
- Automatización de saldos y auditoría con triggers y procedimientos SQL.
- Pruebas automáticas y documentación técnica ampliada.
- Script de inicialización automática de base de datos.
- **Validación de persona:** Función `persona_existe(persona_id)` para verificar la existencia antes de operar sobre préstamos.

---

## 📦 Estructura del Proyecto

```text
📁 app-presopuesto/
├── 📄 README.md 
├── 📄 requirements.txt
├── 📄 config.yaml
├── 📁 src/
│   └── 📁 presupuesto/
│       ├── 📄 excel_csv_analysis.py
│       ├── 📁 api/
│       ├── 📁 models/
│       ├── 📁 controllers/
│       ├── 📁 services/
│       ├── 📁 notificaciones/
│       ├── 📁 auditoria/
│       └── 📁 inversiones/
├── 📁 base_de_datos/
│   └── 📁 script_bd/
│       ├── 📁 create/
│       │   ├── create_tables.sql
│       │   ├── create_triggers.sql
│       │   ├── create_views.sql
│       │   ├── create_functions.sql
│       │   └── create_investments.sql
│       └── 📁 comments/
│           └── comentarios.sql
├── 📁 docs/
│   ├── 📄 USER_GUIDE.md
│   ├── 📄 SECURITY.md
│   ├── 📄 roadmap.md
│   ├── 📄 FAQ.md
│   ├── 📄 DATA_MODEL.md
│   ├── 📄 CONTRIBUTING.md
│   ├── 📄 CODE_OF_CONDUCT.md
│   ├── 📄 CHANGELOG.md
│   ├── 📄 ARCHITECTURE.md
│   └── 📄 API_REFERENCE.md
├── 📁 documentacion/
│   ├── 📄 roadmap.md
│   └── 📄 sugerencia_IA.md
└── 📁 data/
    └── 📁 db/
        └── 📄 init_db.bat
```

### 📋 Descripción de carpetas

**Código fuente (`src/`):**
- `presupuesto/`: Backend principal
  - `excel_csv_analysis.py`: Análisis y visualización de datos CSV
  - `api/`: Endpoints RESTful
  - `models/`: Modelos ORM
  - `controllers/`: Lógica de negocio
  - `services/`: Servicios auxiliares
  - `notificaciones/`: Notificaciones
  - `auditoria/`: Auditoría y logs
  - `inversiones/`: Gestión de inversiones y activos

**Base de datos (`base_de_datos/`):**
- Scripts SQL de creación, triggers, vistas y funciones
- Documentación y comentarios

**Documentación (`docs/` y `documentacion/`):**
- Guías de usuario, arquitectura, API, seguridad, contribución, FAQ y modelo de datos
- Roadmap y sugerencias IA

**Datos (`data/`):**
- Script de inicialización de base de datos

---

## 🗄️ Base de Datos

- Tablas principales: moneda, estado_movimiento, estado_prestamo, estado_tarjeta, persona, accion, activo, beneficiario, categoria, deuda_financiada, tipo_movimiento, cuenta, movimiento, prestamo, presupuesto, presupuesto_categoria, tarjeta_credito, transaccion_programada, prestamo_movimiento, movimiento_tarjeta, inversion.
- Llaves foráneas para integridad referencial.
- Triggers para actualización automática de saldos y auditoría.
- Procedimientos y funciones para recálculo de saldos y generación de reportes.
- Vistas para análisis financiero.
- Datos de prueba incluidos.

---

## 📝 Funcionalidades

- **Gestión completa:** CRUD de cuentas, movimientos, activos, tarjetas, préstamos e inversiones vía API RESTful.
- **Validación de persona:** Verificación previa en operaciones de préstamos.
- **Automatización de saldos y auditoría:** Triggers y procedimientos SQL.
- **Categorización automática:** Reglas y modelos IA.
- **Exportación de reportes:** CSV, Excel y PDF.
- **Control de acceso:** JWT y roles.
- **Notificaciones y configuración personalizada.**
- **Inicialización automática de base de datos.**
- **Análisis avanzado:** Script Python para visualización y agrupación de datos.

---

## ⚙️ Automatización SQL

- **Triggers:** Actualizan saldos y registran auditoría tras operaciones.
- **Procedimientos y funciones:** Recalculo de saldos, reclasificación de categorías, reportes personalizados.
- **Vistas:** Resúmenes y reportes avanzados.

---

## 🚀 Instalación

1. Ejecuta el script de inicialización:
   ```bash
   data\db\init_db.bat
   ```
   O manualmente:
   ```bash
   mysql -u usuario -p < base_de_datos/script_bd/create/create_tables.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_triggers.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_views.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_investments.sql
   ```
2. (Opcional) Agrega datos iniciales.

---

## 📊 Ejemplo de consulta

```sql
SELECT * FROM v_cuenta_saldos;
SELECT * FROM v_movimientos_detalle WHERE id_cuenta = 1;
SELECT * FROM v_inversion_saldos;
```

---

## 📚 Documentación

- Scripts y documentación técnica en `/base_de_datos/script_bd/create/` y `/documentacion/`.
- Guías y referencias en `/docs/`.

---

## 👨‍💻 Autor

Esteban Fabián Patiño Montealegre

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera.

```bash
flask run
```

---

## 🚀 Uso

- Registro y consulta de transacciones (`/src/presupuesto/api/movimientos/`)
- Gestión de presupuestos, movimientos, préstamos, tarjetas e inversiones
- Visualización y exportación de reportes financieros
- Validación de persona en operaciones de préstamos

---

## 📝 Buenas Prácticas

- Integridad referencial y uso de catálogos
- Automatización con triggers y procedimientos
- Validación robusta y modularización
- Control de acceso y auditoría
- Documentación clara y actualizada

---

## 📁 Archivos clave

- [`README.md`](README.md)
- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`USER_GUIDE.md`](docs/USER_GUIDE.md)
- [`API_REFERENCE.md`](docs/API_REFERENCE.md)
- [`CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- [`CHANGELOG.md`](docs/CHANGELOG.md)
- [`SECURITY.md`](docs/SECURITY.md)
- [`CODE_OF_CONDUCT.md`](docs/CODE_OF_CONDUCT.md)
- [`FAQ.md`](docs/FAQ.md)
- [`DATA_MODEL.md`](docs/DATA_MODEL.md)
- [`requirements.txt`](requirements.txt)
- [`init_db.bat`](data/db/init_db.bat)
- Carpeta [`docs/`](docs/)
- Carpeta [`documentacion/`](documentacion/)
- Carpeta [`base_de_datos/`](base_de_datos/)
- Carpeta [`presupuesto/`](presupuesto/)
- Carpeta [`data/`](data/)

## 📚 Documentación y Sugerencias

- [Roadmap](documentacion/roadmap.md)
- [Sugerencias IA](documentacion/sugerencia_IA.md)
- [Arquitectura](docs/ARCHITECTURE.md)
- [Guía de usuario](docs/USER_GUIDE.md)
- [Referencia API](docs/API_REFERENCE.md)
- [Guía de contribución](docs/CONTRIBUTING.md)
- [Registro de cambios](docs/CHANGELOG.md)
- [Política de seguridad](docs/SECURITY.md)
- [Código de conducta](docs/CODE_OF_CONDUCT.md)
- [Preguntas frecuentes](docs/FAQ.md)
- [Modelo de datos](docs/DATA_MODEL.md)
- [Script de inicialización DB](data/db/init_db.bat)

---

# Análisis y Visualización de Movimientos Financieros

Este módulo permite analizar y visualizar movimientos financieros desde archivos CSV, realizando limpieza, agrupaciones y gráficos.

## Requisitos

- Python 3.8+
- pandas
- matplotlib

Se recomienda usar un entorno virtual y un archivo `requirements.txt` para instalar dependencias:

```bash
pip install pandas matplotlib
```

## Uso

1. Coloca tu archivo `movimientos_simulados.csv` en la raíz o define la variable de entorno `PRESUPUESTO_CSV_PATH`.
2. Ejecuta:
```bash
python src/presupuesto/excel_csv_analysis.py
```

## Funcionalidades

- Limpieza y conversión de datos
- Agrupaciones y resúmenes por año, mes, categoría, tipo de inversión
- Exportación y visualización automática
- Manejo de errores

## Ejemplo de gráficos

- Totales por año, mes, categoría, tipo de inversión
- Top categorías por año
- Evolución mensual por categoría
- Distribución y participación por categoría
- Histogramas y heatmaps

## Buenas prácticas

- Modularización y documentación
- Validación y manejo de errores
- Guardado de resultados en CSV

## Personalización

Modifica el script para agregar nuevas agrupaciones, gráficos o exportar resultados adicionales.

---

## 👨‍💻 Autor

Desarrollado por **Esteban Fabián Patiño Montealegre**

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera.