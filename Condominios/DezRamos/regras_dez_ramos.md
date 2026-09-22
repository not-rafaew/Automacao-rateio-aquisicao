# Regras de Negócio - Condomínio Dez Ramos

Este documento descreve as regras utilizadas pela automação para interpretar
e processar os rateios do Condomínio Dez Ramos.

## Estrutura do PDF

- O PDF é processado página por página.
- O texto de cada página é extraído e processado linha por linha.
- Cada apartamento possui suas próprias despesas.
- Ao encontrar um novo apartamento, o apartamento anterior é finalizado e salvo.

## Identificação dos apartamentos

- Um novo apartamento é identificado pelo padrão `BLXX-APXXXX`.
- Na mesma identificação também é procurado o vencimento no formato `DD/MM/AAAA`.
- O número após `BL` é utilizado como Bloco.
- O número após `AP` é utilizado como Unidade.
- Ao encontrar um novo apartamento, os dados do apartamento anterior são salvos antes de iniciar o próximo.

Exemplo:

`BL01-AP0105 ... 10/09/2026`

É interpretado como:

- Bloco: 01
- Unidade: 0105
- Vencimento: 10/09/2026

## Despesas reconhecidas

A automação reconhece atualmente as seguintes despesas:

- Cota do Mês
- Água-Esgoto
- Energia
- Fundo de Reserva
- Cota Extra
- Segurança Externa
- Instalação - Projeto Solar

Cada despesa é identificada através de sua descrição no PDF.

## Cota do Mês

- A Cota do Mês é identificada pela descrição `Taxa Condominial`.
- Ela pode aparecer na mesma linha de identificação do apartamento ou em uma linha posterior.

## Água-Esgoto

- É identificada pela descrição `Água-Esgoto`.
- A referência do mês pode ou não aparecer entre a descrição e o valor.
- Os dois formatos são aceitos pela automação.

## Energia

- É identificada pela descrição `Energia`.
- A referência do mês aparece antes do valor da despesa.

## Fundo de Reserva

- É identificado diretamente pela descrição `Fundo de Reserva`.
- O valor encontrado é associado ao apartamento atual.

## Instalação - Projeto Solar

- É identificada pela descrição `Instalação - Projeto Solar`.
- A descrição contém também a indicação da parcela no formato `X/X`.
- O Projeto Solar pode aparecer na mesma linha de identificação do apartamento ou posteriormente.

## Cota Extra

A Cota Extra necessita de um tratamento especial porque a ordem do texto
extraído do PDF pode variar.

A descrição utilizada para identificá-la começa com:

`Custeio das despesas referentes ao registro da`

A parcela e o valor podem aparecer em diferentes posições durante a extração.

A automação trata três situações:

### Descrição e valor juntos

Quando a descrição e o valor aparecem na mesma linha, o valor é utilizado
diretamente como Cota Extra.

### Descrição antes do valor

Quando a descrição é encontrada primeiro, a automação marca internamente que
está aguardando o valor da Cota Extra.

Quando uma linha de parcela e valor é encontrada posteriormente, esse valor é
associado à Cota Extra do apartamento atual.

### Valor antes da descrição

Em alguns casos, a extração do PDF apresenta primeiro uma linha contendo
somente a parcela e o valor.

Nesse caso, o valor é armazenado temporariamente como uma possível Cota Extra.

Se a descrição da Cota Extra aparecer posteriormente, o valor armazenado é
confirmado e associado ao apartamento.

Essas informações temporárias são utilizadas apenas durante a leitura e não
são exportadas para a planilha final.

## Valores negativos

- As despesas aceitam valores negativos.
- Valores negativos devem permanecer negativos.
- Não é realizada conversão para valor absoluto.

## Totais do PDF

- Os totais são obtidos através do Resumo Contábil do PDF.
- Somente linhas do resumo que seguem o padrão de conta contábil são enviadas para o processamento dos totais.
- Cada verba é identificada pelo seu nome.
- O valor localizado no final da linha é utilizado como total daquela verba.

São procurados totais para:

- Cota do Mês
- Água-Esgoto
- Energia
- Fundo de Reserva
- Cota Extra
- Segurança Externa
- Instalação - Projeto Solar

## Final da leitura

- Quando um novo apartamento é encontrado, o apartamento anterior é salvo.
- Após o processamento de todas as páginas, o último apartamento também é salvo.
- Campos temporários utilizados no tratamento da Cota Extra são removidos antes do apartamento ser adicionado ao resultado final.

## Exportação

Cada apartamento pode possuir:

- Bloco
- Unidade
- Vencimento
- Cota do Mês
- Água-Esgoto
- Energia
- Fundo de Reserva
- Cota Extra
- Segurança Externa
- Instalação - Projeto Solar

Após a leitura, os apartamentos são convertidos para um DataFrame e utilizados
na geração da planilha final.