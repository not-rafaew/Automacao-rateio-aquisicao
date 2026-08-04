#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

#-------------------------------------------------------------------------------------------------------#

#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento():
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "", #Salva o vencimento.

     "Cota do Mes": None,
     "Multa Inf Reg Interno" : None,
     "Salao de Festas" : None, #Salva o salão de festas.
     "Seguro Cont Assis 24H OPC" : None, #Salva o seguro.
     "Dif. Doc Pago a Menor" : None, #Salva o dif doc pago a menor.
     "Dif. Doc Pago a Maior" : None, #Salva o dif doc pago a maior.
     "Purificador de Agua" : None, #Salva o purificador de agua.
     "Copos Salao de Festas" : None, #Salva o purificador de agua.
     "Tag de Acesso" : None, #Salva a tag de acesso.
     "Leitura de Agua" : None, #Salva a leitura de agua.
     "Religacao de Agua" : None, #Salva religação de agua.
     "Agua Area Comum" : None, #Salva Agua area comum.
     "Utensilios Salao de Festas" : None, #Salva utensilios salão de festas
     "Desconto Agua" : None, #Salva desconto de agua.
     
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
        r"APTO (\d+) - BL\. (\w) (\d{2}/\d{2}/\d{4})", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento())

        apartamento["Unidade"] = resultado.group(1)
        apartamento["Bloco"] = resultado.group(2)
        apartamento["Vencimento"] = resultado.group(3)

        return

#DESPESAS

#Cota do mes
    resultado_cota_do_mes = re.search(
        r"1 CONDOMÍNIO (-?\d+,\d+)",
        linha
    )


    if resultado_cota_do_mes:

        valor = converter_valor(resultado_cota_do_mes.group(1))

        if apartamento["Cota do Mes"] is None:

            if valor < 0:
                apartamento["Cota do Mes"] = 0
            else:
                apartamento["Cota do Mes"] = valor
        
        return
    
#Salão de festas
    resultado_salao_de_festas = re.search(
        r"732 USO SALAO DE FESTAS 1/1 (\d+,\d+)", 
        linha
    )

    if resultado_salao_de_festas:

        valor = converter_valor(resultado_salao_de_festas.group(1))

        if apartamento["Salao de Festas"] is None:

            apartamento["Salao de Festas"] = valor
        else:
            apartamento["Salao de Festas"] += valor
        
        return
    
#Seguro
    resultado_seguro_cont_assis_24H_OPC = re.search(
        r"883 SEGURO CONT ASSIS 24H (\d+,\d+)\*",
        linha
    )

    if resultado_seguro_cont_assis_24H_OPC:
        apartamento["Seguro Cont Assis 24H OPC"] = converter_valor(resultado_seguro_cont_assis_24H_OPC.group(1))

        return

#Dif Doc Pago a Menor
    resultado_dif_doc_pago_a_menor = re.search (
        r"953 DIF. DOC PAGO A MENOR 1/1 (\d+,\d+)", 
        linha
    )

    if resultado_dif_doc_pago_a_menor:
        apartamento["Dif. Doc Pago a Menor"] = converter_valor(resultado_dif_doc_pago_a_menor.group(1))

        return

#Dif Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952 DIF. DOC PAGO A MAIOR 1/1 (-\d+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:
        apartamento["Dif. Doc Pago a Maior"] = converter_valor(resultado_dif_doc_pago_a_maior.group(1))

        return


#Purificador de agua
    resultado_purificador_de_agua = re.search(
        r"1208 PURIFICADOR DE ÁGUA (\d+,\d+)",
        linha
    )

    if resultado_purificador_de_agua:
        apartamento["Purificador de Agua"] = converter_valor(resultado_purificador_de_agua.group(1))

        return


