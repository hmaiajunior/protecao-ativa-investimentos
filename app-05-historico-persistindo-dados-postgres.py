import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

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

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        dados = resposta.json().get("results", [])[0].get("historicalDataPrice", [])
        return dados
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar {ticker}: {e}")
        return []

def salvar_dados_no_banco(session, ticker, dados_historicos):
    """Salva os dados históricos no banco de dados, apenas registros novos"""
    novos_registros = []
    for dado in dados_historicos:
        data_cotacao = datetime.utcfromtimestamp(dado["date"])  # Convertendo Unix timestamp para datetime
        existe = session.query(
            exists().where(
                DadosHistoricosAcoes.ticker == ticker,
                DadosHistoricosAcoes.data == data_cotacao
            )
        ).scalar()

        # Apenas adiciona o registro se ainda não existir no banco
        if not existe:
            registro = DadosHistoricosAcoes(
                fechamento=dado["close"],
                fechamento_ajustado=dado["adjustedClose"],
                ticker=ticker,
                moeda="BRL",  # Padrão
                data=data_cotacao
            )
            novos_registros.append(registro)

    if novos_registros:
        try:
            session.bulk_save_objects(novos_registros)  # Salva os dados em lote
            session.commit()
            print(f"{len(novos_registros)} novos registros salvos para {ticker}.")
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar os dados para {ticker}: {e}")
    else:
        print(f"Nenhum novo registro para o ticker {ticker}.")

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

    # Criar tabela no banco de dados
    criar_tabela()

    # Iniciar sessão no banco de dados
    session = Session()

    print("Consultando e salvando dados históricos incrementais das ações na API Brapi...")
    for ticker in codigos_acoes:
        dados_historicos = consultar_dados_historicos(ticker)
        if dados_historicos:
            salvar_dados_no_banco(session, ticker, dados_historicos)
        else:
            print(f"Não foi possível obter os dados históricos para o ticker {ticker}.")

    session.close()

if __name__ == "__main__":
    main()
