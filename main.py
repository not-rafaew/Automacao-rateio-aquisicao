from Condominios.Marechal.marechal import extrair_marechal
from Condominios.Ilhabela.ilhabela import extrair_ilhabela
from Condominios.DuetBarra.duet_barra import extrair_duet
from Condominios.Aurum.Aurum_v2 import extrair_aurum
from Exportacao.salvar_excel import salvar_excel
from pathlib import Path

caminho_pdf = r"C:\Users\guug0\OneDrive\Desktop\Rateios\Aurum\Quadro de Rateio 709 - Junho.pdf"
df, totais_pdf = extrair_aurum(caminho_pdf)

#print("DATAFRAME:")
#print(df)

#print("\nTOTAIS DO PDF:")
#print(totais_pdf)

caminho_saida = Path("Dados") / "Saida" / "Aurum" / "Teste.xlsx"

salvar_excel(
    df,
    caminho_saida,
    totais_pdf
)

