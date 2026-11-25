from pathlib import Path
import importlib
import pandas as pd

caminho = Path(__file__).resolve().parent / "Condominios"

campos_ignorados = {
    "Bloco",
    "Unidade",
    "Vencimento"
}

padronização = {
    "Agua": "Água",
    "Consumo de Gas": "Consumo de Gás",
    "Gas": "Gás",
    "Cota do Mes": "Cota do mês",
    "Fundo Reserva": "Fundo de Reserva",
    "Energia Eletrica": "Energia Elétrica",
    "Energia / Elétrica": "Energia Elétrica",
    "Água-Esgoto": "Água e Esgoto",
    "Salão de Festa": "Salão de Festas",
    "Agua Geral": "Água Geral",
    "Agua Area Comum": "Água Área Comum",
    "Reforco Orcamentario": "Reforço Orçamentário",

    "Fundo de Pintura {parcelas['fundo_pintura']}": "Fundo de Pintura",
    "Seguro {parcelas['seguro']}": "Seguro",
    "Desobstrucão Esgoto {parcelas['desobstrucao_esgoto']}": "Desobstrução Esgoto",
    "Telhado {parcelas['telhado']}": "Telhado",
    "desconto Água XX/XX": "Desconto Água"
}

dados = []


for pasta in caminho.iterdir():

    if pasta.is_dir() and pasta.name != "__pycache__":

        nome_condominio = pasta.name

        despesas_condominio = set()

        for arquivo in pasta.glob("*.py"):

            if arquivo.name == "__init__.py":
                continue

            modulo = importlib.import_module(
                f"Condominios.{nome_condominio}.{arquivo.stem}"
            )

            if not hasattr(modulo, "novo_apartamento"):
                continue


            if nome_condominio == "Aleixo":

                parcelas = {
                    "emprestimo_60": "XX/60",
                    "emprestimo_48": "XX/48",
                    "coluna_agua": "XX/XX",
                    "laje": "XX/XX"
                }

                despesas = modulo.novo_apartamento(parcelas)

            elif nome_condominio == "DezRamos":

                despesas = modulo.novo_apartamento("XX/XX")

            elif nome_condominio == "DuetBarra":

                despesas = modulo.novo_apartamento(
                    "Laudo Técnico - Fech. Varanda XX/XX"
                )

            elif nome_condominio == "Ilhabela":

                parcelas = {
                    "seguro": "XX/XX",
                    "desobstrucao_esgoto": "XX/XX",
                    "fundo_pintura": "XX/XX",
                    "telhado": "XX/XX",
                    "desconto_agua": "XX/XX",
                }

                despesas = modulo.novo_apartamento(parcelas)

            elif nome_condominio == "SierraAndorra":

                parcelas = {
                    "cota_ambiental": "XX/XX",
                    "fundo_obras": "XX/XX",
                }

                despesas = modulo.novo_apartamento(parcelas)

            else:
                despesas = modulo.novo_apartamento()

            despesas_condominio.update(despesas.keys())

        despesas_condominio.difference_update(campos_ignorados)

        despesas_condominio = {
            padronização.get(despesa, despesa)
            for despesa in despesas_condominio
        }

        despesas_condominio = {
            despesa.replace("XX/XX", "").strip().rstrip("-").strip()
            for despesa in despesas_condominio
        }

        for despesa in sorted(despesas_condominio):

            dados.append({
                "Condominio": nome_condominio,
                "Despesa": despesa
            })

df = pd.DataFrame(dados)

print(df.to_string(index=False))

print(f"Total de despesas mapeadas: {len(df)}")

saida = Path(__file__).resolve().parent / "Despesas_dos_condominios.xlsx"

df.to_excel("Despesas_dos_condominios.xlsx", index=False)

print(f"Planilha salva em: {saida}")

