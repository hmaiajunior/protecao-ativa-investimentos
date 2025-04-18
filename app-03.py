import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def consultar_dados_acao(ticker):
    """Consulta a API da Brapi para obter informações de uma única ação"""
    token = os.getenv("BRAPI_TOKEN")
    if not token:
        print("Erro: Token não encontrado na variável de ambiente 'BRAPI_TOKEN'.")
        return {}

    url = f"https://brapi.dev/api/quote/{ticker}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json().get("results", [])[0]
        return dados
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar {ticker}: {e}")
        return {}

def exibir_dados_acao(acao):
    """Exibe os dados de uma única ação"""
    codigo = acao.get("symbol", "N/A")
    fechamento_anterior = acao.get("regularMarketPreviousClose", "N/A")
    preco_atual = acao.get("regularMarketPrice", "N/A")
    data_hora_ultimo_preco = acao.get("regularMarketTime", "N/A")

    print(f"Código: {codigo}")
    print(f"Fechamento do dia anterior: {fechamento_anterior}")
    print(f"Preço atual: {preco_atual}")
    print(f"Data e hora do último preço: {data_hora_ultimo_preco}")
    print("-" * 40)

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

    # Consultar os dados de cada ação individualmente
    print("Consultando dados das ações na API Brapi...")
    for ticker in codigos_acoes:
        dados_acao = consultar_dados_acao(ticker)
        if dados_acao:
            exibir_dados_acao(dados_acao)
        else:
            print(f"Não foi possível obter os dados para o ticker {ticker}.")

if __name__ == "__main__":
    main()
