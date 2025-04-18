from dotenv import load_dotenv

import requests


# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

token = os.getenv("BRAPI_TOKEN")
if not token:
    print("ro: Token não encontrado na variável de ambiente 'BRAPI_TOKEN'.")
return 


rl = "https://brapi.dev/api/quote/"
resosta = requests.get(url)
dados = resposta.json()
print (dados)