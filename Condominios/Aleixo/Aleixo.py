#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

#-------------------------------------------------------------------------------------------------------#

#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento(parcelas):
    return{
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "", #Salva o vencimento.

     "Cota do mês": None,
     "Fundo de Reserva" : None,
     "Água e Esgoto" : None,

     f"Taxa Extra Ref. Empréstimo - {parcelas['emprestimo_60']}": None,
     f"Taxa Extra Ref. Empréstimo - {parcelas['emprestimo_48']}": None,
     f"Taxa Extra Ref. Substituição da Coluna de Água - {parcelas['coluna_agua']}": None,
     f"Cota Extra Obra Reestru. Laje 406 - {parcelas['laje']}": None,

    }

#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):

    if apartamento["Unidade"]:
       apartamentos.append(apartamento.copy())

#-------------------------------------------------------------------------------------------------------#

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def identificar_parcelas(texto):

    parcelas = {
        "emprestimo_60": "",
        "emprestimo_48": "",
        "coluna_agua": "",
        "laje": ""
    }

    resultado = re.search(
        r"Taxa Extra ref\. Empréstimo.*?(\d+)/60",
        texto,
        re.IGNORECASE
    )

    if resultado:
        parcelas["emprestimo_60"] = (
            f"{int(resultado.group(1)):02d}/60"
        )

    resultado = re.search(
      r"Taxa Extra ref\. Empréstimo.*?(\d+)/48",  
      texto,
      re.IGNORECASE
    )

    if resultado:
        parcelas["emprestimo_48"] = (
            f"{int(resultado.group(1)):02d}/48"
        )

    resultado = re.search(
       r"substitui[çc][aã]o da coluna de [áa]gua.*?(\d+)/(\d+)",
       texto,
       re.IGNORECASE | re.DOTALL 
    )

    if resultado:
        parcelas["coluna_agua"] = (
            f"{int(resultado.group(1)):02d}/"
            f"{int(resultado.group(2)):02d}"  
        )

    resultado = re.search(
        r"reestrutura[çc][aã]o da laje.*?(\d+)/(\d+)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if resultado:
        parcelas["laje"] = (
          f"{int(resultado.group(1)):02d}/"
          f"{int(resultado.group(2)):02d}"  
        )

    return parcelas

def processar_linha(linha, apartamento, apartamentos, parcelas):

    #IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"APT-(\d{4}).*?(\d{2}/\d{2}/\d{4})", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento(parcelas))

        apartamento["Unidade"] = f"APT-{resultado.group(1)}"
        apartamento["Vencimento"] = resultado.group(2)

    # Cota do Mes
    resultado_cota = re.search(
        r"(-?[\d\.]+,\d{2})$",
        linha
    )

    if "Taxa Condominial" in linha and resultado_cota:

        valor = converter_valor(
            resultado_cota.group(1)
        )

        if apartamento["Cota do mês"] is None:
            apartamento["Cota do mês"] = valor
        else:
            apartamento["Cota do mês"] += valor



    # Agua
    if "Agua e Esgoto" in linha:
        resultado_agua = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_agua:
            valor = converter_valor(resultado_agua.group(1))

            if apartamento["Água e Esgoto"] is None:
                apartamento["Água e Esgoto"] = valor
            else:
                apartamento["Água e Esgoto"] += valor


    # Fundo de Reserva
    if "Fundo de Reserva" in linha:
        resultado_fundo = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_fundo:
            valor = converter_valor(resultado_fundo.group(1))

            if apartamento["Fundo de Reserva"] is None:
                apartamento["Fundo de Reserva"] = valor
            else:
                apartamento["Fundo de Reserva"] += valor


    # Taxa Extra Ref. Empréstimo - XX/6
    if "Taxa Extra ref. Empréstimo" in linha and re.search(r"\d+/60", linha):
        resultado_taxa_extra = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_taxa_extra:
            valor = converter_valor(resultado_taxa_extra.group(1))

            nome_coluna = (
                f"Taxa Extra Ref. Empréstimo - {parcelas['emprestimo_60']}"
            )

            if apartamento[nome_coluna] is None:
                apartamento[nome_coluna] = valor
            else:
                apartamento[nome_coluna] += valor


      # Taxa Extra Ref. Empréstimo - XX/48
    if "Taxa Extra ref. Empréstimo" in linha and re.search(r"\d+/48", linha):
        resultado_emprestimo = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_emprestimo:
            valor = converter_valor(resultado_emprestimo.group(1))

            nome_coluna = (
                f"Taxa Extra Ref. Empréstimo - {parcelas['emprestimo_48']}"
            )

            if apartamento[nome_coluna] is None:
                apartamento[nome_coluna] = valor
            else:
                apartamento[nome_coluna] += valor

#Taxa Extra Coluna Agua
    if "Taxa extra ref.substituiçao da coluna de água" in linha:

        resultado_coluna_agua = re.search(
            r"\d+/\d+\s+(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_coluna_agua:
            valor = converter_valor(
                resultado_coluna_agua.group(1)
            )

            nome_coluna = (
                f"Taxa Extra Ref. Substituição da Coluna de Água - "
                f"{parcelas['coluna_agua']}"
            )

            if apartamento[nome_coluna] is None:
                apartamento[nome_coluna] = valor
            else:
                apartamento[nome_coluna] += valor


#Cota Extra - Laje
    if "Cota Extra -da obra de reestruturação da laje" in linha:

        resultado_cota_extra_laje = re.search(
            r"\d+/\d+\s+(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_cota_extra_laje:
            valor = converter_valor(
                resultado_cota_extra_laje.group(1)
            )

            nome_coluna = (
                f"Cota Extra Obra Reestru. Laje 406 - "
                f"{parcelas['laje']}"
            )

            if apartamento[nome_coluna] is None:
                apartamento[nome_coluna] = valor
            else:
                apartamento[nome_coluna] += valor


def processar_totais(linha,totais_pdf):

    #Cota do mes
    if " - Cotas Condominiais " in linha:

        resultado = re.search(
           r"(-?[\d\.]+,\d{2})$", 
           linha
        )

        if resultado:
            totais_pdf["Cota do mês"] = converter_valor(
                resultado.group(1)
            )

    #Agua e esgoto
    if " - Água " in linha:

        resultado = re.search(
           r"(-?[\d\.]+,\d{2})$",
           linha 
        )

        if resultado:
           totais_pdf["Água e Esgoto"] = converter_valor(
                resultado.group(1)
           )

    # Emprestimos /48
    if " - Emprestimo " in linha:

        resultado = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado:
            totais_pdf["Emprestimo"] = converter_valor(
                resultado.group(1)
            )

    # Fundo de Reserva
    if " - Fundo de Reserva " in linha:

        resultado = re.search(
           r"(-?[\d\.]+,\d{2})$",
           linha 
        )

        if resultado:
           totais_pdf["Fundo de Reserva"] = converter_valor(
                resultado.group(1)
            )

    # Emprestimos /60
    if  " - Taxa Extra ref. Empréstimo " in linha:

        resultado = re.search(
          r"(-?[\d\.]+,\d{2})$",
          linha  
        )

        if resultado:
            totais_pdf["Taxa Extra Ref. Empréstimo"] = converter_valor(
                resultado.group(1)
            )

    # Cota extra consolidada
    if " - Cota Extra " in linha:

        resultado = re.search(
           r"(-?[\d\.]+,\d{2})$",
           linha 
        )

        if resultado:
          totais_pdf["Cota Extra"] = converter_valor(
                resultado.group(1)
            )


def extrair_aleixo(caminho_pdf):

    
    apartamentos = []

    totais_pdf = {}

    with pdfplumber.open(caminho_pdf) as pdf:

        texto_completo = ""

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""
            texto_completo += texto + "\n"

        parcelas = identificar_parcelas(texto_completo)

        print("\nPARCELAS ENCONTRADAS:")
        print(parcelas)

        apartamento = novo_apartamento(parcelas)

        for linha in texto_completo.splitlines():


            processar_linha(
                linha,
                apartamento,
                apartamentos,
                parcelas
            )

            processar_totais(
                linha,
                totais_pdf
            )

    salvar_apartamento(
        apartamento,
        apartamentos
    )


    df = pd.DataFrame(apartamentos)

    return df, totais_pdf