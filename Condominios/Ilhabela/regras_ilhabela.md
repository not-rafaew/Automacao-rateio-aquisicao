# Regras de Negócio - Ilhabela

- A unidade é utilizada como identificador principal de cada boleto.
- A extração considera apenas os lançamentos pertencentes ao apartamento atual.
- A competência é obtida diretamente do rateio.
- O vencimento é extraído do rateio.
- Os valores monetários são convertidos para o formato decimal utilizado pelo sistema.
- Despesas parceladas são identificadas automaticamente, independentemente da quantidade de parcelas (ex.: 1/3, 2/5, 10/12).
- Caso uma despesa não exista no rateio, seu valor permanece nulo.
- A Cota do Mês pode possuir lançamentos positivos e negativos. O sistema realiza a soma dos lançamentos e, quando o resultado é igual a zero, o campo é mantido nulo na planilha de saída.
- As despesas extraídas são exportadas para Excel mantendo o nome original de cada lançamento.