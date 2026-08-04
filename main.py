from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Exportacao.salvar_excel import salvar_excel
from pathlib import Path

caminho_pdf = r"C:\Users\Rafael Soares\Desktop\Rateios\Duet Barra\Duet Barra-Rateio-06.26.pdf"

df, totais_pdf = extrair_duet(caminho_pdf)


caminho_saida = Path("Dados") / "Saida" / "Duet_Barra" / "Teste.xlsx"

salvar_excel(
    df,
    caminho_saida,
    totais_pdf
)

#salvar_excel(df, saida)
