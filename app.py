from flask import Flask, render_template, request, send_file
import tempfile
from pathlib import Path
import webbrowser
import threading
from datetime import datetime
from uuid import uuid4

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
from Condominios.Esplendor.Esplendor import extrair_esplendor
from Condominios.Bougainvillea.Bougainvillea import extrair_bougainvillea
from Condominios.Aurum.Aurum_OMA import extrair_aurum_oma
from Condominios.Aurum.Aurum_OMA_NOOCR import extrair_aurum_oma_noocr
from Condominios.Sapucaia.sapucaia import extrair_sapucaia

from Exportacao.layout_revo import montar_layout_revo
from Exportacao.validacao import gerar_validacao
from Exportacao.salvar_validacao import salvar_validacao
from Exportacao.salvar_csv import salvar_csv

app = Flask(__name__)
pasta_resultados = tempfile.TemporaryDirectory()

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
    "conviva": extrair_conviva,
    "esplendor": extrair_esplendor,
    "bougainvillea": extrair_bougainvillea,
    "aurum_oma": extrair_aurum_oma,
    "aurum_oma_noocr": extrair_aurum_oma_noocr,
    "sapucaia": extrair_sapucaia
}

@app.route("/", methods=["GET", "POST"])
def inicio():
    
    if request.method == "POST":

        condominio = request.form.get("condominio")
        arquivo = request.files.get("arquivo")

        vencimento = request.form.get("vencimento")
        competencia = request.form.get("competencia")

        if not vencimento or not competencia:
            return render_template(
                "index.html",
                erro="Selecione o vencimento e a competência"
            )

        try:
            vencimento = datetime.strptime(
                vencimento, "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

            competencia = datetime.strptime(
                competencia, "%Y-%m"
            ).strftime("%m/%Y")

        except ValueError:
            return render_template(
                "index.html",
                erro="Formato de data invalido."
            )

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

            df["Vencimento"] = vencimento

            print(df.columns.tolist())
            print(totais_pdf)
            
            # Gera a validação das despesas
            relatorio = gerar_validacao(
                df,
                totais_pdf,
                condominio
            )

            # Verifica a validação geral
            aprovado = bool(relatorio) and all(
                verba["Status"] == "OK"
                for verba in relatorio
            )

            # Montar o layout Revo
            df = montar_layout_revo(df, competencia)

            # Identificar único da geração
            identificador = str(uuid4())

            # Cria a pasta dos resultados
            pasta_saida = (
                Path(pasta_resultados.name)
                / identificador.replace("-", "")
            )

            pasta_saida.mkdir()

            # Caminhos dos arquivos
            caminho_csv = pasta_saida / "aquisicao.csv"
            caminho_excel = pasta_saida / "validacao.xlsx"

            # Exportar as despesas
            salvar_csv(df, caminho_csv)

            # Exportar a validação
            salvar_validacao(relatorio, caminho_excel)

            # Envia os resultados para o front-end
            return render_template (
                "index.html",
                relatorio=relatorio,
                aprovado=aprovado,
                identificador=identificador,
                condominio=condominio
            )

    return render_template("index.html")

@app.route("/download/<uuid:identificador>/<tipo>")
def download(identificador, tipo):

    arquivos = {
        "aquisicao": "aquisicao.csv",
        "validacao": "validacao.xlsx"
    }

    if tipo not in arquivos:
        return "Arquivo inválido", 404

    caminho = (
        Path(pasta_resultados.name)
        / identificador.hex
        / arquivos[tipo]
    )

    if not caminho.exists():
        return "Arquivo não encontrado", 404

    return send_file(
        caminho,
        as_attachment=True,
        download_name=arquivos[tipo]
    )

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    app.run()