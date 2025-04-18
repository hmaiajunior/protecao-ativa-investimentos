O software em questão visa o levantamento de todas as ações que são aceitas em garantia na B3, para que seja feita uma análise comparativa entre o valor de fechamento dessas ações para que seja apontada a maior e a menor diferença do fechamento.

Objetivo é encontrar ações que são boas para realizar operações de arbitragem. 

Ideal são ações onde a diferença entre eles fique dentro de um range não muito grande e que oscilem bastante durante o dia dando oportunidade de day/trade

Será utilizada a API Brapi para consulta dos dados das ações.

Analisar todas as informações que podem afetar as operações de pares de ações:

* Valor entre as ações
* Se são aceitas como garantia
* valor pago de dividendos


API:

"symbol": Código da ação
"regularMarketChange": Variação diária
"regularMarketTime": Data e hora do último preço
"regularMarketPrice": Preço atual
"regularMarketPreviousClose": Fechamento do dia anterior


URL Base: https://brapi.dev/api

1 - Levantamento das ações aceitas em garantia na B3 - OK

2 - Criar as funções que irão ser usadas no programa:
    - Ler as ações que são aceitas em garantia de um arquivo txt.
    - Fazer a função que irá conectar-se ao banco de dados Postgres
    - Salvar os dados de cada uma das ações no banco de dados
    - Connectar o dashboard ao banco de dados
    - Realizar as consultas necessárias no dashboard


