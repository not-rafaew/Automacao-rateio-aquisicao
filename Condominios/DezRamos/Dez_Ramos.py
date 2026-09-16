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
     "Agua-Esgoto" : None,
     "Energia" : None, 
     "Fundo de Reserva" : None,
     "Cota Extra": None,
     "Segurança Externa" : None, 
     "Instalação - Projeto Solar" : None,     
    }

#-------------------------------------------------------------------------------------------------------#
#Salva o apartamento atual na lista.
def salvar_apartamento(apartamento, apartamentos):

    if apartamento["Unidade"]:

        apartamento_salvo = apartamento.copy()

        apartamento_salvo.pop(
            "_possivel_cota_extra",
            None
        )

        apartamento_salvo.pop(
            "_aguardando_cota_extra",
            None
        )
        
        apartamentos.append(apartamento_salvo)

#-------------------------------------------------------------------------------------------------------#

def processar_linha(linha, apartamento, apartamentos):

    if (
        "BL01-AP0105" in linha
        or apartamento.get("Unidade") == "0105"
     ):
        print(
            "DEBUG 0105 |",
            "UNIDADE:", apartamento.get("Unidade"),
            "| AGUARDANDO:", apartamento.get("_aguardando_cota_extra"),
            "| POSSIVEL:", apartamento.get("_possivel_cota_extra"),
            "| COTA:", apartamento.get("Cota Extra"),
            "| LINHA:", repr(linha)
        )

#IDENTIFICANDO APARTAMENTO
    resultado = re.search(
        r"BL(\d+)-AP(\d+).*?(\d{2}/\d{2}/\d{4})", 
        linha
    )

    if resultado:
        salvar_apartamento(apartamento, apartamentos)

        apartamento.clear()
        apartamento.update(novo_apartamento())

        apartamento["Bloco"] = resultado.group(1)
        apartamento["Unidade"] = resultado.group(2)
        apartamento["Vencimento"] = resultado.group(3)


          # Cota do mes 
        resultado_cota_do_mes = re.search(
            r"Taxa Condominial\s+(-?[\d\.]+,\d{2})",
            linha
        )

        if resultado_cota_do_mes:
            valor = converter_valor(
                resultado_cota_do_mes.group(1)
            )

            apartamento["Cota do Mes"] = valor


        # Projeto Solar
        resultado_projeto_solar = re.search(
            r"Instalação - Projeto Solar\s+\d+/\d+\s+(-?[\d\.]+,\d{2})",
            linha
        )

        if resultado_projeto_solar:

            valor = converter_valor(
                resultado_projeto_solar.group(1)
            )

            apartamento["Instalação - Projeto Solar"] = valor

       

        # Cota extra
        #Verifica se a cota extra começa na mesma linha do apartamento
        if "Custeio das despesas referentes ao registro da" in linha:

            resultado_cota_extra = re.search(
              r"\d+/\d+\s+(-?[\d\.]+,\d{2})",
              linha  
            )

            # Caso valor tambem esteja na mesma linha
            if resultado_cota_extra:

                apartamento["Cota Extra"] = converter_valor(
                    resultado_cota_extra.group(1)
                )

            # Caso a descrição esteja na linha do apartamento,
            # Mas o valor venhas nas proximas linhas
            else:
                
                apartamento["_aguardando_cota_extra"] = True

        return


