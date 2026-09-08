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

def extrair_aurum(caminho_pdf):

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

    bloco_atual = ""
    verbas_extras = []

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            palavras = pagina.extract_words()
            colunas = encontrar_colunas(palavras)

            verbas_extras = [
                nome
                for nome in colunas
                if nome != "Total"
            ]

            print ("Verbas Encontradas:", verbas_extras)

            tabelas = pagina.extract_tables(
                table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                }
            )

            
            for tabela in tabelas:

                    
                for linha in tabela:

                    #Ignora linhas vazias
                    if not linha:
                        continue

                    #Cabeçalho
                    if linha and linha[0] == "Devedor":
                        continue

                    #Mudança de bloco
                    texto_linha = " ".join(
                        str(celula) for celula in linha if celula
                    )

                    if "Bloco:" in texto_linha:
                        bloco_atual = texto_linha.replace("Bloco:", "").replace (" ", "")
                        continue


                    if "títulos" in texto_linha.lower():
                        print ("ACHEI OS TOTAIS")
                        print (linha)
                        processar_totais(linha, totais_pdf, verbas_extras)
                        continue


                    processar_linha(
                        linha,
                        apartamentos,
                        bloco_atual
                    )
                        
            print("COLUNAS ENCONTRADAS:")
            print(colunas)

            for palavra in palavras:
                if palavra["top"] <= 105:
                    print(
                        palavra["text"],
                        "| x0:", round(palavra["x0"], 2),
                        "| x1:", round(palavra["x1"], 2),
                         "| top:", round(palavra["top"], 2)
                    )
            preencher_despesas(
                palavras,
                apartamentos,
                colunas
            )

    print("QUANTIDADE DE APARTAMENTOS:", len(apartamentos))
    print("APARTAMENTOS:", apartamentos)
    df = pd.DataFrame(apartamentos)

    return df, totais_pdf


def processar_linha(linha, apartamentos, bloco_atual):

    unidade = None
    vencimento = None
    indice_vencimento = None

    for indice, celula in enumerate(linha):

        if not celula:
            continue

        celula = celula.strip()

        #Procura vencimento
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", celula):
            vencimento = celula
            indice_vencimento = indice

        #Procura a unidade
        if re.fullmatch(r"000[A-Z0-9]+", celula):
            unidade = celula

    if unidade is None or vencimento is None:
        return
        
    apartamento = novo_apartamento()

    apartamento["Bloco"] = bloco_atual
    apartamento["Unidade"] = unidade
    apartamento["Vencimento"] = vencimento

    #Pega a célula logo depois do vencimento
    agua = linha[indice_vencimento + 1]

    if agua:
        apartamento["Agua"] = converter_valor(agua)

    #Cota do mes
    indice_cota = indice_vencimento + 2

    while indice_cota < len(linha) and not linha[indice_cota]:
        indice_cota += 1

    if indice_cota < len(linha):
        cota = linha[indice_cota]

        apartamento["Cota do Mes"] = converter_valor(cota)

    #Energia elétrica
    indice_energia = indice_cota + 1

    if indice_energia < len(linha):
        energia = linha[indice_energia]

        if energia:
            apartamento["Energia Eletrica"] = converter_valor(energia)

    print("ADICIONANDO:", apartamento["Unidade"])
    apartamentos.append(apartamento)


def preencher_despesas(palavras, apartamentos, colunas):

    colunas_ordenadas = sorted(
        colunas.items(),
        key=lambda item: item[1]
    )

    print("COLUNAS ORDENADAS:")
    print(colunas_ordenadas)

    for palavra in palavras:

        texto = palavra["text"]
        x = palavra["x0"]
        top = palavra["top"]



        # Fundo Reserva
        for i in range(len(colunas_ordenadas) - 1):

            verba_atual = colunas_ordenadas[i]
            proxima_coluna = colunas_ordenadas[i + 1]

            nome_verba = verba_atual[0]
            x_inicio = verba_atual[1]
            x_fim = proxima_coluna[1]

            #Se a proxima coluna for total,
            # Usa o meio entre as duas como limite
            if proxima_coluna[0] == "Total":
                 x_fim = (x_inicio + x_fim) / 2

            if x_inicio <= x < x_fim:

                    if re.fullmatch(
                        r"-?\d{1,3}(?:\.\d{3})*,\d{2}",
                        texto
                    ):

                        for unidade_palava in palavras:

                            unidade = unidade_palava["text"]

                            if re.fullmatch(
                                r"\d{6}|0000M\d+",
                                unidade
                            ):

                                top_unidade = unidade_palava["top"]

                                if abs(top - top_unidade) < 2:

                                    for apartamento in apartamentos:

                                        if apartamento["Unidade"] == unidade:

                                            apartamento[nome_verba] = converter_valor(texto)

                                            break                


def processar_totais(linha, totais_pdf, verbas_extras):

    #Junta todas as células da linha em um unico texto
    texto_linha = " ".join(
        str(valor) for valor in linha if valor
    )

    # Encontra todos os valores monetários, inclusive negativos
    valores = re.findall(
        r"-?\d{1,3}(?:\.\d{3})*,\d{2}",
        texto_linha
    )

    #Os tres primeiros valores são sempre:
    #Água, Cota do Mês e Energia Elétrica
    totais_pdf["Agua"] = converter_valor(valores[0])
    totais_pdf["Cota do Mes"] = converter_valor(valores[1])
    totais_pdf["Energia Eletrica"] = converter_valor(valores[2])

    # Depois vêm as verbas extras encontradas no cabeçalho
    valores_extras = valores[3:-1]

    for verba, valor in zip(verbas_extras, valores_extras):
        totais_pdf[verba] = converter_valor(valor)

    print("TOTAIS PDF:")
    print(totais_pdf)

    
def encontrar_colunas(palavras):

    colunas = {}

    # Verifica se existe a palavra "(Desconto) no cabeçalho"
    tem_desconto = False

    for palavra in palavras:
        texto = palavra["text"].lower()
        top = palavra["top"]

        if top <= 105 and "desconto" in texto:
            tem_desconto = True
            break

    for palavra in palavras:

        texto = palavra["text"].lower()
        x = palavra["x0"]
        top = palavra["top"]

        # Palavras da região do cabeçalho

        if top > 105:
            continue

        if "fundo" in texto:
            colunas["Fundo Reserva"] = x

        if "consumo" in texto:
                    colunas["Consumo de Gas"] = x

        if "multa" in texto:
                    colunas["Multa Regulamento Interno"] = x

        if "reembolso" in texto:
                    colunas["Reembolsos Diversos"] = x

        if texto == "salão":

            if tem_desconto:

                if "Salão de Festas (Desconto)" not in colunas:
                    colunas["Salão de Festas (Desconto)"] = x

                else:
                    colunas["Salão de Festas"] = x

            else:
                colunas["Salão de Festas"] = x

        if texto == "total":
            colunas["Total"] = x

    return colunas