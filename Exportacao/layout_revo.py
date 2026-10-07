import pandas as pd

def montar_layout_revo(df, competencia):
    df_revo = pd.DataFrame(index=df.index)

    #Colunas obrigatorias do Revo

    if "Bloco" in df.columns:
        df_revo["Bloco"] = df["Bloco"]
    else:
        df_revo["Bloco"] = ""

    df_revo["Unidade"] = df["Unidade"]
    df_revo["Vencimento"] = df["Vencimento"]

    df_revo["Competencia"] = competencia

    df_revo["DescontoPontualidade"] = ""
    df_revo["Valor Negociado"] = ""
    df_revo["Livre2"] = ""
    df_revo["Livre3"] = ""
    df_revo["Livre4"] = ""
    df_revo["Livre5"] = ""

    df_revo["Cota do mês"] = df["Cota do mês"]

    colunas_fixas_origem = [
        "Bloco",
        "Unidade",
        "Vencimento",
        "Cota do mês",
    ]

    for coluna in df.columns:

        if coluna not in colunas_fixas_origem:
            df_revo[coluna] = df[coluna]

    return df_revo



