import pandas as pd
import os

PATH = "data/mapa_provincias.csv"

def cargar_mapa(municipios):
    if os.path.exists(PATH):
        return pd.read_csv(PATH)
    else:
        return pd.DataFrame({
            "municipio": municipios,
            "provincia": ""
        })


def guardar_mapa(df):
    df.to_csv(PATH, index=False)


def aplicar_mapa(df, map_df):
    map_dict = dict(zip(map_df["municipio"], map_df["provincia"]))
    df["Provincia"] = df["municipio_clean"].map(map_dict)
    df["Provincia"] = df["Provincia"].fillna("Sin Clasificar")
    return df
