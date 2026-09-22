# Regras de Negócio - Condomínio Aurum Bela Vista

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio Aurum Bela Vista.

## Estrutura do PDF

- O PDF é processado página por página.
- As informações principais dos apartamentos são extraídas através das tabelas do PDF.
- Algumas despesas adicionais são identificadas pela posição das palavras e valores na página.
- O cabeçalho de cada página é analisado para identificar quais verbas extras estão presentes no rateio.

## Identificação dos blocos

- O bloco atual é identificado através da linha que contém "Bloco:".
- Após a identificação, os apartamentos seguintes são associados a esse bloco.
- Quando um novo "Bloco:" é encontrado, o bloco atual é atualizado.

## Identificação dos apartamentos

- Uma linha só é considerada um apartamento válido quando possui uma unidade e um vencimento.
- O vencimento deve seguir o formato `DD/MM/AAAA`.
- A unidade é identificada pelo padrão utilizado no PDF, começando por `000`.
- Caso a linha não possua unidade ou vencimento, ela é ignorada.

## Verbas principais

As três primeiras verbas possuem posições conhecidas na tabela:

- Água
- Cota do Mês
- Energia Elétrica

A Água é obtida na célula seguinte ao vencimento.

A Cota do Mês é procurada após a Água. Caso existam células vazias entre elas,
essas células são ignoradas até que o próximo valor seja encontrado.

A Energia Elétrica é obtida após a Cota do Mês.

## Verbas extras

Além das verbas principais, o PDF pode apresentar despesas adicionais.

Atualmente, a automação reconhece:

- Fundo Reserva
- Consumo de Gás
- Multa Regulamento Interno
- Reembolsos Diversos
- Salão de Festas
- Salão de Festas (Desconto)

As verbas extras não dependem de uma posição fixa na tabela.

O cabeçalho da página é analisado para descobrir quais verbas estão presentes
e a posição horizontal de cada uma.

Depois disso, os valores são associados à verba correspondente de acordo com
sua posição horizontal no PDF.

Para identificar a qual apartamento o valor pertence, a posição vertical do
valor é comparada com a posição vertical da unidade.

## Salão de Festas e Desconto

- O cabeçalho é verificado para identificar a existência da palavra "Desconto".
- Quando existe desconto, a automação diferencia as colunas:
  - Salão de Festas (Desconto)
  - Salão de Festas
- Sem a indicação de desconto, a coluna é tratada normalmente como Salão de Festas.

## Valores negativos

- A automação aceita valores monetários negativos.
- Valores negativos devem permanecer negativos.
- Eles podem representar descontos ou ajustes presentes no rateio.

## Totais do PDF

- O quadro de totais é identificado através da palavra "títulos".
- Os três primeiros valores encontrados no quadro correspondem, nesta ordem, a:
  1. Água
  2. Cota do Mês
  3. Energia Elétrica
- Os valores seguintes correspondem às verbas extras identificadas no cabeçalho.
- O último valor representa o total geral e não é utilizado como uma verba individual.

## Exportação

Cada apartamento pode possuir as seguintes informações:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Água
- Energia Elétrica
- Fundo Reserva
- Consumo de Gás
- Multa Regulamento Interno
- Reembolsos Diversos
- Salão de Festas

As informações extraídas são convertidas para um DataFrame e posteriormente
utilizadas na geração da planilha final.