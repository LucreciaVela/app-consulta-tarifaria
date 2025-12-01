
import streamlit as st
import pandas as pd
import difflib
from urllib.parse import quote

# Configurar página
st.set_page_config(page_title="Tarifas Interurbanas ERSeP", layout="centered")

# Cargar datos
df_tarifas = pd.read_pickle("tarifario.pkl")
df_localidades = pd.read_pickle("localidades.pkl")

# Encabezado con logo
st.image("logo ersep.jpg", width=180)
st.markdown("<h2 style='text-align: center;'>Consulta de Tarifas - Transporte Interurbano Córdoba (ERSeP)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ingrese el origen y destino del viaje para obtener la tarifa vigente.</p>", unsafe_allow_html=True)

# Función para normalizar texto
def normalizar(texto):
    return str(texto).strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

# Diccionario de localidades normalizadas
localidades_unicas = df_localidades['Nombre'].dropna().unique().tolist()
localidades_normalizadas = {normalizar(loc): loc for loc in localidades_unicas}

# Formulario de búsqueda
with st.form("busqueda_tarifa"):
    col1, col2 = st.columns(2)
    with col1:
        origen_input = st.text_input("Origen")
    with col2:
        destino_input = st.text_input("Destino")
    submitted = st.form_submit_button("Consultar Tarifa")

# Función para buscar localidad por coincidencia flexible
def buscar_localidad(cadena):
    normal = normalizar(cadena)
    coincidencias = difflib.get_close_matches(normal, localidades_normalizadas.keys(), n=1, cutoff=0.6)
    if coincidencias:
        return localidades_normalizadas[coincidencias[0]]
    return None

# Procesar búsqueda
if submitted:
    origen_valido = buscar_localidad(origen_input)
    destino_valido = buscar_localidad(destino_input)

    if origen_valido and destino_valido:
        resultados = df_tarifas[
            ((df_tarifas['Origen'] == origen_valido) & (df_tarifas['Destino'] == destino_valido)) |
            ((df_tarifas['Origen'] == destino_valido) & (df_tarifas['Destino'] == origen_valido))
        ].copy()

        if not resultados.empty:
            resultados['Tarifa'] = resultados['Tarifa'].map(lambda x: f"$ {x:,.2f}")
            resultados = resultados[['Empresa', 'Modalidad', 'Tarifa']].drop_duplicates().reset_index(drop=True)

            st.success("Resultado encontrado:")
            st.dataframe(resultados.style.hide(axis='index'), use_container_width=True)

            # Crear mensaje múltiple para compartir
            mensaje = f"🚌 ERSeP – Tarifa Interurbano Córdoba\n"
            mensaje += f"📍 Origen: {origen_valido.upper()}\n📍 Destino: {destino_valido.upper()}\n"
            for _, row in resultados.iterrows():
                mensaje += f"🏢 {row['Empresa']} – {row['Modalidad']}: {row['Tarifa']}\n"

            st.markdown("### Texto para compartir")
            st.text_area(" ", mensaje, height=150, label_visibility="collapsed")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<a href='https://wa.me/?text={quote(mensaje)}' target='_blank'><button style='background-color:#25D366;color:white;padding:10px 15px;font-size:16px;border:none;border-radius:5px;'>📲 Compartir por WhatsApp</button></a>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<a href='mailto:?subject=Tarifa Interurbano ERSeP&body={quote(mensaje)}'><button style='background-color:#0072C6;color:white;padding:10px 15px;font-size:16px;border:none;border-radius:5px;'>✉️ Compartir por Email</button></a>", unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🔄 Nueva búsqueda"):
                st.experimental_rerun()
        else:
            st.warning("No se encontró un recorrido con ese origen y destino.")
    else:
        st.error("No se reconocieron las localidades ingresadas. Verifique los nombres.")
