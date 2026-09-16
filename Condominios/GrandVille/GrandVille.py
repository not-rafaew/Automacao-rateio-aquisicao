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
     "Fundo de Reserva": None,
     "Agua Geral" : None,
     "Tarifa Bancaria" : None, 
    }

def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def salvar_apartamento(apartamento, apartamentos):
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())


def processar_linha(linha, apartamentos):

    resultado = re.fullmatch(
        r"(\d+)\s+(\d+)\s+(\d{2}/\d{2}/\d{4})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})",
        linha.strip()
    )

    if resultado:
        
        apartamento = novo_apartamento()

        apartamento["Unidade"] = resultado.group(1)
        apartamento["Bloco"] = resultado.group(2)
        apartamento["Vencimento"] = resultado.group(3)

        apartamento["Cota do Mes"] = converter_valor(resultado.group(4))
        apartamento["Fundo de Reserva"] = converter_valor(resultado.group(5))
        apartamento["Agua Geral"] = converter_valor(resultado.group(6))
        apartamento["Tarifa Bancaria"] = converter_valor(resultado.group(7))

        salvar_apartamento(apartamento, apartamentos)


def processar_totais(linha, totais_pdf):

    resultado = re.fullmatch(
        r"(\d+)\s+cobranças\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})\s+"
        r"(-?[\d\.]+,\d{2})",
        linha.strip()
    )

    if resultado:
        
        totais_pdf["Cota do Mes"] = converter_valor(resultado.group(2))
        totais_pdf["Fundo de Reserva"] = converter_valor(resultado.group(3))
        totais_pdf["Agua Geral"] = converter_valor(resultado.group(4))
        totais_pdf["Tarifa Bancaria"] = converter_valor(resultado.group(5))

        print(totais_pdf)

def extrair_grandville(caminho_pdf):

    apartamentos = []

    totais_pdf = {
        "Cota do Mes": 0,
        "Fundo de Reserva": 0,
        "Agua Geral": 0,
        "Tarifa Bancaria": 0,
    }

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():
                processar_linha(linha, apartamentos)
                processar_totais(linha, totais_pdf)

    df = pd.DataFrame(apartamentos)

    print(df)

    return df, totais_pdf


            


    