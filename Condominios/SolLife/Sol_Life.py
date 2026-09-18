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
     #"Acordo" : None,
     "Cedae" : None, 
     "Agua Area Comum" : None,
     "Dif. da Agua do Mes Anterior": None,
     "Fundo de Reserva" : None,    
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

#Processa cada linha encontrada no PDF
def processar_linha(linha, apartamento, apartamentos):

    # Identificando apartamento
    resultado = re.search(
        r"^(\d+)-(\d+)\s+(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado:
        # Salva o apartamento anterior

        salvar_apartamento(
            apartamento,
            apartamentos
        )

        #Limpa e prepara o novo apartamento
        apartamento.clear()
        apartamento.update(novo_apartamento())

        # Bloco e unidade
        apartamento["Bloco"] = resultado.group(1)
        apartamento["Unidade"] = resultado.group(2)

        return

    # Cota
    resultado_cota = re.search(
        r"1\.2\.01 - Cota Condominial\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_cota:

        apartamento["Cota do Mes"] = converter_valor(
            resultado_cota.group(1)
        )

        return

    # Acordo
    #resultado_acordo = re.search(
      #  r"1\.2\.31 - Acordo(?:\s+-\s+\d+/\d+)?\s+(-?[\d\.]+,\d{2})",
     #   linha
   # )

   # if resultado_acordo:

       # apartamento["Acordo"] = converter_valor(
       #     resultado_acordo.group(1)
       # )

      #  return


    # Cedae 
    resultado_cedae = re.search(
        r"1\.2\.32 - Cedae\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_cedae:

        apartamento["Cedae"] = converter_valor(
            resultado_cedae.group(1)
        )

        return

    # Agua Area Comum

    resultado_agua_area_comum = re.search(
        r"1\.2\.70 - Água Área Comum\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_agua_area_comum:

        apartamento["Agua Area Comum"] = converter_valor(
            resultado_agua_area_comum.group(1)
        )

        return

    # Diferença da agua do Mes Anteriror

    resultado_diferenca_agua = re.search(
        r"1\.2\.121 - DIF\. DA ÁGUA DO MÊS ANTERIOR\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_diferenca_agua:

        apartamento["Dif. da Agua do Mes Anterior"] = converter_valor(
            resultado_diferenca_agua.group(1)
        )

        return

    # Fundo de Reserva

    resultado_fundo = re.search(
        r"1\.4\.03 - Fundo de Reserva\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_fundo:

        apartamento["Fundo de Reserva"] = converter_valor(
            resultado_fundo.group(1)
        )

        return
    

def extrair_sollife(caminho_pdf):

    apartamentos = []
    apartamento = novo_apartamento()

    totais_pdf = {
        "Cota do Mes": 0,
       # "Acordo" : 0,
        "Cedae" : 0, 
        "Agua Area Comum" : 0,
        "Dif. da Agua do Mes Anterior": 0,
        "Fundo de Reserva" : 0, 
    }

    quadro_totais = False

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():

                if "Total de receitas das unidades" in linha:
                    quadro_totais = True
                    continue

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

    salvar_apartamento(
        apartamento,
        apartamentos
    )

    df = pd.DataFrame(apartamentos)

    print(df)

    return df, totais_pdf

def processar_totais(linha, totais_pdf):

    # Cota
    resultado_cota = re.search(
        r"1\.2\.01 - Cota Condominial\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_cota:

        totais_pdf["Cota do Mes"] = converter_valor(
            resultado_cota.group(1)
        )

        return

    # Acordo
   # resultado_acordo = re.search(
   #     r"1\.2\.31 - Acordo.*?\s+(-?[\d\.]+,\d{2})$",
    #    linha
   # )

   # if resultado_acordo:

     #   totais_pdf["Acordo"] = converter_valor(
     #       resultado_acordo.group(1)
     #   )

     #   return


    # Cedae 
    resultado_cedae = re.search(
        r"1\.2\.32 - Cedae\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_cedae:

        totais_pdf["Cedae"] = converter_valor(
            resultado_cedae.group(1)
        )

        return

    # Agua Area Comum

    resultado_agua_area_comum = re.search(
        r"1\.2\.70 - Água Área Comum\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_agua_area_comum:

        totais_pdf["Agua Area Comum"] = converter_valor(
            resultado_agua_area_comum.group(1)
        )

        return

    # Diferença da agua do Mes Anteriror

    resultado_diferenca_agua = re.search(
        r"1\.2\.121 - DIF\. DA ÁGUA DO MÊS ANTERIOR\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_diferenca_agua:

        totais_pdf["Dif. da Agua do Mes Anterior"] = converter_valor(
            resultado_diferenca_agua.group(1)
        )

        return

    # Fundo de Reserva

    resultado_fundo = re.search(
        r"1\.4\.03 - Fundo de Reserva\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_fundo:

        totais_pdf["Fundo de Reserva"] = converter_valor(
            resultado_fundo.group(1)
        )

        return