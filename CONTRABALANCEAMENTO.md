# Ordem contrabalanceada por integrante

Matriz de contrabalanceamento do experimento: define, para cada
integrante, em que ordem e com qual tratamento (`com_ia`/`sem_ia`) cada um dos
4 katas de [katas/](katas/) e resolvido. Cada integrante resolve os 4 katas,
2 com IA e 2 sem IA, conforme o enunciado do LAB02.

## O que o contrabalanceamento evita

1. **Aprendizado/ordem entre katas**: se todo mundo resolvesse os katas na
   mesma sequencia, o kata que cai por ultimo sempre se beneficiaria do
   "aquecimento" da sessao, e isso seria indistinguivel de uma diferenca real
   de dificuldade entre katas.
2. **Kata confundido com tratamento**: se um kata especifico fosse sempre
   resolvido com IA (por todos os integrantes), um resultado melhor nesse kata
   nao permitiria separar "efeito da IA" de "esse kata era mais facil".
3. **Fadiga/aprendizado confundido com tratamento**: se um integrante fizesse
   os 2 trials com IA em bloco e só depois os 2 sem IA (ou vice-versa), o
   cansaço/aprendizado acumulado na sessão ficaria misturado com o efeito do
   tratamento. Por isso o tratamento alterna a cada trial, nunca em bloco.

## Metodo

* **Ordem dos katas**: quadrado latino 4x4 (linhas = integrante, colunas =
  posicao 1a-4a), usando 3 das 4 linhas, uma rotacao ciclica por integrante
  (Arthur K1K2K3K4, Felipe K2K3K4K1, Gabriel K3K4K1K2). Nenhum integrante
  repete a sequencia de outro, e cada kata cai em 3 das 4 posicoes possiveis
  entre os 3 integrantes (so nao cobre a 4a linha do quadrado, que ficaria
  ociosa com apenas 3 integrantes).
* **Tratamento por posicao**: um padrao alternado de periodo 2 (nunca dois
  trials seguidos com o mesmo tratamento). Arthur e Felipe usam a fase
  "sem_ia, com_ia, sem_ia, com_ia" (na ordem de cada um); Gabriel usa a fase
  invertida "com_ia, sem_ia, com_ia, sem_ia". Isso garante que cada kata seja
  feito com os dois tratamentos por integrantes diferentes (nunca 3x0) e que
  nem todo mundo comece a sessao com o mesmo tratamento.

Limitação assumida: com 3 integrantes e 2 fases de tratamento possíveis, a
divisão de quem começa com IA vs. manual fica 2-para-1 (Felipe e Gabriel
começam com `com_ia`, Arthur com `sem_ia`); não há como equilibrar 50/50 com
N ímpar. Fica registrado aqui como ameaça à validade menor do desenho.

## Matriz (por integrante)

| Integrante | 1º trial | 2º trial | 3º trial | 4º trial |
| --- | --- | --- | --- | --- |
| Arthur | Cofre de Senhas (`sem_ia`) | Elevador do Prédio (`com_ia`) | Etiquetas de Preço (`sem_ia`) | Fila do Caixa (`com_ia`) |
| Felipe | Elevador do Prédio (`com_ia`) | Etiquetas de Preço (`sem_ia`) | Fila do Caixa (`com_ia`) | Cofre de Senhas (`sem_ia`) |
| Gabriel | Etiquetas de Preço (`com_ia`) | Fila do Caixa (`sem_ia`) | Cofre de Senhas (`com_ia`) | Elevador do Prédio (`sem_ia`) |

## Conferência por kata

| Kata | Feito com IA por | Feito sem IA por |
| --- | --- | --- |
| Cofre de Senhas | Gabriel | Arthur, Felipe |
| Elevador do Prédio | Arthur, Felipe | Gabriel |
| Etiquetas de Preço | Gabriel | Arthur, Felipe |
| Fila do Caixa | Arthur, Felipe | Gabriel |

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
| Felipe | 1 | elevador-do-predio | com_ia | `trial-felipe-01-elevador-do-predio-com_ia` |
| Felipe | 2 | etiquetas-de-preco | sem_ia | `trial-felipe-02-etiquetas-de-preco-sem_ia` |
| Felipe | 3 | fila-do-caixa | com_ia | `trial-felipe-03-fila-do-caixa-com_ia` |
| Felipe | 4 | cofre-de-senhas | sem_ia | `trial-felipe-04-cofre-de-senhas-sem_ia` |
| Gabriel | 1 | etiquetas-de-preco | com_ia | `trial-gabriel-01-etiquetas-de-preco-com_ia` |
| Gabriel | 2 | fila-do-caixa | sem_ia | `trial-gabriel-02-fila-do-caixa-sem_ia` |
| Gabriel | 3 | cofre-de-senhas | com_ia | `trial-gabriel-03-cofre-de-senhas-com_ia` |
| Gabriel | 4 | elevador-do-predio | sem_ia | `trial-gabriel-04-elevador-do-predio-sem_ia` |

Cada linha vira uma Issue individual no GitHub Projects, atribuída (Assignee)
ao integrante correspondente, conforme pedido no enunciado do LAB02.
