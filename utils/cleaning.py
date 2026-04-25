import pandas as pd
import unicodedata
import re

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'[^a-z\s]', '', texto)
    texto = " ".join(texto.split())
    return texto


def aplicar_transformacion(df, col, accion):
    if accion == "Mayúsculas":
        df[col] = df[col].astype(str).str.upper()

    elif accion == "Minúsculas":
        df[col] = df[col].astype(str).str.lower()

    elif accion == "Capitalizar":
        df[col] = df[col].astype(str).str.title()

    elif accion == "Eliminar espacios":
        df[col] = df[col].astype(str).str.strip()

    elif accion == "Entero":
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    elif accion == "Float":
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
