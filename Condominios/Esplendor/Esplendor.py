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
        "Repasse 5% Garantidora": None,
        "Água e Esgoto": None,
        "Energia / Elétrica": None,
        "Dif. Cob. Repasse Garantidora": None,
        "Salão de Festas": None,
        "Churrasqueira": None,
        "Desconto Salão de Festas": None,
        "Honorários - Ação Águas do Rio": None,
        "Multa Infração Convenção/Reg. Interno": None,

        "Contratação do Zelador e Auxiliar de Portaria - Aprovado AGE 06.04.25": None,
        "Assessoria Jurídica - AGE 31.07.25": None,
        "Ressarcimento Dano Reparo Portão": None,
        "Diferença Cobrada a Menor": None,
        "Segunda Via do Cartão": None,
        "Devolução da Diferença Cobrada a Maior": None,
        "Estorno do Pagamento do Salão": None,
        "Cota Extra - Enxoval": None,
        "Cota Paga - Protest": None,
        "Devolução Parte Cobrança Uso de Espaço" : None,
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
      r"BLOCO\s+(\d+)\s*-\s*BL\s+(\d+)\s*-\s*AP\s+(\d+)",
      linha,
      re.IGNORECASE
    )

    if resultado:

        if apartamento["Unidade"]:
            apartamentos.append(apartamento.copy())

        apartamento.clear()
        apartamento.update(novo_apartamento())

        bloco = resultado.group(2)
        unidade = resultado.group(3)

        apartamento["Bloco"] = bloco
        apartamento["Unidade"] = f"BL {bloco}- AP {unidade}"

        return

#Assessoria Juridica
    resultado = re.search(
      r"ASSESSORIA JUR[IÍ]DICA\s*-\s*(?:APROVADO\s+)?AGE\s*31\.07\.25.*?R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento[
          "Assessoria Jurídica - AGE 31.07.25"
        ] = converter_valor(resultado.group(1))
        return

