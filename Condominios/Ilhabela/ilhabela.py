#Bibliotecas usadas
import pdfplumber #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.

#-------------------------------------------------------------------------------------------------------#

#Esses campos serão preenchidos conforme as informações forem encontradas no PDF.
def novo_apartamento(parcelas):
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "", #Salva o vencimento.

     "Cota do mês": None,
     "Água": None,
     "Fundo de Pintura {parcelas['fundo_pintura']}" : None,
     "Seguro Cont. Assis. 24H OPC" : None,
     "Tarifa Basica de Água" : None,
     "Fundo Reserva (5%)" : None,
     "Leitura de Água" : None,
     "Clube de Vantagens" : None,
     "Seguro {parcelas['seguro']}" : None,
     "Desobstrucão Esgoto {parcelas['desobstrucao_esgoto']}" : None,  
     "Salão de Festas" : None,
     "Telhado {parcelas['telhado']}": None,
     "Dif Doc Pago a Maior" :None,
     "Dif Doc Pago a Menor" :None,
     "Bonificacao Indevida" :None, 
     "Cameras" : None,   
    }

#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):

# Regra de negócio da Cota do Mês
    if apartamento["Cota do mês"] == 0:
        apartamento["Cota do mês"] = None


#So salva se existir uma unidade cadastrada.
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

#-------------------------------------------------------------------------------------------------------#


#Processa uma linha do PDF, identifica o tipo de informação
#E preenche os dados do apartamento atual
def processar_linha(linha, apartamento, apartamentos, parcelas):

#IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"APTO (\d+) - BL\. (\w) (\d{2}/\d{2}/\d{4})", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento(parcelas))

        apartamento["Unidade"] = f"APTO {resultado.group(1)}"
        apartamento["Bloco"] = f"BL. {resultado.group(2)}"
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

        if apartamento["Cota do mês"] is None:
            apartamento["Cota do mês"] = 0

        apartamento["Cota do mês"] += valor

        return
    

