import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def ler_acoes_txt(nome_arquivo):
    """Lê os códigos das ações de um arquivo .txt"""
    try:
        with open(nome_arquivo, "r") as arquivo:
            acoes = arquivo.read().splitlines()
            return acoes
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []

def consultar_dados_acoes(codigos_acoes):
    # Carrega o token da variável de ambiente
    token = os.getenv("BRAPI_TOKEN")
    if not token:
        print("Erro: Token não encontrado na variável de ambiente 'BRAPI_TOKEN'.")
        return[]
    
    []

    # Construção da URL e cabeçalho
    url = f"https://brapi.dev/api/quote/{','.join(codigos_acoes)}"
    headers = {
        "Authorization": f"Bearer {token}"  # Passando o token no cabeçalho
    }

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json().get("results", [])
        return dados
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
        return 

def exibir_dados_acoes(dados_acoes):
    """Exibe as informações relevantes das ações"""
    for acao in dados_acoes:
        codigo = acao.get("symbol", "N/A")
        fechamento_anterior = acao.get("previousClose", "N/A")
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
    
    print("Lendo códigos das ações do arquivo...")
    codigos_acoes = ler_acoes_txt(nome_arquivo)
    
    if codigos_acoes:
        print("Consultando dados das ações na API Brapi...")
        dados_acoes = consultar_dados_acoes(codigos_acoes)
        
        if dados_acoes:
            print("Exibindo dados das ações:")
            exibir_dados_acoes(dados_acoes)
        else:
            print("Nenhuma informação retornada pela API.")
    else:
        print("Nenhum código de ação encontrado no arquivo.")

if __name__ == "__main__":
    main()
