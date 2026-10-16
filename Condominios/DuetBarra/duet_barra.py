#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.


#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento(nome_coluna_laudo):
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.

     "Cota do mês": None,
     "Fundo de Reserva" : None,
     "Água" : None,
     "Energia Área Comum" : None,
     nome_coluna_laudo: None,
     "Salão de Festa" : None, 
     "Churrasqueira": None, 
     "Enxoval" : None,
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
def processar_linha(linha, apartamento, apartamentos, nome_coluna_laudo):


#IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"BLOCO\s+(\d+)\s*-\s*(\d+)", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento(nome_coluna_laudo))

        apartamento["Bloco"] = f"BL{int(resultado.group(1)):02d}"
        apartamento["Unidade"] = int(resultado.group(2))

        return
    
#DESPESAS

#Cota do mês
    resultado_cota_do_mes = re.search(
        r"PRINCIPAL\s*->\s*COTA CONDOMINIAL.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_cota_do_mes:

        apartamento["Cota do mês"] = converter_valor(
            resultado_cota_do_mes.group(1)
       )

        return

#Agua
    resultado_agua = re.search(
        r"(?:AGUA/ESGOTO|PRINCIPAL)\s*->\s*ÁGUA.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_agua:

        apartamento["Água"] = converter_valor(
            resultado_agua.group(1)
    )

        return


#Energia Area Comum
    resultado_energia_area_comum = re.search(
        r"(?:ENERGIA|PRINCIPAL)\s*->\s*ENERGIA.*?R\$\s*(-?\d+,\d+)",
        linha
    )

    if resultado_energia_area_comum:

        apartamento["Energia Área Comum"] = converter_valor(
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

        apartamento[nome_coluna_laudo] = valor

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

        apartamento["Salão de Festa"] = converter_valor(
            resultado_salao_de_festas.group(1)
    )

        return
    

#Extrai as informações dos boletos do condominio Duet Barra
def extrair_duet(caminho_pdf):

    apartamentos = []

    with pdfplumber.open(caminho_pdf) as pdf:

        texto_completo = ""

        for pagina in pdf.pages:
            texto_completo += (pagina.extract_text() or "") + "\n"

        parcela_laudo = identificar_parcela_laudo(texto_completo)

        print ("\nPARCELA LAUDO")
        print (parcela_laudo)

        nome_coluna_laudo = (
            f"Laudo Técnico - Fech. Varanda {parcela_laudo}"
        )
        
        print("\nNOME COLUNA LAUDO:")
        print(nome_coluna_laudo)

        apartamento = novo_apartamento(
            nome_coluna_laudo
        )

        totais_pdf = {
            "Cota do mês": 0,
            "Fundo de Reserva": 0,
            "Água": 0,
            "Energia Área Comum": 0,
            nome_coluna_laudo: 0,
            "Salão de Festa": 0,
            "Churrasqueira": 0,
            "Enxoval": 0,
        }

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
                        totais_pdf,
                        nome_coluna_laudo
                    )
                
                else:
                    # Caso especial da Cota Extra
                    if "COTA EXTRA / RATEIO" in linha and i + 1 < len(linhas):

                         linha_cota_extra = linha + " " + linhas[i + 1]

                         processar_linha(
                            linha_cota_extra,
                            apartamento,
                            apartamentos,
                            nome_coluna_laudo
                        )


                    else: processar_linha(
                        linha,
                        apartamento,
                        apartamentos,
                        nome_coluna_laudo
                    )

    salvar_apartamento(apartamento, apartamentos)

    df = pd.DataFrame(apartamentos)

    
    return df, totais_pdf

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def identificar_parcela_laudo(texto):

    resultado = re.search(
      r"LAUDO TÉCNICO DE FECHAMENTO DE VARANDA.*?"
      r"CORTINA DE VIDRO\s+(\d+)/(\d+)",
      texto,
      re.IGNORECASE | re.DOTALL
    )

    if resultado:

        parcela = (
           f"{int(resultado.group(1)):02d}/"
           f"{int(resultado.group(2)):02d}" 
        )

        return parcela

    return ""

#Processar os totais 
def processar_totais(linha, totais_pdf, nome_coluna_laudo):
    
    resultado_cota_do_mes = re.search(
        r"PRINCIPAL\s*->\s*COTA CONDOMINIAL.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_cota_do_mes:

        totais_pdf["Cota do mês"] = converter_valor(
            resultado_cota_do_mes.group(1)
       )

        return

#Agua
    resultado_agua = re.search(
        r"(?:AGUA/ESGOTO|PRINCIPAL)\s*->\s*ÁGUA.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_agua:

        totais_pdf["Água"] = converter_valor(
            resultado_agua.group(1)
    )

        return


#Energia Area Comum
    resultado_energia_area_comum = re.search(
        r"(?:ENERGIA|PRINCIPAL)\s*->\s*ENERGIA.*?R\$\s*(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_energia_area_comum:

        totais_pdf["Energia Área Comum"] = converter_valor(
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
        
        totais_pdf[nome_coluna_laudo] = converter_valor(
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

        totais_pdf["Salão de Festa"] = converter_valor(
            resultado_salao_de_festas.group(1)
    )

        return

