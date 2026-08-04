# 📃 Automação de Rateio de Condominios

Projeto desenvolvido em Python para automatizar a leitura rateios de condomínios em PDF e gerar uma planilha em excel contendo as informações de cada apartamento

O objetivo é eliminar o trabalho manual das planilhas, reduzindo o tempo de trabalho e erros humanos.


---

# Funcionalidades

- Leitura automática de arquivos PDF.
- Identificação dos apartamenos.
- Extrair as despesas de cada unidade.
- Converter valor monetário.
- Geração automática de excel
- Remoção de colunas vazias.

---

# Tecnologias Utilizadas

- Python 3
- pdflumber
- pandas
- openpyxl

---

# Como executar

1. Clone o repositório.

2. Instale as depencências.

```bash
pip install -r requirements.txt
```

3. Informe o caminho do PDF no arquivo `main.py`.

4. Execute.

A planilha será gerada automaticamente na pasta de saída.

# Regras de Negócio

As regras utilizadas nas aquisições encontram-se em: 

```
docs/regras_negocio.md
```

---

# Melhorias Futuras

- Suporte para novos condomínios.
- Interface gráfica.
- Seleção do PDF pelo usúario.
- Geração automática de relatórios 


---

# Autor

Desenvolvido por Rafael Soares.

