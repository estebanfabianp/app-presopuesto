import pandas as pd

def cargar_excel(ruta_archivo):
    """
    Carga un archivo Excel y retorna un DataFrame de pandas.
    """
    df = pd.read_excel(ruta_archivo)
    return df

def resumen_basico(df):
    """
    Realiza un análisis básico del DataFrame:
    - Muestra las primeras filas
    - Estadísticas descriptivas
    - Tipos de datos
    """
    print("Primeras filas:")
    print(df.head())
    print("\nEstadísticas descriptivas:")
    print(df.describe(include='all'))
    print("\nTipos de datos:")
    print(df.dtypes)

def analizar_columna(df, columna):
    """
    Muestra un resumen de una columna específica.
    """
    if columna in df.columns:
        print(f"\nResumen de la columna '{columna}':")
        print(df[columna].value_counts())
        print(df[columna].describe())
    else:
        print(f"La columna '{columna}' no existe en el archivo.")

if __name__ == "__main__":
    ruta = input("Ingrese la ruta del archivo Excel: ")
    df = cargar_excel(ruta)
    resumen_basico(df)
    col = input("\nIngrese el nombre de una columna para analizar (o deje vacío para omitir): ")
    if col:
        analizar_columna(df, col)
