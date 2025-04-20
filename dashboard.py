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


# Consulta para obter os dados desejados
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

# Gráfico interativo
st.subheader("Gráfico de Variação Diária por Ticker")
grafico = dados.groupby("ticker")["ocorrencias_variacao_acima_1"].mean().reset_index()
st.bar_chart(data=grafico, x="ticker", y="ocorrencias_variacao_acima_1")