🚀 **Roadmap del proyecto app-presopuesto**

---

🔹 **Fase 1 – MVP (Gestión básica de finanzas personales)**

**Objetivo:** Contar con una aplicación que permita registrar y consultar movimientos, presupuestos y reportes simples.

- **Backend básico:** Flask + MySQL
- **Tablas:** usuario, cuentas, movimientos, presupuestos, categorías.
- **Funcionalidad CRUD:** Para movimientos y presupuestos.
- **Integridad:** Llaves foráneas y restricciones (CHECK, NOT NULL, etc.).

**Carga manual de movimientos:**

- Registrar ingresos y gastos desde un formulario.
- Asociar cada movimiento a una cuenta y categoría.

**Reportes iniciales:**

- Listado de movimientos filtrados por fecha y categoría.
- Resumen de ingresos vs. gastos del mes.

👉 Con esto tendrás una app útil y estable.

---

🔹 **Fase 2 – Categorización automática (IA + Analítica de datos)**

**Objetivo:** Implementar inteligencia para clasificar gastos automáticamente.

- **Dataset inicial:** Cargar extractos bancarios (CSV/Excel) como datos de entrenamiento.  
  Campos: fecha, descripción, monto, categoría (asignada manualmente).

- **Categorización con reglas simples:**  
  Ejemplo: si la descripción contiene "mercado" → categoría alimentación.

- **Modelo de Machine Learning:**  
  Entrenar un modelo (Naive Bayes, SVM o modelos NLP ligeros) para categorizar movimientos según la descripción.  
  Evaluar métricas como accuracy y f1-score.

- **Analítica básica:**  
  Identificación de patrones de gasto.  
  Alertas: “Este mes tu gasto en transporte creció un 20% respecto al promedio”.

👉 Aquí aplicarás IA y analítica de datos en un caso real.

---

🔹 **Fase 3 – Optimización y visualización avanzada**

**Objetivo:** Mejorar la experiencia del usuario y entregar insights claros.

- **Dashboard interactivo:**  
  Gráficas de flujo de caja, gasto por categoría y proyección de saldo.  
  Comparación entre presupuesto y gasto real.

- **Estrategias financieras:**  
  Implementar el método de la bola de nieve para deudas.  
  Recomendaciones automáticas de ahorro (“Si reduces ocio un 10%, ahorras X en 3 meses”).

---

🔹 **Fase 4 – Expansión: inversiones (acciones y fondos)**

**Objetivo:** Ampliar el sistema más allá de los presupuestos.

- **Tablas:** acciones, fondos, portafolios, inversiones.
- **Cálculos:** rentabilidad, valor actual, ganancia/pérdida.
- **Reportes:** evolución del portafolio y diversificación.

👉 Esta fase puede esperar hasta dominar la categorización con IA.

---

🔹 **Fase 5 – Expansión: Forex y análisis de mercados**

**Objetivo:** Integrar Forex y mercados financieros al sistema.

- **Integración con APIs de Forex:** (ejemplo: exchangeratesapi.io, Alpha Vantage).
- **Registro de operaciones en divisas.**
- **Reportes:** ganancia/pérdida por tipo de cambio.
- **Análisis predictivo:** proyecciones con series temporales (ARIMA, Prophet, LSTM).

👉 Aquí aplicarás analítica avanzada y modelos de predicción.

---

📌 **Resumen**

1. Primero lo esencial: MVP con cuentas, movimientos y presupuestos.
2. Luego lo inteligente: categorización automática con IA y analítica.
3. Después lo visual y estratégico: dashboards, reportes y estrategias financieras.
4. Finalmente lo avanzado: inversiones, fondos y Forex.