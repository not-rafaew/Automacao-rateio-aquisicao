# Compara os totais do PDF com os totais calculados
def validar_totais(totais_pdf, totais_calculados):

    resultado = {}

    for verba, valor_pdf in totais_pdf.items():

        valor_calculado = totais_calculados.get(verba)

        if valor_calculado is None:
            resultado[verba] = False
            continue

        resultado[verba] = (
            round(valor_pdf, 2) ==
            round(valor_calculado, 2)
        )

    return resultado

# Calcula os totais das despesas
def calcular_totais(df, totais_pdf, condominio=None):

    totais_calculados ={}

    for verba in totais_pdf:

        # Regras específicas do Aleixo
        if condominio == "aleixo":

            if verba ==  "Cota Extra":

                coluna_agua = next(
                    (
                        coluna for coluna in df.columns
                        if coluna.startswith(
                            "Taxa Extra Ref. Substituição da Coluna de Água - "
                        )
                    ),
                    None
                )

                coluna_laje = next(
                    (
                        coluna for coluna in df.columns
                        if coluna.startswith(
                            "Cota Extra Obra Reestru. Laje 406 - "
                        )
                    ),
                    None
                )

                total_agua = 0
                total_laje = 0

                if coluna_agua is not None:
                    total_agua = df[coluna_agua].fillna(0).sum()

                if coluna_laje is not None:
                    total_laje = df[coluna_laje].fillna(0).sum()

                totais_calculados[verba] = (
                    total_agua + total_laje
                )

                continue

            elif verba in [
                "Taxa Extra Ref. Empréstimo",
                "Emprestimo"
            ]:

                parcela = (
                    "/60"
                    if verba == "Taxa Extra Ref. Empréstimo"
                    else "/48"
                )

                coluna = next(
                    (
                        coluna for coluna in df.columns
                        if coluna.startswith(
                            "Taxa Extra Ref. Empréstimo - "
                        )
                        and coluna.endswith(parcela)
                    ),
                    None
                )

                if coluna is not None:
                    totais_calculados[verba] = (
                        df[coluna].fillna(0).sum()
                    )
                continue

        # Regra padrão dos demais condomínios
        if verba in df.columns:

            totais_calculados[verba] = (
                df[verba].fillna(0).sum()
            )

    return totais_calculados

#Gera o relatório de validação
def gerar_validacao(df, totais_pdf, condominio=None):

    totais_calculados = calcular_totais(
        df,
        totais_pdf,
        condominio
    )

    resultado = validar_totais(
        totais_pdf,
        totais_calculados
    )

    relatorio = []

    for verba in totais_pdf:

        valor_pdf = round(float(totais_pdf[verba]), 2)

        valor_calculado = totais_calculados.get(verba)

        if valor_calculado is not None:
            valor_calculado = round(
                float(valor_calculado), 2
            )

        relatorio.append({
            "Verba": verba,
            "PDF": valor_pdf,
            "Calculado": valor_calculado,
            "Status": "OK" if resultado[verba] else "ERRO"
        })
    
    return relatorio

            
