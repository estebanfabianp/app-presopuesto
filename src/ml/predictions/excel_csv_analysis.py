import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

# ---------------------------------------------------------------------------
# Script de análisis y visualización de movimientos financieros desde un archivo CSV.
# Realiza limpieza de datos, agrupaciones y genera gráficos para el análisis de gastos.
# ---------------------------------------------------------------------------

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Definir ruta del archivo de datos (usar variable de entorno o ruta relativa)
DATA_PATH = os.getenv(
    "PRESUPUESTO_CSV_PATH",
    os.path.join(os.path.dirname(__file__), "..", "movimientos_simulados.csv")
)

# Función para cargar datos
def cargar_datos(path):
    try:
        df = pd.read_csv(path, sep=";", encoding="latin-1")
        logging.info("Archivo cargado correctamente.")
        return df
    except Exception as e:
        logging.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

# Función para limpiar nombres de columnas y corregir errores de digitación
def limpiar_columnas(df):
    df.columns = df.columns.str.replace(
        r'[^A-Za-z0-9 áéíóúÁÉÍÓÚñÑ/]', '', regex=True
    ).str.strip()
    df = df.rename(columns={
        'Descripcin': 'Descripción',
        'Fecha de Transaccin': 'Fecha de Transacción'
    })
    return df

# Función para limpiar strings en todo el DataFrame
def limpiar_strings(df):
    return df.applymap(
        lambda x: x if not isinstance(x, str)
        else pd.Series(x).str.replace(
            r'[^A-Za-z0-9 áéíóúÁÉÍÓÚñÑ/]', '', regex=True
        ).iloc[0]
    )

# Función para limpiar columnas numéricas
def limpiar_numericos(df, cols):
    for col in cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# Función para graficar barras
def plot_bar(df, x, y, title, xlabel='', ylabel='', rotation=0):
    plt.figure(figsize=(8, 5))
    df.plot(x=x, y=y, kind='bar', legend=False)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right")
    plt.tight_layout()
    plt.show()

# Función para guardar resultados en CSV
def guardar_csv(df, nombre):
    out_path = os.path.join(os.path.dirname(__file__), f"{nombre}.csv")
    df.to_csv(out_path, index=False)
    logging.info(f"Archivo guardado: {out_path}")

# -------------------- PROCESAMIENTO --------------------

df = cargar_datos(DATA_PATH)
if df.empty:
    exit(1)

df = limpiar_columnas(df)
df = limpiar_strings(df)
df = limpiar_numericos(df, ["Valor Original", "Cargos y Abonos", "Saldo a Diferir"])

# Mostrar nombres de columnas para referencia
logging.info(f"Columnas: {list(df.columns)}")

# Convertir la columna de fecha a tipo datetime
df['Fecha de Transacción'] = pd.to_datetime(df['Fecha de Transacción'], errors='coerce')

# Crear columnas de año, mes, trimestre, día de la semana y día del mes
df['Año'] = df['Fecha de Transacción'].dt.year
df['Mes'] = df['Fecha de Transacción'].dt.month
df['Trimestre'] = df['Fecha de Transacción'].dt.to_period('Q')
df['DiaSemana'] = df['Fecha de Transacción'].dt.day_name()
df['DiaMes'] = df['Fecha de Transacción'].dt.day

# -------------------- AGRUPACIONES Y VISUALIZACIONES --------------------

# Ejemplo modularizado: Total por año
gastos_por_ano = df.groupby('Año')['Cargos y Abonos'].sum().reset_index()
logging.info("Gastos por año:")
print(gastos_por_ano)
plot_bar(gastos_por_ano, x='Año', y='Cargos y Abonos', title='Total por Año', ylabel='Total')

# Guardar resultados
guardar_csv(gastos_por_ano, "gastos_por_ano")

# %%
gastos_por_fecha = (
    df.groupby(['Fecha de Transacción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Fecha de Transacción', 'Cargos y Abonos'], ascending=[True, False])
)

print(gastos_por_fecha)


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

# Agrupar por trimestre y descripción (categoría)
df['Trimestre'] = df['Fecha de Transacción'].dt.to_period('Q')
gastos_por_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Trimestre', 'Cargos y Abonos'], ascending=[True, False])
)
print(gastos_por_trimestre_categoria)

