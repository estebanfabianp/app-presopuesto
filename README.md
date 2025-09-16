# Sistema de Gestión Financiera Personal

Este proyecto permite gestionar cuentas, movimientos, presupuestos, préstamos, tarjetas, inversiones y activos. Incluye automatización de saldos, reportes, categorización automática, exportación de datos y análisis avanzado en Python.

## 🆕 Actualizaciones recientes

- Nuevos módulos: inversiones, activos, auditoría, notificaciones y configuración.
- Endpoints RESTful ampliados y control de acceso por roles (usuario, admin) con JWT.
- Exportación de reportes en CSV, Excel y PDF.
- Paginación y filtrado en endpoints.
- Automatización de saldos y auditoría con triggers y procedimientos SQL.
- Pruebas automáticas y documentación técnica ampliada.
- Rutas de archivos y documentación actualizadas y organizadas.
- Script de inicialización automática de base de datos.

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

### 📋 Descripción de carpetas actuales:

**📦 Código fuente (`src/`):**
- `presupuesto/`: Aplicación principal del backend
  - `excel_csv_analysis.py`: Análisis y visualización de datos CSV
  - `api/`: Endpoints y rutas de la API RESTful
  - `models/`: Modelos de datos y ORM
  - `controllers/`: Lógica de negocio y controladores
  - `services/`: Servicios auxiliares y utilidades
  - `notificaciones/`: Módulo de notificaciones
  - `auditoria/`: Sistema de auditoría y logs
  - `inversiones/`: Gestión de inversiones y activos

**🗄️ Base de datos (`base_de_datos/`):**
- `script_bd/create/`: Scripts SQL de creación de tablas, triggers, vistas y funciones
- `script_bd/comments/`: Documentación y comentarios de base de datos

**📚 Documentación (`docs/`):**
- Guías de usuario, arquitectura, API reference
- Políticas de seguridad y contribución
- FAQ y modelo de datos

**📝 Documentación técnica (`documentacion/`):**
- `roadmap.md`: Planificación del proyecto
- `sugerencia_IA.md`: Sugerencias de IA y mejoras

**💾 Datos (`data/`):**
- `db/init_db.bat`: Script de inicialización de base de datos

---

## 🗄️ Base de Datos

- Tablas principales: moneda, estado_movimiento, estado_prestamo, estado_tarjeta, persona, accion, activo, beneficiario, categoria, deuda_financiada, tipo_movimiento, cuenta, movimiento, prestamo, presupuesto, presupuesto_categoria, tarjeta_credito, transaccion_programada, prestamo_movimiento, movimiento_tarjeta, inversion.
- Llaves foráneas para integridad referencial.
- Triggers para actualización automática de saldos y auditoría de acciones.
- Procedimientos y funciones para recálculo de saldos, reclasificación de categorías y generación de reportes.
- Vistas para reportes y análisis financiero.
- Datos de prueba incluidos en scripts SQL.

---

## 📝 Funcionalidades y Procesos

- **Gestión de cuentas, movimientos, activos, tarjetas, préstamos e inversiones:** CRUD completo vía API RESTful (`/src/presupuesto/api/`).
- **Automatización de saldos y auditoría:** Triggers y procedimientos en `/base_de_datos/script_bd/create/`.
- **Categorización automática de movimientos:** Reglas y modelos IA en `/src/presupuesto/services/` y `/documentacion/sugerencia_IA.md`.
- **Exportación de reportes:** Endpoints y procesos en `/src/presupuesto/controllers/` y `/src/presupuesto/services/`.
- **Control de acceso y autenticación:** JWT y roles en `/src/presupuesto/api/usuarios/`.
- **Notificaciones y configuración personalizada:** Módulos en `/src/presupuesto/notificaciones/`.
- **Procesos automáticos:** Triggers para actualización de saldos, auditoría y notificaciones.
- **Inicialización de base de datos:** Script automatizado en `/data/db/init_db.bat`.
- **Visualización y análisis avanzado:** Script Python en `/src/presupuesto/excel_csv_analysis.py`.

---

## ⚙️ Automatización y lógica en SQL

- **Triggers:** Actualizan saldos y registran auditoría tras operaciones en movimientos, tarjetas, préstamos e inversiones.
- **Procedimientos y funciones:** Recalculo de saldos, reclasificación de categorías, generación de reportes personalizados.
- **Vistas:** Resúmenes y reportes avanzados para cuentas, movimientos, tarjetas, préstamos e inversiones.

---

## 🚀 Instalación rápida

1. Ejecuta el script de inicialización automática:
   ```bash
   data\db\init_db.bat
   ```
   
   O manualmente, crea la base de datos y ejecuta los scripts en este orden:
   ```bash
   mysql -u usuario -p < base_de_datos/script_bd/create/create_tables.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_triggers.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_views.sql
   mysql -u usuario -p < base_de_datos/script_bd/create/create_investments.sql
   ```
2. (Opcional) Agrega datos iniciales según tus necesidades.

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

- Scripts comentados y organizados por funcionalidad en `/base_de_datos/script_bd/create/`.
- Documentación técnica ampliada en `/documentacion/`.
- Archivos clave y rutas actualizadas en la sección de documentación.

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

Accede a los endpoints para operaciones como:
- Registro y consulta de transacciones (`/src/presupuesto/api/movimientos/`)
- Gestión de presupuestos, movimientos, préstamos, tarjetas e inversiones
- Visualización de reportes financieros y exportación de datos

---

## 📝 Buenas Prácticas Implementadas

- Integridad referencial y uso de catálogos.
- Automatización con triggers y procedimientos.
- Validación robusta y modularización del código.
- Control de acceso y auditoría.
- Documentación clara y actualizada.
- Procesos automáticos para saldos y auditoría.

---

## 📁 Archivos clave del proyecto

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

Este módulo permite analizar y visualizar movimientos financieros a partir de archivos CSV, realizando limpieza, agrupaciones y generación de gráficos.

## Requisitos

- Python 3.8+
- pandas
- matplotlib

Se recomienda usar un entorno virtual y un archivo `requirements.txt` para instalar dependencias:

```bash
pip install pandas matplotlib
```

## Uso

1. Coloca tu archivo `movimientos_simulados.csv` en la carpeta raíz o define la variable de entorno `PRESUPUESTO_CSV_PATH`.
2. Ejecuta el script principal:

```bash
python src/presupuesto/excel_csv_analysis.py
```

## Funcionalidades principales

- Limpieza y conversión de datos.
- Agrupaciones y resúmenes por año, mes, categoría, tipo de inversión.
- Exportación de resultados y visualizaciones automáticas.
- Modularización y manejo de errores.

## Ejemplo de gráficos generados

- Total por año, mes, categoría, tipo de inversión.
- Top 5 categorías por año.
- Evolución mensual por categoría.
- Distribución de gastos por categoría.
- Participación por categoría.
- Histograma y dispersión de montos.
- Heatmap año/mes vs categoría.

## Buenas prácticas aplicadas

- Modularización y documentación clara.
- Validación y manejo de errores.
- Guardado de resultados en archivos CSV.

## Estructura recomendada

```text
src/
    presupuesto/
        excel_csv_analysis.py
movimientos_simulados.csv
README.md
requirements.txt
```

## Personalización

Puedes modificar el script para agregar nuevas agrupaciones, gráficos o exportar resultados adicionales.

---

## 👨‍💻 Autor

Desarrollado por **Esteban Fabián Patiño Montealegre**

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera personal.