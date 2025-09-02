import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report

# 1. Conexión a la BD
# ⚠️ Cambia usuario, password, host y base
engine = create_engine("mysql+pymysql://usuario:password@localhost/mydb")

# 2. Leer datos de la tabla movimiento (ajusta nombres de columnas si difieren)
query = """
SELECT 
    codigo AS descripcion_pago,
    c.nombre AS categoria
FROM movimiento m
JOIN categoria c ON m.id_categoria = c.id_categoria
"""
df = pd.read_sql(query, engine)

print("Muestra de datos:\n", df.head())

# 3. Preparación
X = df["descripcion_pago"]
y = df["categoria"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 4. Modelo: TF-IDF + Naive Bayes
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X_train, y_train)

# 5. Evaluación
y_pred = model.predict(X_test)
print("Precisión:", accuracy_score(y_test, y_pred))
print("\nReporte de clasificación:\n", classification_report(y_test, y_pred))

# 6. Guardar modelo
joblib.dump(model, "modelo_categorias_gastos.pkl")

# 7. Probar con un pago nuevo
nuevo_pago = ["UBER RIDES"]
pred = model.predict(nuevo_pago)
print("Categoría predicha:", pred[0])
