# 💡 Ideas para mejoras futuras y aspectos a considerar en el desarrollo

Este documento recopila ideas, sugerencias y posibles mejoras para el proyecto **app-presopuesto**.  
Se organiza por prioridad y estado de avance para facilitar el seguimiento.

---

## 🚀 Alta prioridad
- [ ] Crear un **trigger** que, al registrar un movimiento con número de cuotas mayor a 1, lo envíe a la tabla *deudas financiadas*, donde se pueda visualizar el avance de la deuda y el saldo pendiente.  
- [ ] Al agregar un movimiento, tener en cuenta el **producto asociado** para actualizar automáticamente el saldo actual.  
- [ ] Implementar un **procedimiento almacenado** para recalcular saldos cuando sea necesario ejecutarlo manualmente.  
- [ ] Investigar e implementar un mecanismo para **proteger las contraseñas** de los usuarios.  

---

## 📊 Media prioridad
- [ ] Definir y gestionar **estados** como “conciliado” y estados del producto.  
- [ ] Probar la **extensión Jupyter** en VS Code para validar modelos iniciales de categorización de gastos.  
- [ ] Generar un **modelo entidad–relación (MER)** y guardarlo como imagen dentro de la documentación.  
- [ ] Permitir que los usuarios configuren **gastos recurrentes**, con opción de añadirlos fácilmente mediante un botón.  
- [ ] Analizar la **frecuencia de gastos** para generar sugerencias automáticas de gastos recurrentes y añadirlos a la lista de pendientes.  
- [ ] Implementar comparación **presupuesto vs. gastos reales** para identificar desviaciones.  
- [ ] Permitir la creación de **presupuestos mensuales y anuales**, similar a aplicaciones de referencia.  

---

## 💡 Baja prioridad / Futuro
- [ ] Habilitar que una **categoría pueda tener subcategorías**.  
- [ ] Asociar un **beneficiario** con una categoría o subcategoría sugerida, si aplica.  
- [ ] Ofrecer diferentes formas de **visualizar la información**, adaptables según las preferencias del usuario.  
- [ ] Implementar **notificaciones de pagos programados**, para recordar vencimientos.  
- [ ] Para los pagos programados, permitir configurar un **rango de fechas** y mostrar un botón en la pantalla principal para marcar el pago como realizado.  

---

## 🤖 Ideas para IA y Analítica
- [ ] Implementar categorización automática de gastos con un modelo de **Machine Learning**.  
- [ ] Analizar patrones de gasto para generar recomendaciones personalizadas de ahorro.  
- [ ] Explorar predicciones de flujo de caja mensual usando modelos de series temporales.  

---

## 🔗 Referencias / Inspiración
- [YNAB - You Need a Budget](https://www.youneedabudget.com/)  
- [Artículo: Clasificación de transacciones bancarias con ML](https://towardsdatascience.com/)  
- [Documentación oficial de MySQL Triggers](https://dev.mysql.com/doc/refman/8.0/en/triggers.html)  

