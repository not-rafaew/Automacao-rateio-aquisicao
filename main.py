from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Condominios.Aurum.Aurum_v2 import extrair_aurum
from Condominios.DezRamos.Dez_Ramos import extrair_dez_ramos
from Exportacao.salvar_excel import salvar_excel
from pathlib import Path


caminho_pdf = r"C:\Users\guug0\OneDrive\Desktop\Rateios\Dez Ramos\Dez_Ramos-Rateio-09.25.pdf"
df, totais_pdf = extrair_dez_ramos(caminho_pdf)

#print("DATAFRAME:")
#print(df)

#print("\nTOTAIS DO PDF:")
#print(totais_pdf)

caminho_saida = Path("Dados") / "Saida" / "Dez_Ramos" / "Teste.xlsx"

salvar_excel(
    df,
    caminho_saida,
    totais_pdf
)

