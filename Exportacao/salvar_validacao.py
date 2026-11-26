import pandas as pd

def salvar_validacao(relatorio, caminho_saida):

    df_validacao = pd.DataFrame (
        relatorio,
        columns=["Verba", "PDF", "Calculado", "Status"]
    )

    aprovado = bool(relatorio) and all(
        verba["Status"] == "OK"
        for verba in relatorio
    )

    df_validacao.loc[len(df_validacao)] = {
        "Verba": "VALIDAÇÃO GERAL",
        "PDF": None,
        "Calculado": None,
        "Status": "APROVADA" if aprovado else "REPROVADA"
    }

    df_validacao.to_excel(caminho_saida, index=False)