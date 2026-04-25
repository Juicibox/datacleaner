import streamlit as st
import pandas as pd

from utils.cleaning import aplicar_transformacion, limpiar_texto
from utils.mapping import cargar_mapa, guardar_mapa, aplicar_mapa
from utils.merge import hacer_merge

st.set_page_config(layout="wide")
st.title("🧹 Data Wrangling App")

# =========================
# 1. CARGA
# =========================
file = st.file_uploader("Sube dataset principal", type=["csv", "xlsx"])

if file:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.session_state["df"] = df

# =========================
# 2. DATA PREVIEW
# =========================
if "df" in st.session_state:

    df = st.session_state["df"]

    st.subheader("Vista previa")
    st.dataframe(df.head())

    # =========================
    # 3. TRANSFORMACIONES
    # =========================
    st.subheader("Transformaciones")

    col = st.selectbox("Columna", df.columns)
    accion = st.selectbox(
        "Acción",
        ["Mayúsculas", "Minúsculas", "Capitalizar", "Eliminar espacios", "Entero", "Float"]
    )

    if st.button("Aplicar transformación"):
        df = aplicar_transformacion(df, col, accion)
        st.session_state["df"] = df
        st.success("OK")

    # =========================
    # 4. NUEVA COLUMNA
    # =========================
    st.subheader("Nueva columna")

    new_col = st.text_input("Nombre")

    col1 = st.selectbox("Columna 1", df.columns, key="n1")
    col2 = st.selectbox("Columna 2", df.columns, key="n2")

    if st.button("Concatenar"):
        df[new_col] = df[col1].astype(str) + " " + df[col2].astype(str)
        st.session_state["df"] = df

    # =========================
    # 5. LIMPIEZA MUNICIPIO
    # =========================
    st.subheader("Normalización municipio")

    col_mun = st.selectbox("Columna municipio", df.columns)

    if st.button("Generar municipio_clean"):
        df["municipio_clean"] = df[col_mun].apply(limpiar_texto)
        st.session_state["df"] = df

    # =========================
    # 6. MAPPING PROVINCIAS
    # =========================
    if "municipio_clean" in df.columns:

        st.subheader("Mapping Provincias")

        municipios = sorted(df["municipio_clean"].dropna().unique())

        map_df = cargar_mapa(municipios)

        map_df = st.data_editor(map_df, num_rows="dynamic")

        if st.button("Guardar mapa"):
            guardar_mapa(map_df)
            st.success("Mapa guardado")

        if st.button("Aplicar provincias"):
            df = aplicar_mapa(df, map_df)
            st.session_state["df"] = df

    # =========================
    # 7. MERGE
    # =========================
    st.subheader("Merge con archivo externo")

    ref = st.file_uploader("Sube referencia", type=["csv", "xlsx"], key="ref")

    if ref:
        if ref.name.endswith(".csv"):
            df_ref = pd.read_csv(ref)
        else:
            df_ref = pd.read_excel(ref)

        col_df = st.selectbox("Columna base", df.columns)
        col_ref = st.selectbox("Columna referencia", df_ref.columns)

        cols_add = st.multiselect("Columnas a agregar", df_ref.columns)

        how = st.selectbox("Tipo join", ["left", "inner"])

        if st.button("Aplicar merge"):
            df = hacer_merge(df, df_ref, col_df, col_ref, cols_add, how)
            st.session_state["df"] = df
            st.success("Merge aplicado")

    # =========================
    # 8. DESCARGA
    # =========================
    st.subheader("Descargar")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button("Descargar CSV", csv, "output.csv", "text/csv")
