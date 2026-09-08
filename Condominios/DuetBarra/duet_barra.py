#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.


#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento():
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.

     "Cota do Mes": None,
     "Agua" : None,
     "Churrasqueira": None,
     "Cota Extra": None,
     "Energia Area Comum" : None, 
     "Enxoval" : None,
     "Fundo de Reserva" : None,
     "Salao de Festas" : None, 
    }




#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):


#So salva se existir uma unidade cadastrada.
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

#-------------------------------------------------------------------------------------------------------#


#Processa uma linha do PDF, identifica o tipo de informação
#E preenche os dados do apartamento atual
def processar_linha(linha, apartamento, apartamentos):


#IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"BLOCO\s+(\d+)\s*-\s*(\d+)", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento())

        apartamento["Bloco"] = resultado.group(1)
        apartamento["Unidade"] = resultado.group(2)

        return
    
#DESPESAS

#Cota do mes
    resultado_cota_do_mes = re.search(
        r"PRINCIPAL\s*->\s*COTA CONDOMINIAL.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_cota_do_mes:

        apartamento["Cota do Mes"] = converter_valor(
            resultado_cota_do_mes.group(1)
       )

        return

#Agua
    resultado_agua = re.search(
        r"(?:AGUA/ESGOTO|PRINCIPAL)\s*->\s*ÁGUA.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_agua:

        apartamento["Agua"] = converter_valor(
            resultado_agua.group(1)
    )

        return


#Energia Area Comum
    resultado_energia_area_comum = re.search(
        r"(?:ENERGIA|PRINCIPAL)\s*->\s*ENERGIA.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_energia_area_comum:

        apartamento["Energia Area Comum"] = converter_valor(
            resultado_energia_area_comum.group(1)
    )

        return
    

#Enxoval
    resultado_enxoval = re.search(
        r"FUNDO DE MELHORIAS\s*->\s*ENXOVAL.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_enxoval:

        apartamento["Enxoval"] = converter_valor(
            resultado_enxoval.group(1)
    )

        return

#Churrasqueira
    resultado_churrasqueira = re.search(
        r"CHURRASQUEIRA.*?R\$\s*(-?[\d.]+,\d+)",
        linha
    )

    if resultado_churrasqueira:
        apartamento["Churrasqueira"] = converter_valor(
            resultado_churrasqueira.group(1)
        )

        return

#Cota Extra

    resultado_cota_extra = re.search(
        r"COTA EXTRA / RATEIO.*?R\$\s*(-?[\d.]+,\d+)",
        linha
    )

    if resultado_cota_extra:

        valor = converter_valor(
            resultado_cota_extra.group(1)
    )

        apartamento["Cota Extra"] = valor

        print(
            "COTA EXTRA:",
            apartamento["Unidade"],
            valor
        )

        return

#Fundo de Reserva
    resultado_fundo_de_reserva = re.search(
        r"FUNDO DE RESERVA\s*->\s*FUNDO DE RESERVA.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_fundo_de_reserva:

        apartamento["Fundo de Reserva"] = converter_valor(
            resultado_fundo_de_reserva.group(1)
    )

        return
    

#Salão de Festas
    resultado_salao_de_festas = re.search(
        r"AREA COMUM\s*->\s* SALAO DE FESTAS.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_salao_de_festas:

        apartamento["Salao de Festas"] = converter_valor(
            resultado_salao_de_festas.group(1)
    )

        return
    

#Extrai as informações dos boletos do condominio Duet Barra
def extrair_duet(caminho_pdf):

    apartamentos = []

    apartamento = novo_apartamento()

    totais_pdf = {
    "Cota do Mes": 0,
    "Agua": 0,
    "Energia Area Comum": 0,
    "Enxoval": 0,
    "Churrasqueira": 0,
    "Cota Extra": 0,
    "Fundo de Reserva": 0,
    "Salao de Festas": 0,
    }


    with pdfplumber.open(caminho_pdf) as pdf:

        chegou_nos_totais = False

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            linhas = texto.splitlines()

            for i, linha in enumerate(linhas):


                # Ao encontrar a seção de totais, para a leitura.
                if "SOMA DAS VERBAS" in linha:
                    chegou_nos_totais = True
                    continue

                if chegou_nos_totais:
                    processar_totais(
                         linha,
                        totais_pdf
                    )
                
                else:
                    # Caso especial da Cota Extra
                    if "COTA EXTRA / RATEIO" in linha and i + 1 < len(linhas):

                         linha_cota_extra = linha + " " + linhas[i + 1]

                         processar_linha(
                            linha_cota_extra,
                            apartamento,
                            apartamentos
                        )


                    else: processar_linha(
                        linha,
                        apartamento,
                        apartamentos,
                    )

    salvar_apartamento(apartamento, apartamentos)

    df = pd.DataFrame(apartamentos)

    
    return df, totais_pdf

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))


#Processar os totais 
def processar_totais(linha, totais_pdf):
    
    resultado_cota_do_mes = re.search(
        r"PRINCIPAL\s*->\s*COTA CONDOMINIAL.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_cota_do_mes:

        totais_pdf["Cota do Mes"] = converter_valor(
            resultado_cota_do_mes.group(1)
       )

        return

#Agua
    resultado_agua = re.search(
        r"(?:AGUA/ESGOTO|PRINCIPAL)\s*->\s*ÁGUA.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_agua:

        totais_pdf["Agua"] = converter_valor(
            resultado_agua.group(1)
    )

        return


#Energia Area Comum
    resultado_energia_area_comum = re.search(
        r"(?:ENERGIA|PRINCIPAL)\s*->\s*ENERGIA.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_energia_area_comum:

        totais_pdf["Energia Area Comum"] = converter_valor(
            resultado_energia_area_comum.group(1)
    )

        return
    

#Enxoval
    resultado_enxoval = re.search(
        r"FUNDO DE MELHORIAS\s*->\s*ENXOVAL.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_enxoval:

        totais_pdf["Enxoval"] = converter_valor(
            resultado_enxoval.group(1)
    )

        return
    
#Churrasqueira
    resultado_churrasqueira = re.search(
        r"CHURRASQUEIRA.*?R\$\s*(-?[\d.]+,\d+)",
        linha
    )

    if resultado_churrasqueira:
        totais_pdf["Churrasqueira"] = converter_valor(
            resultado_churrasqueira.group(1)
        )

        return

#Cota Extra
    resultado_cota_extra = re.search(
        r"PRINCIPAL\s*->\s*COTA EXTRA / RATEIO.*?R\$\s*(-?[\d.]+,\d+)",
        linha
    )

    if resultado_cota_extra:
        
        totais_pdf["Cota Extra"] = converter_valor(
            resultado_cota_extra.group(1)
        )

        return

#Fundo de Reserva
    resultado_fundo_de_reserva = re.search(
        r"FUNDO DE RESERVA\s*->\s*FUNDO DE RESERVA.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_fundo_de_reserva:

        totais_pdf["Fundo de Reserva"] = converter_valor(
            resultado_fundo_de_reserva.group(1)
    )

        return
    

#Salão de Festas
    resultado_salao_de_festas = re.search(
        r"AREA COMUM\s*->\s* SALAO DE FESTAS.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_salao_de_festas:

        totais_pdf["Salao de Festas"] = converter_valor(
            resultado_salao_de_festas.group(1)
    )

        return

