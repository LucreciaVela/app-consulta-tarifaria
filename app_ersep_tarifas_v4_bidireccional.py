import streamlit as st
import pandas as pd
import difflib
from urllib.parse import quote

# --------------------------------------------------
# Configurar página
# --------------------------------------------------
st.set_page_config(page_title="Tarifas Interurbanas ERSeP", layout="centered")

# --------------------------------------------------
# Cargar datos
# --------------------------------------------------
df_tarifas = pd.read_pickle("tarifario.pkl")
df_tarifas = df_tarifas[df_tarifas["Empresa"].str.upper() != "ERSA"]
# Se mantiene por compatibilidad, aunque ya no lo usamos:
try:
    df_localidades = pd.read_pickle("localidades.pkl")
except Exception:
    df_localidades = None

# --------------------------------------------------
# Encabezado con logo
# --------------------------------------------------
st.image("logo ersep.jpg", width=180)
st.markdown(
    "<h2 style='text-align: center;'>Consulta de Tarifas - Transporte Interurbano Córdoba (ERSeP)</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>Ingrese el origen y destino del viaje para obtener la tarifa vigente.</p>",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Función para normalizar texto (clave para tolerar errores)
# --------------------------------------------------
def normalizar(texto):
    return (
        str(texto)
        .strip()
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

# Agregamos columnas normalizadas en el propio tarifario
df_tarifas["Origen_norm"] = df_tarifas["Origen"].apply(normalizar)
df_tarifas["Destino_norm"] = df_tarifas["Destino"].apply(normalizar)

# Lista de localidades normalizadas existentes en la base REAL
localidades_totales_norm = sorted(
    set(df_tarifas["Origen_norm"].dropna().tolist())
    | set(df_tarifas["Destino_norm"].dropna().tolist())
)

# --------------------------------------------------
# Función para buscar localidad (entrada del usuario)
# sobre la lista de localidades normalizadas reales
# --------------------------------------------------
def buscar_localidad(cadena):
    normal = normalizar(cadena)
    coincidencias = difflib.get_close_matches(
        normal,
        localidades_totales_norm,
        n=1,
        cutoff=0.5,  # bastante permisivo: cordob, cordova, rio cebalo, etc.
    )
    if coincidencias:
        return coincidencias[0]  # devolvemos el nombre normalizado
    return None

# --------------------------------------------------
# Formulario de búsqueda
# --------------------------------------------------
with st.form("busqueda_tarifa"):
    col1, col2 = st.columns(2)
    with col1:
        origen_input = st.text_input("Origen")
    with col2:
        destino_input = st.text_input("Destino")
    submitted = st.form_submit_button("Consultar Tarifa")

# --------------------------------------------------
# Procesar búsqueda
# --------------------------------------------------
if submitted:
    origen_norm = buscar_localidad(origen_input)
    destino_norm = buscar_localidad(destino_input)

    if origen_norm and destino_norm:
        # Filtramos por columnas NORMALIZADAS (no por el texto tal cual)
        mask = (
            (df_tarifas["Origen_norm"] == origen_norm)
            & (df_tarifas["Destino_norm"] == destino_norm)
        ) | (
            (df_tarifas["Origen_norm"] == destino_norm)
            & (df_tarifas["Destino_norm"] == origen_norm)
        )

        resultados = df_tarifas[mask].copy()

        if not resultados.empty:
            # Elegimos la forma "bonita" para mostrar (la primera que aparezca)
            origen_mostrar = resultados.iloc[0]["Origen"]
            destino_mostrar = resultados.iloc[0]["Destino"]

            # Formatear tarifa
            resultados["Tarifa"] = resultados["Tarifa"].map(
                lambda x: f"$ {x:,.2f}"
            )

            # Mostrar solo Empresa, Modalidad y Tarifa, sin duplicados
            resultados_mostrar = (
                resultados[["Empresa", "Modalidad", "Tarifa"]]
                .drop_duplicates()
                .reset_index(drop=True)
            )

            st.success(
                f"Resultados para el tramo: {origen_mostrar} – {destino_mostrar}"
            )
            st.dataframe(
                resultados_mostrar.style.hide(axis="index"),
                use_container_width=True,
            )

            # Crear mensaje múltiple para compartir
            mensaje = "🚌 ERSeP – Tarifa Interurbano Córdoba\n"
            mensaje += f"📍 Origen: {str(origen_mostrar).upper()}\n"
            mensaje += f"📍 Destino: {str(destino_mostrar).upper()}\n"
            for _, row in resultados_mostrar.iterrows():
                mensaje += (
                    f"🏢 {row['Empresa']} – {row['Modalidad']}: {row['Tarifa']}\n"
                )

            st.markdown("### Texto para compartir")
            st.text_area(" ", mensaje, height=150, label_visibility="collapsed")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"<a href='https://wa.me/?text={quote(mensaje)}' target='_blank'>"
                    "<button style='background-color:#25D366;color:white;padding:10px 15px;"
                    "font-size:16px;border:none;border-radius:5px;'>📲 Compartir por WhatsApp</button></a>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"<a href='mailto:?subject=Tarifa Interurbano ERSeP&body={quote(mensaje)}'>"
                    "<button style='background-color:#0072C6;color:white;padding:10px 15px;"
                    "font-size:16px;border:none;border-radius:5px;'>✉️ Compartir por Email</button></a>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            if st.button("🔄 Nueva búsqueda"):
                st.experimental_rerun()
        else:
            st.warning("No se encontró un recorrido con ese origen y destino.")
    else:
        st.error(
            "No se reconocieron las localidades ingresadas. Probá corrigiendo la escritura "
            "o acercándote más al nombre real (ej.: 'cordoba', 'rio ceballos')."
        )

