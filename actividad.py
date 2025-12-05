import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar el archivo Excel
file_path = "worldbank_latam_2014_2024.xls.xlsx"  # cámbialo si está en otra carpeta
df = pd.read_excel(file_path, sheet_name="Data")
print(df.head())
df.describe()
df.info()

#mostrando nombre de las columns.
for i, col in enumerate(df.columns):
    print(i, "->", col)

# Ver cuántos indicadores distintos hay
print("\nIndicadores disponibles:")
print(df["Nombre serie"].unique())

# Ejemplo 1: filtrar solo PIB (current US$)
pib = df[df["Nombre serie"] == "PIB (current US$)"]

# Ejemplo 2: filtrar Inflación (%)
inflacion = df[df["Nombre serie"].str.contains("Inflation", case=False, na=False)]

# Pasar de formato ancho (años como columnas) a formato largo
df=df_melted = df.melt(
    id_vars=["Pais", "Nombre serie"],  #columns que se mantienen fijas
    var_name="Años",                    #nuevo nombre de columna para lo que eran los encabezados (2014-2024)
    value_name="Valores"                 #nuevo nombre de columna para los valores de cada año
)

# Revisar el nuevo formato
print("\nDataset transformado a formato largo (tidy data):")
print(df_melted.head(20))

#exportar a excel el df modificado.
df.to_excel("dataset_modificado.xlsx", index=False)

import pandas as pd

#correlacion PIB/Inflacion, nos permmite ver impacto del PIB a la inflacion.
# Alto Crecimiento del PIB → Bajo Desempleo → Alta Inflación
# Bajo Crecimiento del PIB → Alto Desempleo → Baja Inflación

# --- . Filtrar PIB e Inflación ---
pib = df[df["Nombre serie"] == "PIB (current US$)"]
inflacion = df[df["Nombre serie"].str.contains("Inflación", case=False, na=False)]

# --- . Renombrar columna de valores ---
pib = pib.rename(columns={"Valores": "PIB"})
inflacion = inflacion.rename(columns={"Valores": "Inflacion"})

# --- . Unir por Pais y Años ---
df_merge = pd.merge(
    pib[["Pais", "Años", "PIB"]],
    inflacion[["Pais", "Años", "Inflacion"]],
    on=["Pais", "Años"],
    how="inner"
)
print(df_merge.head())

# --- . Calcular correlación PIB vs Inflación por país ---
correlaciones=(
    df_merge.groupby("Pais")[["PIB", "Inflacion"]]
    .corr().unstack()['PIB']['Inflacion'].dropna())


# --- . Ordenar correlaciones ---
top_positivas = correlaciones.sort_values(ascending=False).head(5)
top_negativas = correlaciones.sort_values(ascending=True).head(5)

print("📊 Top 5 correlaciones MÁS POSITIVAS:")
print(top_positivas)
print("\n📉 Top 5 correlaciones MÁS NEGATIVAS:")
print(top_negativas)

#PIB vs/exportacion e importacion. 
# La correlación PIB vs exportaciones e importaciones me ayuda a identificar si el crecimiento de un país está más ligado al comercio exterior o al consumo interno.
#  Eso es clave para entender su vulnerabilidad ante crisis globales y diseñar políticas económicas o estrategias de inversión.

# --- . Filtrar PIB, Exportaciones e Importaciones ---
pib = df[df["Nombre serie"] == "PIB (current US$)"].rename(columns={"Valores": "PIB"})
exportaciones = df[df["Nombre serie"].str.contains("Exportaciones", case=False, na=False)].rename(columns={"Valores": "Exportaciones"})
importaciones = df[df["Nombre serie"].str.contains("Importaciones", case=False, na=False)].rename(columns={"Valores": "Importaciones"})

# --- . Merge en una sola tabla ---
df_merge = pib.merge(exportaciones, on=["Pais", "Años"], how="inner") \
              .merge(importaciones, on=["Pais", "Años"], how="inner")

# --- . Correlaciones PIB vs Exportaciones ---
corr_export = df_merge.groupby("Pais")[["PIB", "Exportaciones"]].corr().unstack()['PIB']['Exportaciones'].dropna()
print("📊 Correlación PIB vs Exportaciones (Top 5):")
print(corr_export.sort_values(ascending=False).head(5))

# --- . Correlaciones PIB vs Importaciones ---
corr_import = df_merge.groupby("Pais")[["PIB", "Importaciones"]].corr().unstack()['PIB']['Importaciones'].dropna()

print("\n📉 Correlación PIB vs Importaciones (Top 5):")
print(corr_import.sort_values(ascending=False).head(5))

#--- . Balanza comercial =Exportaciones−Importaciones 
# Si la balanza es positiva → el país exporta más de lo que importa (superávit).
# Si es negativa → importa más de lo que exporta (déficit).
# El PIB de América Latina no depende únicamente de tener superávit comercial

# --- . Filtrar PIB, Exportaciones e Importaciones ---
pib = df[df["Nombre serie"] == "PIB (current US$)"].rename(columns={"Valores": "PIB"})
exportaciones = df[df["Nombre serie"].str.contains("Exportaciones", case=False, na=False)].rename(columns={"Valores": "Exportaciones"})
importaciones = df[df["Nombre serie"].str.contains("Importaciones", case=False, na=False)].rename(columns={"Valores": "Importaciones"})

# --- . Unir todo en una sola tabla ---
df_merge = pib.merge(exportaciones, on=["Pais", "Años"], how="inner") \
              .merge(importaciones, on=["Pais", "Años"], how="inner")

# --- . Calcular balanza comercial ---
df_merge["Balanza"] = df_merge["Exportaciones"] - df_merge["Importaciones"]

# --- . Correlación PIB vs Balanza por país ---
corr_balanza = df_merge.groupby("Pais")[["PIB", "Balanza"]].corr().iloc[0::2, -1].dropna()

print("📊 Top 5 correlaciones MÁS POSITIVAS (PIB vs Balanza Comercial):")
print(corr_balanza.sort_values(ascending=False).head(5))

print("\n📉 Top 5 correlaciones MÁS NEGATIVAS (PIB vs Balanza Comercial):")
print(corr_balanza.sort_values().head(5))

#El análisis PIB vs Valor Agregado Industrial (% del PIB)
# es clave porque te mete en el corazón de la estructura económica
#Esto me ayudó a entender no solo cuánto crecen las economías, sino de qué dependen para crecer



# --- . Filtrar PIB y Valor Agregado Industrial ---
pib = df[df["Nombre serie"] == "PIB (current US$)"].rename(columns={"Valores": "PIB"})
industrial = df[df["Nombre serie"].str.contains("Valor agregado industrial", case=False, na=False)].rename(columns={"Valores": "Industrial"})

# --- . Unir datasets por Pais y Año ---
df_merge = pd.merge(
    pib[["Pais", "Años", "PIB"]],
    industrial[["Pais", "Años", "Industrial"]],
    on=["Pais", "Años"],
    how="inner"
)

# --- . Calcular correlaciones PIB vs Industrial por país ---
correlaciones = df_merge.groupby("Pais")[["PIB", "Industrial"]].corr().iloc[0::2, -1].dropna()

print("📊 Top 5 correlaciones MÁS POSITIVAS (PIB vs Valor Industrial):")
print(correlaciones.sort_values(ascending=False).head(5))

print("\n📉 Top 5 correlaciones MÁS NEGATIVAS (PIB vs Valor Industrial):")
print(correlaciones.sort_values().head(5))

















