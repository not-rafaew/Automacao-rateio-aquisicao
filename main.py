from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Condominios.Aurum.Aurum_v2 import extrair_aurum
from Condominios.DezRamos.Dez_Ramos import extrair_dez_ramos
from Condominios.GrandVille.GrandVille import extrair_grandville
from Condominios.SierraAndorra.Sierra_Andorra import extrair_sierraandorra
from Exportacao.salvar_excel import salvar_excel
from pathlib import Path


caminho_pdf = r"C:\Users\guug0\Downloads\BOLETOS 10-09-2026.pdf"
df, totais_pdf = extrair_sierraandorra(caminho_pdf)

#print("DATAFRAME:")
#print(df)

#print("\nTOTAIS DO PDF:")
#print(totais_pdf)

caminho_saida = Path("Dados") / "Saida" / "Sierra_Andorra" / "Teste.xlsx"

salvar_excel(
    df,
    caminho_saida,
    totais_pdf
)

