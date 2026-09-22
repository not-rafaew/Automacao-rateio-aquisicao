# Regras de Negócio - Condomínio Sol Life

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio Sol Life.

## Estrutura do PDF

- O PDF é processado página por página.
- O texto de cada página é extraído e processado linha por linha.
- Cada apartamento é identificado antes de suas respectivas despesas.
- As despesas são identificadas através de seus códigos e descrições.
- Ao final do PDF existe uma seção com os totais das receitas das unidades.

## Identificação dos apartamentos

Um novo apartamento é identificado através de uma linha no formato:

`Bloco-Unidade Valor`

Exemplo:

`1-101 1.234,56`

O primeiro número representa o Bloco e o segundo representa a Unidade.

O valor presente nessa linha não é utilizado como uma verba individual.

Ao encontrar um novo apartamento, o apartamento anterior é salvo antes de
iniciar o processamento do próximo.

## Identificação das despesas

As despesas são identificadas através dos códigos e descrições utilizados
no próprio PDF.

Atualmente, a automação reconhece:

- Cota do Mês
- Cedae
- Água Área Comum
- Diferença da Água do Mês Anterior
- Fundo de Reserva

## Cota do Mês

A Cota do Mês é identificada através do código e descrição:

`1.2.01 - Cota Condominial`

O valor encontrado é associado ao apartamento que está sendo processado.

## Cedae

A despesa de Cedae é identificada através de:

`1.2.32 - Cedae`

O valor encontrado é associado ao apartamento atual.

## Água Área Comum

A despesa é identificada através de:

`1.2.70 - Água Área Comum`

O valor encontrado é armazenado na coluna `Agua Area Comum`.

## Diferença da Água do Mês Anterior

A diferença referente ao consumo de água do mês anterior é identificada através de:

`1.2.121 - DIF. DA ÁGUA DO MÊS ANTERIOR`

O valor encontrado é armazenado na coluna:

`Dif. da Agua do Mes Anterior`

## Fundo de Reserva

O Fundo de Reserva é identificado através de:

`1.4.03 - Fundo de Reserva`

O valor encontrado é associado ao apartamento atual.

## Acordo

Existe tratamento previsto para a verba:

`1.2.31 - Acordo`

Porém, essa verba está atualmente desativada no código.

A estrutura foi mantida comentada para possibilitar sua implementação caso
seja necessário processar Acordos futuramente.

Enquanto estiver desativada, valores de Acordo não são adicionados aos
apartamentos nem aos totais exportados.

## Valores negativos

- As despesas aceitam valores negativos.
- Valores negativos devem permanecer negativos.
- Não é realizada conversão para valor absoluto.

## Quadro de Totais

O início da seção de totais é identificado através da expressão:

`Total de receitas das unidades`

Quando essa expressão é encontrada, a automação deixa de processar linhas como
despesas de apartamentos e passa a procurar os totais das verbas.

Essa separação evita que os valores do resumo sejam associados ao último
apartamento processado.

## Identificação dos Totais

No quadro de totais, são utilizadas as mesmas descrições e códigos das
despesas individuais:

- `1.2.01 - Cota Condominial` → Cota do Mês
- `1.2.32 - Cedae` → Cedae
- `1.2.70 - Água Área Comum` → Água Área Comum
- `1.2.121 - DIF. DA ÁGUA DO MÊS ANTERIOR` → Diferença da Água do Mês Anterior
- `1.4.03 - Fundo de Reserva` → Fundo de Reserva

Os valores encontrados são armazenados separadamente em `totais_pdf` para
posterior validação e exportação.

O total de Acordo não é processado atualmente.

## Final da Leitura

- Enquanto `Total de receitas das unidades` não for encontrado, as linhas são
  processadas como dados dos apartamentos.
- Depois dessa expressão, as linhas são processadas somente como possíveis totais.
- Ao encontrar um novo apartamento, o apartamento anterior é salvo.
- Após finalizar todas as páginas, o último apartamento também é salvo.

## Exportação

Cada apartamento pode possuir:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Cedae
- Água Área Comum
- Diferença da Água do Mês Anterior
- Fundo de Reserva

O campo de Vencimento existe na estrutura do apartamento, mas atualmente não
é preenchido pela extração do Sol Life.

Após a leitura, os apartamentos são convertidos para um DataFrame e utilizados
na geração da planilha final.