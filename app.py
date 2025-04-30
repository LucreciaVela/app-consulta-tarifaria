
import pandas as pd
import streamlit as st

# Cargar los datos desde un archivo CSV (ejemplo de prueba)
@st.cache_data
def cargar_datos():
    return pd.read_csv("tarifas_demo.csv")

df = cargar_datos()

st.title("Consulta de Tarifas de Transporte")
st.subheader("Ingrese el origen y destino para conocer el valor de la tarifa")

# Obtener listas únicas de localidades
localidades = sorted(set(df["Origen"]).union(set(df["Destino"])))

# Selección de origen y destino con autocompletado
origen = st.selectbox("Origen", localidades)
destino = st.selectbox("Destino", localidades)

# Botón para buscar
if st.button("Buscar tarifa"):
    resultados = df[(df["Origen"] == origen) & (df["Destino"] == destino)]

    if not resultados.empty:
        st.success(f"Se encontraron {len(resultados)} resultado(s)")
        st.dataframe(resultados)
    else:
        st.warning("No se encontraron tarifas para ese trayecto.")
