# Sistema de Gestión de Presupuestos

Aplicación personal de finanzas que integra inteligencia artificial para ayudarte a gestionar ingresos, gastos, deudas, inversiones y ahorro de forma inteligente y automatizada.

---

## 📖 Descripción

Este proyecto consiste en el desarrollo de una aplicación para la **gestión personal de finanzas**, centrada en facilitar el control de movimientos bancarios, presupuestos, deudas e inversiones.

**Principales funcionalidades:**
- Carga y categorización automática de transacciones bancarias (reglas e IA).
- Administración de cuentas, préstamos, tarjetas de crédito y activos financieros.
- Control de deudas y pagos recurrentes.
- Gestión de inversiones en acciones y fondos.
- Creación y seguimiento de presupuestos, con comparación de gasto real por categoría.
- Reportes visuales: flujo de caja, resumen mensual, gastos por categoría, desempeño presupuestal, informes anuales, etc.
- Estrategias de pago (ejemplo: método de la bola de nieve).
- Futuras versiones: recomendaciones personalizadas de ahorro, inversión y reducción de deuda.

---

## 🛠️ Tecnologías y dependencias

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate
- **Base de datos:** MySQL/MariaDB
- **ORM:** SQLAlchemy
- **Conector:** PyMySQL
- **Seguridad:** bcrypt
- **IA y análisis:** pandas, scikit-learn, matplotlib (para futuras versiones)
- **Entorno:** python-dotenv, venv

Ver dependencias completas en [`requirements.txt`](requirements.txt).

---

## 🗺️ Roadmap

El desarrollo del proyecto se organiza en fases:

1. **MVP:** CRUD de usuarios, cuentas, movimientos y presupuestos; reportes simples.
2. **Categorización automática:** Reglas simples y modelos de machine learning para clasificar gastos.
3. **Visualización avanzada:** Dashboards interactivos, estrategias financieras y recomendaciones.
4. **Expansión a inversiones:** Gestión de acciones, fondos y portafolios.
5. **Integración Forex y mercados:** APIs de divisas, análisis predictivo y reportes avanzados.

Más detalles en [`documentacion/roadmap.md`](documentacion/roadmap.md).

---

## 📂 Estructura del Proyecto

```
/base de datos/              — Scripts SQL (tablas, llaves foráneas, vistas, funciones, SP, jobs, datos iniciales)
├── 01_create_tables.sql
├── 02_create_foreign_keys.sql
├── 03_create_views.sql
├── 04_create_functions.sql
├── 05_create_procedures.sql
├── 06_create_jobs.sql
└── 07_insert_data.sql

/presupuesto/                — Backend (API Flask y modelos SQLAlchemy)
├── controllers/             — Lógica de negocio y endpoints
├── models/                  — Modelos de datos
├── views/                   — Rutas Flask

/documentacion/              — Documentos técnicos y sugerencias
├── roadmap.md
├── sugerencia_IA.md

requirements.txt             — Dependencias del proyecto
app-presopuesto.code‑workspace — Configuración del editor
README.md                    — Documentación principal
venv/                        — Entorno virtual (excluido de producción)
```

---

## ⚙️ Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/estebanfabianp/app-presopuesto.git
   cd app-presopuesto
   ```

2. (Opcional) Crea y activa el entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Inicializa la base de datos:

   ```bash
   mysql -u usuario -p < base\ de\ datos/01_create_tables.sql
   mysql -u usuario -p < base\ de\ datos/02_create_foreign_keys.sql
   mysql -u usuario -p < base\ de\ datos/07_insert_data.sql
   ```

5. Ejecuta la API:

   ```bash
   flask run
   ```

---

## 🚀 Uso

Accede a los endpoints para realizar operaciones como:
- Registro y consulta de transacciones
- Gestión de presupuestos y movimientos
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

---

## 📊 Ejemplo de Consulta SQL

```sql
-- Resumen de gastos por categoría para un usuario:
SELECT m.categoria, SUM(m.monto) AS total_gastado
FROM movimiento m
JOIN cuenta c ON m.cuenta_id = c.id_cuenta
WHERE c.usuario_id = 1 AND m.tipo = 'gasto'
GROUP BY m.categoria;
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
- Carpeta [`/presupuesto/`](presupuesto/): Código fuente del backend.

---

## 📚 Documentación y Sugerencias

- [Roadmap del proyecto](documentacion/roadmap.md)
- [Sugerencias de IA y mejoras](documentacion/sugerencia_IA.md)
- [Arquitectura del sistema](ARCHITECTURE.md)
- [Guía de usuario](USER_GUIDE.md)
- [Referencia de la API](API_REFERENCE.md)
- [Guía de contribución](CONTRIBUTING.md)

---

## 👨‍💻 Autor

Desarrollado por **Esteban Fabián Patiño Montealegre**

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera personal.
