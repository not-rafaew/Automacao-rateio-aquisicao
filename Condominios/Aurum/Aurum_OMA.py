#Bibliotecas usadas
import pymupdf #Biblioteca de ler PDFs.
import re # Biblioteca de Regex, utilizada para procurar padrões e palavras no PDF.
import pandas as pd # Biblioteca para controlar planilhas em python.
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
   r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
)
def novo_apartamento():
    return{
     "Bloco" : "", #Salva o bloco.
     "Unidade" : "", #Salva a unidade.
     "Vencimento" : "",

     "Cota do Mes": None,
     "Agua": None,
     "Consumo de Energia Eletrica" : None,
     "Fundo de Reserva" : None, 
     "Consumo de Gas" : None,
     "Multa Regulamento Interno" : None,
     "Reembolsos Diversos" : None, 
     "Salão de Festas" : None, 
     "Espaço Gourmet": None,
    }

def converter_valor(valor):
    return float(valor.replace(".", "").replace(",", "."))

def processar_linha(elementos, apartamentos):

    unidades = []

    quantidade = None
    total_unidade = None

    cota_mes = None
    fundo_reserva = None
    energia = None
    agua = None
    espaco_gourmet = None
    gas = None

    for elemento in elementos:

        texto = elemento["texto"].replace(",", "", 1) if elemento["texto"].endswith(",") else elemento["texto"]
        left = elemento["left"]

        if left < 1400:

            if re.fullmatch(r"000[A-Z0-9]+", texto):
                unidades.append(texto)

        elif 1450 <= left < 1650:

            if texto.isdigit():
                quantidade = int(texto)

        elif 1650 <= left < 1900:
            total_unidade = converter_valor(texto)

        elif 1900 <= left < 2150:
            cota_mes = converter_valor(texto)

        elif 2150 <= left < 2450:
            fundo_reserva = converter_valor(texto)

        elif 2450 <= left < 2700:
            energia = converter_valor(texto)

        elif 2700 <= left < 2950:
            agua = converter_valor(texto)

        elif 2950 <= left < 3200:
            espaco_gourmet = converter_valor(texto)

        elif left >= 3200:
            gas = converter_valor(texto)

    if not unidades:
         return

    if quantidade is not None and len(unidades) != quantidade:
        print(
            f"AVISO: quantidade diferente na linha. "
            f"Unidades encontradas: {len(unidades)} | "
            f"Quantidade informada: {quantidade}"
        )

    for unidade in unidades:

        apartamento = novo_apartamento()

        apartamento["Bloco"] = "0"
        apartamento["Unidade"] = unidade
        apartamento["Vencimento"] = ""

        apartamento["Cota do Mes"] = cota_mes
        apartamento["Fundo de Reserva"] = fundo_reserva
        apartamento["Consumo de Energia Eletrica"] = energia
        apartamento["Agua"] = agua
        apartamento["Espaço Gourmet"] = espaco_gourmet
        apartamento["Consumo de Gas"] = gas

        apartamentos.append(apartamento)


def processar_totais(elementos):

    totais_pdf = {
        "Cota do Mes": 0,
        "Fundo de Reserva": 0,
        "Consumo de Energia Eletrica": 0,
        "Agua": 0,
        "Espaço Gourmet": 0,
        "Consumo de Gas": 0,
    }

    for elemento in elementos:

        texto = elemento["texto"]
        left = elemento["left"]

        print ("TOTAL:", repr(texto), "LEFT", left)

        if texto.endswith(","):
            texto = texto[:-1]

        if 1900 <= left < 2150:
            totais_pdf["Cota do Mes"] = converter_valor(texto)

        elif 2150 <= left < 2450:
            totais_pdf["Fundo de Reserva"] = converter_valor(texto)

        elif 2450 <= left < 2700:
            totais_pdf["Consumo de Energia Eletrica"] = converter_valor(texto)

        elif 2700 <= left < 2950:
            totais_pdf["Agua"] = converter_valor(texto)

        elif 2950 <= left < 3200:
           totais_pdf["Espaço Gourmet"] = converter_valor(texto)

        elif left >= 3200:
           totais_pdf["Consumo de Gas"] = converter_valor(texto)

    return totais_pdf


def extrair_aurum_oma(caminho_pdf):

    apartamentos = []
    totais_pdf = []

    pdf = pymupdf.open(caminho_pdf)

    pagina = pdf[0]

    imagem = pagina.get_pixmap(dpi=300)

    imagem.save("teste_aurum.png")

    dados = pytesseract.image_to_data(
        "teste_aurum.png",
        lang="por",
        output_type=pytesseract.Output.DICT
    )

    linhas = {}

    for i in range(len(dados["text"])):

        texto = dados["text"][i].strip()

        if not texto:
            continue

        top = dados["top"][i]
        left = dados["left"][i]

        top_linha = None

        for top_existente in linhas:

            if abs(top - top_existente) <= 5:
                top_linha = top_existente
                break

        if top_linha is None:
            top_linha = top
            linhas[top_linha] = []

        linhas[top_linha].append({
            "texto": texto,
            "left": left
        })

    for top, elementos in sorted(linhas.items()):

        elementos.sort(key=lambda elemento: elemento["left"])

        textos = [elemento["texto"] for elemento in elementos]
        
        if "Total" in textos and "rateado" in textos:
            totais_pdf = processar_totais(elementos)
            continue

            print("\nTOTAL RATEADO:")

            for elemento in elementos:
                print(
                    elemento["texto"],
                    "->",
                    elemento["left"]
                )
        tem_unidade = any(
            re.fullmatch(
              r"000[A-Z0-9]+,?",
              elemento["texto"]  
            )
            for elemento in elementos
        )

        if not tem_unidade:
            continue

        processar_linha(elementos, apartamentos)

    df = pd.DataFrame(apartamentos)

    print(df)
    print()
    print("QUANTIDADE DE APARTAMENTOS", len(df))

    print()
    print("TOTAIS EXTRAÍDOS:")

    print("Cota do Mes:", df["Cota do Mes"].sum())
    print("Fundo dee Reserva:", df["Fundo de Reserva"].sum())
    print(
        "Energia:",
        df["Consumo de Energia Eletrica"].sum()
    )
    print("Agua:", df["Agua"].sum())
    print("Espaço Gourmet:", df["Espaço Gourmet"].sum())
    print("Gas:", round(df["Consumo de Gas"].sum(), 2))

    pdf.close
        
    return df, totais_pdf