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
     "Agua": None,
     "Energia Eletrica" : None,
     "Fundo Reserva" : None, 
     "Consumo de Gas" : None,
     "Multa Regulamento Interno" : None,
     "Reembolsos Diversos" : None, 
     "Salão de Festas" : None, 
    }

def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

#-------------------------------------------------------------------------------------------------------#

def processar_linha(linha, apartamentos):


#DESPESAS

    resultado = re.search(
     r"(.+?)\s+([A-Z0-9]{6})\s+(\d{2}/\d{2}/\d{4})",
     linha

    )

    if resultado:


     apartamento = novo_apartamento()

     apartamento["Bloco"] = "BLOCO"
     apartamento["Unidade"] = resultado.group(2)
     apartamento["Vencimento"] = resultado.group(3)

     resto = linha[resultado.end():].strip()

     valores = resto.split()

     #Agua, Cota, Energia e Fundo sempre existem
     apartamento["Agua"] = converter_valor(valores[0])
     apartamento["Cota do Mes"] = converter_valor(valores[1])
     apartamento["Energia Eletrica"] = converter_valor(valores[2])
     apartamento["Fundo Reserva"] = converter_valor(valores[3])

     #Verifica quais despesas extras existem

     if len(valores) == 6:
        apartamento["Consumo de Gas"] = converter_valor(valores[4])


     elif len(valores) == 8:

        apartamento["Multa Regulamento Interno"] = converter_valor(valores[4])
        apartamento["Reembolsos Diversos"] = converter_valor(valores[5])
        apartamento["Salão de Festas"] = converter_valor(valores[6])


     apartamentos.append(apartamento)




def extrair_Aurum(caminho_pdf):

    apartamentos = []


    totais_pdf = {
    "Cota do Mes": 0,
    "Agua": 0,
    "Energia Eletrica" : 0,
    "Fundo Reserva" : 0, 
    "Consumo de Gas" : 0,
    "Multa Regulamento Interno" : 0,
    "Reembolsos Diversos" : 0, 
    "Salão de Festas" : 0, 
    }


    with pdfplumber.open(caminho_pdf) as pdf:

     for pagina in pdf.pages:

        texto = pagina.extract_text() or ""

        linhas = texto.splitlines()

        for linha in linhas:

            if "títulos" in linha.lower():

               processar_linha(
                linha,
                totais_pdf
               )

               continue

            processar_linha(
                linha,
                apartamentos
            )
 
    df = pd.DataFrame(apartamentos)
    
        
    return df, totais_pdf

def processar_totais(linha, totais_pdf):

    partes = linha.split()

    totais_pdf["Agua"] = converter_valor(partes[2])

    totais_pdf["Cota do Mes"] = converter_valor(partes[3])

    totais_pdf["Energia Eletrica"] = converter_valor(partes[4])

    totais_pdf["Fundo Reserva"] = converter_valor(partes[5])

    totais_pdf["Consumo de Gas"] = converter_valor(partes[6])

    totais_pdf["Multa Regulamento Interno"] = converter_valor(partes[7])

    totais_pdf["Reembolsos Diversos"] = converter_valor(partes[8])

    totais_pdf["Salão de Festas"] = converter_valor(partes[9])

    print (partes)
           

       