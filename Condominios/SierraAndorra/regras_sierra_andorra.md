# Regras de Negócio - Condomínio Sierra Andorra

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio Sierra Andorra.

## Estrutura do PDF

- O PDF é processado página por página.
- O texto de cada página é extraído e processado linha por linha.
- A primeira parte do documento contém os apartamentos e suas despesas.
- Ao final do documento existe um quadro com os totais das verbas.

## Identificação dos apartamentos

- Um novo apartamento é identificado através da linha que contém:
  - Bloco
  - Unidade
  - Descrição `Cota condominial`
  - Referência no formato `MM/AAAA`
  - Valor da Cota do Mês
- O primeiro número encontrado representa o Bloco.
- O segundo número representa a Unidade.
- Ao encontrar um novo apartamento, o apartamento anterior é salvo antes de iniciar o próximo.

## Processamento das despesas

As despesas são encontradas nas linhas seguintes ao apartamento e associadas
ao apartamento que está sendo processado.

A automação reconhece:

- Cota do Mês
- Fundo de Reserva
- Cota Extra
- Fundo de Obras
- Salão de Festas

## Cota do Mês

- É identificada pela descrição `Cota condominial`.
- A Cota do Mês também é utilizada para identificar o início de um novo apartamento.
- Seu valor é obtido diretamente da linha de identificação do apartamento.

## Fundo de Reserva

- É identificado pela descrição `Fundo de Reserva`.
- A linha também possui uma referência no formato `MM/AAAA`.
- O valor encontrado é associado ao apartamento atual.

## Cota Extra

- No PDF, a Cota Extra aparece com a descrição `Cota ambiental`.
- Apesar do nome utilizado no PDF ser `Cota ambiental`, a informação é exportada na coluna `Cota Extra`.
- A linha possui uma referência de parcela no formato `XX/XX`.

## Fundo de Obras

- É identificado pela descrição `Fundo de obras`.
- A linha possui uma referência de parcela no formato `XX/XX`.
- O valor encontrado é associado ao apartamento atual.

## Salão de Festas

- É identificado pela descrição `Salão de festas`.
- A linha possui uma referência no formato `XX/XX`.
- O valor encontrado é associado ao apartamento atual.

## Valores negativos

- As despesas aceitam valores negativos.
- Valores negativos devem permanecer negativos.
- Não é realizada conversão para valor absoluto.

## Quadro de Totais

O início do quadro de totais é identificado pela expressão:

`Discriminação das verbas`

A partir desse ponto, a automação deixa de procurar apartamentos e passa a
processar somente os totais das despesas.

Essa separação é importante para evitar que informações do quadro de totais
sejam interpretadas como dados de apartamentos.

## Identificação dos Totais

Cada total é identificado através das descrições presentes no quadro:

- `COTAS DO MÊS Cota condominial` → Cota do Mês
- `COTAS DO MÊS - FUNDO Fundo de Reserva` → Fundo de Reserva
- `COTA EXTRA Cota ambiental` → Cota Extra
- `FUNDO DE OBRAS Fundo de obras` → Fundo de Obras
- `Salão de Festas Salão de festas` → Salão de Festas

O valor localizado no final de cada linha é utilizado como total da respectiva verba.

## Final da Leitura

- Enquanto o quadro de totais não for encontrado, as linhas são processadas como possíveis dados de apartamentos.
- Depois de encontrar `Discriminação das verbas`, todas as linhas seguintes são tratadas como possíveis totais.
- Ao terminar todas as páginas, o último apartamento em processamento é salvo.

## Exportação

Cada apartamento pode possuir:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Fundo de Reserva
- Cota Extra
- Fundo de Obras
- Salão de Festas

Após a leitura, os apartamentos são convertidos para um DataFrame e utilizados
na geração da planilha final.