# Hipóteses, Variáveis e Ameaças à Validade

Este documento cobre a parte do Passo 1 (Desenho do Experimento) referente a
hipóteses (H0/H1), variáveis dependentes/independentes, tratamentos, tipo de
projeto experimental e ameaças à validade. A escolha e a justificativa das
katas ([katas/README.md](katas/README.md)) e da ordem contrabalanceada
([CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md)) estão em documentos
próprios e não são repetidas aqui. A junção de tudo num documento único de
desenho experimental é tratada à parte.

## Variável independente

Uso de assistente de IA generativa na resolução do kata, variável binária
categórica com dois níveis:

- `com_ia`: resolução com o assistente de IA habilitado.
- `sem_ia`: resolução manual, sem autocomplete nem chat de IA.

O assistente usado em todos os trials `com_ia` do grupo é o **Claude
(versão gratuita, claude.ai)**, fixado para os três integrantes para manter o
tratamento comparável dentro do experimento, conforme exigido no enunciado.

## Tratamentos

| Tratamento | Descrição |
| --- | --- |
| `com_ia` | Participante resolve o kata podendo consultar o Claude livremente (prompts, geração e revisão de código), dentro do time-box. |
| `sem_ia` | Participante resolve o kata sozinho, sem qualquer assistente de IA, dentro do time-box. |

Cada integrante passa pelos dois tratamentos (within-subject): 2 katas com
`com_ia` e 2 com `sem_ia`, em ordem contrabalanceada
(ver [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md)).

## Tipo de projeto experimental

**Crossover / within-subject contrabalanceado.** Cada um dos 3 integrantes do
grupo atua como seu próprio controle, passando pelos dois níveis da variável
independente (`com_ia` e `sem_ia`) em katas diferentes. Isso controla a
variação individual de habilidade entre pessoas, que teria peso grande demais
num desenho between-subject com apenas 3 participantes.

Dois cuidados adicionais no desenho, ambos implementados em
[CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md):

1. **Ordem dos katas** contrabalanceada entre integrantes (rotação cíclica),
   para que nenhum kata se beneficie sistematicamente de estar sempre no
   início ou no fim da sessão.
2. **Tratamento alternado a cada trial** (nunca dois trials seguidos com o
   mesmo tratamento), para não confundir fadiga/aprendizado acumulado na
   sessão com o efeito do tratamento.

## Variáveis dependentes e hipóteses por RQ

### RQ1: Tempo

- **Variável dependente primária**: tempo até passar em todos os testes de
  aceitação ("time-to-green"), em minutos. Trial que atinge o time-box de 35
  min sem sucesso é registrado como censurado em 35 min (não descartado).
- **Métrica agregada**: mediana do time-to-green por tratamento (`com_ia` vs.
  `sem_ia`), dado o N pequeno (4 trials/integrante, 12 no total) e a
  sensibilidade da média a outliers.
- **Opcional/exploratória**: nº de prompts/interações com o Claude por trial
  `com_ia`, para discussão qualitativa (não entra no teste estatístico).

**H0₁**: a mediana do time-to-green não difere entre os tratamentos `com_ia`
e `sem_ia`.
**H1₁**: a mediana do time-to-green é diferente (menor ou maior) entre os
tratamentos `com_ia` e `sem_ia`.

### RQ2: Defeitos

- **Variáveis dependentes**:
  - Taxa de sucesso: % de testes de aceitação passando ao final do time-box
    (métrica primária, normaliza katas com números diferentes de testes).
  - Nº absoluto de testes falhando ao final do tempo (métrica complementar).
- **Opcional**: densidade de defeitos (testes falhando / KLOC), caso se queira
  comparar katas de tamanhos diferentes, não obrigatória aqui, já que os 4
  katas foram calibrados para complexidade comparável
  (ver [katas/README.md](katas/README.md)).

**H0₂**: a mediana da taxa de sucesso dos testes de aceitação não difere
entre `com_ia` e `sem_ia`.
**H1₂**: a mediana da taxa de sucesso dos testes de aceitação é diferente
entre `com_ia` e `sem_ia`.

### RQ3: Estrutura do código

