import pandas as pd
from utils.cleaning import limpiar_texto

def hacer_merge(df, df_ref, col_df, col_ref, cols_add, how="left"):
    
    df["key_clean"] = df[col_df].apply(limpiar_texto)
    df_ref["key_clean"] = df_ref[col_ref].apply(limpiar_texto)

    df_merge = pd.merge(
        df,
        df_ref[["key_clean"] + cols_add],
        on="key_clean",
        how=how
    )

    return df_merge
