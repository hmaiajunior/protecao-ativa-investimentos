from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import os
from database import Base, DadosHistoricosAcoes

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Lê as variáveis separadas do arquivo .env (sem SSL)
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Monta a URL de conexão ao banco PostgreSQL (sem ?sslmode=...)
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Cria o engine e a sessão
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Consulta inicial para exibir os tickers e suas ocorrências
query = """
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
"""
dados = pd.read_sql(query, engine)

# Configuração do título do dashboard
st.title("Dashboard de Ações")

# Exibição dos dados
st.subheader("Tabela de Ações com Variação Diária Acima de R$1,00")
st.dataframe(dados)

# Gráfico interativo com média de ocorrências
st.subheader("Gráfico de Variação Diária por Ticker")
grafico = dados.groupby("ticker")["ocorrencias_variacao_acima_1"].mean().reset_index()
st.bar_chart(data=grafico, x="ticker", y="ocorrencias_variacao_acima_1")

# Seleção de tickers para comparação
st.subheader("Comparação de Ações")
tickers = dados["ticker"].tolist()
acao1 = st.selectbox("Selecione a primeira ação:", tickers)
acao2 = st.selectbox("Selecione a segunda ação:", tickers)

# Consulta de comparação entre as ações selecionadas
if acao1 and acao2 and acao1 != acao2:
    query_comparacao = f"""
    SELECT 
        elet3.data AS data,
        elet3.fechamento AS fechamento_{acao1.lower()},
        elet6.fechamento AS fechamento_{acao2.lower()},
        elet3.variacao_diaria AS variacao_diaria_{acao1.lower()},
        elet6.variacao_diaria AS variacao_diaria_{acao2.lower()},
        ROUND(ABS(CAST(elet3.fechamento AS NUMERIC) - CAST(elet6.fechamento AS NUMERIC)), 2) AS diferenca_fechamento,
        CASE
            WHEN elet3.fechamento > elet6.fechamento THEN '{acao1}'
            WHEN elet6.fechamento > elet3.fechamento THEN '{acao2}'
            ELSE 'IGUAL'
        END AS acao_maior_valor
    FROM 
        dados_historicos_acoes AS elet3
    JOIN 
        dados_historicos_acoes AS elet6
    ON 
        elet3.data = elet6.data
    WHERE 
        elet3.ticker = '{acao1}'
        AND elet6.ticker = '{acao2}';
    """
    dados_comparacao = pd.read_sql(query_comparacao, engine)

    # Exibição do gráfico comparativo
    st.subheader(f"Comparação entre {acao1} e {acao2}")
    st.dataframe(dados_comparacao)

    # # Gráfico de diferença de fechamento ao longo do tempo
    # st.line_chart(data=dados_comparacao, x="data", y=["fechamento_" + acao1.lower(), "fechamento_" + acao2.lower()])

    # Exibição do gráfico de diferença de fechamento
    st.subheader(f"Diferença de Fechamento entre {acao1} e {acao2}")
    st.line_chart(data=dados_comparacao, x="data", y="diferenca_fechamento")