# Cota do Mes
    resultado_cota_do_mes = re.search(
        r"Taxa Condominial\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_cota_do_mes:

        valor = converter_valor(
            resultado_cota_do_mes.group(1)
        )

        apartamento["Cota do Mes"] = valor

        return


# Agua-Esgoto
    resultado_agua_esgoto = re.search(
        r"Água-Esgoto(?:\s+ref\.\s+\d{2}/\d{4})?\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_agua_esgoto:
        
        valor = converter_valor(
            resultado_agua_esgoto.group(1)
        )
    
        apartamento["Agua-Esgoto"] = valor

        return

# Energia
    resultado_energia = re.search(
        r"Energia\s+ref\.\s+\d{2}/\d{4}\s+(-?[\d\.]+,\d{2})",
        linha 
    )

    if resultado_energia:
        
        valor = converter_valor(
            resultado_energia.group(1)
        )

        apartamento["Energia"] = valor

        return

# Fundo de Reserva
    resultado_fundo_de_reserva = re.search(
        r"Fundo de Reserva\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_fundo_de_reserva:

        valor = converter_valor(
            resultado_fundo_de_reserva.group(1)
        )

        apartamento["Fundo de Reserva"] = valor

        return

# Cota extra
#Caso 1:
# O valor apareceu ANTES da descrição
    resultado_parcela_solitaria = re.fullmatch(
        r"\d+/\d+\s+(-?[\d\.]+,\d{2})",
        linha.strip()
    )

    if resultado_parcela_solitaria:

        valor = converter_valor(
            resultado_parcela_solitaria.group(1)
        )

        # Se já vimos a descrição, esse valor é a cota extra
        if apartamento.get ("_aguardando_cota_extra"):

            apartamento["Cota Extra"] = valor

            apartamento.pop(
                "_aguardando_cota_extra",
                None
            )
            return

        #Senão guarda porque a descrição pode aparecer depois
        apartamento["_possivel_cota_extra"] = valor

        return
    # encontrou a descrição da cota extra
    if "Custeio das despesas referentes ao registro da" in linha:

        #Caso normal: descrição e valor estão juntos
        resultado_cota_extra = re.search(
            r"\d+/\d+\s+(-?[\d\.]+,\d{2})",
            linha
        )

        if resultado_cota_extra:

            apartamento["Cota Extra"] = converter_valor(
                resultado_cota_extra.group(1)
            )
            return
        
        #O valor apareceu antes da descrição
        if "_possivel_cota_extra" in apartamento:

            apartamento["Cota Extra"] = apartamento.pop(
                "_possivel_cota_extra"
            )

            return

        #A descrição veio primeiro
        # Agora esperamos o valor nas proximas linhas.
        apartamento["_aguardando_cota_extra"] = True

        return

# Segurança Externa
    resultado_seguranca_externa = re.search(
        r"Segurança Externa\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_seguranca_externa:

        valor = converter_valor(
            resultado_seguranca_externa.group(1)
        )

        apartamento["Segurança Externa"] = valor

        return

# Projeto Solar
    resultado_projeto_solar = re.search(
        r"Instalação - Projeto Solar\s+\d+/\d+\s+(-?[\d\.]+,\d{2})",
        linha
    )

    if resultado_projeto_solar:

        valor = converter_valor(
            resultado_projeto_solar.group(1)
        )

        apartamento["Instalação - Projeto Solar"] = valor

        return

def extrair_dez_ramos(caminho_pdf):

    apartamentos = []
    apartamento = novo_apartamento()

    totais_pdf = {
    "Cota do Mes": 0,
    "Agua-Esgoto" : 0,
    "Energia" : 0, 
    "Fundo de Reserva" : 0,
    "Cota Extra": 0,
    "Segurança Externa" : 0, 
    "Instalação - Projeto Solar" : 0, 
    }

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text() or ""

            for linha in texto.splitlines():

                processar_linha(
                    linha,
                    apartamento,
                    apartamentos
                )

                if apartamento.get("Unidade") == "0109":
                    print(
                        "DEBUG 0109:",
                        repr(linha)
                    )

                # Processa apenas as linhas do Resumo Contabil
                if re.match(r"1\.\d+\s+-", linha):
                    processar_totais(
                        linha,
                        totais_pdf
                    )

    salvar_apartamento(apartamento, apartamentos)

    df = pd.DataFrame(apartamentos)

    print(df)

    # Teste da quantidade de despesas encontradas
    print("\n=== QUANTIDADE PREENCHIDA ===")

    print(df[
        [
            "Cota do Mes",
            "Agua-Esgoto",
            "Energia",
            "Fundo de Reserva",
            "Cota Extra",
            "Segurança Externa",
            "Instalação - Projeto Solar"
        ]
    ].count())

    # Teste da soma das despesas
    print("\n=== SOMAS ===")

    print(df[
        [
            "Cota do Mes",
            "Agua-Esgoto",
            "Energia",
            "Fundo de Reserva",
            "Cota Extra",
            "Segurança Externa",
            "Instalação - Projeto Solar"
        ]
    ].sum())

    return df, totais_pdf

#Converte um valor do formato brasileiro para float.
def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_totais(linha, totais_pdf):

    # Cota do Mes
    resultado_cota_do_mes = re.search(
        r"Taxa Condominial.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_cota_do_mes:

        valor = converter_valor(
            resultado_cota_do_mes.group(1)
        )

        totais_pdf["Cota do Mes"] = valor

        return


# Agua-Esgoto
    resultado_agua_esgoto = re.search(
        r"Água-Esgoto.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_agua_esgoto:
        
        valor = converter_valor(
            resultado_agua_esgoto.group(1)
        )
    
        totais_pdf["Agua-Esgoto"] = valor

        return

# Energia
    resultado_energia = re.search(
        r"Energia.*?(-?[\d\.]+,\d{2})$",
        linha 
    )

    if resultado_energia:
        
        valor = converter_valor(
            resultado_energia.group(1)
        )

        totais_pdf["Energia"] = valor

        return

# Fundo de Reserva
    resultado_fundo_de_reserva = re.search(
        r"Fundo de Reserva.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_fundo_de_reserva:

        valor = converter_valor(
            resultado_fundo_de_reserva.group(1)
        )

        totais_pdf["Fundo de Reserva"] = valor

        return

# Cota extra

    resultado_cota_extra = re.search(
        r"Cota Extra.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_cota_extra:

        valor = converter_valor(
            resultado_cota_extra.group(1)
        )

        totais_pdf["Cota Extra"] = valor

        return

# Segurança Externa
    resultado_seguranca_externa = re.search(
        r"Segurança Externa.*?(-?[\d\.]+,\d{2})$",
        linha
    )

    if resultado_seguranca_externa:

        valor = converter_valor(
            resultado_seguranca_externa.group(1)
        )

        totais_pdf["Segurança Externa"] = valor

        return

# Instalação - Projeto Solar 
    resultado_instalacao_projeto_solar = re.search(
        r"Instalação - Projeto Solar.*?(-?[\d\.]+,\d{2})$",
        linha
    ) 

    if resultado_instalacao_projeto_solar:

        valor = converter_valor(
            resultado_instalacao_projeto_solar.group(1)
        )

        totais_pdf["Instalação - Projeto Solar"] = valor

        return