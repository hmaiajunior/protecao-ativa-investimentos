import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

def criar_tabela():
    """Cria a tabela no banco de dados, se não existir."""
    Base.metadata.create_all(engine)
    print("Tabela criada/verificada com sucesso!")


def consultar_dados_historicos(ticker):
    """Consulta os dados históricos dos últimos 90 dias de uma ação"""
    token = os.getenv("BRAPI_TOKEN")
    if not token:
        print("Erro: Token não encontrado na variável de ambiente 'BRAPI_TOKEN'.")
        return []

    # URL para buscar os dados históricos da ação
    url = f"https://brapi.dev/api/quote/{ticker}?range=3mo&interval=1d&token={token}"
    #print(f"URL gerada para {ticker}: {url}")  # Log para verificar a URL

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        #print(f"Resposta bruta da API para {ticker}: {resposta.text}")  # Log da resposta bruta
        dados = resposta.json().get("results", [])[0].get("historicalDataPrice", [])
        return dados
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar {ticker}: {e}")
        return []

def exibir_dados_historicos(ticker, dados_historicos):
    """Exibe os dados históricos relevantes da ação"""
    if dados_historicos:
        print(f"Histórico da ação: {ticker}")
        print("Data\t\tFechamento\tAjuste\t\tCódigo")
        print("-" * 50)
        for dado in dados_historicos:
            # Convertendo data Unix para formato legível
            date = datetime.utcfromtimestamp(dado.get("date", 0)).strftime("%Y-%m-%d") if dado.get("date") else "N/A"
            close = dado.get("close", "N/A")
            adjusted_close = dado.get("adjustedClose", "N/A")
            symbol = ticker
            print(f"{date}\t{close}\t\t{adjusted_close}\t\t{symbol}")
        print("-" * 50)
    else:
        print(f"Sem dados históricos disponíveis para o ticker {ticker}.")

def main():
    # Nome do arquivo .txt com os códigos das ações
    nome_arquivo = "acoes.txt"

    # Ler os códigos das ações do arquivo
    try:
        with open(nome_arquivo, "r") as arquivo:
            codigos_acoes = arquivo.read().splitlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        return

    # Consultar e exibir os dados históricos de cada ação
    print("Consultando dados históricos das ações na API Brapi...")
    for ticker in codigos_acoes:
        dados_historicos = consultar_dados_historicos(ticker)
        exibir_dados_historicos(ticker, dados_historicos)

if __name__ == "__main__":
    main()