# Cobtratação do zelador e auxiliar de portaria
    resultado = re.search(
      r"CONTRATAÇÃO DO ZELADOR E AUXILIAR DE PORTARIA"
      r"(?=.*APROVADO)(?=.*AGE\s+06\.04\.25)"
      r".*?R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        valor = resultado.group(1) or resultado.group(2)

        apartamento[
          "Contratação do Zelador e Auxiliar de Portaria - Aprovado AGE 06.04.25"
        ] = converter_valor(valor)
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

# Repasse 5% Garantidora
    resultado = re.search(
      r"REPASSE 5% GARANTIDORA.*?R\$\s*(-?[\d.]+,\d+)",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Repasse 5% Garantidora"] = converter_valor(
            resultado.group(1)
        )
        return

# Água e esgoto
    resultado = re.search(
      r"(?:AGUA/ESGOTO\s*->\s*AGUA/ESGOTO.*?|^\s*[ÁA]GUA E ESGOTO\s+)R\$\s*([\d.]+,\d{2})",
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
       r"ENERGIA ELETRICA\s*->\s*ENERGIA ELETRICA.*?R\$\s*(-?[\d.]+,\d+)",
       linha,
       re.IGNORECASE
    )

    if resultado:
        apartamento["Energia / Elétrica"] = converter_valor(
            resultado.group(1)
        )
        return

# DIF. COB. REPASSE GARANTIDORA
    resultado = re.search(
      r"DIF\.COB\.REPASSE GARANTIDORA.*?(-?)R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        valor = converter_valor(resultado.group(2))

        if resultado.group(1) == "-":
            valor = -valor

        apartamento["Dif. Cob. Repasse Garantidora"] = valor
        return

# Churrasqueira
    resultado = re.search(
      r"USO\s+CHURRASQUEIRA.*?R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Churrasqueira"] = converter_valor(
            resultado.group(1)
        )
        return

#Devolução parte cobrança uso de espaço

    resultado = re.search(
      r"DEV\.PARTE COB\. USO DE ESP[EÊ]ÇO.*?(-?)R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        valor = converter_valor(resultado.group(2))

        if resultado.group(1) == "-":
            valor = -valor

        apartamento["Devolução Parte Cobrança Uso de Espaço"] = valor
        return

# Salão de Festas
    if "DESCONTO USO SALÃO DE FESTAS" not in linha.upper():

        resultado = re.search(
            r"^\s*(?:USO SAL[AÃ]O DE FESTAS|SAL[AÃ]O DE FESTAS\s*(?:#|->)\s*SAL[AÃ]O DE FESTAS).*?R\$\s*([\d.]+,\d{2})",
            linha,
            re.IGNORECASE
        )

        if resultado:
            apartamento["Salão de Festas"] = converter_valor(
                resultado.group(1)
            )
            return

# Desconto salão de festas
    if "DESCONTO USO SALÃO DE FESTAS" in linha.upper():

        resultado = re.search(
            r"DESCONTO USO SALÃO DE FESTAS.*?-R\$\s*([\d.]+,\d+)",
            linha,
            re.IGNORECASE
        )

        if resultado:
            apartamento["Desconto Salão de Festas"] = -converter_valor(
                resultado.group(1)
            )
            return

# Multa Infração Convenção/Reg. Interno

    resultado = re.search(
        r"MULTA\s+INFRAÇÃO.*?R\$\s*(-?[\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Multa Infração Convenção/Reg. Interno"] = converter_valor (
            resultado.group(1)
        )
        return

# Ressarcimento Dano Reparo Portão
    resultado = re.search(
      r"RESSARCIMENTO DANO REPARO.*?R\$\s*([\d.]+,\d+)",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Ressarcimento Dano Reparo Portão"] = (
            converter_valor(resultado.group(1))
        )
        return

#Diferença Cobrada a Menor
    resultado = re.search(
      r"^\s*DIFERENÇA COBRADA A MENOR.*?R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Diferença Cobrada a Menor"] = converter_valor(
            resultado.group(1)
        )
        return

# Segunda Via do Cartão
    resultado = re.search(
        r"^\s*2[ªº]?\s*VIA DO CART[AÃ]O.*?R\$\s*([\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Segunda Via do Cartão"] = converter_valor(
            resultado.group(1)
        )
        return

# Devolução da Diferença Cobrada a Maior
    resultado = re.search(
      r"^\s*DEVOLUÇÃO DA DIFERENÇA COBRADA A MAIOR.*?-\s*R\$\s*([\d.]+,\d{2})",
      linha,
      re.IGNORECASE
    )

    if resultado:
        apartamento["Devolução da Diferença Cobrada a Maior"] = -converter_valor(
            resultado.group(1)
        )
        return

# Estorno do Pagamento do Salão
    resultado = re.search (
         r"ESTORNO DO PAGAMENTO DO ALUGUEL DO SAL[AÃ]O.*?-\s*R\$\s*([\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Estorno do Pagamento do Salão"] = -converter_valor(
            resultado.group(1)
        )
        return

# Honorarios - Ação Aguas do Rio
    resultado = re.search(
        r"HONOR[ÁA]RIOS\s*-\s*AÇÃO EM FACE DA ÁGUAS DO RIO.*?R\$\s*([\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Honorários - Ação Águas do Rio"] = converter_valor(
            resultado.group(1)
        )
        return

# Cota Extra - Enxoval
    resultado = re.search(
        r"COTA EXTRA\s*-\s*ENXOVAL.*?R\$\s*([\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Cota Extra - Enxoval"] = converter_valor(
            resultado.group(1)
        )
        return

# Cota paga - Protest
    resultado = re.search(
        r"COTA PAGA ATRAV[ÉE]S DO BOLETO DA PROTEST.*?-\s*R\$\s*([\d.]+,\d{2})",
        linha,
        re.IGNORECASE
    )

    if resultado:
        apartamento["Cota Paga - Protest"] = -converter_valor(
            resultado.group(1)
        )
        return

def extrair_esplendor(caminho_pdf):

    apartamentos = []

    totais_pdf = {
        "Cota do mês": 0,
        "Fundo de Reserva": 0,
        "Repasse 5% Garantidora": 0,
        "Água e Esgoto": 0,
        "Energia / Elétrica": 0,
        "Dif. Cob. Repasse Garantidora": 0,
        "Salão de Festas": 0,
        "Churrasqueira": 0,
        "Desconto Salão de Festas": 0,
        "Multa Infração Convenção/Reg. Interno": 0,
        "Contratação do Zelador e Auxiliar de Portaria - Aprovado AGE 06.04.25": 0,
        "Assessoria Jurídica - AGE 31.07.25": 0,
        "Ressarcimento Dano Reparo Portão": 0,
        "Diferença Cobrada a Menor": 0,
        "Segunda Via do Cartão": 0,
        "Devolução da Diferença Cobrada a Maior": 0,
        "Estorno do Pagamento do Salão": 0,
        "Honorários - Ação Águas do Rio": 0,
        "Cota Extra - Enxoval": 0,
        "Cota Paga - Protest": 0,
        "Devolução Parte Cobrança Uso de Espaço": 0,

    }

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

            linhas = texto.split("\n")

            if bloco_pendente:

                for linha_atual in linhas[:5]:

                    resultado_unidade = re.match(
                       r"^\s*(\d{4})\b",
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
                if "BLOCO" in linha_upper:

                    if re.search(r"-\s*AP\s*$", linha, re.IGNORECASE):

                        if i + 1 < len(linhas):

                            proxima_linha = linhas[i + 1]

                            resultado = re.match(
                                r"^\s*(\d{4})\b",
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

                # Ressarcimento Dano Reparo Portão
                if (
                    "RESSARCIMENTO DANO REPARO" in linha.upper()
                    and "R$" not in linha
                    and i + 1 < len(linhas)
                ):
                    proxima = linhas[i + 1]

                    if "OUTROS CRÉDITOS" in proxima.upper():
                        linha = linha + " " + proxima

                # Fundo de Reserva
                if (
                    "FUNDO DE RESERVA -> FUNDO DE" in linha_upper
                    and "R$" not in linha
                    and i + 1 < len(linhas)
                ):
                    linha = linha + " " + linhas[i + 1]

                # Repasse e diferença de cobrança
                if (
                     "CONDOMÍNIO -> COTA EXTRA" in linha_upper
                     and i > 0
                ):
                    anterior = linhas[i - 1]

                    if "DIF.COB.REPASSE GARANTIDORA" in anterior.upper():
                        linha = anterior + " " + linha

                    elif "REPASSE 5% GARANTIDORA" in anterior.upper():
                        linha = anterior + " " + linha

                # Multa
                if (
                    "MULTA INFRAÇÃO" in linha.upper()
                    and "R$" not in linha
                    and i + 1 < len(linhas)
                ):
                    proxima = linhas[i + 1]

                    if re.match(r"^\s*R\$", proxima):
                        linha = linha + " " + proxima

                # Contratação do Zelador
                if (
                    "CONTRATAÇÃO DO ZELADOR" in linha_upper
                    and "R$" not in linha
                    and i + 2 < len(linhas)
                ):
                    linha = (
                        linha
                        + " "
                        + linhas[i + 1]
                        + " "
                        + linhas[i + 2]
                    )

                # Salão de Festas e Churrasqueira
                if (
                    "SALÃO DE FESTAS -> SALAO DE" in linha_upper
                    and i + 1 < len(linhas)
                ):
                    proxima = linhas[i + 1]

                    if (
                        "USO CHURRASQUEIRA" in proxima.upper()
                        or "USO SALÃO DE FESTAS" in proxima.upper()
                        or "USO SALAO DE FESTAS" in proxima.upper()
                    ):
                        linha = linha + " " + proxima

                processar_linha(
                    linha,
                    apartamento,
                    apartamentos
              )

    # Adiciona o ultimo apartamento
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

    df = pd.DataFrame(apartamentos)

    return df, totais_pdf

def processar_totais(texto, totais_pdf):

    resultado = re.search(
       r"ÁGUA E ESGOTO\s+R\$\s*([\d.]+,\d+)",
       texto,
       re.IGNORECASE
    )

    if resultado:
        totais_pdf["Água e Esgoto"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
      r"\bCONDOMÍNIO(?:\s+\d{2}/\d{4})?\s+R\$\s*([\d.]+,\d{2})",
      texto,
      re.IGNORECASE
    )
    if resultado:
        totais_pdf["Cota do mês"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
       r"DESCONTO USO SALÃO DE FESTAS\s+-R\$\s*([\d.]+,\d+)",
       texto,
       re.IGNORECASE
    )
    if resultado:
        totais_pdf["Desconto Salão de Festas"] = -converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
      r"DIF\.COB\.REPASSE GARANTIDORA"
      r".*?(-?)R\$\s*([\d.]+,\d{2})",
      texto,
      re.IGNORECASE
    )
    if resultado:

        valor = converter_valor(resultado.group(2))

        if resultado.group(1) == "-":
            valor *= -1

        totais_pdf["Dif. Cob. Repasse Garantidora"] = valor

    resultado = re.search(
      r"ENERGIA/ELETRICA\s+R\$\s*([\d.]+,\d+)",
      texto,
      re.IGNORECASE
    )

    if resultado:
        totais_pdf["Energia / Elétrica"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
      r"\bFUNDO DE RESERVA(?:\s+\d{2}/\d{4})?\s+R\$\s*([\d.]+,\d{2})",
      texto,
      re.IGNORECASE
    )
    if resultado:
        totais_pdf["Fundo de Reserva"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
      r"MULTA INFRAÇÃO(?:/REGULAMENTO|\s+CONVENÇÃO/REG\.?\s*INTERNO).*?R\$\s*(-?[\d.]+,\d{2})",
      texto,
      re.IGNORECASE
    )
    if resultado:
        totais_pdf["Multa Infração Convenção/Reg. Interno"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
      r"REPASSE 5% GARANTIDORA.*?R\$\s*([\d.]+,\d+)",
      texto,
      re.IGNORECASE
    )
    if resultado:
        totais_pdf["Repasse 5% Garantidora"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
        r"USO CHURRASQUEIRA.*?R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )
    if resultado:
        totais_pdf["Churrasqueira"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
       r"(?<!DESCONTO )(?:USO SAL[AÃ]O DE FESTAS|SAL[AÃ]O DE FESTAS\s*#\s*SAL[AÃ]O DE FESTAS)(?:\s+\d{2}/\d{4})?\s+R\$\s*([\d.]+,\d{2})",
       texto,
       re.IGNORECASE
    )
    if resultado:
        totais_pdf["Salão de Festas"] = converter_valor(
            resultado.group(1)
        )

    resultado = re.search(
    r"CONTRATAÇÃO DO ZELADOR E AUXILIAR DE PORTARIA\s*-\s*APROVADO[\s\S]{0,180}?R\$\s*([\d.]+,\d{2})",
    texto,
    re.IGNORECASE
    )

    if resultado:
        totais_pdf[
            "Contratação do Zelador e Auxiliar de Portaria - Aprovado AGE 06.04.25"
        ] = converter_valor(resultado.group(1))

    # Assessoria Jurídica
    resultado = re.search(
    r"ASSESSORIA JUR[IÍ]DICA\s*-\s*(?:APROVADO\s+)?AGE\s*31\.07\.25.*?R\$\s*([\d.]+,\d{2})",
    texto,
    re.IGNORECASE
    )

    if resultado:
        totais_pdf[
            "Assessoria Jurídica - AGE 31.07.25"
        ] = converter_valor(resultado.group(1))

    resultado = re.search(
        r"RESSARCIMENTO DANO REPARO PORTÃO.*?R\$\s*(-?[\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Ressarcimento Dano Reparo Portão"] = converter_valor(
            resultado.group(1)
        )

    # Diferença Cobrada a Menor
    resultado = re.search(
        r"DIFERENÇA COBRADA A MENOR.*?R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Diferença Cobrada a Menor"] = converter_valor(
            resultado.group(1)
        )

    # Segunda via do cartão
    resultado = re.search(
      r"2[ªº]?\s*VIA DO CART[AÃ]O.*?R\$\s*([\d.]+,\d{2})",
      texto,
      re.IGNORECASE
    )

    if resultado:
        totais_pdf["Segunda Via do Cartão"] = converter_valor(
            resultado.group(1)
        )

    # Devolução da Diferença Cobrada a Maior
    resultado = re.search(
        r"DEVOLUÇÃO DA DIFERENÇA COBRADA A MAIOR.*?-\s*R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Devolução da Diferença Cobrada a Maior"] = -converter_valor(
            resultado.group(1)
        )

    # Estorno do Pagamento do Salão
    resultado = re.search(
        r"ESTORNO DO PAGAMENTO DO ALUGUEL DO SAL[AÃ]O.*?-\s*R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Estorno do Pagamento do Salão"] = -converter_valor(
            resultado.group(1)
        )

    # Honorarios - Ação Aguas do Rio
    resultado = re.search(
        r"HONOR[ÁA]RIOS\s*-\s*AÇÃO EM FACE DA ÁGUAS DO RIO.*?R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Honorários - Ação Águas do Rio"] = converter_valor(
            resultado.group(1)
        )

    #Cota Extra - Enxoval
    resultado = re.search(
        r"COTA EXTRA\s*-\s*ENXOVAL.*?R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Cota Extra - Enxoval"] = converter_valor(
            resultado.group(1)
        )

    # Cota paga - Protest
    resultado = re.search(
        r"COTA PAGA ATRAV[ÉE]S DO BOLETO DA PROTEST.*?-\s*R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:
        totais_pdf["Cota Paga - Protest"] = -converter_valor(
            resultado.group(1).replace("R$", "")
        )

    #Devolução parte cobrança uso de espaço

    resultado = re.search(
        r"DEV\.PARTE COB\. USO DE ESP[EÊ]ÇO.*?(-?)R\$\s*([\d.]+,\d{2})",
        texto,
        re.IGNORECASE
    )

    if resultado:

        valor = converter_valor(resultado.group(2))

        if resultado.group(1) == "-":
         valor = -valor

        totais_pdf["Devolução Parte Cobrança Uso de Espaço"] = valor

