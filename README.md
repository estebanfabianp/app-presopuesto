# Sistema de Gestión de Presupuestos

Este proyecto consiste en el desarrollo de una aplicación para la **gestión de finanzas personales**.  
La aplicación permite cargar información de **extractos bancarios** y, mediante un modelo de categorización, clasificar automáticamente los movimientos financieros.  

Además, incluye un módulo visual que muestra las **deudas vigentes de tarjetas de crédito**, como avances bancarios, número de cuotas pendientes y montos por pagar.  

En futuras versiones, se espera que la aplicación sugiera **estrategias de pago** (como el método de la bola de nieve) y que compare el **presupuesto planificado** con el **gasto real por categoría**, identificando patrones de consumo. De esta forma, el usuario podrá mejorar sus hábitos financieros, cumplir con su presupuesto y fomentar el ahorro.  

El sistema implementa una **base de datos** y una **API** para la gestión de:  
- Presupuestos personales  
- Movimientos financieros  
- Préstamos  
- Tarjetas de crédito  
- Activos  

---

## 📂 Estructura del Proyecto  

- **base de datos/**: Scripts SQL para crear y poblar la base de datos.  
- **presupuesto/**: Código fuente de la API y modelos SQLAlchemy.  
- **controllers/**: Controladores para operaciones CRUD de cada entidad.  
- **models/**: Modelos SQLAlchemy para cada tabla.  
- **views/**: Vistas Flask que exponen endpoints REST.  

---

## ⚙️ Instalación  

1. Clona el repositorio.  
2. Instala las dependencias del backend (Flask, SQLAlchemy, PyMySQL, etc.):  
   ```bash
   pip install -r requirements.txt
   ```
3. Crea la base de datos ejecutando:  
   ```bash
   mysql -u usuario -p < base de datos/Create.sql
   ```
4. Inserta datos de prueba:  
   ```bash
   mysql -u usuario -p mydb < base de datos/datos_prueba.sql
   ```

---

## 🚀 Uso  

1. Ejecuta la API Flask:  
   ```bash
   flask run
   ```
2. Accede a los endpoints para realizar operaciones **CRUD** sobre personas, productos, movimientos, presupuestos, etc.  

---

## 📝 Buenas Prácticas Implementadas  

- Uso de claves primarias y foráneas para asegurar integridad referencial.  
- Tablas de catálogo en lugar de ENUMs para mayor flexibilidad.  
- Comentarios descriptivos en tablas y columnas.  
- Restricciones `CHECK` para garantizar valores válidos.  
- Relación muchos a muchos entre presupuesto y categoría.  
- Contraseñas almacenadas mediante **hash** para mayor seguridad.  

---

## 📊 Ejemplo de Consulta SQL  

```sql
-- Obtener movimientos de una persona
SELECT m.*, c.nombre AS categoria, b.nombre AS beneficiario
FROM movimiento m
JOIN categoria c ON m.id_categoria = c.id_categoria
JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
WHERE m.id_persona = 1;
```

---

## 👨‍💻 Autor

Desarrollado por Esteban Fabian Patiño Montealegre
