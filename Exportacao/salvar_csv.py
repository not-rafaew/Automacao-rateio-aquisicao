def salvar_csv(df, caminho_saida):

    #Cria uma copia para preservar o DataFrame original
    df = df.copy()

    #Substitui valores zerados por vazio
    df = df.replace(0, None)

    #Preenche valores nulos
    df = df.fillna("")

    # Colunas que devem permanecer na exportação
    colunas_obrigatorias = [
        "Bloco",
        "Unidade",
        "Vencimento",
        "Competencia",
        "DescontoPontualidade",
        "Valor Negociado",
        "Livre2",
        "Livre3",
        "Livre4",
        "Livre5",
        "Cota do Mes" 
    ]

    colunas_manter = []

    for coluna in df.columns:

        if coluna in colunas_obrigatorias:
            colunas_manter.append(coluna)

        elif (df[coluna] != "").any():
            colunas_manter.append(coluna)

    df = df[colunas_manter]

    #Exportar para CSV
    df.to_csv(
        caminho_saida,
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig"
    )


