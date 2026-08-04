# Regras de Negócio - Condomínio Marechal Rondon II

Este documento descreve as regras utilizadas para interpretar corretamente os rateios do Marechal.

## Estrutura do PDF.

- Cada página é dividida em duas colunas.
- As colunas são processadas separadamente.
- A leitura ocorre de cima para baixo.

## Identificação dos apartamentos

- Um apartamento é identificado pela linha contendo unidade, bloco e vencimento.
- Ao encontrar um novo apartamento, o registro anterior é finalizado.

## Processamento das despesas

- Algumas despesas podem aparecer mais de uma vez.
- Nesses casos, seus valores são somados.

## Valores negativos

- Descontos devem permanecer negativos.
- Não é realizada conversão para valores absolutos.

## Final da leitura

- Ao encontrar o quadro "TOTAIS", a leitura da coluna é encerrada.

## Exportação

- Colunas completamente vazias são removidas.
- Valores nulos são exportados como células vazias.
- Valores iguais a zero são convertidos para células vazias.