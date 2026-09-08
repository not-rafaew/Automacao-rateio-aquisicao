import pdfplumber

caminho_pdf = r"C:\Users\Rafael Soares\Desktop\Rateio Aurum\Previa de cota condominial - Aurum Bela Vista - Dezembro.pdf"

with pdfplumber.open(caminho_pdf) as pdf:

    pagina = pdf.pages[0]

    palavras = pagina.extract_words()

    for palavra in palavras:

        if palavra["text"] == "000032":

            print(palavra)