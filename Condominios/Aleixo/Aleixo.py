#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

#-------------------------------------------------------------------------------------------------------#

#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento():
    return{
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "", #Salva o vencimento.

     "Cota do Mes": None,
     "Agua" : None,
     "Emprestimo": None,
     "Fundo de Reserva" : None,
     "Taxa Extra ref. Emprestimo": None, 
     "Taxa Extra Coluna de Agua": None,
     "Cota Extra Laje": None,
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


def processar_linha(linha, apartamento, apartamentos):

    #IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"APT-(\d{4}).*?(\d{2}/\d{2}/\d{4})", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento())

        apartamento["Unidade"] = resultado.group(1)
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

        if apartamento["Cota do Mes"] is None:
            apartamento["Cota do Mes"] = valor
        else:
            apartamento["Cota do Mes"] += valor



    # Agua
    if "Agua e Esgoto" in linha:
        resultado_agua = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_agua:
            valor = converter_valor(resultado_agua.group(1))

            if apartamento["Agua"] is None:
                apartamento["Agua"] = valor
            else:
                apartamento["Agua"] += valor


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


    # Taxa Extra ref. Empréstimo
    if "Taxa Extra ref. Empréstimo" in linha and re.search(r"\d+/60", linha):
        resultado_taxa_extra = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_taxa_extra:
            valor = converter_valor(resultado_taxa_extra.group(1))

            if apartamento["Taxa Extra ref. Emprestimo"] is None:
                apartamento["Taxa Extra ref. Emprestimo"] = valor
            else:
                apartamento["Taxa Extra ref. Emprestimo"] += valor


      # Taxa Extra ref. Empréstimo
    if "Taxa Extra ref. Empréstimo" in linha and re.search(r"\d+/48", linha):
        resultado_emprestimo = re.search(
            r"(-?[\d\.]+,\d{2})$",
            linha
        )

        if resultado_emprestimo:
            valor = converter_valor(resultado_emprestimo.group(1))

            if apartamento["Emprestimo"] is None:
                apartamento["Emprestimo"] = valor
            else:
                apartamento["Emprestimo"] += valor

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

            if apartamento["Taxa Extra Coluna de Agua"] is None:
                apartamento["Taxa Extra Coluna de Agua"] = valor
            else:
                apartamento["Taxa Extra Coluna de Agua"] += valor


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

            if apartamento["Cota Extra Laje"] is None:
                apartamento["Cota Extra Laje"] = valor
            else:
                apartamento["Cota Extra Laje"] += valor


def processar_totais(linha,totais_pdf):

    # Cota do Mes
    resultado_cota_do_mes = re.search(
        r"1\.01\s*-\s*Cotas Condominiais.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_cota_do_mes:

        valor = converter_valor(
            resultado_cota_do_mes.group(1)
        )

        totais_pdf["Cota do Mes"] = valor

        return


    # Agua
    resultado_agua = re.search(
        r"1\.10\s*-\s*Água.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_agua:

        valor = converter_valor(
            resultado_agua.group(1)
        )

        totais_pdf["Agua"] = valor

        return

    # Fundo de Reserva
    resultado_fundo = re.search(
        r"1\.13\s*-\s*Fundo de Reserva.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_fundo:

        valor = converter_valor(
            resultado_fundo.group(1)
        )

        totais_pdf["Fundo de Reserva"] = valor

        return


    # Taxa Extra ref. Empréstimo
    resultado_taxa_extra = re.search(
        r"1\.21\s*-\s*Taxa Extra ref\. Empréstimo.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_taxa_extra:

        valor = converter_valor(
            resultado_taxa_extra.group(1)
        )

        totais_pdf["Taxa Extra ref. Emprestimo"] = valor

        return


    #Emprestimo
    resultado_emprestimo = re.search(
        r"1\.1004\s*-\s*Emprestimo.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_emprestimo:

        valor = converter_valor(
            resultado_emprestimo.group(1)
        )

        totais_pdf["Emprestimo"] = valor

        return


    #Cota Extra
    resultado_cota_extra = re.search(
        r"1\.56\s*-\s*Cota Extra.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_cota_extra:

        valor = converter_valor(
            resultado_cota_extra.group(1)
        )

        totais_pdf["Cota Extra"] = valor

        return


def extrair_aleixo(caminho_pdf):

    apartamentos = []
    apartamento = novo_apartamento()

    totais_pdf = {
        "Cota do Mes": 0,
        "Agua": 0,
        "Emprestimo": 0,
        "Fundo de Reserva": 0,
        "Taxa Extra ref. Emprestimo": 0,
        "Cota Extra": 0
    }

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():


                processar_linha(
                    linha,
                    apartamento,
                    apartamentos
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