#Agua
    resultado_agua = re.search(
        r"2\s+AGUA\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_agua:

        apartamento["Água"] = converter_valor(
            resultado_agua.group(1)
        )

        return

#Seguro
    resultado_seguro = re.search(
        r"3\s+SEGURO(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_seguro:
        
        nome_coluna_seguro = (
           f"Seguro {parcelas['seguro']}" 
        )

        apartamento[nome_coluna_seguro] = converter_valor(
            resultado_seguro.group(1)
        )

        return
    

#Desobstrucao Esgoto
    resultado_desobstrucao_esgoto = re.search(
        r"78\s+DESOBSTRUCAO ESGOTO(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_desobstrucao_esgoto:
        
        nome_coluna_desobstrucao = (
           f"Desobstrução Esgoto {parcelas['desobstrucao_esgoto']}"  
        )

        apartamento[nome_coluna_desobstrucao] = converter_valor(
            resultado_desobstrucao_esgoto.group(1)
        )

        return


#Fundo de Pintura
    resultado_fundo_de_pintura = re.search(
        r"89\s+FUNDO DE PINTURA(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_fundo_de_pintura:
        
        nome_coluna_fundo_pintura = (
           f"Fundo de Pintura {parcelas['fundo_pintura']}" 
        )

        apartamento[nome_coluna_fundo_pintura] = converter_valor(
            resultado_fundo_de_pintura.group(1)
        )

        return
    

#Salão de festas
    resultado_salao_de_festas = re.search(
        r"732 USO SALAO DE FESTAS 1/1 (\d+,\d+)", 
        linha
    )

    if resultado_salao_de_festas:

        valor = converter_valor(resultado_salao_de_festas.group(1))

        if apartamento["Salão de Festas"] is None:

            apartamento["Salão de Festas"] = valor
        else:
            apartamento["Salão de Festas"] += valor
        
        return
    

#Seguro Cont Assis 24h
    resultado_seguro_cont_assis_24h = re.search(
        r"883\s+SEGURO CONT ASSIS 24H\s+(-?\d+,\d+)\*",
        linha
    )

    if resultado_seguro_cont_assis_24h:
        apartamento["Seguro Cont. Assis. 24H OPC"] = converter_valor(resultado_seguro_cont_assis_24h.group(1))

        return


#Dif Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952\s+DIF. DOC PAGO A MAIOR(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:
        apartamento["Dif Doc Pago a Maior"] = converter_valor(resultado_dif_doc_pago_a_maior.group(1))

        return
    

#Dif Doc Pago a Menor
    resultado_dif_doc_pago_a_menor = re.search(
        r"953\s+DIF. DOC PAGO A MENOR(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_menor:
        apartamento["Dif Doc Pago a Menor"] = converter_valor(resultado_dif_doc_pago_a_menor.group(1))

        return

#Tarifa Basica de Agua
    resultado_tarifa_basica_de_agua = re.search(
        r"997\s+TARIFA BASICA DE AGUA\s+(-?\d+,\d+)",
        linha
    )

    if resultado_tarifa_basica_de_agua:
        apartamento["Tarifa Basica de Água"] = converter_valor(resultado_tarifa_basica_de_agua.group(1))

        return

#Telhado
    resultado_telhado = re.search(
        r"1195\s+TELHADO(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_telhado:
        
        nome_coluna_telhado = (
           f"Telhado {parcelas['telhado']}" 
        )

        apartamento[nome_coluna_telhado] = converter_valor(
            resultado_telhado.group(1)
        )

        return

#Fundo Reserva
    resultado_fundo_reserva = re.search(
        r"1242\s+FUNDO RESERVA\s+\(5%\)\s+(-?\d+,\d+)",
        linha
    )

    if resultado_fundo_reserva:
        apartamento["Fundo Reserva (5%)"] = converter_valor(resultado_fundo_reserva.group(1))

        return
    

#Leitura de Agua
    resultado_leitura_de_agua = re.search(
        r"1334\s+LEITURA DE ÁGUA\s+(-?\d+,\d+)",
        linha
    )

    if resultado_leitura_de_agua:
        apartamento["Leitura de Água"] = converter_valor(resultado_leitura_de_agua.group(1))

        return
    

#Bonificacao Indevida
    resultado_bonificacao_indevida = re.search(
        r"1340\s+BONIFICAÇÃO INDEVIDA(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_bonificacao_indevida:
        apartamento["Bonificacao Indevida"] = converter_valor(resultado_bonificacao_indevida.group(1))

        return
    

#Clube de Vantagens
    resultado_clube_de_ventagens = re.search(
        r"1717\s+CLUBE DE VANTAGENS\s+(-?\d+,\d+)\*",
        linha
    )

    if resultado_clube_de_ventagens:
        apartamento["Clube de Vantagens"] = converter_valor(resultado_clube_de_ventagens.group(1))

        return
    

#Cameras
    resultado_cameras = re.search(
        r"1764\s+CAMERAS(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_cameras:
        apartamento["Cameras"] = converter_valor(resultado_cameras.group(1))

        return


#-------------------------------------------------------------------------------------------------------#
def identificar_parcelas(texto):

    parcelas = {
        "seguro": "",
        "desobstrucao_esgoto": "",
        "fundo_pintura": "",
        "telhado": ""

    }

    resultado = re.search(
       r"3\s+SEGURO\s+(\d+)/(\d+)",
       texto,
       re.IGNORECASE 
    )

    if resultado:
        parcelas["seguro"] = (
           f"{int(resultado.group(1)):02d}/"
           f"{int(resultado.group(2)):02d}" 
        )

    resultado = re.search(
      r"78\s+DESOBSTRUCAO ESGOTO\s+(\d+)/(\d+)",
      texto,
      re.IGNORECASE  
    )

    if resultado:
        parcelas["desobstrucao_esgoto"] = (
           f"{int(resultado.group(1)):02d}/"
           f"{int(resultado.group(2)):02d}" 
        )

    resultado = re.search (
       r"89\s+FUNDO DE PINTURA\s+(\d+)/(\d+)",
       texto,
       re.IGNORECASE 
    )

    if resultado:
        parcelas["fundo_pintura"] = (
           f"{int(resultado.group(1)):02d}/"
           f"{int(resultado.group(2)):02d}" 
        )

    resultado = re.search(
        r"1195\s+TELHADO\s+(\d+)/(\d+)",
        texto,
        re.IGNORECASE
    )

    if resultado:
        parcelas["telhado"] = (
            f"{int(resultado.group(1)):02d}/"
            f"{int(resultado.group(2)):02d}"
        )

    return parcelas


#Extrai as informações dos boletos do condominio Ilhabela
def extrair_ilhabela(caminho_pdf):

    #Lista onde serão aramzenados todos os apartamentos encontrados
    apartamentos = [] #Cria uma lista onde vamos guardar todos os apartamentos encontrados.



    #Coordenadas utilizadas para dividir cada pagina em duas colunas.
    LIMITE_ESQUERDA = (0, 0, 298, 842)
    LIMITE_DIREITA  = (298, 0, 596, 842)


    #Abre o pdf.
    #o "with" fecha o arquivo automaticamente quando terminar.
    with pdfplumber.open (caminho_pdf) as pdf: 

        texto_completo = ""

        for pagina in pdf.pages:
            texto_completo += (pagina.extract_text() or "") + "\n"

        parcelas = identificar_parcelas(texto_completo)

        nome_coluna_fundo_pintura = (
           f"Fundo de Pintura {parcelas['fundo_pintura']}" 
        )

        nome_coluna_seguro = (
            f"Seguro {parcelas['seguro']}"
        )

        nome_coluna_desobstrucao = (
           f"Desobstrução Esgoto {parcelas['desobstrucao_esgoto']}" 
        )

        nome_coluna_telhado = (
           f"Telhado {parcelas['telhado']}" 
        )

        totais_pdf = {}

        apartamento = novo_apartamento(parcelas)

        print ("PARCELAS ENCONTRADAS", parcelas)

    
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
                        totais_pdf,
                        nome_coluna_seguro,
                        nome_coluna_desobstrucao,
                        nome_coluna_fundo_pintura,
                        nome_coluna_telhado 
                    )
                                
                else: processar_linha(
                        linha,
                        apartamento,
                        apartamentos,
                        parcelas
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
                            totais_pdf,
                            nome_coluna_seguro,
                            nome_coluna_desobstrucao,
                            nome_coluna_fundo_pintura,
                            nome_coluna_telhado
                        )
                                                
                    else:
                        processar_linha(
                              linha,
                              apartamento,
                              apartamentos,
                              parcelas
                        )


    #Salva o ultimo apartamento processado
    salvar_apartamento(apartamento, apartamentos)

    #Converte a lista de apartamentos em um DataFrame
    df = pd.DataFrame(apartamentos)

    return df, totais_pdf

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_totais(linha, totais_pdf, nome_coluna_seguro, nome_coluna_desobstrucao, nome_coluna_fundo_pintura, nome_coluna_telhado):


    #Cota do mes
    resultado_cota_do_mes = re.search(
        r"1\s+CONDOMÍNIO\s+(-?[\d\.]+,\d+)",
        linha
    )
    
    
    if resultado_cota_do_mes:
    
        valor = converter_valor(resultado_cota_do_mes.group(1))
    
        if valor > 0:
            totais_pdf["Cota do mês"] = valor
            
            return
    
#Agua
    resultado_agua = re.search(
       r"2\s+AGUA\s+(-?[\d.]+,\d+)",
       linha 
    )

    if resultado_agua:
        totais_pdf["Água"] = converter_valor(
            resultado_agua.group(1)
        )

        return

#Seguro
    resultado_seguro = re.search(
        r"3\s+SEGURO\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_seguro:
        totais_pdf[nome_coluna_seguro] = converter_valor(resultado_seguro.group(1))

        return
    

#Desobstrucao Esgoto
    resultado_desobstrucao_esgoto = re.search(
        r"78\s+DESOBSTRUCAO ESGOTO\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_desobstrucao_esgoto:
        totais_pdf[nome_coluna_desobstrucao] = converter_valor(resultado_desobstrucao_esgoto.group(1))

        return


#Fundo de Pintura
    resultado_fundo_de_pintura = re.search(
        r"89\s+FUNDO DE PINTURA\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_fundo_de_pintura:
        totais_pdf[nome_coluna_fundo_pintura] = converter_valor(resultado_fundo_de_pintura.group(1))

        return
    

#Salão de festas
    resultado_salao_de_festas = re.search(
        r"732 USO SALAO DE FESTAS\s+(-?[\d\.]+,\d+)", 
        linha
    )

    if resultado_salao_de_festas:

        valor = converter_valor(resultado_salao_de_festas.group(1))

        if "Salão de Festas" not in totais_pdf:
           
            totais_pdf["Salão de Festas"] = valor
        else:
            totais_pdf["Salão de Festas"] += valor
        
        return
    

#Seguro Cont Assis 24h
    resultado_seguro_cont_assis_24h = re.search(
        r"883\s+SEGURO CONT ASSIS 24H OPC\s+(-?[\d\.]+,\d+)\s*\*?",
        linha
    )

    if resultado_seguro_cont_assis_24h:
        totais_pdf["Seguro Cont. Assis. 24H OPC"] = converter_valor(resultado_seguro_cont_assis_24h.group(1))

        return


#Dif Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952\s+DIF. DOC PAGO A MAIOR(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:
        totais_pdf["Dif Doc Pago a Maior"] = converter_valor(resultado_dif_doc_pago_a_maior.group(1))

        return
    

#Dif Doc Pago a Menor
    resultado_dif_doc_pago_a_menor = re.search(
        r"953\s+DIF. DOC PAGO A MENOR(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_menor:
        totais_pdf["Dif Doc Pago a Menor"] = converter_valor(resultado_dif_doc_pago_a_menor.group(1))

        return

#Tarifa Basica de Agua
    resultado_tarifa_basica_de_agua = re.search(
        r"997\s+TARIFA BASICA DE AGUA\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_tarifa_basica_de_agua:
        totais_pdf["Tarifa Basica de Água"] = converter_valor(resultado_tarifa_basica_de_agua.group(1))

        return

#Telhado
    resultado_telhado = re.search(
        r"1195\s+TELHADO\s+(-?[\d\.]+,\d+)",
        linha
    )

    if resultado_telhado:
        totais_pdf[nome_coluna_telhado] = converter_valor(resultado_telhado.group(1))

        return


#Fundo Reserva
    resultado_fundo_reserva = re.search(
        r"1242\s+FUNDO RESERVA\s+\(5%\)\s+(-?\d+,\d+)",
        linha
    )

    if resultado_fundo_reserva:
        totais_pdf["Fundo Reserva (5%)"] = converter_valor(resultado_fundo_reserva.group(1))

        return
    

#Leitura de Agua
    resultado_leitura_de_agua = re.search(
        r"1334\s+LEITURA DE ÁGUA\s+(-?\d+,\d+)",
        linha
    )

    if resultado_leitura_de_agua:
        totais_pdf["Leitura de Água"] = converter_valor(resultado_leitura_de_agua.group(1))

        return
    

#Bonificacao Indevida
    resultado_bonificacao_indevida = re.search(
        r"1340\s+BONIFICAÇÃO INDEVIDA(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_bonificacao_indevida:
        totais_pdf["Bonificacao Indevida"] = converter_valor(resultado_bonificacao_indevida.group(1))

        return
    

#Clube de Vantagens
    resultado_clube_de_ventagens = re.search(
        r"1717\s+CLUBE DE VANTAGENS\s+(-?[\d\.]+,\d+)\s*\*?",
        linha
    )

    if resultado_clube_de_ventagens:
        totais_pdf["Clube de Vantagens"] = converter_valor(resultado_clube_de_ventagens.group(1))

        return
    

#Cameras
    resultado_cameras = re.search(
        r"1764\s+CAMERAS(?:\s+\d+/\d+)?\s+(-?\d+,\d+)",
        linha
    )

    if resultado_cameras:
        totais_pdf["Cameras"] = converter_valor(resultado_cameras.group(1))

        return