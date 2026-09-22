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
     "Reforco Orcamentario": None,
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

def processar_totais(texto, totais_pdf):

    linhas = texto.splitlines()
    

    encontrou_quadro = False
    tem_reforco = False
    valores_totais = []

    for linha in linhas:


        linha_corrigida = corrigir_texto_duplicado(linha)

        #Inicio do quadro
        if "CONTA" in linha_corrigida:
            encontrou_quadro = True

        if not encontrou_quadro:
            continue

        # Identifica qual conta estamos lendo
        if "4344" in linha_corrigida:
            tem_reforco = True

        #Procura valor monetario
        valores = re.findall(
           r"\d{1,3}(?:\.\d{3})+,\d{2}",
           linha_corrigida 
        )

        # Agua e cota aparecem juntos
        if not tem_reforco and len(valores) == 2:

            totais_pdf["Agua e Esgoto"] = converter_valor(valores[0])
            totais_pdf["Cota do Mes"] = converter_valor(valores[1])

        for valor in valores:
            valores_totais.append(converter_valor(valor))

    if tem_reforco and len(valores_totais) >= 4:

        totais_pdf["Reforco Orcamentario"] = valores_totais[1]
        totais_pdf["Agua e Esgoto"] = valores_totais[2]
        totais_pdf["Cota do Mes"] = valores_totais[3]


    # MODELO SEM REFORÇO
    elif not tem_reforco:

        # Remove valores repetidos
        valores_unicos = []

        for valor in valores_totais:
            if valor not in valores_unicos:
                valores_unicos.append(valor)

        # Precisamos de:
        # Água + Cota + Total Geral
        if len(valores_unicos) >= 3:

            total_geral = None

            # Descobre qual valor é a soma dos outros dois
            for i in range(len(valores_unicos)):
                for j in range(len(valores_unicos)):
                    for k in range(len(valores_unicos)):

                        if i == j or i == k or j == k:
                            continue

                        if abs(
                            valores_unicos[i]
                            - (
                                valores_unicos[j]
                                + valores_unicos[k]
                            )
                        ) < 0.01:

                            total_geral = valores_unicos[i]
                            break

                    if total_geral is not None:
                        break

                if total_geral is not None:
                    break

            # Remove somente o Total Geral
            if total_geral is not None:

                valores_verbas = [
                    valor
                    for valor in valores_unicos
                    if valor != total_geral
                ]

                if len(valores_verbas) >= 2:

                    totais_pdf["Agua e Esgoto"] = valores_verbas[0]
                    totais_pdf["Cota do Mes"] = valores_verbas[1]



def processar_grupo(grupo, apartamentos):

    # Percorre todas as unidades que pertencem ao grupo.abs
    for unidade in grupo["Unidades"]:

        #Cria um novo apartamento vazio.
        apartamento = novo_apartamento()

        # preenche os dados do apartamento
        apartamento["Bloco"] = grupo["Bloco"]
        apartamento["Unidade"] = unidade
        apartamento["Agua e Esgoto"] = grupo["Agua e Esgoto"]
        apartamento["Cota do Mes"] = grupo["Cota do Mes"]
        apartamento["Reforco Orcamentario"] = grupo["Reforco Orcamentario"]

        #Salva o apartamento na lista.
        salvar_apartamento(
            apartamento,
            apartamentos
        )


def extrair_soldoengenho(caminho_pdf):

    grupos = []
    apartamentos = []
    totais_pdf = {
        "Cota do Mes": 0,
        "Agua e Esgoto": 0,
        "Reforco Orcamentario": 0
    }

    unidades_temporarias = []
    bloco_atual = ""
    quantidade_esperada = 0

    agua_atual = None
    cota_atual = None
    reforco_atual = None

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            processar_totais(texto, totais_pdf)

            for linha in texto.splitlines():

                # Corrige os caracteres duplicados no PDF.
                linha = corrigir_texto_duplicado(linha)

                if "133.000,00" in linha:
                    print ("ANTERIOR >>>", repr(linha_anterior))
                    print ("ATUAL >>>", repr(linha))

                linha_anterior = linha

                if (
                    "CONDOMíNIO" in linha
                    or "ESGOTO" in linha
                    or "179.325" in linha
                    or "133.00" in linha
                    or "46.325" in linha
                ):
                    print("TOTAL >>>", repr(linha))

                # Procura unidades na linha.
                unidades_encontradas = re.findall(
                    r"\b(?:000)?[1-5]0[1-8]\b",
                    linha
                )


                for unidade in unidades_encontradas:
                    unidades_temporarias.append(
                        str(int(unidade))
                    )

                # Procura o bloco.
                resultado_bloco = re.match(
                    r"^(1[0-3]|[1-9])(?:\s|$)",
                    linha.strip()
                )

                if resultado_bloco:

                    bloco_encontrado = resultado_bloco.group(1)

                    # Bloco 1 possui 20 unidades.
                    if bloco_encontrado == "1":
                        quantidade_esperada = 20
                    else:
                        quantidade_esperada = 40

                    bloco_atual = bloco_encontrado

                # Procura os valores de agua e condominio
                valores_linha = re.findall(
                   r"R\$\s*(-?[\d\.]+,\d{2})",
                   linha
                )

                if len(valores_linha) == 3:
                    agua_atual = converter_valor(valores_linha[0])
                    cota_atual = converter_valor(valores_linha[1])

                elif len(valores_linha) == 4:
                    reforco_atual = converter_valor(valores_linha[0])
                    agua_atual = converter_valor(valores_linha[1])
                    cota_atual = converter_valor(valores_linha[2])

                # Se já sabemos o bloco e atingimos a quantidade esperada,
                # podemos salvar o grupo.
                if (
                    bloco_atual
                    and quantidade_esperada > 0
                    and len(unidades_temporarias) >= quantidade_esperada
                    and agua_atual is not None
                    and cota_atual is not None
                ):

                    unidades_do_bloco = unidades_temporarias[:quantidade_esperada]

                    grupos.append({
                        "Bloco": bloco_atual,
                        "Quantidade": quantidade_esperada,
                        "Unidades": unidades_do_bloco,
                        "Agua e Esgoto": agua_atual,
                        "Cota do Mes": cota_atual,
                        "Reforco Orcamentario": reforco_atual
                    })

                    # Mantém as unidades que já pertencem ao próximo bloco.
                    unidades_temporarias = unidades_temporarias[quantidade_esperada:]

                    bloco_atual = ""
                    quantidade_esperada = 0
                    agua_atual = None
                    cota_atual = None
                    reforco_atual = None

    for grupo in grupos:

        processar_grupo(
            grupo,
            apartamentos
        )

    df = pd.DataFrame(apartamentos)

    return df, totais_pdf
