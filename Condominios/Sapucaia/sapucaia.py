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

     "Cota do mês": None,
     "Devolução Luz": None,
     "Devolução" : None,
     "Seguro Cont. Assis. 24H OPC" : None,
     "Clube de Vantagens": None,
     "Reserva de Ambientes Site" : None,
     "Dif. Doc Pago a Maior" : None,
     "Unidades Agrupadas" : [],
     
    }

#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):

#So salva se existir uma unidade cadastrada.
    if not apartamento["Unidade"]:
        return
    
    unidades_agrupadas = apartamento["Unidades Agrupadas"]

    #Caso existam casas agrupadas
    if unidades_agrupadas:

        quantidade = len(unidades_agrupadas)

        for unidade in unidades_agrupadas:

            nova_casa = apartamento.copy()

            nova_casa["Unidade"] = unidade

            #Divide todas as despesas
            for campo, valor in nova_casa.items():

                if isinstance(valor, (int, float)):

                    nova_casa[campo] = round(
                        valor / quantidade, 2
                    )

            # Remove o campo auxiliar
            nova_casa.pop("Unidades Agrupadas")

            apartamentos.append (nova_casa)

    else:
        nova_casa = apartamento.copy()

        nova_casa.pop("Unidades Agrupadas")

        apartamentos.append(nova_casa)

#-------------------------------------------------------------------------------------------------------#


