# Regras de Negócio - Duet Barra

- O bloco e a unidade são identificados a partir do cabeçalho de cada apartamento.
- O vencimento não é utilizado no processamento deste condomínio.
- O sistema interrompe a leitura ao encontrar a seção "SOMA DAS VERBAS", evitando processar os totais gerais do relatório.
- Algumas despesas podem apresentar variações na hierarquia (ex.: "ÁGUA/ESGOTO -> ÁGUA" ou "PRINCIPAL -> ÁGUA"), sendo ambas reconhecidas pela automação.