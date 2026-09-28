#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

def novo_apartamento():
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "",

     "Cota do Mes": None,
     "Rateio Extra": None,
     "Fundo de Reserva" : None,
     "Gas" : None, 
    }

def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def salvar_apartamento(apartamento, apartamentos):
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())


def identificar_verbas(linha):

    if "Unidade/Bloco" not in linha:
        return None

    verbas_encontradas = []

    nomes_pdf = {
        "Rateio Extra": "Rateio Extra",
        "Fundo de Reserva": "Fundo de Reserva",
        "Condomínio": "Cota do Mes",
        "Gás": "Gas"
    }

    for nome_pdf, nome_sistema in nomes_pdf.items():

        posicao = linha.find(nome_pdf)

        if posicao != -1:
            verbas_encontradas.append(
                (posicao, nome_sistema)
            )

    verbas_encontradas.sort()

    verbas = [
        nome for posicao, nome in verbas_encontradas
    ]

    print ("VERBAS ENCONTRADAS:")
    print (verbas)

    return verbas


def processar_linha(linha, apartamentos, verbas_ativas):

    if not verbas_ativas:
        return

    resultado = re.fullmatch(
        r"(\d+)\s+Bloco\s+(\d+)\s+(\d{2}/\d{2}/\d{4})\s+(.+)",
        linha.strip()
    )

    if not resultado:
        return

    valores = re.findall(
        r"-?[\d\.]+,\d{2}",
        resultado.group(4)
    )

    # Precisa ter:
    # quantidade de verbas + o Total
    if len(valores) != len(verbas_ativas) + 1:
        return

    apartamento = novo_apartamento()

    apartamento["Unidade"] = resultado.group(1)
    apartamento["Bloco"] = resultado.group(2)
    apartamento["Vencimento"] = resultado.group(3)

    for indice, verba in enumerate(verbas_ativas):
        apartamento[verba] = converter_valor(
            valores[indice]
        )

    salvar_apartamento(apartamento, apartamentos)


def processar_totais(linha, totais_pdf, verbas_ativas):

    if not verbas_ativas:
        return

    resultado = re.fullmatch(
        r"(\d+)\s+cobranças\s+(.+)",
        linha.strip()
    )

    if not resultado:
        return

    valores = re.findall(
        r"-?[\d\.]+,\d{2}",
        resultado.group(2)
    )

    # Precisa ter:
    # quantidade de verbas + o Total geral
    if len(valores) != len(verbas_ativas) + 1:
        return

    for indice, verba in enumerate(verbas_ativas):
        totais_pdf[verba] = converter_valor(
            valores[indice]
        )


def extrair_conviva(caminho_pdf):

    apartamentos = []

    verbas_ativas = []

    totais_pdf = {
        "Cota do Mes": 0,
        "Rateio Extra": 0,
        "Fundo de Reserva": 0,
        "Gas": 0,
    }

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():

                verbas_encontradas = identificar_verbas(linha)

                if verbas_encontradas:
                    verbas_ativas = verbas_encontradas

                processar_linha(linha, apartamentos, verbas_ativas)
                processar_totais(linha, totais_pdf, verbas_ativas)

    df = pd.DataFrame(apartamentos)

    print(df)

    return df, totais_pdf