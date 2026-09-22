# Regras de Negócio - Condomínio Parque Sol do Engenho

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio Parque Sol do Engenho.

## Estrutura do PDF

- O PDF é processado página por página.
- Diferente de outros condomínios, as informações não são organizadas como um apartamento completo por linha.
- As unidades são agrupadas por bloco.
- Cada grupo de unidades compartilha os mesmos valores de despesas.
- Existem diferentes modelos de PDF, incluindo versões com e sem Reforço Orçamentário.

## Correção de Texto Duplicado

Algumas versões do PDF apresentam caracteres duplicados durante a extração
realizada pelo `pdfplumber`.

Exemplos:

`000101` pode ser extraído como `000000110011`.

`92,65` pode ser extraído como `9922,,6655`.

Para corrigir esse problema, a automação utiliza a função
`corrigir_texto_duplicado()`.

A função mantém um caractere a cada duas posições, reconstruindo o texto
original antes de realizar as demais análises.

Essa correção é necessária para que unidades, blocos, valores e descrições
possam ser identificados corretamente.

## Identificação das Unidades

As unidades podem aparecer em dois formatos diferentes dependendo do modelo do PDF:

- `101`
- `000101`

A automação aceita os dois formatos.

Antes de salvar, a unidade é convertida para número e novamente para texto,
removendo os zeros existentes no início.

Exemplo:

`000101` → `101`

São consideradas unidades válidas dentro do padrão utilizado pelo condomínio,
evitando que outros números presentes no PDF sejam interpretados como apartamentos.

## Identificação dos Blocos

O condomínio possui 13 blocos.

Os blocos são identificados através de números de `1` até `13` encontrados no
início da linha.

A quantidade esperada de unidades depende do bloco:

- Bloco 1: 20 unidades
- Blocos 2 até 13: 40 unidades cada

No total, são esperadas 500 unidades.

## Agrupamento das Unidades

As unidades encontradas são armazenadas temporariamente até que seja possível
identificar completamente o grupo ao qual pertencem.

Um grupo somente é finalizado quando:

- O bloco foi identificado.
- A quantidade esperada de unidades foi encontrada.
- O valor de Água e Esgoto foi identificado.
- O valor da Cota do Mês foi identificado.

Quando o grupo é finalizado, os mesmos valores são associados a todas as
unidades pertencentes àquele bloco.

Caso unidades do próximo bloco já tenham sido encontradas durante a leitura,
elas permanecem armazenadas para serem utilizadas no próximo grupo.

## Despesas Reconhecidas

A automação trabalha atualmente com:

- Cota do Mês
- Água e Esgoto
- Reforço Orçamentário

O Reforço Orçamentário não está presente em todos os modelos de PDF.

## Identificação das Despesas

A quantidade de valores monetários encontrada na linha é utilizada para
identificar o modelo do rateio.

### Modelo sem Reforço Orçamentário

Quando são encontrados três valores monetários:

- Primeiro valor: Água e Esgoto
- Segundo valor: Cota do Mês
- Terceiro valor: Total

O Total não é armazenado como uma verba individual.

### Modelo com Reforço Orçamentário

Quando são encontrados quatro valores monetários:

- Primeiro valor: Reforço Orçamentário
- Segundo valor: Água e Esgoto
- Terceiro valor: Cota do Mês
- Quarto valor: Total

O Total não é armazenado como uma verba individual.

## Distribuição das Despesas

Após a identificação de um grupo, a automação cria individualmente cada
apartamento pertencente a ele.

Todos os apartamentos do grupo recebem:

- Bloco
- Unidade
- Água e Esgoto
- Cota do Mês
- Reforço Orçamentário, quando existente

Dessa forma, informações apresentadas de forma agrupada no PDF são transformadas
em registros individuais para a planilha final.

## Totais do PDF

O quadro de totais possui diferenças entre os modelos de PDF.

O início do quadro é identificado através da expressão `CONTA`.

As principais contas utilizadas são:

- Conta 4344: Reforço Orçamentário
- Conta 4356: Água e Esgoto
- Conta 476: Cota do Mês

## Totais com Reforço Orçamentário

Quando a conta `4344` é encontrada, a automação identifica que o PDF possui
Reforço Orçamentário.

Nesse modelo, os valores do quadro seguem a estrutura conhecida utilizada
pela automação para obter:

- Reforço Orçamentário
- Água e Esgoto
- Cota do Mês

O Total Geral não é utilizado como uma verba individual.

## Totais sem Reforço Orçamentário

Nos modelos sem Reforço Orçamentário, a estrutura do texto extraído pode variar.

Além disso, algumas versões podem apresentar os valores do quadro de totais
duplicados durante a extração.

Por esse motivo, a automação:

1. Coleta os valores encontrados no quadro.
2. Remove valores repetidos causados pela duplicação do PDF.
3. Procura três valores correspondentes a Água, Cota e Total Geral.
4. Identifica matematicamente o Total Geral através da relação:

`Água e Esgoto + Cota do Mês = Total Geral`

5. Remove o Total Geral.
6. Utiliza os dois valores restantes como Água e Esgoto e Cota do Mês.

Essa lógica permite processar diferentes versões do PDF sem depender apenas
da posição em que o Total Geral aparece no texto extraído.

## Valores Monetários

Os valores são convertidos do formato brasileiro para `float`.

Exemplo:

`1.234,56` → `1234.56`

Os padrões utilizados também permitem a identificação de valores negativos
nas despesas dos apartamentos.

## Final da Leitura

- Todos os grupos identificados são armazenados durante a leitura do PDF.
- Após o processamento das páginas, cada grupo é convertido em apartamentos individuais.
- Cada unidade recebe as despesas correspondentes ao seu grupo.
- Os apartamentos são então convertidos para um DataFrame.

## Exportação

Cada apartamento pode possuir:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Reforço Orçamentário
- Água e Esgoto

O campo de Vencimento existe na estrutura do apartamento, mas atualmente não
é preenchido pela extração do Sol do Engenho.

Após a leitura, os apartamentos são convertidos para um DataFrame e utilizados
na geração da planilha final.