- **Variáveis dependentes**:
  - Complexidade ciclomática média (McCabe) por método, via CK (métrica
    WMC/complexity), sobre o código Java produzido.
  - Duplicação de código: % de linhas duplicadas via PMD CPD.
  - LOC (linhas de código) como métrica de controle, obrigatória junto das
    duas acima, para não deixar verbosidade do código gerado por IA
    disfarçar de complexidade/duplicação real.
- **Opcional (aprofundamento)**: Índice de Manutenibilidade, se o grupo
  decidir usar uma ferramenta que o calcule para Java; não obrigatório com
  CK/PMD.

**H0₃**: a mediana da complexidade ciclomática média (e/ou da % de
duplicação) não difere entre o código produzido `com_ia` e `sem_ia`.
**H1₃**: a mediana da complexidade ciclomática média (e/ou da % de
duplicação) é diferente entre o código produzido `com_ia` e `sem_ia`.

## Quantidade de medições

3 integrantes × 4 trials cada = **12 trials no total**, 6 `com_ia` e 6
`sem_ia` (2 de cada tratamento por integrante). Amostra pequena, consistente
com a recomendação do enunciado de usar mediana/IQR nas estatísticas
descritivas e teste de Wilcoxon (pareado, não paramétrico) na análise
inferencial, dado o desenho within-subject.

## Ameaças à validade

| Ameaça | Risco | Mitigação adotada |
| --- | --- | --- |
| Efeito de aprendizado entre katas | Um kata resolvido mais tarde na sessão se beneficiaria do "aquecimento", misturando esse efeito com o do tratamento. | Ordem dos katas contrabalanceada por integrante (rotação cíclica), ver [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md). |
| Kata confundido com tratamento | Se um kata fosse sempre feito com IA por todos, um resultado melhor nele não distinguiria "efeito da IA" de "kata mais fácil". | Cada kata é feito com os dois tratamentos, por integrantes diferentes (nunca 3x0 num único tratamento), ver tabela de conferência em [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md). |
| Fadiga/aprendizado confundido com tratamento | Fazer os 2 trials com IA em bloco (e só depois os 2 sem IA) misturaria cansaço/aprendizado acumulado da sessão com o efeito do tratamento. | Tratamento alternado a cada trial (nunca dois trials seguidos com o mesmo tratamento). |
| Familiaridade prévia com a ferramenta de IA | Integrantes com mais experiência prévia com o Claude tendem a extrair mais proveito dele, inflando o efeito do tratamento por habilidade individual com a ferramenta, não pelo tratamento em si. | Não há controle experimental para isso (N=3 não permite estratificar); registrado como limitação a ser discutida no Relatório Final, junto do nível de experiência prévia de cada integrante com o Claude. |
| Vazamento de solução já vista/memorização | Se os katas fossem exercícios clássicos (LeetCode/HackerRank), o Claude poderia reproduzir uma solução vista em treinamento em vez de efetivamente ajudar, inflando artificialmente o ganho `com_ia`. | Katas autorais do grupo, de baixa indexação, ver [katas/README.md](katas/README.md). |
| Dificuldade desigual entre katas | Mesmo calibrados para ficar perto do teto do time-box manualmente, diferenças residuais de dificuldade entre os 4 katas podem se misturar ao efeito do tratamento em comparações que não sejam corretamente pareadas por integrante/posição. | Mitigado pelo desenho crossover (cada integrante passa pelos dois tratamentos) e pela conferência de que cada kata aparece nos dois tratamentos; discutido como limitação residual no Relatório Final. |
| Censura no time-box | Um trial que não termina em 35 min é um dado incompleto, não um "tempo real" de conclusão; tratá-lo como dado comum distorceria a mediana. | Registrado como censurado em exatamente 35 min (não descartado), sinalizado no `results/time_results.csv` pelo status (`sucesso`/`censurado`/`abortado`) gerado por `scripts/time_trial.sh`. |
| Ambiente/hardware entre integrantes | Máquinas, IDEs ou latência de rede diferentes entre integrantes podem afetar o tempo de forma alheia ao tratamento. | Não controlado experimentalmente (fora do escopo do grupo padronizar hardware); registrado como limitação. |
