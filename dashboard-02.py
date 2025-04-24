from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import os

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

# Configuração do título do dashboard
st.title("Dashboard de Ações")

# Escolha da aba para navegação
menu = st.radio(
    "Selecione uma aba:", 
    ["Visualização Geral", "Margem de Garantia"]
)

# Tela: Visualização Geral
if menu == "Visualização Geral":
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

    # Exibição dos dados
    st.subheader("Tabela de Ações com Variação Diária Acima de R$1,00")
    st.dataframe(dados)

    # Gráfico interativo com média de ocorrências
    st.subheader("Gráfico de Variação Diária por Ticker")
    grafico = dados.groupby("ticker")["ocorrencias_variacao_acima_1"].mean().reset_index()
    st.bar_chart(data=grafico, x="ticker", y="ocorrencias_variacao_acima_1")

# Tela: Margem de Garantia
elif menu == "Margem de Garantia":
    st.subheader("Calculadora de Margem de Garantia")

    # Inserir dados das ações pelo usuário
    st.write("Escolha os tickers para cálculo da margem:")
    col1, col2 = st.columns(2)

    # Dados da ação comprada
    with col1:
        st.text("Dados da Ação Comprada")
        nome_acao_comprada = st.text_input("Ticker da ação comprada (ex.: PETR4):", value="PETR4")
        quantidade_comprada = st.number_input("Quantidade comprada:", min_value=1, value=100)

    # Dados da ação vendida
    with col2:
        st.text("Dados da Ação Vendida")
        nome_acao_vendida = st.text_input("Ticker da ação vendida (ex.: PRIO3):", value="PRIO3")
        quantidade_vendida = st.number_input("Quantidade vendida:", min_value=1, value=100)

    # Consultar o valor de fechamento mais recente do banco de dados
    def consultar_preco_fechamento(ticker):
        query = f"""
        SELECT fechamento
        FROM dados_historicos_acoes
        WHERE ticker = '{ticker}'
        ORDER BY data DESC
        LIMIT 1;
        """
        resultado = pd.read_sql(query, engine)
        if not resultado.empty:
            return resultado.iloc[0]["fechamento"]
        else:
            st.error(f"Ticker {ticker} não encontrado ou sem dados disponíveis.")
            return None

    # Obter os valores de fechamento mais recentes
    preco_comprada = consultar_preco_fechamento(nome_acao_comprada)
    preco_vendida = consultar_preco_fechamento(nome_acao_vendida)

    # Cálculo da Margem de Garantia
    if st.button("Calcular Margem de Garantia") and preco_comprada and preco_vendida:
        # Operação 01: Margem para ação vendida
        margem_vendida = preco_vendida * quantidade_vendida * 1.2

        # Operação 02: Margem para ação comprada
        margem_comprada = (preco_comprada * quantidade_comprada) / 2

        # Resultado final
        margem_total = margem_comprada - margem_vendida

        # Exibição dos resultados
        st.write(f"**Preço da ação comprada ({nome_acao_comprada}):** R${preco_comprada:.2f}")
        st.write(f"**Preço da ação vendida ({nome_acao_vendida}):** R${preco_vendida:.2f}")
        st.write(f"**Margem necessária para {nome_acao_vendida} (vendida):** R${margem_vendida:.2f}")
        st.write(f"**Margem necessária para {nome_acao_comprada} (comprada):** R${margem_comprada:.2f}")
        st.write(f"**Margem total necessária:** R${margem_total:.2f}")
        st.warning("Os preços utilizados para o cálculo são apenas estimativas. Para obter valores exatos, entre em contato com sua corretora.")
