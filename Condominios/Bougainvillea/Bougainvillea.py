#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

def novo_apartamento():
    return {
        "Bloco" : "", #Salva o bloco.
        "Unidade" : "", #Salva a unidade.
        "Vencimento" : "", #Salva o vencimento.

        "Cota do mês": None,
        "Fundo de Reserva": None,
        "Água e Esgoto": None,
        "Energia / Elétrica": None,
    }

#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):

#So salva se existir uma unidade cadastrada.
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_linha(linha, apartamento, apartamentos):

    #novo apartamento
    resultado = re.search(
      r"BOUGA[I]?NVILLEA\s+II\s*-\s*AP\s+(\d{4})\b",
      linha,
      re.IGNORECASE
    )

    if resultado:

        if apartamento["Unidade"]:
            apartamentos.append(apartamento.copy())

        apartamento.clear()
        apartamento.update(novo_apartamento())

        bloco = "1"
        unidade = resultado.group(1)

        apartamento["Bloco"] = bloco
        apartamento["Unidade"] = f"AP {unidade}"

        return

# Cota do mes
    resultado = re.search(
       r"(?:CONDOMÍNIO\s*->\s*CONDOMÍNIO.*?|^\s*CONDOMÍNIO(?:\s+\d{2}/\d{4})?\s+)R\$\s*([\d.]+,\d{2})",
       linha,
       re.IGNORECASE
    )

    if resultado:
        apartamento["Cota do mês"] = converter_valor(
            resultado.group(1)
        )
        return

# Fundo de reserva
    resultado = re.search(
      r"(?:FUNDO DE RESERVA\s*->.*?FUNDO DE RESERVA.*?|^\s*FUNDO DE RESERVA(?:\s+\d{2}/\d{4})?\s+)R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Fundo de Reserva"] = converter_valor(
            resultado.group(1)
        )
        return

# Água e esgoto
    resultado = re.search(
      r"(?:(?:CONDOMÍNIO|AGUA/ESGOTO)\s*->\s*AGUA/ESGOTO.*?|^\s*[ÁA]GUA E ESGOTO\s+)R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Água e Esgoto"] = converter_valor(
            resultado.group(1)
        )
        return

# Energia Eletrica
    resultado = re.search(
       r"(?:CONDOMÍNIO|ENERGIA\s+EL[ÉE]TRICA)\s*->\s*ENERGIA\s+EL[ÉE]TRICA.*?R\$\s*(-?[\d.]+,\d+)",
       linha,
       re.IGNORECASE
    )

    if resultado:
        apartamento["Energia / Elétrica"] = converter_valor(
            resultado.group(1)
        )
        return

def extrair_bougainvillea(caminho_pdf):

    apartamentos = []

    totais_pdf = {
        "Cota do mês": 0,
        "Fundo de Reserva": 0,
        "Água e Esgoto": 0,
        "Energia / Elétrica": 0,
    }

    vencimento = ""
    apartamento = novo_apartamento()

    bloco_pendente = None

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if not texto:
                continue

            # Não processa a página de totais como de fosse apartamento
            if "RESUMO DO QUADRO DE RATEIO" in texto.upper():
                processar_totais(
                    texto,
                    totais_pdf
                )
                continue

            resultado_vencimento = re.search(
                r"QUADRO DE RATEIO\s*-\s*(\d{2}/\d{2}/\d{4})",
                texto,
                re.IGNORECASE
            )

            if resultado_vencimento:
                vencimento = resultado_vencimento.group(1)

            linhas = texto.split("\n")

            if bloco_pendente:

                for linha_atual in linhas[:12]:

                    resultado_unidade = re.match(
                       r"^\s*(\d{4})\s*(?=\(FR\.|HIERARQUIA|$)",
                       linha_atual
                    )

                    if resultado_unidade:

                        linha_completa = (
                            bloco_pendente + " " + resultado_unidade.group(1)
                        )

                        processar_linha(
                            linha_completa,
                            apartamento,
                            apartamentos
                        )

                        bloco_pendente = None
                        break

            for i, linha in enumerate(linhas):

                linha_upper = linha.upper()

                # Cabeçalho do apartamento
                if re.search(r"BOUGA[I]?NVILLEA\s+II\s*-\s*AP", linha, re.IGNORECASE):

                    if re.search(r"-\s*AP\s*$", linha, re.IGNORECASE):

                        if i + 1 < len(linhas):

                            proxima_linha = linhas[i + 1]

                            resultado = re.match(
                                r"^\s*(\d{4})\s*(?=\(FR\.|HIERARQUIA|$)",
                                proxima_linha
                            )

                            if resultado:
                                linha = linha + " " + resultado.group(1)

                            else:

                                bloco_pendente = linha

                                continue

                        else:

                            bloco_pendente = linha

                            continue

                processar_linha(
                    linha,
                    apartamento,
                    apartamentos
              )

    # Adiciona o ultimo apartamento
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

    df = pd.DataFrame(apartamentos)

    df["Vencimento"] = vencimento

    return df, totais_pdf

def processar_totais(texto, totais_pdf):

    resultado = re.search(
        r"(?:(?:CONDOMÍNIO|AGUA/ESGOTO)\s*->\s*AGUA/ESGOTO|CONDOMÍNIO\s*->\s*AGUA/ESGOTO|ÁGUA E ESGOTO)[^\n]*?R\$\s*([\d.]+,\d{2})(?:\s+R\$\s*([\d.]+,\d{2}))?\s*$",
        texto,
        re.IGNORECASE | re.MULTILINE
    )

    if resultado:
        totais_pdf["Água e Esgoto"] = converter_valor(
            resultado.group(2) or resultado.group(1)
        )

    resultado = re.search(
        r"(?:CONDOMÍNIO\s*->\s*CONDOMÍNIO|^\s*CONDOMÍNIO(?:\s+\d{2}/\d{4})?\s+(?=R\$))[^\n]*?R\$\s*([\d.]+,\d{2})(?:\s+R\$\s*([\d.]+,\d{2}))?\s*$",
        texto,
        re.IGNORECASE | re.MULTILINE
    )

    if resultado:
        totais_pdf["Cota do mês"] = converter_valor(
            resultado.group(2) or resultado.group(1)
        )

    resultado = re.search(
        r"(?:CONDOMÍNIO\s*->\s*ENERGIA\s+EL[ÉE]TRICA|ENERGIA/ELETRICA)[^\n]*?R\$\s*([\d.]+,\d{2})(?:\s+R\$\s*([\d.]+,\d{2}))?\s*$",
        texto,
        re.IGNORECASE | re.MULTILINE
    )

    if resultado:
        totais_pdf["Energia / Elétrica"] = converter_valor(
            resultado.group(2) or resultado.group(1)
        )

    resultado = re.search(
        r"(?:FUNDO DE RESERVA)[^\n]*?R\$\s*([\d.]+,\d{2})(?:\s+R\$\s*([\d.]+,\d{2}))?\s*$",
        texto,
        re.IGNORECASE | re.MULTILINE
    )

    if resultado:
        totais_pdf["Fundo de Reserva"] = converter_valor(
            resultado.group(2) or resultado.group(1)
        )

