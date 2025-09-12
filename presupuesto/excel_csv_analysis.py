import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo (ajusta la ruta a tu PC)
df = pd.read_csv("C:\\Users\\Asus\\Desktop\\Copia de 3322_AGO2025.csv", sep=";", encoding="latin-1")

# Limpiar columnas numéricas
for col in ["Valor Original", "Cargos y Abonos", "Saldo a Diferir"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(".", "", regex=False)   # quitar separadores de miles
        .str.replace(",", ".", regex=False)  # convertir decimales
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Agrupar por descripción y tomar top 5
gastos_por_desc = (
    df.groupby("Descripción")["Cargos y Abonos"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

# Crear gráfico
plt.figure(figsize=(8, 5))
gastos_por_desc.plot(kind="bar", color="skyblue")
plt.title("Top 5 gastos por descripción")
plt.ylabel("Valor ($)")
plt.xlabel("Descripción")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
