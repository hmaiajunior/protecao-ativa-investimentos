O software em questão visa o levantamento de todas as ações que são aceitas em garantia na B3, para que seja feita uma análise comparativa entre o valor de fechamento dessas ações para que seja apontada a maior e a menor diferença do fechamento.

Objetivo é encontrar ações que são boas para realizar operações de arbitragem. 

Ideal são ações onde a diferença entre eles fique dentro de um range não muito grande e que oscilem bastante durante o dia dando oportunidade de day/trade

Será utilizada a API Brapi para consulta dos dados das ações. 

API:

"symbol": Código da ação
"regularMarketChange": Variação diária
"regularMarketTime": Data e hora do último preço
"regularMarketPrice": Preço atual
"regularMarketPreviousClose": Fechamento do dia anterior


