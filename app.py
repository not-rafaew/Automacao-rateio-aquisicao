from flask import Flask, render_template, request, send_file
import tempfile
from pathlib import Path
from io import BytesIO
import webbrowser
import threading

from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Condominios.Aurum.Aurum_v2 import extrair_aurum
from Condominios.DezRamos.Dez_Ramos import extrair_dez_ramos
from Condominios.GrandVille.GrandVille import extrair_grandville
from Condominios.SierraAndorra.Sierra_Andorra import extrair_sierraandorra
from Condominios.SolLife.Sol_Life import extrair_sollife
from Condominios.Sol_Engenho.Sol_Engenho import extrair_soldoengenho
from Condominios.Aleixo.Aleixo import extrair_aleixo
from Condominios.Conviva.Conviva import extrair_conviva

from Exportacao.salvar_excel import salvar_excel
from Exportacao.salvar_excel_aleixo import salvar_excel_aleixo

app = Flask(__name__)

extratores = {
    "marechal": extrair_marechal,
    "ilhabela": extrair_ilhabela,
    "duet_barra": extrair_duet,
    "aurum": extrair_aurum,
    "dez_ramos": extrair_dez_ramos,
    "grandville": extrair_grandville,
    "sierra_andorra": extrair_sierraandorra,
    "sol_life": extrair_sollife,
    "sol_engenho": extrair_soldoengenho,
    "aleixo": extrair_aleixo,
    "conviva": extrair_conviva
}

@app.route("/", methods=["GET", "POST"])
def inicio():
    
    if request.method == "POST":

        condominio = request.form.get("condominio")
        arquivo = request.files.get("arquivo")

        if not condominio:
            return render_template(
                "index.html",
                erro="Selecione um condominio"
            )

        if not arquivo or arquivo.filename == "":
            return render_template(
                "index.html",
                erro="Selecione um arquivo PDF."
            )

        if not arquivo.filename.lower().endswith(".pdf"):
            return render_template(
                "index.html",
                erro="O arquivo selecionado deve ser um PDF"
            )

        print ("Condominio:", condominio)
        print ("Arquivo", arquivo.filename)

        with tempfile.TemporaryDirectory() as pasta_temporaria:

            caminho_pdf = Path(pasta_temporaria) / arquivo.filename

            arquivo.save(caminho_pdf)

            print ("PDF salvo em:")
            print (caminho_pdf)

            print ("Arquivo existe?")
            print (caminho_pdf.exists())

            extrator = extratores[condominio]

            df, totais_pdf = extrator(caminho_pdf)

            print ("quantidade de registros:")
            print(len(df))

            print ("Totais do PDF:")
            print (totais_pdf)

            caminho_excel = Path(pasta_temporaria) / "resultado.xlsx"

            if condominio == "aleixo":
                salvar_excel_aleixo(
                    df,
                    caminho_excel,
                    totais_pdf
                )
            else:
                salvar_excel(
                    df,
                    caminho_excel,
                    totais_pdf
                )

            print ("Excel gerado em:")
            print (caminho_excel)

            print ("Excel existe?")
            print (caminho_excel.exists())

            with open(caminho_excel, "rb") as arquivo_excel:
                excel_memoria = BytesIO(arquivo_excel.read())

            return send_file(
                excel_memoria,
                as_attachment=True,
                download_name="resultado.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    return render_template("index.html")

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    app.run()