import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Consulta Tarifaria ERSeP",
    page_icon="🚌",
    layout="centered"
)

st.title("🚌 Consulta Tarifaria – RG ERSeP N° 60")
st.markdown(
    "Aplicación de consulta de tarifas del **transporte interurbano de pasajeros** "
    "según el **Cuadro Tarifario RG N° 60**."
)

# -------------------------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------------------------

@st.cache_data
def cargar_tarifas(path_excel: str) -> pd.DataFrame:
    """
    Lee el cuadro tarifario desde el Excel oficial y devuelve
    un DataFrame limpio.
    """
    xls_path = Path(path_excel)

    if not xls_path.exists():
        st.error(
            f"No se encuentra el archivo `{path_excel}` en el repositorio.\n\n"
            "Subí el Excel al mismo nivel que este archivo `.py` y volvé a ejecutar la app."
        )
        return pd.DataFrame()

    df = pd.read_excel(xls_path, sheet_name="CUADRO TARIFARIO RG 60")

    # Normalización de columnas esperadas
    columnas_esperadas = [
        "CUIT", "EMPRESA", "MODALIDAD", "ORIGEN", "DESTINO", "TARIFA RG 60"
    ]
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        st.error(
            "El Excel no tiene las columnas esperadas. Faltan: "
            + ", ".join(faltantes)
        )
        return pd.DataFrame()

    # Limpieza básica de textos
    for col in ["CUIT", "EMPRESA", "MODALIDAD", "ORIGEN", "DESTINO"]:
        df[col] = df[col].astype(str).str.strip()

    # Nos aseguramos que tarifa sea numérica
    df["TARIFA RG 60"] = pd.to_numeric(df["TARIFA RG 60"], errors="coerce")

    return df


df = cargar_tarifas("CUADRO TARIFARIO RG N° 60.xlsx")

if df.empty:
    st.stop()

# -------------------------------------------------------------------
# PANEL DE FILTROS
# -------------------------------------------------------------------

st.subheader("🔍 Parámetros de búsqueda")

# Lista de localidades a partir de ORIGEN y DESTINO (bidireccional)
localidades = pd.unique(
    pd.concat([df["ORIGEN"], df["DESTINO"]], ignore_index=True)
).tolist()
localidades = sorted(localidades)

col1, col2 = st.columns(2)
with col1:
    origen = st.selectbox("Origen", localidades, index=0)
with col2:
    destino = st.selectbox("Destino", localidades, index=0)

col3, col4 = st.columns(2)
with col3:
    empresas = ["TODAS"] + sorted(df["EMPRESA"].unique().tolist())
    empresa_sel = st.selectbox("Empresa", empresas, index=0)

with col4:
    modalidades = ["TODAS"] + sorted(df["MODALIDAD"].unique().tolist())
    modalidad_sel = st.selectbox("Modalidad", modalidades, index=0)

st.caption("La búsqueda es **bidireccional**: se consideran tanto ORIGEN→DESTINO como DESTINO→ORIGEN.")

# -------------------------------------------------------------------
# BÚSQUEDA DE TARIFA
# -------------------------------------------------------------------

if st.button("Consultar tarifa"):
    if origen == destino:
        st.warning("El origen y el destino no pueden ser iguales.")
    else:
        # Filtro bidireccional
        mask_od = (
            ((df["ORIGEN"] == origen) & (df["DESTINO"] == destino)) |
            ((df["ORIGEN"] == destino) & (df["DESTINO"] == origen))
        )

        df_filtrado = df[mask_od].copy()

        if empresa_sel != "TODAS":
            df_filtrado = df_filtrado[df_filtrado["EMPRESA"] == empresa_sel]

        if modalidad_sel != "TODAS":
            df_filtrado = df_filtrado[df_filtrado["MODALIDAD"] == modalidad_sel]

        if df_filtrado.empty:
            st.error("No se encontraron tarifas para la combinación seleccionada.")
        else:
            st.subheader("📋 Resultado de la consulta")

            # Ordenar por empresa/modalidad para que quede prolijo
            df_filtrado = df_filtrado.sort_values(
                by=["EMPRESA", "MODALIDAD", "ORIGEN", "DESTINO"]
            )

            # Mostrar tabla amigable
            df_mostrar = df_filtrado[
                ["EMPRESA", "MODALIDAD", "ORIGEN", "DESTINO", "TARIFA RG 60"]
            ].rename(columns={"TARIFA RG 60": "Tarifa RG 60 ($)"})

            st.dataframe(
                df_mostrar.style.format({"Tarifa RG 60 ($)": "{:,.2f}"}),
                use_container_width=True
            )

            # Si hay más de un registro, mostrar rangos
            tarifa_min = df_filtrado["TARIFA RG 60"].min()
            tarifa_max = df_filtrado["TARIFA RG 60"].max()

            if tarifa_min == tarifa_max:
                st.success(
                    f"Tarifa RG 60 vigente para el tramo **{origen} – {destino}**: "
                    f"**${tarifa_min:,.2f}**"
                )
            else:
                st.info(
                    f"Rango de tarifas RG 60 para el tramo **{origen} – {destino}**: "
                    f"entre **${tarifa_min:,.2f}** y **${tarifa_max:,.2f}**, "
                    f"según empresa/modalidad."
                )

# -------------------------------------------------------------------
# INFORMACIÓN ADICIONAL
# -------------------------------------------------------------------

st.markdown("---")
st.caption(
    "Fuente: Cuadro Tarifario **RG ERSeP N° 60**. "
    "Aplicación de consulta para uso interno del Área Tarifas – ERSeP."
)
