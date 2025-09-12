# Sistema de Gestión Financiera Personal

Este proyecto es una aplicación para la gestión de finanzas personales, permitiendo el control de cuentas, movimientos, presupuestos, préstamos, tarjetas de crédito, inversiones y más. Incluye automatización de saldos mediante triggers y procedimientos, así como vistas para reportes y análisis.

---

## 📦 Estructura del Proyecto

```
/base de datos/
  └── script_bd/
      └── create/
          ├── create_tables.sql      # Definición de tablas principales (estructura y relaciones)
          ├── create_triggers.sql    # Triggers para actualización automática de saldos
          ├── create_views.sql       # Vistas para reportes y consultas
          ├── create_functions.sql   # Funciones y procedimientos almacenados
/presupuesto/                        # Backend/API (Flask, modelos, controladores)
documentacion/                       # Documentación técnica y sugerencias
README.md                            # Este archivo
```

---

## 🗄️ Base de Datos

- **Tablas principales:** moneda, estado_movimiento, estado_prestamo, estado_tarjeta, persona, accion, activo, beneficiario, categoria, deuda_financiada, tipo_movimiento, cuenta, movimiento, prestamo, presupuesto, presupuesto_categoria, tarjeta_credito, transaccion_programada, prestamo_movimiento, movimiento_tarjeta.
- **Llaves foráneas:** Integridad referencial entre movimientos, cuentas, personas, tarjetas, préstamos, etc.
- **Triggers:** Actualización automática de saldos en cuenta, tarjeta_credito y prestamo tras operaciones en sus movimientos asociados.
- **Procedimientos y funciones:** Recalculo y reclasificación de saldos y categorías.
- **Vistas:** Resúmenes y detalles de saldos y movimientos para facilitar reportes y análisis.
- **Datos de prueba:** Incluidos en los scripts para facilitar pruebas y desarrollo.

---

## 📝 Funcionalidades implementadas

- **Gestión de cuentas y movimientos:** Registro y actualización automática de saldos.
- **Gestión de tarjetas de crédito:** Movimientos y saldo actualizado automáticamente.
- **Gestión de préstamos:** Movimientos y saldo actualizado automáticamente.
- **Catálogos:** Monedas y estados normalizados.
- **Presupuestos y categorías:** Relación y control de presupuestos por categoría.
- **Triggers y procedimientos:** Automatización de lógica de negocio en la base de datos.
- **Vistas SQL:** Consultas para reportes de saldos y movimientos detallados.
- **Funciones:** Reclasificación de categorías de movimientos por rango de fecha.

---

## ⚙️ Automatización y lógica en SQL

- **Triggers:**  
  - `tr_update_saldo_cuenta_after_insert/update/delete`  
  - `tr_update_saldo_tarjeta_after_insert/update/delete`  
  - `tr_update_saldo_prestamo_after_insert/update/delete`  
  Actualizan los saldos automáticamente tras cambios en movimientos.

- **Procedimientos y funciones:**  
  - `sp_recalcular_saldo_cuenta`
  - `sp_recalcular_saldo_tarjeta`
  - `sp_recalcular_saldo_prestamo`
  - `reclasificar_categoria_movimientos`
  Permiten recalcular manualmente los saldos y reclasificar categorías de movimientos.

- **Vistas:**  
  - `v_cuenta_saldos`: Resumen de saldos por cuenta.
  - `v_movimientos_detalle`: Detalle de movimientos con información relacionada.
  - `v_tarjeta_saldos`: Resumen de saldos de tarjetas de crédito.
  - `v_prestamo_saldos`: Resumen de préstamos y su saldo.

---

## 🚀 Instalación rápida

1. Crea la base de datos y ejecuta los scripts en este orden:
   ```bash
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_tables.sql
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_triggers.sql
   mysql -u usuario -p < base\ de\ datos\script_bd\create\create_views.sql
   ```
2. (Opcional) Agrega datos iniciales según tus necesidades (ya incluidos algunos datos de prueba).

---

## 📊 Ejemplo de consulta

```sql
-- Consulta de saldo actual de todas las cuentas:
SELECT * FROM v_cuenta_saldos;

-- Consulta de movimientos detallados:
SELECT * FROM v_movimientos_detalle WHERE id_cuenta = 1;
```

---

## 📚 Documentación adicional

- Los scripts están comentados y organizados por funcionalidad.
- Puedes modificar los triggers, procedimientos y funciones para adaptarlos a tus reglas de negocio.
- Para más detalles sobre la estructura, revisa los archivos SQL en `/base de datos/script_bd/create/`.

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
- [Registro de cambios](CHANGELOG.md)
- [Política de seguridad](SECURITY.md)
- [Código de conducta](CODE_OF_CONDUCT.md)
- [Preguntas frecuentes](FAQ.md)
- [Modelo de datos](DATA_MODEL.md)

---

## 👨‍💻 Autor

Desarrollado por **Esteban Fabián Patiño Montealegre**

---

## ℹ Acerca del proyecto

Aplicación personal basada en IA para aprender Python y mejorar la gestión financiera personal.
