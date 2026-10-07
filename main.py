from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Condominios.Aurum.Aurum_v2 import extrair_aurum
from Condominios.Aurum.Aurum_OMA import extrair_aurum_oma
from Condominios.DezRamos.Dez_Ramos import extrair_dez_ramos
from Condominios.GrandVille.GrandVille import extrair_grandville
from Condominios.SierraAndorra.Sierra_Andorra import extrair_sierraandorra
from Condominios.SolLife.Sol_Life import extrair_sollife
from Condominios.Sol_Engenho.Sol_Engenho import extrair_soldoengenho
from Condominios.Aleixo.Aleixo import extrair_aleixo
from Condominios.Conviva.Conviva import extrair_conviva
from Exportacao.salvar_excel import salvar_excel
from Exportacao.layout_revo import montar_layout_revo
from Exportacao.salvar_excel_aleixo import salvar_excel_aleixo
from pathlib import Path

caminho_pdf = r"C:\Users\guug0\OneDrive\Desktop\Rateios\Aleixo\Aleixo-Rateio-10.26.pdf"
df, totais_pdf = extrair_aleixo(caminho_pdf)

df_revo = montar_layout_revo(
    df,
    "07/2026"
)

print("\nCOLUNAS DO DF ORIGINAL:")
print(df.columns.tolist())

print("\nCOLUNAS DO DF REVO:")
print(df_revo.columns.tolist())

print("DATAFRAME:")
print(df)

print("\nTOTAIS PDF:")
print(totais_pdf)


caminho_saida = Path("Dados") / "Saida" / "Aleixo" / "Teste.xlsx"

#salvar_excel(
#   df_revo,
#   caminho_saida,
#   totais_pdf
#)

salvar_excel_aleixo(
    df_revo,
    caminho_saida,
    totais_pdf
)

