# Regras de Negócio - Condomínio Aleixo

Este documento descreve as regras utilizadas para extrair e validar os dados dos PDFs de rateio do Condomínio Aleixo.

---

## 1. Estrutura do PDF

O PDF possui duas áreas principais:

1. Resumo contábil com os totais das verbas do condomínio.
2. Lançamentos individuais de cada apartamento.

Os lançamentos individuais são utilizados para montar o DataFrame e gerar a planilha Excel.

O resumo contábil é utilizado para validar se os valores extraídos dos apartamentos correspondem aos totais informados no PDF.

---

## 2. Identificação dos apartamentos

Os apartamentos são identificados por linhas no formato:

APT-0101
APT-0102
APT-0201
APT-0406

O Condomínio Aleixo não possui blocos.

Por isso, números como `0101`, `0204` e `0406` representam diretamente o número completo da unidade e não uma combinação de bloco e apartamento.

Além da unidade, a mesma linha contém o vencimento utilizado no registro do apartamento.

Exemplo:

APT-0101 ... 15/10/2026

Resultado:

Unidade: 0101  
Vencimento: 15/10/2026

---

## 3. Verbas dos apartamentos

Cada apartamento pode possuir as seguintes verbas:

- Cota do Mes
- Agua
- Emprestimo
- Fundo de Reserva
- Taxa Extra ref. Emprestimo
- Taxa Extra Coluna de Agua
- Cota Extra Laje

Os valores são identificados pelas descrições existentes nas linhas do PDF.

Quando uma mesma verba aparece mais de uma vez para o mesmo apartamento, os valores são somados.

Essa regra também permite considerar lançamentos negativos, como descontos.

Exemplo:

Taxa Condominial: 330,43  
Desconto: -330,43

Resultado:

Cota do Mes = 0,00

---

## 4. Empréstimos

O PDF pode possuir dois lançamentos com descrições semelhantes:

Taxa Extra ref. Empréstimo

Para diferenciar os dois lançamentos, é utilizado o número total de parcelas informado no PDF.

### Taxa Extra ref. Emprestimo

Lançamentos com parcelamento terminado em `/60` são armazenados em:

`Taxa Extra ref. Emprestimo`

Exemplo:

16/60 59,13

### Emprestimo

Lançamentos com parcelamento terminado em `/48` são armazenados em:

`Emprestimo`

Exemplo:

7/48 128,54

O número da parcela atual pode mudar a cada mês. Por isso, a identificação considera o total de parcelas (`/60` ou `/48`) e não o número da parcela atual.

---

## 5. Cota Extra

No lançamento individual dos apartamentos existem duas despesas diferentes relacionadas à Cota Extra.

Elas devem permanecer separadas na planilha para permitir a identificação do motivo de cada cobrança.

### Taxa Extra Coluna de Agua

Corresponde ao lançamento referente à substituição da coluna de água.

Exemplo:

Taxa extra ref. substituição da coluna de água ... 4/10 62,50

O valor é armazenado na coluna:

`Taxa Extra Coluna de Agua`

### Cota Extra Laje

Corresponde ao lançamento referente à obra de reestruturação da laje do apartamento 406.

Exemplo:

Cota Extra - da obra de reestruturação da laje ... 3/4 78,13

O valor é armazenado na coluna:

`Cota Extra Laje`

As duas despesas não devem ser unificadas nas colunas dos apartamentos.

---

## 6. Validação da Cota Extra

No resumo contábil do PDF, as duas despesas anteriores não possuem totais separados.

O resumo apresenta apenas:

`1.56 - Cota Extra`

Por isso, somente durante a validação os valores das duas colunas são somados.

A regra utilizada é:

Taxa Extra Coluna de Agua
+
Cota Extra Laje
=
Cota Extra calculada

Exemplo do rateio de outubro:

Taxa Extra Coluna de Agua:

62,50 x 24 apartamentos = 1.500,00

Cota Extra Laje:

78,13 x 24 apartamentos = 1.875,12

Total calculado:

1.500,00 + 1.875,12 = 3.375,12

Esse resultado é comparado com o valor `Cota Extra` existente no resumo contábil do PDF.

As duas colunas continuam separadas na planilha Excel.

---

## 7. Totais do PDF

Os totais são extraídos do resumo contábil utilizando os códigos das verbas.

São consideradas:

- `1.01` - Cotas Condominiais
- `1.10` - Água
- `1.1004` - Emprestimo
- `1.13` - Fundo de Reserva
- `1.21` - Taxa Extra ref. Empréstimo
- `1.56` - Cota Extra

Os valores encontrados são armazenados em `totais_pdf`.

A Cota Extra permanece como uma única verba em `totais_pdf`, pois é dessa forma que ela aparece no resumo do PDF.

---

## 8. Validação dos valores

Para as verbas comuns, o total de cada coluna dos apartamentos é comparado diretamente com o respectivo valor do resumo do PDF.

Exemplo:

Cota do Mes calculada → Cota do Mes do PDF  
Agua calculada → Agua do PDF  
Emprestimo calculado → Emprestimo do PDF  
Fundo de Reserva calculado → Fundo de Reserva do PDF  
Taxa Extra ref. Emprestimo calculada → Taxa Extra ref. Emprestimo do PDF

A Cota Extra possui uma regra específica:

Taxa Extra Coluna de Agua + Cota Extra Laje → Cota Extra do PDF

Essa validação específica é realizada pelo exportador próprio do Aleixo.

---

## 9. Exportação para Excel

O Condomínio Aleixo utiliza um exportador específico:

`salvar_excel_aleixo.py`

Esse exportador mantém as duas despesas de Cota Extra separadas na planilha:

- Taxa Extra Coluna de Agua
- Cota Extra Laje

Durante a validação, o exportador soma essas duas colunas e compara o resultado com `Cota Extra` do resumo do PDF.

O `salvar_excel.py` geral não é alterado, evitando que uma regra específica do Aleixo afete os demais condomínios.

---

## 10. Resultado final

A extração do Aleixo gera uma linha para cada apartamento contendo:

- Unidade
- Vencimento
- Cota do Mes
- Agua
- Emprestimo
- Fundo de Reserva
- Taxa Extra ref. Emprestimo
- Taxa Extra Coluna de Agua
- Cota Extra Laje

Ao final da planilha é adicionada a tabela de validação dos totais.

A validação geral é considerada aprovada quando todos os valores calculados correspondem aos valores encontrados no resumo do PDF.