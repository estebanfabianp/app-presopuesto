# Sistema de Gestión de Presupuestos

Este proyecto implementa una base de datos y una API para la gestión de presupuestos personales, movimientos financieros, préstamos, tarjetas de crédito y activos.

## Estructura del Proyecto

- **base de datos/**: Scripts SQL para crear y poblar la base de datos.
- **presupuesto/**: Código fuente de la API y modelos SQLAlchemy.
- **controllers/**: Controladores para operaciones CRUD de cada entidad.
- **models/**: Modelos SQLAlchemy para cada tabla.
- **views/**: Vistas Flask para exponer endpoints REST.

## Instalación

1. Clona el repositorio.
2. Instala las dependencias del backend (por ejemplo, Flask, SQLAlchemy, pymysql).
   ```
   pip install -r requirements.txt
   ```
3. Crea la base de datos ejecutando el script:
   ```
   mysql -u usuario -p < base de datos/Create.sql
   ```
4. Inserta datos de prueba:
   ```
   mysql -u usuario -p mydb < base de datos/datos_prueba.sql
   ```

## Uso

- Ejecuta la API Flask:
  ```
  flask run
  ```
- Accede a los endpoints para realizar operaciones CRUD sobre personas, productos, movimientos, presupuestos, etc.

## Buenas Prácticas

- Uso de claves primarias y foráneas para integridad referencial.
- Tablas catálogo en vez de ENUMs para flexibilidad.
- Comentarios descriptivos en tablas y columnas.
- Restricciones `CHECK` para asegurar valores válidos.
- Relación muchos a muchos entre presupuesto y categoría.
- Contraseñas almacenadas como hash.

## Ejemplo de Consulta SQL

```sql
-- Obtener movimientos de una persona
SELECT m.*, c.nombre AS categoria, b.nombre AS beneficiario
FROM movimiento m
JOIN categoria c ON m.id_categoria = c.id_categoria
JOIN beneficiario b ON m.id_beneficiario = b.id_beneficiario
WHERE m.id_persona = 1;
```

## Autor

Desarrollado por [Tu Nombre].
