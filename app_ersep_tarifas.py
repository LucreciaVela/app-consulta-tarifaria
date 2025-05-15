
import streamlit as st
import pandas as pd
import difflib
from urllib.parse import quote

# Cargar datos
df_tarifas = pd.read_pickle("tarifario.pkl")
df_localidades = pd.read_pickle("localidades.pkl")

# Encabezado con logo
st.image("logo ersep.jpg", width=200)
st.title("Consulta de Tarifas - Transporte Interurbano Córdoba (ERSeP)")
st.markdown("Ingrese el origen y destino del viaje para obtener la tarifa vigente.")

# Normalización para búsqueda flexible
def normalizar(texto):
    return str(texto).strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

localidades_unicas = df_localidades['Nombre'].dropna().unique().tolist()
localidades_normalizadas = {normalizar(loc): loc for loc in localidades_unicas}

# Input del usuario
col1, col2 = st.columns(2)
with col1:
    origen_input = st.text_input("Origen")
with col2:
    destino_input = st.text_input("Destino")

def buscar_localidad(cadena):
    normal = normalizar(cadena)
    coincidencias = difflib.get_close_matches(normal, localidades_normalizadas.keys(), n=1, cutoff=0.6)
    if coincidencias:
        return localidades_normalizadas[coincidencias[0]]
    return None

# Buscar y mostrar resultados
if origen_input and destino_input:
    origen_valido = buscar_localidad(origen_input)
    destino_valido = buscar_localidad(destino_input)

    if origen_valido and destino_valido:
        resultados = df_tarifas[
            (df_tarifas['Origen'] == origen_valido) & (df_tarifas['Destino'] == destino_valido)
        ]
        if not resultados.empty:
            st.success("Resultado encontrado:")
            st.dataframe(resultados[['Empresa', 'Modalidad', 'KM', 'Tarifa']])

            # Mensaje para compartir
            fila = resultados.iloc[0]
            mensaje = f"""🚌 ERSeP – Tarifa Interurbano Córdoba
📍 Origen: {fila['Origen']}
📍 Destino: {fila['Destino']}
💲 Tarifa vigente: ${fila['Tarifa']:,.2f}
"""
            st.text_area("Texto para compartir", mensaje, height=100)

            # Botones de compartir
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"[📤 WhatsApp](https://wa.me/?text={quote(mensaje)})")
            with col2:
                st.markdown(f"[✉️ Email](mailto:?subject=Tarifa Interurbano ERSeP&body={quote(mensaje)})")
            with col3:
                st.code(mensaje, language="text")
                st.caption("Copie el texto para compartirlo en otras redes")

        else:
            st.warning("No se encontró un recorrido con ese origen y destino.")
    else:
        st.error("No se reconocieron las localidades ingresadas. Verifique los nombres.")
