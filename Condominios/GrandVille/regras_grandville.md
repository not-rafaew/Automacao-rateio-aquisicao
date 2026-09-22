# Regras de Negócio - Condomínio GrandVille

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio GrandVille.

## Estrutura do PDF

- O PDF é processado página por página.
- O texto de cada página é extraído e processado linha por linha.
- Cada apartamento possui todas as suas informações principais na mesma linha.
- A posição das informações é fixa.

## Identificação dos apartamentos

Uma linha é considerada um apartamento válido quando apresenta, nesta ordem:

1. Unidade
2. Bloco
3. Vencimento
4. Cota do Mês
5. Fundo de Reserva
6. Água Geral
7. Tarifa Bancária
8. Total

O vencimento deve seguir o formato `DD/MM/AAAA`.

A linha inteira precisa corresponder ao padrão esperado para ser processada.
Linhas que não seguem essa estrutura são ignoradas.

## Processamento das despesas

As despesas possuem posições fixas na linha.

A automação associa os valores da seguinte forma:

- Primeiro valor: Cota do Mês
- Segundo valor: Fundo de Reserva
- Terceiro valor: Água Geral
- Quarto valor: Tarifa Bancária

O último valor presente na linha corresponde ao total do apartamento e não é
armazenado como uma verba individual.

## Valores negativos

- As despesas aceitam valores negativos.
- Valores negativos devem permanecer negativos.
- Não é realizada conversão para valor absoluto.

## Totais do PDF

O quadro de totais é identificado por uma linha no formato:

`X cobranças ...`

Após a quantidade de cobranças, os valores aparecem na mesma ordem utilizada
nas linhas dos apartamentos:

1. Cota do Mês
2. Fundo de Reserva
3. Água Geral
4. Tarifa Bancária
5. Total Geral

O Total Geral não é armazenado como uma verba individual.

## Final da leitura

- Todas as páginas do PDF são processadas.
- Cada linha que corresponde ao padrão de apartamento é adicionada à lista.
- Não é necessário manter um apartamento atual entre diferentes linhas, pois
  cada registro contém todas as informações necessárias na própria linha.

## Exportação

Cada apartamento possui:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Fundo de Reserva
- Água Geral
- Tarifa Bancária

Após a leitura, os apartamentos são convertidos para um DataFrame e utilizados
na geração da planilha final.