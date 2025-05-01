import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz

# @st.cache_data
def cargar_datos():
    return pd.read_csv("tarifas_real.csv")

df = cargar_datos()

st.title("Consulta de Tarifas de Transporte")
st.subheader("Ingrese el origen y destino para conocer el valor de la tarifa")

origen_input = st.text_input("Origen")
destino_input = st.text_input("Destino")

def buscar_coincidencias(texto, opciones, limite=3):
    resultados = process.extract(texto, opciones, scorer=fuzz.WRatio, limit=limite)
    return [r[0] for r in resultados if r[1] > 70]

if st.button("Buscar tarifa"):
    if origen_input and destino_input:
        origenes_similares = buscar_coincidencias(origen_input, df["Origen"].unique())
        destinos_similares = buscar_coincidencias(destino_input, df["Destino"].unique())

        resultados = df[df["Origen"].isin(origenes_similares) & df["Destino"].isin(destinos_similares)]

        if not resultados.empty:
            st.success(f"Se encontraron {len(resultados)} resultado(s)")
            st.dataframe(resultados)
        else:
            st.warning("No se encontraron tarifas para ese trayecto.")
    else:
        st.info("Por favor complete ambos campos.")
