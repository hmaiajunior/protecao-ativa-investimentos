==> Comparando dados de fechamento entre pares de ações

SELECT 
    elet3.data AS data,
    elet3.fechamento AS fechamento_elet3,
    elet6.fechamento AS fechamento_elet6,
    elet3.variacao_diaria AS variacao_diaria_elet3,
    elet6.variacao_diaria AS variacao_diaria_elet6,
    ROUND(ABS(CAST(elet3.fechamento AS NUMERIC) - CAST(elet6.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
    ROUND(ABS(CAST(elet3.fechamento_ajustado AS NUMERIC) - CAST(elet6.fechamento_ajustado AS NUMERIC)), 2) AS diferenca_fechamento_ajustado,
    CASE
        WHEN elet3.fechamento > elet6.fechamento THEN 'ELET3'
        WHEN elet6.fechamento > elet3.fechamento THEN 'ELET6'
        ELSE 'IGUAL' -- Caso os valores sejam iguais
    END AS acao_maior_valor
FROM 
    dados_historicos_acoes AS elet3
JOIN 
    dados_historicos_acoes AS elet6
ON 
    elet3.data = elet6.data
WHERE 
    elet3.ticker = 'ELET3'
    AND elet6.ticker = 'ELET6';

======================================================================================================================================================


SELECT 
    ggbr4.data AS data,
    ggbr4.fechamento AS fechamento_ggbr4,
    klbn11.fechamento AS fechamento_klbn11,
    ggbr4.variacao_diaria AS variacao_diaria_ggbr4,
    klbn11.variacao_diaria AS variacao_diaria_klbn11,
    ROUND(ABS(CAST(ggbr4.fechamento AS NUMERIC) - CAST(klbn11.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
    ROUND(ABS(CAST(ggbr4.fechamento_ajustado AS NUMERIC) - CAST(klbn11.fechamento_ajustado AS NUMERIC)), 2) AS diferenca_fechamento_ajustado,
    CASE
        WHEN ggbr4.fechamento > klbn11.fechamento THEN 'GGBR4'
        WHEN klbn11.fechamento > ggbr4.fechamento THEN 'KLBN11'
        ELSE 'IGUAL' -- Caso os valores sejam iguais
    END AS acao_maior_valor
FROM 
    dados_historicos_acoes AS ggbr4
JOIN 
    dados_historicos_acoes AS klbn11
ON 
    ggbr4.data = klbn11.data
WHERE 
    ggbr4.ticker = 'GGBR4'
    AND klbn11.ticker = 'KLBN11';

======================================================================================================================================================


SELECT 
    itub4.data AS data,
    itub4.fechamento AS fechamento_itub4,
    bpac11.fechamento AS fechamento_bpac11,
    itub4.variacao_diaria AS variacao_diaria_itub4,
    bpac11.variacao_diaria AS variacao_diaria_bpac11,
    ROUND(ABS(CAST(itub4.fechamento AS NUMERIC) - CAST(bpac11.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
    ROUND(ABS(CAST(itub4.fechamento_ajustado AS NUMERIC) - CAST(bpac11.fechamento_ajustado AS NUMERIC)), 2) AS diferenca_fechamento_ajustado,
    CASE
        WHEN itub4.fechamento > bpac11.fechamento THEN 'ITUB4'
        WHEN bpac11.fechamento > itub4.fechamento THEN 'BPAC11'
        ELSE 'IGUAL' -- Caso os valores sejam iguais
    END AS acao_maior_valor
FROM 
    dados_historicos_acoes AS itub4
JOIN 
    dados_historicos_acoes AS bpac11
ON 
    itub4.data = bpac11.data
WHERE 
    itub4.ticker = 'ITUB4'
    AND bpac11.ticker = 'BPAC11';


======================================================================================================================================================

==> Consulta que mostra a diferença entre os valores de fechamento de 1 VALE3 contra 3 BRAP4

SELECT 
    vale3.data AS data,
    vale3.fechamento AS fechamento_vale3,
    brap4.fechamento AS fechamento_brap4,
    ROUND(ABS(CAST(vale3.fechamento AS NUMERIC) - 3 * CAST(brap4.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
    CASE
        WHEN vale3.fechamento > 3 * brap4.fechamento THEN 'VALE3'
        WHEN 3 * brap4.fechamento > vale3.fechamento THEN '3x BRAP4'
        ELSE 'IGUAL'
    END AS acao_maior_valor
FROM 
    dados_historicos_acoes AS vale3
JOIN 
    dados_historicos_acoes AS brap4
ON 
    vale3.data = brap4.data
WHERE 
    vale3.ticker = 'VALE3'
    AND brap4.ticker = 'BRAP4';

======================================================================================================================================================

SELECT 
    elet6.data AS data,
    elet6.fechamento AS fechamento_elet6,
    engi11.fechamento AS fechamento_engi11,
    elet6.variacao_diaria AS variacao_diaria_elet6,
    engi11.variacao_diaria AS variacao_diaria_engi11,
    ROUND(ABS(CAST(elet6.fechamento AS NUMERIC) - CAST(engi11.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
    ROUND(ABS(CAST(elet6.fechamento_ajustado AS NUMERIC) - CAST(engi11.fechamento_ajustado AS NUMERIC)), 2) AS diferenca_fechamento_ajustado,
    CASE
        WHEN elet6.fechamento > engi11.fechamento THEN 'ELET6'
        WHEN engi11.fechamento > elet6.fechamento THEN 'ENGI11'
        ELSE 'IGUAL' -- Caso os valores sejam iguais
    END AS acao_maior_valor
FROM 
    dados_historicos_acoes AS ELET6
JOIN 
    dados_historicos_acoes AS ENGI11
ON 
    elet6.data = engi11.data
WHERE 
    elet6.ticker = 'ELET6'
    AND engi11.ticker = 'ENGI11';


======================================================================================================================================================



ALTER TABLE dados_historicos_acoes
ADD COLUMN variacao_diaria FLOAT;


select * from dados_historicos_acoes where ticker = 'PETR4'

select distinct ticker from dados_historicos_acoes 


==> Cálculo de quantas vezes a variação diaria foi acima de R$1,00 em cada uma das ações

SELECT 
    ticker,
    COUNT(*) AS ocorrencias_variacao_acima_1
FROM 
    dados_historicos_acoes
WHERE 
    variacao_diaria > 1.00
GROUP BY 
    ticker
ORDER BY 
    ocorrencias_variacao_acima_1 DESC;


==> Verificar data/horário da última atualização em uma tabela

SELECT MAX(data) AS ultima_data_disponivel
FROM dados_historicos_acoes;