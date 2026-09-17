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
     "Fundo de Reserva" : None,
     "Cota Extra" : None, 
     "Fundo de Obras" : None,
     "Salao de Festas": None,   
    }

#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):


#So salva se existir uma unidade cadastrada.
    if apartamento["Unidade"]:
        apartamentos.append(apartamento.copy())

#-------------------------------------------------------------------------------------------------------#

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_linha(linha, apartamento, apartamentos):

    # Identificando apartamento
    resultado = re.search(
        r"^(\d+)\s+(\d+).*?Cota condominial\s+\d{2}/\d{4}\s+(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado:

        # Salva o apartamento anterior
        salvar_apartamento(
            apartamento,
            apartamentos
        )

        # Limpa e prepara o novo apartamento
        apartamento.clear()
        apartamento.update(novo_apartamento())

        # Bloco e unidade
        apartamento["Bloco"] = resultado.group(1)
        apartamento["Unidade"] = resultado.group(2)

        # Cota do Mes
        apartamento["Cota do Mes"] = converter_valor(
            resultado.group(3)
        )

        return

    # Fundo de reserva
    resultado_fundo = re.search(
        r"Fundo de Reserva\s+\d{2}/\d{4}\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_fundo:
        apartamento["Fundo de Reserva"] = converter_valor(
            resultado_fundo.group(1)
        )
        return

    # Cota Ambiental
    resultado_cota_ambiental = re.search(
         r"Cota ambiental\s+\d{2}/\d{2}\s+(-?[\d\.]+,\d{2})",
         linha
    )

    if resultado_cota_ambiental:
        apartamento["Cota Extra"] = converter_valor(
            resultado_cota_ambiental.group(1)
        )
        return

    # Fundo de Obras
    resultado_fundo_obras = re.search(
        r"Fundo de obras\s+\d{2}/\d{2}\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_fundo_obras:
        apartamento["Fundo de Obras"] = converter_valor(
            resultado_fundo_obras.group(1)
        )
        return

    #Salão de Festas
    resultado_salao = re.search(
       r"Salão de festas\s+\d{2}/\d{2}\s+(-?[\d\.]+,\d{2})",
       linha 
    )

    if resultado_salao:
        apartamento["Salao de Festas"] = converter_valor(
            resultado_salao.group(1)
        )
        return


def processar_totais (linha, totais_pdf):

    #Cota do Mes
    resultado_cota = re.search(
      r"COTAS DO MÊS Cota condominial.*?(-?[\d\.]+,\d{2})$",
      linha  
    )

    if resultado_cota:
        totais_pdf["Cota do Mes"] = converter_valor(
            resultado_cota.group(1)
        )
        return

    # Fundo de reserva
    resultado_fundo = re.search(
        r"COTAS DO MÊS - FUNDO Fundo de Reserva.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_fundo:
        totais_pdf["Fundo de Reserva"] = converter_valor(
            resultado_fundo.group(1)
        )
        return

    # Cota Ambiental
    resultado_cota_ambiental = re.search(
         r"COTA EXTRA Cota ambiental.*?(-?[\d\.]+,\d{2})$",
         linha
    )

    if resultado_cota_ambiental:
        totais_pdf["Cota Extra"] = converter_valor(
            resultado_cota_ambiental.group(1)
        )
        return

    # Fundo de Obras
    resultado_fundo_obras = re.search(
        r"FUNDO DE OBRAS Fundo de obras.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_fundo_obras:
        totais_pdf["Fundo de Obras"] = converter_valor(
            resultado_fundo_obras.group(1)
        )
        return

    #Salão de Festas
    resultado_salao = re.search(
       r"Salão de Festas Salão de festas.*?(-?[\d\.]+,\d{2})$",
       linha 
    )

    if resultado_salao:
        totais_pdf["Salao de Festas"] = converter_valor(
            resultado_salao.group(1)
        )
        return


def extrair_sierraandorra(caminho_pdf):

    apartamentos = []
    apartamento = novo_apartamento()

    totais_pdf = {
        "Cota do Mes": 0,
        "Fundo de Reserva": 0,
        "Cota Extra": 0,
        "Fundo de Obras": 0,
        "Salao de Festas": 0,
    }

    quadro_totais = False

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():

                #Chegou no quadro de totais
                if "Discriminação das verbas" in linha:
                    quadro_totais = True
                    continue

                # Processa somente a parte dos apartamentos
                if not quadro_totais:

                    processar_linha(
                        linha,
                        apartamento,
                        apartamentos
                    )
                else:
                    processar_totais(
                        linha,
                        totais_pdf
                    )

    salvar_apartamento(apartamento, apartamentos)

    df = pd.DataFrame(apartamentos)

    print(df)

    return df, totais_pdf
