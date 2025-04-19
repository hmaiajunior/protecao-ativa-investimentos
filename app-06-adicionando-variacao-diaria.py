import requests
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
        resultado = resposta.json().get("results", [])[0]
        dados_historicos = resultado.get("historicalDataPrice", [])
        
        # Adicionar cálculo de `variacao_diaria` para cada registro
        for dado in dados_historicos:
            high = dado.get("high")
            low = dado.get("low")
            if high is not None and low is not None:
                # Calcula a diferença entre high e low e arredonda para 2 casas decimais
                dado["variacao_diaria"] = round(high - low, 2)
            else:
                dado["variacao_diaria"] = None  # Define como None se os valores não existirem

        return dados_historicos
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar {ticker}: {e}")
        return []

def salvar_dados_no_banco(session, ticker, dados_historicos):
    """Salva os dados históricos no banco de dados, atualizando registros existentes e inserindo novos."""
    novos_registros = []
    registros_a_atualizar = []

    for dado in dados_historicos:
        data_cotacao = datetime.utcfromtimestamp(dado["date"])  # Convertendo Unix timestamp para datetime

        # Verifica se o registro já existe no banco pelo ticker e pela data
        registro_existente = session.query(DadosHistoricosAcoes).filter_by(
            ticker=ticker,
            data=data_cotacao
        ).first()

        if registro_existente:
            # Verifica se algum valor precisa ser atualizado
            if (
                registro_existente.variacao_diaria != dado.get("variacao_diaria") or
                registro_existente.fechamento != dado.get("close") or
                registro_existente.fechamento_ajustado != dado.get("adjustedClose")
            ):
                registro_existente.variacao_diaria = dado.get("variacao_diaria")
                registro_existente.fechamento = dado.get("close")
                registro_existente.fechamento_ajustado = dado.get("adjustedClose")
                registros_a_atualizar.append(registro_existente)
        else:
            # Cria um novo registro se ele ainda não existir no banco
            registro = DadosHistoricosAcoes(
                fechamento=dado["close"],
                fechamento_ajustado=dado["adjustedClose"],
                variacao_diaria=dado.get("variacao_diaria"),
                ticker=ticker,
                moeda="BRL",  # Padrão
                data=data_cotacao
            )
            novos_registros.append(registro)

    # Inserir novos registros no banco
    if novos_registros:
        try:
            session.bulk_save_objects(novos_registros)  # Salva os dados em lote
            session.commit()
            print(f"{len(novos_registros)} novos registros salvos para {ticker}.")
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar os dados para {ticker}: {e}")

    # Atualizar registros existentes
    if registros_a_atualizar:
        try:
            session.bulk_save_objects(registros_a_atualizar)  # Atualiza os registros modificados
            session.commit()
            print(f"{len(registros_a_atualizar)} registros atualizados para {ticker}.")
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar os dados para {ticker}: {e}")

    if not novos_registros and not registros_a_atualizar:
        print(f"Nenhum novo ou atualizado registro para o ticker {ticker}.")



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