def processar_linha (linha, apartamento, apartamentos):

    # Identificando a casa
    resultado = re.search(
       r"CASA (\d+) (\d{2}/\d{2}/\d{4})",
       linha
    )

    if resultado: 
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento())

        apartamento["Unidade"] = f"CASA {resultado.group(1)}"
        apartamento["Vencimento"] = resultado.group(2)

        return

    # Identifica casas agrupadas
    resultado_agrupamento = re.search(
       r"G CASA\s+(\d+)/(\d+)",
       linha 
    )

    if resultado_agrupamento:

        apartamento["Unidades Agrupadas"] = [
            f"CASA {resultado_agrupamento.group(1)}",
            f"CASA {resultado_agrupamento.group(2)}",
        ]

        return

    # DESPESAS

    #Cota do mes
    resultado_cota_do_mes = re.search(
        r"^1\s+CONDOMÍNIO\s+(-?[\d.]+,\d+)",
        linha.strip()
    )

    if resultado_cota_do_mes:

        valor = converter_valor(
            resultado_cota_do_mes.group(1)
        )

        if apartamento["Cota do mês"] is None:
            apartamento["Cota do mês"] = 0

        apartamento["Cota do mês"] += valor

        return

    # Devolução Luz
    resultado_devolucao_luz = re.search(
        r"744\s+DEVOLUCAO LUZ\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_devolucao_luz:

        valor = converter_valor(
            resultado_devolucao_luz.group(1)
        )

        if apartamento["Devolução Luz"] is None:
            apartamento["Devolução Luz"] = 0

        apartamento["Devolução Luz"] += valor

        return

    # Devolução
    resultado_devolucao = re.search(
        r"856\s+DEVOLUÇÃO(?:\s+1/1)?\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_devolucao:

        apartamento["Devolução"] = converter_valor(
            resultado_devolucao.group(1)
        )

        return

    # Seguro
    resultado_seguro = re.search(
        r"883\s+SEGURO CONT ASSIS 24H\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_seguro:

        apartamento["Seguro Cont. Assis. 24H OPC"] = converter_valor(
            resultado_seguro.group(1)
        )

        return

    # Dif. Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952\s+DIF\.\s+DOC PAGO A MAIOR(?:\s+1/1)?\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:

        apartamento["Dif. Doc Pago a Maior"] = converter_valor(
            resultado_dif_doc_pago_a_maior.group(1)
        )

        return

    # Clube de Vantagens
    resultado_clube_de_vantagens = re.search(
        r"1717\s+CLUBE DE VANTAGENS\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_clube_de_vantagens:

        apartamento["Clube de Vantagens"] = converter_valor(
            resultado_clube_de_vantagens.group(1)
        )

        return

    # Reserva de Ambientes Site
    resultado_reserva_de_ambientes = re.search(
        r"1722\s+RESERVA DE AMBIENTES(?:\s+1/1)?\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_reserva_de_ambientes:

        valor = converter_valor(
            resultado_reserva_de_ambientes.group(1)
        )

        if apartamento["Reserva de Ambientes Site"] is None:
            apartamento["Reserva de Ambientes Site"] = 0

        apartamento["Reserva de Ambientes Site"] += valor

        return

def extrair_sapucaia(caminho_pdf):

    # Lista onde serão armazenadas todas as casas
    apartamentos = []

    # Cria uma nova unidade
    apartamento = novo_apartamento()

    totais_pdf = {}

    # Coordenadas para dividir a página em duas colunas
    LIMITE_ESQUERDA = (0, 0, 298, 842)
    LIMITE_DIREITA = (298, 0, 596, 842)

    # Abre o PDF
    with pdfplumber.open(caminho_pdf) as pdf:

        chegou_nos_totais = False

        # Percorre todas as páginas
        for pagina in pdf.pages:

            # Divide a página
            esquerda = pagina.crop(LIMITE_ESQUERDA)
            direita = pagina.crop(LIMITE_DIREITA)

            # Extrai os textos
            texto_esquerda = esquerda.extract_text() or ""
            texto_direita = direita.extract_text() or ""

            # Divide os textos em linhas
            linhas_esquerda = texto_esquerda.splitlines()
            linhas_direita = texto_direita.splitlines()

            # Processa a coluna esquerda
            for linha in linhas_esquerda:

                if "TOTAIS" in linha:
                    chegou_nos_totais = True
                    continue

                if chegou_nos_totais:
                    processar_totais(linha, totais_pdf)

                else:
                    processar_linha(
                        linha,
                        apartamento,
                        apartamentos
                    )

            # Processa a coluna direita
            for linha in linhas_direita:

                if "TOTAIS" in linha:
                    chegou_nos_totais = True
                    continue

                if chegou_nos_totais:
                    processar_totais(linha, totais_pdf)

                else:
                    processar_linha(
                        linha,
                        apartamento,
                        apartamentos
                    )

    # Salva a última casa processada
    salvar_apartamento(apartamento, apartamentos)

    # Converte a lista em um DataFrame
    df = pd.DataFrame(apartamentos)

    return df, totais_pdf

def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))


def processar_totais(linha, totais_pdf):

    # Cota do mês
    resultado_cota_do_mes = re.search(
        r"^1\s+CONDOMÍNIO\s+(-?[\d.]+,\d+)",
        linha.strip()
    )

    if resultado_cota_do_mes:

        totais_pdf["Cota do mês"] = converter_valor(
            resultado_cota_do_mes.group(1)
        )

        return

    # Devolução Luz
    resultado_devolucao_luz = re.search(
        r"744\s+DEVOLUCAO LUZ\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_devolucao_luz:

        totais_pdf["Devolução Luz"] = converter_valor(
            resultado_devolucao_luz.group(1)
        )

        return

    # Devolução
    resultado_devolucao = re.search(
        r"856\s+DEVOLUÇÃO\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_devolucao:

        totais_pdf["Devolução"] = converter_valor(
            resultado_devolucao.group(1)
        )

        return

    # Seguro
    resultado_seguro = re.search(
        r"883\s+SEGURO CONT ASSIS 24H OPC\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_seguro:

        totais_pdf["Seguro Cont. Assis. 24H OPC"] = converter_valor(
            resultado_seguro.group(1)
        )

        return

    # Dif. Doc Pago a Maior
    resultado_dif_doc_pago_a_maior = re.search(
        r"952\s+DIF\.\s+DOC PAGO A MAIOR\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_dif_doc_pago_a_maior:

        totais_pdf["Dif. Doc Pago a Maior"] = converter_valor(
            resultado_dif_doc_pago_a_maior.group(1)
        )

        return

    # Clube de Vantagens
    resultado_clube_de_vantagens = re.search(
        r"1717\s+CLUBE DE VANTAGENS\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_clube_de_vantagens:

        totais_pdf["Clube de Vantagens"] = converter_valor(
            resultado_clube_de_vantagens.group(1)
        )

        return

    # Reserva de Ambientes Site
    resultado_reserva_de_ambientes = re.search(
        r"1722\s+RESERVA DE AMBIENTES SITE\s+(-?[\d.]+,\d+)",
        linha
    )

    if resultado_reserva_de_ambientes:

        totais_pdf["Reserva de Ambientes Site"] = converter_valor(
            resultado_reserva_de_ambientes.group(1)
        )

        return