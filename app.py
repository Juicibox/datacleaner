import os
from pathlib import Path

import streamlit as st
import pandas as pd

from utils.cleaning import aplicar_transformacion, limpiar_texto
from utils.mapping import cargar_mapa, aplicar_mapa
from utils.merge import hacer_merge

st.set_page_config(layout="wide")
st.title("Data Wrangling App")

CACHE_PATH = Path(".cache/working_df.pkl")


def guardar_df_en_cache(df: pd.DataFrame) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(CACHE_PATH)


def cargar_df_desde_cache():
    if CACHE_PATH.exists():
        return pd.read_pickle(CACHE_PATH)
    return None


def actualizar_df(df: pd.DataFrame) -> None:
    st.session_state["df"] = df
    guardar_df_en_cache(df)


# Si existe cache y todavía no hay dataframe en memoria, lo recuperamos.
if "df" not in st.session_state:
    cached_df = cargar_df_desde_cache()
    if cached_df is not None:
        st.session_state["df"] = cached_df
        st.session_state["source_file_id"] = "cache"

# =========================
# 1. CARGA
# =========================
file = st.file_uploader("Sube dataset principal", type=["csv", "xlsx"])

if file:
    file_id = (file.name, file.size)

    # Solo recargamos el DataFrame si cambia el archivo de origen.
    if st.session_state.get("source_file_id") != file_id:
        if file.name.endswith(".csv"):
            df_uploaded = pd.read_csv(file)
        else:
            df_uploaded = pd.read_excel(file)

        actualizar_df(df_uploaded)
        st.session_state["source_file_id"] = file_id

if "df" in st.session_state:

    df = st.session_state["df"]

    st.subheader("Vista previa")
    st.dataframe(df.head())

    # =========================
    # 3. TRANSFORMACIONES
    # =========================
    st.subheader("Transformaciones")

    cols_transformacion = st.multiselect(
        "Columnas",
        df.columns,
        default=[df.columns[0]] if len(df.columns) else []
    )
    accion = st.selectbox(
        "Acción",
        ["Mayúsculas", "Minúsculas", "Capitalizar", "Eliminar espacios", "Entero", "Float"]
    )

    if st.button("Aplicar transformación"):
        if not cols_transformacion:
            st.warning("Selecciona al menos una columna.")
        else:
            for col in cols_transformacion:
                df = aplicar_transformacion(df, col, accion)
            actualizar_df(df)
            st.success("Transformación aplicada")

    # =========================
    # 4. NUEVA COLUMNA
    # =========================
    st.subheader("Nueva columna")

    new_col = st.text_input("Nombre")

    col1 = st.selectbox("Columna 1", df.columns, key="n1")
    col2 = st.selectbox("Columna 2", df.columns, key="n2")

    if st.button("Concatenar"):
        df[new_col] = df[col1].astype(str) + " " + df[col2].astype(str)
        actualizar_df(df)

    # =========================
    # 5. LIMPIEZA MUNICIPIO
    # =========================
    st.subheader("Normalización municipio")

    col_mun = st.selectbox("Columna municipio", df.columns)

    if st.button("Generar municipio_clean"):
        df["municipio_clean"] = df[col_mun].apply(limpiar_texto)
        actualizar_df(df)

    # =========================
    # 6. MAPPING PROVINCIAS
    # =========================
    if "municipio_clean" in df.columns:

        st.subheader("Mapping Provincias")
        st.caption("El mapeo se toma desde un diccionario interno (más rápido que CSV/JSON para esta app).")

        municipios = sorted(df["municipio_clean"].dropna().unique())
        map_df = cargar_mapa(municipios)
        map_df = st.data_editor(map_df, num_rows="dynamic", key="map_editor")

        if st.button("Guardar mapa"):
            guardar_mapa(map_df)
            st.success("Mapa guardado")

        if st.button("Aplicar provincias"):
            df = aplicar_mapa(df, map_df)
            actualizar_df(df)
            st.success("Provincias aplicadas")

    # =========================
    # 7. MERGE
    # =========================
    st.subheader("Merge con archivo externo")

    ref = st.file_uploader("Sube referencia (opcional, por defecto Data/loc.csv)", type=["csv", "xlsx"], key="ref")

    df_ref = None

    if ref:
        if ref.name.endswith(".csv"):
            df_ref = pd.read_csv(ref)
        else:
            df_ref = pd.read_excel(ref)
        st.caption("Usando archivo de referencia subido manualmente.")
    else:
        default_ref_path = "Data/loc.csv"
        if os.path.exists(default_ref_path):
            df_ref = pd.read_csv(default_ref_path)
            st.caption(f"Usando archivo de referencia por defecto: {default_ref_path}")

    if df_ref is not None:
        if "Municipio" in df_ref.columns and "municipio_clean" not in df_ref.columns:
            df_ref["municipio_clean"] = df_ref["Municipio"].apply(limpiar_texto)

        col_df_default = list(df.columns).index("municipio_clean") if "municipio_clean" in df.columns else 0

        if "municipio_clean" in df_ref.columns:
            col_ref_default = list(df_ref.columns).index("municipio_clean")
        else:
            col_ref_default = 0

        col_df = st.selectbox("Columna base", df.columns, index=col_df_default)
        col_ref = st.selectbox("Columna referencia", df_ref.columns, index=col_ref_default)

        cols_add = st.multiselect("Columnas a agregar", df_ref.columns)

        how = st.selectbox("Tipo join", ["left", "inner"])

        if st.button("Aplicar merge"):
            df = hacer_merge(df, df_ref, col_df, col_ref, cols_add, how)
            actualizar_df(df)
            st.success("Merge aplicado")
    else:
        st.info("No se encontró archivo externo. Sube uno o crea Data/loc.csv")

    # =========================
    # 8. DESCARGA
    # =========================
    st.subheader("Descargar")

    st.markdown("**Quitar columnas antes de descargar (opcional)**")
    cols_drop = st.multiselect("Columnas a eliminar", df.columns, key="drop_cols")
    if st.button("Aplicar eliminación de columnas"):
        if cols_drop:
            df = df.drop(columns=cols_drop, errors="ignore")
            actualizar_df(df)
            st.success("Columnas eliminadas")
        else:
            st.info("No seleccionaste columnas para eliminar")

    st.markdown("**Vista previa final antes de descargar**")
    filas_preview = st.slider("Filas a previsualizar", min_value=5, max_value=100, value=10, step=5)
    st.dataframe(df.head(filas_preview))

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button("Descargar CSV", csv, "output.csv", "text/csv")

    if st.button("Limpiar cache local"):
        if CACHE_PATH.exists():
            CACHE_PATH.unlink()
        st.success("Cache eliminada")