#Tag de Acesso
    resultado_tag_de_acesso = re.search(
        r"1216\s+TAG DE ACESSO(?:\s+1/1)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_tag_de_acesso:
        apartamento["Tag de Acesso"] = converter_valor(resultado_tag_de_acesso.group(1))

        return

#Leitura de Agua
    resultado_leitura_de_agua = re.search(
        r"1334 LEITURA DE ÁGUA (\d+,\d+)",
        linha
    )

    if resultado_leitura_de_agua:
        apartamento["Leitura de Agua"] = converter_valor(resultado_leitura_de_agua.group(1))


#Religação de Agua
    resultado_religacao_de_agua = re.search(
        r"1424 RELIGAÇÃO DE ÁGUA 1/1 (\d+,\d+)",
        linha
    )

    if resultado_religacao_de_agua:
        apartamento["Religacao de Agua"] = converter_valor(resultado_religacao_de_agua.group(1))


#Agua area Comum
    resultado_agua_area_comum = re.search(
        r"1630\s+AGUA\s+AREA\s+COMUM(?:\s+1/1)?\s+(-?\d+,\d+)",
        linha
    )
    
    if resultado_agua_area_comum:

        valor = converter_valor(resultado_agua_area_comum.group(1))

        apartamento["Agua Area Comum"] = valor
        
        return
    
#Desconto de Agua
    resultado_desconto_agua = re.search(
        r"1532\s+DESCONTO AGUA\s+1/1\s+(-?\d+,\d+)",
        linha
    )

    if resultado_desconto_agua:

        valor = converter_valor(resultado_desconto_agua.group(1))

        if apartamento["Desconto Agua"] is None:
            apartamento["Desconto Agua"] = valor
        else:
            apartamento["Desconto Agua"] += valor
        
        return
    

#Utensilios Salão de Festas
    resultado_utensilios_salao_de_festas = re.search(
        r"1982\s+UTENSILIOS SALÃO DE(?:\s+1/1)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_utensilios_salao_de_festas:
        apartamento["Utensilios Salao de Festas"] = converter_valor(resultado_utensilios_salao_de_festas.group(1))


#Multa
    resultado_multa_inf_reg_interno = re.search(
        r"13\s+MULTA INF REG INTERNO(?:\s+1/1)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_multa_inf_reg_interno:
        apartamento["Multa Inf Reg Interno"] = converter_valor(resultado_multa_inf_reg_interno.group(1))

        return

#Copos Salão de festas
    resultado_copos_salao_de_festas = re.search(
        r"1255\s+COPOS SALÃO DE FESTAS(?:\s+1/1)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_copos_salao_de_festas:
         apartamento["Copos Salao de Festas"] = converter_valor(resultado_copos_salao_de_festas.group(1))

         return
    
#-------------------------------------------------------------------------------------------------------#

#Extrai as informações dos boletos do condominio Marechal Rondon II
def extrair_marechal(caminho_pdf):

    #Lista onde serão aramzenados todos os apartamentos encontrados
    apartamentos = [] #Cria uma lista onde vamos guardar todos os apartamentos encontrados.

    #Cria um novo apartamento
    apartamento = novo_apartamento()

    totais_pdf = {
    "Cota do Mes": 0,
    "Multa Inf Reg Interno" : 0,
    "Salao de Festas" : 0, 
    "Seguro Cont Assis 24H OPC" : 0, 
    "Dif. Doc Pago a Menor" : 0, 
    "Dif. Doc Pago a Maior" : 0, 
    "Purificador de Agua" : 0, 
    "Copos Salao de Festas" : 0, 
    "Tag de Acesso" : 0, 
    "Leitura de Agua" : 0, 
    "Religacao de Agua" : 0, 
    "Agua Area Comum" : 0, 
    "Utensilios Salao de Festas" : 0, 
    "Desconto Agua" : 0, 
    }

    #Coordenadas utilizadas para dividir cada pagina em duas colunas.
    LIMITE_ESQUERDA = (0, 0, 298, 842)
    LIMITE_DIREITA  = (298, 0, 596, 842)


    #Abre o pdf.
    #o "with" fecha o arquivo automaticamente quando terminar.
    with pdfplumber.open (caminho_pdf) as pdf: 

        chegou_nos_totais = False

        #Percorre todas as paginas
        for pagina in pdf.pages:

            #Divide a pagina em esquerda e direita
            esquerda = pagina.crop(LIMITE_ESQUERDA)
            direita = pagina.crop(LIMITE_DIREITA)

            #Extrai os textos
            texto_esquerda = esquerda.extract_text() or ""
            texto_direita = direita.extract_text() or ""

          
            #Divide em linhas
            linhas_esquerda = texto_esquerda.splitlines()
            linhas_direita = texto_direita.splitlines()
            
            #Processa a coluna esquerda
            for linha in linhas_esquerda:

                #Ao encontrar o quadro de totais, interrompe a leitura.
                if "TOTAIS" in linha:
                    chegou_nos_totais = True
                    continue

                if chegou_nos_totais:
                    processar_totais(
                         linha,
                        totais_pdf
                    )
                
                else: processar_linha(
                        linha,
                        apartamento,
                        apartamentos
                    )


            #Se ainda não chegou ao quadro de totais,
            #Processa tambem a coluna direita
            for linha in linhas_direita:

                if "TOTAIS" in linha:
                    chegou_nos_totais = True
                    continue

                if chegou_nos_totais:
                                    
                    processar_totais(
                         linha,
                         totais_pdf
                    )
                                
                else:
                    processar_linha(
                        linha,
                        apartamento,
                        apartamentos
                     )


    #Salva o ultimo apartamento processado
    salvar_apartamento(apartamento, apartamentos)

    #Converte a lista de apartamentos em um DataFrame
    df = pd.DataFrame(apartamentos)

    return df, totais_pdf

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))



def processar_totais(linha, totais_pdf):
    #Cota do mes
    resultado_cota_do_mes = re.search(
        r"1\s+CONDOMÍNIO\s+(-?[\d\.]+,\d+)",
        linha
    )


    if resultado_cota_do_mes:

        valor = converter_valor(resultado_cota_do_mes.group(1))

        if valor > 0:
            totais_pdf["Cota do Mes"] = valor
        
        return
    
#Salão de festas
    resultado_salao_de_festas = re.search(
        r"732\s+USO SALAO DE FESTAS\s+(-?[\d\.]+,\d+)", 
        linha
    )

    if resultado_salao_de_festas:

        valor = converter_valor(resultado_salao_de_festas.group(1))

        totais_pdf["Salao de Festas"] += valor

        return

    
#Seguro
    resultado_seguro_cont_assis_24H_OPC = re.search(
        r"883\s+SEGURO CONT ASSIS 24H OPC\s+(-?[\d\.]+,\d+)\s*\*?",
        linha
    )

    if resultado_seguro_cont_assis_24H_OPC:
        totais_pdf["Seguro Cont Assis 24H OPC"] = converter_valor(resultado_seguro_cont_assis_24H_OPC.group(1))

        return

#Dif Doc Pago a Menor
    resultado_dif_doc_pago_a_menor = re.search (
        r"953 DIF. DOC PAGO A MENOR (-?[\d\.]+,\d+)", 
        linha
    )

    if resultado_dif_doc_pago_a_menor:
        totais_pdf["Dif. Doc Pago a Menor"] = converter_valor(resultado_dif_doc_pago_a_menor.group(1))

        return

#Dif Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952 DIF. DOC PAGO A MAIOR (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:
        totais_pdf["Dif. Doc Pago a Maior"] = converter_valor(resultado_dif_doc_pago_a_maior.group(1))

        return


#Purificador de agua
    resultado_purificador_de_agua = re.search(
        r"1208 PURIFICADOR DE ÁGUA (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_purificador_de_agua:
        totais_pdf["Purificador de Agua"] = converter_valor(resultado_purificador_de_agua.group(1))

        return


#Tag de Acesso
    resultado_tag_de_acesso = re.search(
        r"1216\s+TAG DE ACESSO(?:\s+1/1)?\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_tag_de_acesso:
        totais_pdf["Tag de Acesso"] = converter_valor(resultado_tag_de_acesso.group(1))

        return

#Leitura de Agua
    resultado_leitura_de_agua = re.search(
        r"1334 LEITURA DE ÁGUA (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_leitura_de_agua:
        totais_pdf["Leitura de Agua"] = converter_valor(resultado_leitura_de_agua.group(1))


#Religação de Agua
    resultado_religacao_de_agua = re.search(
        r"1424 RELIGAÇÃO DE ÁGUA (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_religacao_de_agua:
        totais_pdf["Religacao de Agua"] = converter_valor(resultado_religacao_de_agua.group(1))


#Agua area Comum
    resultado_agua_area_comum = re.search(
        r"1630\s+AGUA\s+AREA\s+COMUM(?:\s+1/1)?\s+(-?[\d\.]+,\d+)",
        linha
    )
    
    if resultado_agua_area_comum:

        valor = converter_valor(resultado_agua_area_comum.group(1))

        totais_pdf["Agua Area Comum"] = valor
        
        return
    
# Desconto de Agua
    resultado_desconto_agua = re.search(
        r"1532\s+DESCONTO AGUA\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_desconto_agua:

        valor = converter_valor(resultado_desconto_agua.group(1))

        totais_pdf["Desconto Agua"] += valor

        return
    

#Utensilios Salão de Festas
    resultado_utensilios_salao_de_festas = re.search(
        r"1982\s+UTENSILIOS SALÃO DE FESTA (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_utensilios_salao_de_festas:
        totais_pdf["Utensilios Salao de Festas"] = converter_valor(resultado_utensilios_salao_de_festas.group(1))


#Multa
    resultado_multa_inf_reg_interno = re.search(
        r"13\s+MULTA INF REG INTERNO (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_multa_inf_reg_interno:
        totais_pdf["Multa Inf Reg Interno"] = converter_valor(resultado_multa_inf_reg_interno.group(1))

        return

#Copos Salão de festas
    resultado_copos_salao_de_festas = re.search(
        r"1255\s+COPOS SALÃO DE FESTAS (-?[\d\.]+,\d+)",
        linha
    )

    if resultado_copos_salao_de_festas:
         totais_pdf["Copos Salao de Festas"] = converter_valor(resultado_copos_salao_de_festas.group(1))

         return







