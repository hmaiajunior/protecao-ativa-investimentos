==> Comparando dados de fechamento entre pares de ações

SELECT 
    itub4.data AS data,
    itub4.fechamento AS fechamento_itub4,
    bpac11.fechamento AS fechamento_bpac11,
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



ALTER TABLE dados_historicos_acoes
ADD COLUMN variacao_diaria FLOAT;


select * from dados_historicos_acoes where ticker = 'PETR4'

