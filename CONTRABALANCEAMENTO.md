# Ordem contrabalanceada por integrante

Matriz de contrabalanceamento do experimento: define, para cada
integrante, em que ordem e com qual tratamento (`com_ia`/`sem_ia`) cada um dos
6 katas de [katas/](katas/) e resolvido. Cada integrante resolve os 6 katas,
3 com IA e 3 sem IA.

## O que o contrabalanceamento evita

1. **Aprendizado/ordem entre katas**: se todo mundo resolvesse os katas na
   mesma sequencia, o kata que cai por ultimo sempre se beneficiaria do
   "aquecimento" da sessao, e isso seria indistinguivel de uma diferenca real
   de dificuldade entre katas.
2. **Kata confundido com tratamento**: se um kata especifico fosse sempre
   resolvido com IA (por todos os integrantes), um resultado melhor nesse kata
   nao permitiria separar "efeito da IA" de "esse kata era mais facil".
3. **Fadiga/aprendizado confundido com tratamento**: se um integrante fizesse
   os 3 trials com IA em bloco e só depois os 3 sem IA (ou vice-versa), o
   cansaço/aprendizado acumulado na sessão ficaria misturado com o efeito do
   tratamento. Por isso o tratamento alterna a cada trial, nunca em bloco.

## Metodo

* **Numeração dos katas**: 1 Cofre de Senhas, 2 Elevador do Prédio,
  3 Etiquetas de Preço, 4 Fila do Caixa, 5 Estoque do Depósito,
  6 Blocos Aninhados (os dois últimos são os de dificuldade maior, ver
  [katas/README.md](katas/README.md)).
* **Ordem dos katas**: quadrado 6x6 (linhas = integrante, colunas =
  posicao 1a-6a), usando 3 das 6 linhas, uma rotacao ciclica por integrante
  (Arthur K1K2K3K4K5K6, Felipe K2K3K4K5K6K1, Gabriel K3K4K5K6K1K2). Nenhum
  integrante repete a sequencia de outro, e cada kata cai em 3 das 6 posicoes
  possiveis entre os 3 integrantes.
* **Tratamento por posicao**: um padrao alternado de periodo 2 (nunca dois
  trials seguidos com o mesmo tratamento). Arthur e Felipe usam a fase
  "sem_ia, com_ia, sem_ia, com_ia, sem_ia, com_ia" (na ordem de cada um);
  Gabriel usa a fase invertida "com_ia, sem_ia, com_ia, sem_ia, com_ia,
  sem_ia". Isso garante que cada kata seja feito com os dois tratamentos por
  integrantes diferentes (nunca 3x0) e que nem todo mundo comece a sessao com
  o mesmo tratamento. Essa fase já está refletida nas issues de trial abertas
  no GitHub Projects (ex.: "Kata 1 (sem IA)" ... "Kata 6 (com IA)").

Limitação assumida: com 3 integrantes e 2 fases de tratamento possíveis, a
divisão de quem começa com IA vs. manual fica 2-para-1 (Arthur e Felipe
começam com `sem_ia`, Gabriel com `com_ia`); não há como equilibrar 50/50 com
N ímpar.

## Matriz (por integrante)

| Integrante | 1º trial | 2º trial | 3º trial | 4º trial | 5º trial | 6º trial |
| --- | --- | --- | --- | --- | --- | --- |
| Arthur | Cofre de Senhas (`sem_ia`) | Elevador do Prédio (`com_ia`) | Etiquetas de Preço (`sem_ia`) | Fila do Caixa (`com_ia`) | Estoque do Depósito (`sem_ia`) | Blocos Aninhados (`com_ia`) |
| Felipe | Elevador do Prédio (`sem_ia`) | Etiquetas de Preço (`com_ia`) | Fila do Caixa (`sem_ia`) | Estoque do Depósito (`com_ia`) | Blocos Aninhados (`sem_ia`) | Cofre de Senhas (`com_ia`) |
| Gabriel | Etiquetas de Preço (`com_ia`) | Fila do Caixa (`sem_ia`) | Estoque do Depósito (`com_ia`) | Blocos Aninhados (`sem_ia`) | Cofre de Senhas (`com_ia`) | Elevador do Prédio (`sem_ia`) |

