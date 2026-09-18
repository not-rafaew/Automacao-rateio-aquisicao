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
     "Agua e Esgoto" : None,     
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


def corrigir_texto_duplicado(texto):

    texto_corrigido = ""

    for i in range(0, len(texto), 2):
        texto_corrigido += texto[i]

    return texto_corrigido


def processar_linha(linha, bloco_atual, apartamentos):

    # Corrige os caracteres duplicados no PDF
    linha = corrigir_texto_duplicado(linha)

    # Procura todas as unidades existentes na linha
    unidades = re.findall(
        r"\b000(\d{3})\b",
        linha
    )

    # Salva cada unidade encontrada
    for unidade in unidades:

        apartamento = novo_apartamento()

        apartamento["Bloco"] = bloco_atual
        apartamento["Unidade"] = unidade

        salvar_apartamento(
            apartamento,
            apartamentos
        )



caminho_pdf = r"C:\Users\guug0\OneDrive\Desktop\Rateio - Condomínio Parque Sol do Engenho\Rateio - Condomínio Parque Sol do Engenho\Abril - RATEIO (4) (1) (1).pdf"

with pdfplumber.open(caminho_pdf) as pdf:

    for pagina in pdf.pages:

        texto = pagina.extract_text() or ""

        for linha in texto.splitlines():

            linha = corrigir_texto_duplicado(linha)

            # Blocos que aparecem sozinhos na linha.
            resultado_bloco = re.match(
                r"^(1[0-3]|[1-9])(?:\s|$)",
                linha.strip()
            )

            if resultado_bloco:

                bloco = resultado_bloco.group(1)

                print("BLOCO ENCONTRADO:", bloco)