# Agrupar por día de la semana y descripción (categoría)
df['DiaSemana'] = df['Fecha de Transacción'].dt.day_name()
gastos_por_dia_categoria = (
    df.groupby(['DiaSemana', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['DiaSemana', 'Cargos y Abonos'], ascending=[True, False])
)
print(gastos_por_dia_categoria)

# Agrupar por año y mes (sin categoría)
gastos_por_ano_mes = (
    df.groupby(['Año', 'Mes'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Año', 'Mes'])
)
print(gastos_por_ano_mes)

# Agrupar por año y día de la semana
gastos_por_ano_dia = (
    df.groupby(['Año', 'DiaSemana'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Año', 'DiaSemana'])
)
print(gastos_por_ano_dia)

# Agrupar por mes y día de la semana
gastos_por_mes_dia = (
    df.groupby(['Mes', 'DiaSemana'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Mes', 'DiaSemana'])
)
print(gastos_por_mes_dia)

# Agrupar por trimestre y categoría
gastos_por_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Trimestre', 'Cargos y Abonos'], ascending=[True, False])
)
print(gastos_por_trimestre_categoria)

# Agrupar por año y trimestre
gastos_por_ano_trimestre = (
    df.groupby(['Año', 'Trimestre'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Año', 'Trimestre'])
)
print(gastos_por_ano_trimestre)

# Agrupar por año, mes y descripción (categoría)
gastos_por_ano_mes_categoria = (
    df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Año', 'Mes', 'Cargos y Abonos'], ascending=[True, True, False])
)

print(gastos_por_ano_mes_categoria)

# Agrupar por año y obtener el gasto acumulado por categoría
df['GastoAcumuladoCategoria'] = df.groupby(['Año', 'Descripción'])['Cargos y Abonos'].cumsum()
print(df[['Año', 'Descripción', 'Cargos y Abonos', 'GastoAcumuladoCategoria']])

# Agrupar por día de la semana y mes
gastos_por_dia_mes = (
    df.groupby(['DiaSemana', 'Mes'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['DiaSemana', 'Mes'])
)
print(gastos_por_dia_mes)

# Agrupar por día de la semana y trimestre
gastos_por_dia_trimestre = (
    df.groupby(['DiaSemana', 'Trimestre'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['DiaSemana', 'Trimestre'])
)
print(gastos_por_dia_trimestre)

# Agrupar por año y obtener el total, promedio, máximo y mínimo por categoría
resumen_categoria_ano = (
    df.groupby(['Año', 'Descripción'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'max', 'min', 'count'])
    .reset_index()
    .sort_values(['Año', 'sum'], ascending=[True, False])
)
print(resumen_categoria_ano)

# Agrupar por día de la semana y mostrar el promedio por categoría
promedio_dia_categoria = (
    df.groupby(['DiaSemana', 'Descripción'])['Cargos y Abonos']
    .mean()
    .reset_index()
    .sort_values(['DiaSemana', 'Descripción'])
)
print(promedio_dia_categoria)

# Agrupar por mes y mostrar el total por categoría
gastos_por_mes_categoria_total = (
    df.groupby(['Mes', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['Mes', 'Cargos y Abonos'], ascending=[True, False])
)
print(gastos_por_mes_categoria_total)

# Agrupar por trimestre y mostrar el promedio por categoría
promedio_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .mean()
    .reset_index()
    .sort_values(['Trimestre', 'Descripción'])
)
print(promedio_trimestre_categoria)

# Agrupar por año y obtener el total acumulado por mes
gastos_acumulados_ano_mes = (
    df.groupby(['Año', 'Mes'])['Cargos y Abonos']
    .sum()
    .groupby(level=0).cumsum()
    .reset_index(name='Gasto Acumulado')
)
print(gastos_acumulados_ano_mes)

# Agrupar por categoría y mostrar el gasto promedio mensual
promedio_mensual_categoria = (
    df.groupby(['Descripción', 'Mes'])['Cargos y Abonos']
    .mean()
    .reset_index()
    .groupby('Descripción')['Cargos y Abonos']
    .mean()
    .reset_index(name='Promedio Mensual')
    .sort_values('Promedio Mensual', ascending=False)
)
print(promedio_mensual_categoria)

# Agrupar por día del mes y categoría
df['DiaMes'] = df['Fecha de Transacción'].dt.day
gastos_por_dia_mes_categoria = (
    df.groupby(['DiaMes', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
    .sort_values(['DiaMes', 'Cargos y Abonos'], ascending=[True, False])
)
print(gastos_por_dia_mes_categoria)

# Agrupar por año, mes y obtener el gasto máximo, mínimo y promedio por categoría
resumen_mes_categoria = (
    df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'max', 'min', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes', 'sum'], ascending=[True, True, False])
)
print(resumen_mes_categoria)

# Agrupar por trimestre y obtener el gasto acumulado por categoría
df['GastoAcumuladoTrimestreCategoria'] = df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos'].cumsum()
print(df[['Trimestre', 'Descripción', 'Cargos y Abonos', 'GastoAcumuladoTrimestreCategoria']])

# Agrupar por año y mostrar el total de movimientos (conteo) por categoría
conteo_movimientos_ano_categoria = (
    df.groupby(['Año', 'Descripción'])['Cargos y Abonos']
    .count()
    .reset_index(name='Conteo Movimientos')
    .sort_values(['Año', 'Conteo Movimientos'], ascending=[True, False])
)
print(conteo_movimientos_ano_categoria)

# Agrupar por mes y obtener el gasto máximo, mínimo y promedio total (sin categoría)
resumen_mes_total = (
    df.groupby(['Año', 'Mes'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'max', 'min', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes'])
)
print(resumen_mes_total)

# Agrupar por año, mes y obtener el porcentaje de cada categoría respecto al total mensual
gastos_por_ano_mes_categoria = (
    df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos']
    .sum()
    .reset_index()
)
gastos_por_ano_mes_total = (
    gastos_por_ano_mes_categoria.groupby(['Año', 'Mes'])['Cargos y Abonos']
    .transform('sum')
)
gastos_por_ano_mes_categoria['Porcentaje'] = (
    gastos_por_ano_mes_categoria['Cargos y Abonos'] / gastos_por_ano_mes_total * 100
)
print(gastos_por_ano_mes_categoria[['Año', 'Mes', 'Descripción', 'Cargos y Abonos', 'Porcentaje']])

# Agrupar por año y obtener la desviación estándar de los gastos por categoría
desviacion_categoria_ano = (
    df.groupby(['Año', 'Descripción'])['Cargos y Abonos']
    .std()
    .reset_index(name='DesviacionStd')
    .sort_values(['Año', 'DesviacionStd'], ascending=[True, False])
)
print(desviacion_categoria_ano)

# Agrupar por trimestre y obtener el gasto máximo por categoría
max_gasto_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .max()
    .reset_index(name='MaxGastoTrimestre')
    .sort_values(['Trimestre', 'MaxGastoTrimestre'], ascending=[True, False])
)
print(max_gasto_trimestre_categoria)

# Agrupar por día de la semana y obtener el total de movimientos (conteo) por categoría
conteo_dia_categoria = (
    df.groupby(['DiaSemana', 'Descripción'])['Cargos y Abonos']
    .count()
    .reset_index(name='ConteoMovimientos')
    .sort_values(['DiaSemana', 'ConteoMovimientos'], ascending=[True, False])
)
print(conteo_dia_categoria)

# Agrupar por año, mes y obtener la suma acumulada de gastos por categoría
df['GastoAcumuladoAnoMesCategoria'] = df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos'].cumsum()
print(df[['Año', 'Mes', 'Descripción', 'Cargos y Abonos', 'GastoAcumuladoAnoMesCategoria']])

# Agrupar por trimestre y obtener la desviación estándar de los gastos por categoría
desviacion_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .std()
    .reset_index(name='DesviacionStdTrimestre')
    .sort_values(['Trimestre', 'DesviacionStdTrimestre'], ascending=[True, False])
)
print(desviacion_trimestre_categoria)

# Agrupar por año y obtener el gasto promedio por día del mes
promedio_gasto_dia_mes_ano = (
    df.groupby(['Año', 'DiaMes'])['Cargos y Abonos']
    .mean()
    .reset_index(name='PromedioGastoDiaMes')
    .sort_values(['Año', 'DiaMes'])
)
print(promedio_gasto_dia_mes_ano)

# Agrupar por año, mes y obtener el gasto máximo por día de la semana
max_gasto_ano_mes_dia = (
    df.groupby(['Año', 'Mes', 'DiaSemana'])['Cargos y Abonos']
    .max()
    .reset_index(name='MaxGastoAnoMesDia')
    .sort_values(['Año', 'Mes', 'DiaSemana'])
)
print(max_gasto_ano_mes_dia)

# Agrupar por año, mes y obtener el rango (max - min) de gastos por categoría
rango_gasto_ano_mes_categoria = (
    df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos']
    .agg(lambda x: x.max() - x.min())
    .reset_index(name='RangoGasto')
    .sort_values(['Año', 'Mes', 'RangoGasto'], ascending=[True, True, False])
)
print(rango_gasto_ano_mes_categoria)

# Agrupar por año y obtener el gasto total, promedio, máximo y mínimo por día de la semana
resumen_ano_mes_dia = (
    df.groupby(['Año', 'Mes', 'DiaSemana'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes', 'DiaSemana'])
)
print(resumen_ano_mes_dia)

# Agrupar por año y obtener el gasto máximo, mínimo y promedio por categoría y trimestre
resumen_ano_categoria_trimestre = (
    df.groupby(['Año', 'Descripción', 'Trimestre'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'max', 'min', 'count'])
    .reset_index()
    .sort_values(['Año', 'Descripción', 'Trimestre'])
)
print(resumen_ano_categoria_trimestre)

# Agrupar por año, mes y obtener el gasto total por categoría y día de la semana
gasto_ano_mes_categoria_dia = (
    df.groupby(['Año', 'Mes', 'Descripción', 'DiaSemana'])['Cargos y Abonos']
    .sum()
    .reset_index(name='GastoTotal')
    .sort_values(['Año', 'Mes', 'Descripción', 'DiaSemana'])
)
print(gasto_ano_mes_categoria_dia)

# Agrupar por trimestre y obtener la mediana de gastos por categoría
mediana_gasto_trimestre_categoria = (
    df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos']
    .median()
    .reset_index(name='MedianaGastoTrimestre')
    .sort_values(['Trimestre', 'MedianaGastoTrimestre'], ascending=[True, False])
)
print(mediana_gasto_trimestre_categoria)

# Agrupar por año y obtener el gasto total por trimestre y día de la semana
gasto_ano_trimestre_dia = (
    df.groupby(['Año', 'Trimestre', 'DiaSemana'])['Cargos y Abonos']
    .sum()
    .reset_index(name='GastoTotal')
    .sort_values(['Año', 'Trimestre', 'DiaSemana'])
)
print(gasto_ano_trimestre_dia)

# Agrupar por año, mes y obtener el gasto total, promedio y conteo por categoría y día de la semana
resumen_ano_mes_categoria_dia = (
    df.groupby(['Año', 'Mes', 'Descripción', 'DiaSemana'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes', 'Descripción', 'DiaSemana'])
)
print(resumen_ano_mes_categoria_dia)

# Agrupar por año y obtener el gasto total, promedio y conteo por categoría y día del mes
resumen_ano_categoria_dia_mes = (
    df.groupby(['Año', 'Descripción', 'DiaMes'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Año', 'Descripción', 'DiaMes'])
)
print(resumen_ano_categoria_dia_mes)

# Agrupar por trimestre y obtener el gasto total, promedio y conteo por categoría y día de la semana
resumen_trimestre_categoria_dia = (
    df.groupby(['Trimestre', 'Descripción', 'DiaSemana'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Trimestre', 'Descripción', 'DiaSemana'])
)
print(resumen_trimestre_categoria_dia)

# Agrupar por año, mes y obtener la desviación estándar de los gastos por categoría
desviacion_ano_mes_categoria = (
    df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos']
    .std()
    .reset_index(name='DesviacionStdAnoMes')
    .sort_values(['Año', 'Mes', 'DesviacionStdAnoMes'], ascending=[True, True, False])
)
print(desviacion_ano_mes_categoria)

# Agrupar por año, mes y obtener el gasto total, promedio y conteo por trimestre y categoría
resumen_ano_mes_trimestre_categoria = (
    df.groupby(['Año', 'Mes', 'Trimestre', 'Descripción'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes', 'Trimestre', 'Descripción'])
)
print(resumen_ano_mes_trimestre_categoria)

# Agrupar por año, mes y obtener el gasto total, promedio y conteo por día y categoría
resumen_ano_mes_dia_categoria = (
    df.groupby(['Año', 'Mes', 'DiaMes', 'Descripción'])['Cargos y Abonos']
    .agg(['sum', 'mean', 'count'])
    .reset_index()
    .sort_values(['Año', 'Mes', 'DiaMes', 'sum'], ascending=[True, True, True, False])
)
print(resumen_ano_mes_dia_categoria)

# -------------------- VISUALIZACIONES --------------------

# 1. Total por año
gastos_por_ano = df.groupby('Año')['Cargos y Abonos'].sum().reset_index()
print(gastos_por_ano)
gastos_por_ano.plot(x='Año', y='Cargos y Abonos', kind='bar', title='Total por Año')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 2. Total por mes
gastos_por_mes = df.groupby('Mes')['Cargos y Abonos'].sum().reset_index()
print(gastos_por_mes)
gastos_por_mes.plot(x='Mes', y='Cargos y Abonos', kind='bar', title='Total por Mes')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 3. Total por categoría
gastos_por_categoria = df.groupby('Descripción')['Cargos y Abonos'].sum().reset_index().sort_values('Cargos y Abonos', ascending=False)
print(gastos_por_categoria)
gastos_por_categoria.plot(x='Descripción', y='Cargos y Abonos', kind='bar', title='Total por Categoría')
plt.ylabel('Total')
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# 4. Total por año y categoría
gastos_por_ano_categoria = df.groupby(['Año', 'Descripción'])['Cargos y Abonos'].sum().unstack().fillna(0)
print(gastos_por_ano_categoria)
gastos_por_ano_categoria.plot(kind='bar', stacked=True, title='Total por Año y Categoría')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 5. Total por mes y categoría
gastos_por_mes_categoria = df.groupby(['Mes', 'Descripción'])['Cargos y Abonos'].sum().unstack().fillna(0)
print(gastos_por_mes_categoria)
gastos_por_mes_categoria.plot(kind='bar', stacked=True, title='Total por Mes y Categoría')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 6. Total por año, mes y categoría (heatmap)
gastos_ano_mes_cat = df.groupby(['Año', 'Mes', 'Descripción'])['Cargos y Abonos'].sum().reset_index()
pivot_heatmap = gastos_ano_mes_cat.pivot_table(index=['Año', 'Mes'], columns='Descripción', values='Cargos y Abonos', fill_value=0)
print(pivot_heatmap)
plt.figure(figsize=(12,6))
plt.imshow(pivot_heatmap, aspect='auto', cmap='Blues')
plt.title('Heatmap Año/Mes vs Categoría')
plt.xlabel('Categoría')
plt.ylabel('Año, Mes')
plt.colorbar(label='Total')
plt.xticks(range(len(pivot_heatmap.columns)), pivot_heatmap.columns, rotation=90)
plt.yticks(range(len(pivot_heatmap.index)), [f"{a}-{m}" for a, m in pivot_heatmap.index])
plt.tight_layout()
plt.show()

# 7. Total por trimestre y categoría
gastos_por_trimestre_categoria = df.groupby(['Trimestre', 'Descripción'])['Cargos y Abonos'].sum().unstack().fillna(0)
print(gastos_por_trimestre_categoria)
gastos_por_trimestre_categoria.plot(kind='bar', stacked=True, title='Total por Trimestre y Categoría')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 8. Total por día de la semana
gastos_por_dia_semana = df.groupby('DiaSemana')['Cargos y Abonos'].sum().reindex(
    ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
).reset_index()
print(gastos_por_dia_semana)
gastos_por_dia_semana.plot(x='DiaSemana', y='Cargos y Abonos', kind='bar', title='Total por Día de la Semana')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 9. Total por día del mes
gastos_por_dia_mes = df.groupby('DiaMes')['Cargos y Abonos'].sum().reset_index()
print(gastos_por_dia_mes)
gastos_por_dia_mes.plot(x='DiaMes', y='Cargos y Abonos', kind='bar', title='Total por Día del Mes')
plt.ylabel('Total')
plt.tight_layout()
plt.show()

# 10. Top 5 categorías por año
for ano in sorted(df['Año'].dropna().unique()):
    top5 = df[df['Año'] == ano].groupby('Descripción')['Cargos y Abonos'].sum().sort_values(ascending=False).head(5)
    print(f"Top 5 categorías en {ano}:\n", top5)
    top5.plot(kind='bar', title=f'Top 5 Categorías en {ano}')
    plt.ylabel('Total')
    plt.tight_layout()
    plt.show()

# 11. Evolución mensual por categoría (línea)
for cat in df['Descripción'].unique():
    serie = df[df['Descripción'] == cat].groupby(['Año', 'Mes'])['Cargos y Abonos'].sum()
    serie.index = [f"{a}-{m:02d}" for a, m in serie.index]
    plt.plot(serie.index, serie.values, label=cat)
plt.title('Evolución Mensual por Categoría')
plt.ylabel('Total')
plt.xlabel('Año-Mes')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.show()

# 12. Boxplot de gastos por categoría
df.boxplot(column='Cargos y Abonos', by='Descripción', vert=False, figsize=(10,6))
plt.title('Distribución de Gastos por Categoría')
plt.suptitle('')
plt.xlabel('Cargos y Abonos')
plt.tight_layout()
plt.show()

# 13. Pie chart de participación por categoría (total)
gastos_totales_categoria = df.groupby('Descripción')['Cargos y Abonos'].sum()
gastos_totales_categoria.plot.pie(autopct='%1.1f%%', figsize=(8,8), title='Participación por Categoría')
plt.ylabel('')
plt.tight_layout()
plt.show()

# 14. Histograma de montos de gastos
df['Cargos y Abonos'].plot.hist(bins=30, alpha=0.7, title='Histograma de Montos de Gastos')
plt.xlabel('Monto')
plt.tight_layout()
plt.show()

# 15. Gráfico de dispersión: Valor Original vs Cargos y Abonos
plt.scatter(df['Valor Original'], df['Cargos y Abonos'], alpha=0.5)
plt.title('Valor Original vs Cargos y Abonos')
plt.xlabel('Valor Original')
plt.ylabel('Cargos y Abonos')
plt.tight_layout()
plt.show()

# -------------------- DOCUMENTACIÓN DE GRÁFICOS --------------------
# 1. Total por año: gráfico de barras de los gastos totales por año.
# 2. Total por mes: gráfico de barras de los gastos totales por mes.
# 3. Total por categoría: gráfico de barras de los gastos totales por categoría.
# 4. Total por año y categoría: gráfico de barras apiladas por año y categoría.
# 5. Total por mes y categoría: gráfico de barras apiladas por mes y categoría.
# 6. Heatmap año/mes vs categoría: matriz de calor de gastos por año, mes y categoría.
# 7. Total por trimestre y categoría: gráfico de barras apiladas por trimestre y categoría.
# 8. Total por día de la semana: gráfico de barras por día de la semana.
# 9. Total por día del mes: gráfico de barras por día del mes.
# 10. Top 5 categorías por año: gráfico de barras para las 5 categorías principales de cada año.
# 11. Evolución mensual por categoría: gráfico de líneas de la evolución mensual de cada categoría.
# 12. Boxplot de gastos por categoría: diagrama de caja para la distribución de gastos por categoría.
# 13. Pie chart de participación por categoría: gráfico circular de la participación de cada categoría.
# 14. Histograma de montos de gastos: histograma de los montos de gastos.
# 15. Dispersión Valor Original vs Cargos y Abonos: gráfico de dispersión entre dos variables numéricas.
plt.ylabel('')
plt.tight_layout()
plt.show()

