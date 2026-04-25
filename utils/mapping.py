import pandas as pd

from utils.provincias import MAPA_PROVINCIAS


def cargar_mapa(municipios):
    return pd.DataFrame(
        {
            "municipio": municipios,
            "provincia": [MAPA_PROVINCIAS.get(municipio, "") for municipio in municipios],
        }
    )


def guardar_mapa(df):
    """Compatibilidad hacia atrás: el mapa ahora es interno y no se guarda a CSV."""
    return df


def aplicar_mapa(df, map_df=None):
    if map_df is not None:
        map_dict = dict(zip(map_df["municipio"], map_df["provincia"]))
    else:
        map_dict = MAPA_PROVINCIAS

    df["Provincia"] = df["municipio_clean"].map(map_dict)
    df["Provincia"] = df["Provincia"].fillna("Sin Clasificar")
    return df
