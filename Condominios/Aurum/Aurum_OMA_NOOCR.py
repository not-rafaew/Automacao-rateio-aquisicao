# Bibliotecas usadas
import pdfplumber  # Biblioteca para ler PDFs.
import re          # Biblioteca para procurar padrões.
import pandas as pd  # Biblioteca para trabalhar com DataFrames.


# Cria a estrutura de cada apartamento
def novo_apartamento():
    return {
        "Bloco": "",
        "Unidade": "",
        "Vencimento": "",

        "Cota do mês": None,
        "Agua": None,
        "Energia Eletrica": None,
        "Fundo Reserva": None,
        "Consumo de Gas": None,
        "Salão de Festas (Desconto)": None,
    }


# Converte valores brasileiros para float
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_linha (linha, apartamentos):

    #Pega o campo que contém as unidades
    texto_unidades = linha[1] or ""

    #Procura todas as unidades dentro desse campo
    unidades = re.findall(
      r"\b000[A-Z0-9]+\b",
      texto_unidades  
    )

    # Ignora cabeçalhos, totais e linhas sem unidades
    if not unidades:
        return

    #Confere a quantidade informada no PDF
    quantidade = int(linha[2])

    if len(unidades) != quantidade:
        print("ATENÇÃO: quantidade diferente!", unidades)
        return

    # Percorre cada unidade encontrada
    for unidade in unidades:

        apartamento = novo_apartamento()

        apartamento["Bloco"] = linha[0] or "0"
        apartamento["Unidade"] = unidade

        #Associa as despesas as colunas corretas

        despesas = {
           "Cota do mês": 4,
            "Fundo Reserva": 5,
            "Energia Eletrica": 6,
            "Agua": 7,
            "Salão de Festas (Desconto)": 8,
            "Consumo de Gas": 9, 
        }

        for nome, indice in despesas.items():

            valor = linha[indice]

            if valor:
                apartamento[nome] = converter_valor(valor)
        
        apartamentos.append(apartamento)

def extrair_aurum_oma_noocr(caminho_pdf):
    
    apartamentos = []

    totais_pdf = {
      "Cota do mês": 0,
      "Agua": 0,
      "Energia Eletrica": 0,
      "Fundo Reserva": 0,
      "Consumo de Gas": 0,
      "Salão de Festas (Desconto)": 0,  
    }

    #Abre o PDF
    with pdfplumber.open(caminho_pdf) as pdf:

        #Percorre todas as paginas
        for numero, pagina in enumerate(pdf.pages, start=1):

            print(f"\nPÁGINA {numero}")

            #Extrai as tabelas
            tabelas = pagina.extract_tables(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",             
                }
            )

            #Percorre as tabelas encontradas
            for tabela in tabelas:

                for linha in tabela:

                    if not linha:
                        continue

                    # Identifica a linha de totais
                    if linha[0] and "Total rateado" in linha[0]:

                        print ("LINHA DE TOTAIS ENCONTRADA", linha)

                        processar_totais(linha, totais_pdf)
                        continue

                    processar_linha(linha, apartamentos)
                    

    # Cria o dataframe
    df = pd.DataFrame(apartamentos)
    return df, totais_pdf

def processar_totais(linha, totais_pdf):

    # relaciona cada despesa a coluna do PDF
    despesas = {
      "Cota do mês": 3,
        "Fundo Reserva": 4,
        "Energia Eletrica": 5,
        "Agua": 6,
        "Salão de Festas (Desconto)": 7,
        "Consumo de Gas": 8,  
    }

    #Percorre cada despesa
    for nome, indice in despesas.items():

        # A celula contem o codigo e o valor
        texto = linha[indice]

        if not texto:
            continue

        # Separa o codigo do valor
        valor = texto.split("\n")[-1]

        # Converte e guarda no dicionario

        totais_pdf[nome] = converter_valor(valor)