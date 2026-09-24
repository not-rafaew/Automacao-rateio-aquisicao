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
from Exportacao.salvar_excel import salvar_excel
from Exportacao.salvar_excel_aleixo import salvar_excel_aleixo
from pathlib import Path

caminho_pdf = r"C:\Users\guug0\OneDrive\Desktop\Rateios\Aleixo\Aleixo-Rateio-09.26.pdf"
df, totais_pdf = extrair_aleixo(caminho_pdf)


print("DATAFRAME:")
print(df)

print("\nTOTAIS PDF:")
print(totais_pdf)


caminho_saida = Path("Dados") / "Saida" / "Aleixo" / "Teste.xlsx"

#salvar_excel(
#    df,
#   caminho_saida,
#    totais_pdf
#)

salvar_excel_aleixo(
    df,
    caminho_saida,
    totais_pdf
)

