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

# Configuração da barra lateral para navegação
st.sidebar.title("Dashboard de Ações")
aba_selecionada = st.sidebar.radio(
    "Navegação:",
    ["Visão Geral", "Margem de Garantia", "Variação Diária", "Diferença de Fechamento", "Análise de Variações", "Ações por Setor"]
)

# Estilo do cabeçalho principal
st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        color: #0A74DA;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 22px;
        color: #3D3D3D;
        margin-top: 10px;
    }
    .arrow-up {
        color: green;
        font-size: 20px;
    }
    .arrow-down {
        color: red;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Tela: Visão Geral
if aba_selecionada == "Visão Geral":
    st.markdown("<h1 class='main-title'>Visão Geral das Ações</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Resumo das ocorrências de variação diária acima de R$1,00.</p>", unsafe_allow_html=True)

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
    st.dataframe(dados)

    # Gráfico interativo
    grafico = dados.groupby("ticker")["ocorrencias_variacao_acima_1"].mean().reset_index()
    st.bar_chart(data=grafico, x="ticker", y="ocorrencias_variacao_acima_1")

# Tela: Margem de Garantia
elif aba_selecionada == "Margem de Garantia":
    st.markdown("<h1 class='main-title'>Calculadora de Margem de Garantia</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Selecione os tickers e veja o cálculo automático.</p>", unsafe_allow_html=True)

    query_tickers = """
    SELECT DISTINCT ticker
    FROM dados_historicos_acoes
    ORDER BY ticker;
    """
    tickers_disponiveis = pd.read_sql(query_tickers, engine)["ticker"].tolist()

    col1, col2 = st.columns(2)

    # Seleção de ação comprada
    with col1:
        st.text("Ação Comprada")
        nome_acao_comprada = st.selectbox("Escolha a ação comprada:", tickers_disponiveis)
        quantidade_comprada = st.number_input("Quantidade comprada:", min_value=1, value=100)

    # Seleção de ação vendida
    with col2:
        st.text("Ação Vendida")
        nome_acao_vendida = st.selectbox("Escolha a ação vendida:", tickers_disponiveis)
        quantidade_vendida = st.number_input("Quantidade vendida:", min_value=1, value=100)

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

    preco_comprada = consultar_preco_fechamento(nome_acao_comprada)
    preco_vendida = consultar_preco_fechamento(nome_acao_vendida)

    if st.button("Calcular Margem de Garantia") and preco_comprada and preco_vendida:
        margem_vendida = preco_vendida * quantidade_vendida * 1.2
        margem_comprada = (preco_comprada * quantidade_comprada) / 2
        margem_total = margem_comprada - margem_vendida

        st.write(f"**Preço da ação comprada ({nome_acao_comprada}):** R${preco_comprada:.2f}")
        st.write(f"**Preço da ação vendida ({nome_acao_vendida}):** R${preco_vendida:.2f}")
        st.write(f"**Margem necessária para {nome_acao_vendida} (vendida):** R${margem_vendida:.2f}")
        st.write(f"**Margem necessária para {nome_acao_comprada} (comprada):** R${margem_comprada:.2f}")
        st.write(f"**Margem total necessária:** R${margem_total:.2f}")
        st.warning("Os preços utilizados para o cálculo são apenas estimativas. Para obter valores exatos, entre em contato com sua corretora.")

# Tela: Variação Diária
elif aba_selecionada == "Variação Diária":
    st.markdown("<h1 class='main-title'>Variação Diária das Ações</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Visualize os dados de variação diária por ticker.</p>", unsafe_allow_html=True)

    query_variacao = """
    SELECT ticker, data, variacao_diaria
    FROM dados_historicos_acoes
    WHERE variacao_diaria > 1.00
    ORDER BY ticker, data DESC;
    """
    variacao_dados = pd.read_sql(query_variacao, engine)

    st.dataframe(variacao_dados)
    st.line_chart(data=variacao_dados, x="data", y="variacao_diaria")


# Tela: Diferença de Fechamento
elif aba_selecionada == "Diferença de Fechamento":
    st.markdown("<h1 class='main-title'>Comparação de Fechamento entre Ações</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Selecione dois tickers para visualizar a diferença.</p>", unsafe_allow_html=True)

    query_todos_tickers = """
    SELECT DISTINCT ticker
    FROM dados_historicos_acoes
    ORDER BY ticker;
    """
    todos_tickers = pd.read_sql(query_todos_tickers, engine)["ticker"].tolist()

    acao1 = st.selectbox("Selecione a primeira ação:", todos_tickers)
    acao2 = st.selectbox("Selecione a segunda ação:", todos_tickers)

    if acao1 and acao2 and acao1 != acao2:
        query_comparacao = f"""
        SELECT 
            elet3.data AS data,
            ROUND(CAST(elet3.fechamento AS NUMERIC) - CAST(elet6.fechamento AS NUMERIC), 2) AS diferenca_fechamento
        FROM 
            dados_historicos_acoes AS elet3
        JOIN 
            dados_historicos_acoes AS elet6
        ON 
            elet3.data = elet6.data
        WHERE 
            elet3.ticker = '{acao1}'
            AND elet6.ticker = '{acao2}'
        ORDER BY elet3.data;
        """
        dados_comparacao = pd.read_sql(query_comparacao, engine)

        st.subheader("Tabela de Diferença de Fechamento")
        st.dataframe(dados_comparacao)
        st.subheader(f"Diferença de Fechamento entre {acao1} e {acao2}")
        st.line_chart(data=dados_comparacao, x="data", y="diferenca_fechamento")

# Tela: Análise de Variações
elif aba_selecionada == "Análise de Variações":
    st.markdown("<h1 class='main-title'>Análise de Variações nos Últimos 30 Dias</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Veja as ações que mais variaram e a comparação com o último dia registrado.</p>", unsafe_allow_html=True)

    # Consulta para buscar as 10 ações que mais variaram nos últimos 30 dias
    query_top_variacoes = """
    SELECT ticker, 
           MAX(variacao_diaria) AS maior_variacao, 
           AVG(variacao_diaria) AS media_variacao
    FROM dados_historicos_acoes
    WHERE data >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY ticker
    ORDER BY maior_variacao DESC
    LIMIT 10;
    """
    top_variacoes = pd.read_sql(query_top_variacoes, engine)

    st.write("### As 10 ações que mais variaram nos últimos 30 dias:")
    st.dataframe(top_variacoes)

    # Comparação percentual do último dia registrado com a média dos últimos 30 dias
    st.write("### Comparação percentual do último dia com os últimos 30 dias:")

    comparacoes = []
    for index, row in top_variacoes.iterrows():
        ticker = row["ticker"]
        media_30_dias = row["media_variacao"]

        # Busca da variação do último dia registrado
        query_ultimo_dia = f"""
        SELECT variacao_diaria
        FROM dados_historicos_acoes
        WHERE ticker = '{ticker}'
        ORDER BY data DESC
        LIMIT 1;
        """
        ultimo_dia = pd.read_sql(query_ultimo_dia, engine)

        if not ultimo_dia.empty:
            variacao_ultimo_dia = ultimo_dia.iloc[0]["variacao_diaria"]
            diff_percentual = ((variacao_ultimo_dia - media_30_dias) / media_30_dias) * 100

            if diff_percentual > 0:
                comparacoes.append((ticker, variacao_ultimo_dia, media_30_dias, diff_percentual, "↑"))
            else:
                comparacoes.append((ticker, variacao_ultimo_dia, media_30_dias, diff_percentual, "↓"))

    # Criação de DataFrame para exibir os resultados
    df_comparacoes = pd.DataFrame(comparacoes, columns=[
        "Ticker", "Variação Último Dia", "Média 30 Dias", "Diferença (%)", "Tendência"
    ])
    st.dataframe(df_comparacoes)

# Tela: Ações por Setor
elif aba_selecionada == "Ações por Setor":
    st.markdown("<h1 class='main-title'>Ações por Setor</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Visualize todas as ações segregadas por setor.</p>", unsafe_allow_html=True)

    try:
        # Carregar o arquivo de texto com os setores
        file_path = "ativos-garantia-dividido-setor.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            setores = file.readlines()

        # Exibir os dados formatados
        setores_dict = {}
        for line in setores:
            if ":" in line:
                setor, acoes = line.strip().split(":")
                setores_dict[setor.strip()] = acoes.strip().split(",")

        for setor, acoes in setores_dict.items():
            st.subheader(f"Setor: {setor}")
            st.write(", ".join(acoes))

    except FileNotFoundError:
        st.error("O arquivo 'ativos-garantia-dividido-setor.txt' não foi encontrado no diretório atual.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