## Conferência por kata

| Kata | Feito com IA por | Feito sem IA por |
| --- | --- | --- |
| Cofre de Senhas | Felipe, Gabriel | Arthur |
| Elevador do Prédio | Arthur | Felipe, Gabriel |
| Etiquetas de Preço | Felipe, Gabriel | Arthur |
| Fila do Caixa | Arthur | Felipe, Gabriel |
| Estoque do Depósito | Felipe, Gabriel | Arthur |
| Blocos Aninhados | Arthur | Felipe, Gabriel |

Nenhum kata é feito só com IA ou só sem IA: todos têm as duas condições
representadas por integrantes diferentes.

## Execução (trial-id sugerido)

Para rodar direto com `scripts/time_trial.sh` / `scripts/run_trial.sh`
([SETUP.md](SETUP.md)), sugestão de `<trial-id>` por linha, já na ordem de
execução de cada integrante:

| Integrante | Ordem | Kata | Tratamento | trial-id |
| --- | --- | --- | --- | --- |
| Arthur | 1 | cofre-de-senhas | sem_ia | `trial-arthur-01-cofre-de-senhas-sem_ia` |
| Arthur | 2 | elevador-do-predio | com_ia | `trial-arthur-02-elevador-do-predio-com_ia` |
| Arthur | 3 | etiquetas-de-preco | sem_ia | `trial-arthur-03-etiquetas-de-preco-sem_ia` |
| Arthur | 4 | fila-do-caixa | com_ia | `trial-arthur-04-fila-do-caixa-com_ia` |
| Arthur | 5 | estoque-do-deposito | sem_ia | `trial-arthur-05-estoque-do-deposito-sem_ia` |
| Arthur | 6 | blocos-aninhados | com_ia | `trial-arthur-06-blocos-aninhados-com_ia` |
| Felipe | 1 | elevador-do-predio | sem_ia | `trial-felipe-01-elevador-do-predio-sem_ia` |
| Felipe | 2 | etiquetas-de-preco | com_ia | `trial-felipe-02-etiquetas-de-preco-com_ia` |
| Felipe | 3 | fila-do-caixa | sem_ia | `trial-felipe-03-fila-do-caixa-sem_ia` |
| Felipe | 4 | estoque-do-deposito | com_ia | `trial-felipe-04-estoque-do-deposito-com_ia` |
| Felipe | 5 | blocos-aninhados | sem_ia | `trial-felipe-05-blocos-aninhados-sem_ia` |
| Felipe | 6 | cofre-de-senhas | com_ia | `trial-felipe-06-cofre-de-senhas-com_ia` |
| Gabriel | 1 | etiquetas-de-preco | com_ia | `trial-gabriel-01-etiquetas-de-preco-com_ia` |
| Gabriel | 2 | fila-do-caixa | sem_ia | `trial-gabriel-02-fila-do-caixa-sem_ia` |
| Gabriel | 3 | estoque-do-deposito | com_ia | `trial-gabriel-03-estoque-do-deposito-com_ia` |
| Gabriel | 4 | blocos-aninhados | sem_ia | `trial-gabriel-04-blocos-aninhados-sem_ia` |
| Gabriel | 5 | cofre-de-senhas | com_ia | `trial-gabriel-05-cofre-de-senhas-com_ia` |
| Gabriel | 6 | elevador-do-predio | sem_ia | `trial-gabriel-06-elevador-do-predio-sem_ia` |

Cada linha vira uma Issue individual no GitHub Projects, atribuída (Assignee)
ao integrante correspondente, conforme pedido no enunciado do LAB02.
