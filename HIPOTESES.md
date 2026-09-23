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

Cada integrante passa pelos dois tratamentos (within-subject): 3 katas com
`com_ia` e 3 com `sem_ia`, em ordem contrabalanceada
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
  `sem_ia`), dado o N pequeno (6 trials/integrante, 18 no total) e a
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
  comparar katas de tamanhos diferentes, não obrigatória aqui, já que os
  katas 1-4 foram calibrados para complexidade comparável entre si (os katas
  5-6, de dificuldade intencionalmente maior, são a exceção declarada, ver
  [katas/README.md](katas/README.md)).

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

### Tamanho de efeito (complementa o p-valor de RQ1 e RQ3)

Com N pequeno (18 trials), um p-valor "não significativo" pode só significar
"não deu pra detectar", não "não tem efeito", por isso RQ1 e RQ3 passaram a
ter, além do p-valor, uma medida do tamanho da diferença
([scripts/tamanho_efeito_rq1_rq3.sh](scripts/tamanho_efeito_rq1_rq3.sh)).
As duas medidas usadas não são cálculos independentes, são conversões
diretas das estatísticas de teste já calculadas:

- **r rank-biserial**, a partir do `W+` do Wilcoxon signed-rank pareado por
  kata (6 pares, médias `com_ia`/`sem_ia` por kata, mesmo pareamento do
  teste de estilo em [scripts/normalizacao_estilo_loc.py](scripts/normalizacao_estilo_loc.py),
  já que não existe par literal "mesmo integrante, mesmo kata, dois
  tratamentos" no desenho, ver [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md)).
- **Cliff's delta**, a partir do `U` do Mann-Whitney não pareado (9 `com_ia`
  vs 9 `sem_ia`, ao nível de trial).
- Classificação de magnitude (negligível/pequeno/médio/grande) pelos limiares
  de Romano et al. (2006)/Vargha & Delaney (2000), válida para as duas
  medidas (mesma escala [-1, 1]).

**Resultado real, rodando sobre os 18 trials coletados**
(`results/tamanho_efeito_rq1_rq3.csv`):

| Métrica | Mediana com_ia \| sem_ia | Mann-Whitney p | Cliff's delta |
| --- | --- | --- | --- |
| RQ1: tempo (seg) | 206.5 \| 861.9 | **0.001** | **-0.85 (grande)** |
| RQ3: complexidade ciclomática média | 8.33 \| 9.0 | 0.377 | -0.25 (pequeno) |
| RQ3: duplicação (%) | 0.0 \| 0.0 | 1.000 | 0.0 (negligível) |

RQ1 (tempo) tem um efeito grande e estatisticamente significativo mesmo com
N pequeno: os trials `com_ia` foram consistentemente mais rápidos, não só
"não contraditados pelos dados". RQ3 (complexidade) tem um efeito pequeno,
não significativo, os dados não sustentam diferença de complexidade entre
os tratamentos. A duplicação saiu com **0% em todos os 18 trials** (nenhum
bloco duplicado detectado pelo PMD CPD em nenhum trial), então o teste é
degenerado por falta de variância (mesma situação da varredura de segurança
logo abaixo), o Wilcoxon fica `n/a` (sem diferenças não nulas para
rankear) e o Cliff's delta sai 0/negligível, refletindo a ausência real de
duplicação, não uma falha do teste.

**Ressalva sobre N pequeno**: com 6 pares (Wilcoxon) ou 9 vs 9
(Mann-Whitney), o valor de r/delta tem variância amostral alta, uma
classificação "grande" aqui (caso de RQ1) é indicativa da direção e da
magnitude observada nesta amostra, não uma conclusão populacional forte.
Isso deve ser dito explicitamente ao lado do resultado no Relatório Final,
não só a categoria de magnitude sozinha.

A mesma dupla de medidas (r rank-biserial + Cliff's delta, com
classificação) também foi adicionada ao teste de estilo que já existia em
`scripts/normalizacao_estilo_loc.py` (colunas `wilcoxon_kata_r` e
`cliffs_delta` em `results/lint_normalizado_comparacao.csv`), pela mesma
razão.

### Exploratória: conformidade de estilo (sem H0/H1 formal)

A análise de conformidade com o style guide
([scripts/lint_trials.sh](scripts/lint_trials.sh), PMD `codestyle`, e
[scripts/normalizacao_estilo_loc.sh](scripts/normalizacao_estilo_loc.sh) para
a comparação `com_ia` vs `sem_ia`) não é a RQ3 formal (que usa complexidade
ciclomática e duplicação, ver acima), é uma métrica complementar, sobre
quão bem o código segue convenções de estilo, calculada sobre o mesmo
`src/` final de cada trial.

**Resultado real, rodando sobre os 18 trials coletados**
(`results/lint_normalizado_comparacao.csv`):

| Métrica | Mediana com_ia \| sem_ia | Wilcoxon por kata (r) | Mann-Whitney (delta) |
| --- | --- | --- | --- |
| LOC (verbosidade) | 41 \| 31 | **r = -0,87 (grande)**, p=0,125, n=5 | delta = +0,15 (pequeno), p=0,624 |
| Violações brutas | 10 \| 8 | r = -0,14 (negligível), p=0,844, n=6 | delta = +0,25 (pequeno), p=0,397 |
| Violações por 100 LOC | 27,3 \| 22,6 | r = +0,33 (médio), p=0,562, n=6 | delta = +0,02 (negligível), p=0,950 |

**Achado que precisa de leitura cuidadosa, não só a tabela**: para LOC, o
Wilcoxon pareado por kata (r=-0,87, grande) e o Mann-Whitney não pareado
(delta=+0,15, pequeno) **discordam de sinal**. Isso não é inconsistência dos
testes, é o **tamanho do kata confundindo a comparação bruta**: os 6 katas
têm LOC inerentemente muito diferente entre si (ex.: Cofre de Senhas tende a
gerar bem mais código que Elevador do Prédio, independente do tratamento), e
o contrabalanceamento não distribui os tratamentos igualmente por kata. O
Mann-Whitney, ao juntar os 18 trials sem separar por kata, mistura "efeito
do tratamento" com "que kata calhou de cair em qual tratamento". O Wilcoxon
pareado por kata controla isso (compara `com_ia` com `sem_ia` dentro do
mesmo kata) e é a leitura mais confiável aqui: **dentro do mesmo kata,
`sem_ia` tende a produzir mais LOC que `com_ia`** (4 dos 5 katas com
diferença não nula favorecem `sem_ia`, apesar de p=0,125 não cruzar o
0,05, outra vez, N=5 pares é pequeno demais para conclusão forte, só
indicativo). Nenhuma das duas leituras é "a errada", o ponto é que quem ler
o Relatório Final precisa saber que a comparação bruta de LOC está
confundida pelo kata, e priorizar a versão pareada.

Para violações (brutas e por 100 LOC), as duas leituras concordam em
magnitude pequena/negligível, não há evidência de diferença real de
conformidade de estilo entre `com_ia` e `sem_ia` nesses 18 trials.

**Correlação tempo × violações** ([scripts/correlacao_tempo_violacoes.sh](scripts/correlacao_tempo_violacoes.sh),
Spearman exato, H1 unilateral "trial mais rápido tem mais violações",
`results/correlacao_tempo_violacoes.csv`): a única correlação que cruza
significância unilateral (0,05) é em `com_ia`, análise C (tempo e violações
relativos à média do próprio kata): **rho=-0,594, p(rho<0)=0,049**, nos
trials com IA, terminar mais rápido que a média do kata está associado a
mais violações de estilo que a média do kata. Em `sem_ia`, a mesma análise
dá rho=0,000 (nenhuma relação). As demais análises (A: tempo x violações
brutas; B: tempo x violações por KLOC) não são significativas em nenhum dos
dois tratamentos. Isto é: há um indício (não uma prova, N=9 por tratamento)
de que ir mais rápido com IA tem um custo de conformidade que não aparece na
resolução manual, coerente com um trade-off velocidade/qualidade específico
do uso de IA, mas seria preciso mais dados para confirmar.

**Ressalva sobre N pequeno**: os mesmos limites de RQ1/RQ3 valem aqui, 5-6
pares no Wilcoxon, 9 vs 9 no Mann-Whitney e Spearman. Nenhum desses
resultados deve ser lido como conclusivo isoladamente; são indícios que o
Relatório Final deve reportar com essa ressalva ao lado.

### Exploratória: segurança do código (sem H0/H1 formal)

A issue de "varredura de vulnerabilidades" ([scripts/security_scan.sh](scripts/security_scan.sh),
Semgrep com o ruleset `p/java`, ver [SETUP.md](SETUP.md#7-analises-pos-hoc-estilo-e-seguranca))
foi rodada sobre os 18 trials coletados. **Resultado: 0 achados em todos os 18
trials**, tanto `com_ia` quanto `sem_ia`.

Antes de aceitar esse resultado, a ferramenta foi validada contra um arquivo
Java sintético com vulnerabilidades propositais (uso de MD5, SQL montado por
concatenação, senha hardcoded, deserialização insegura): o Semgrep detectou
corretamente 2 dos 4 problemas plantados (`use-of-md5` e
`formatted-sql-string`), confirmando que a varredura funciona e que o "0" nos
trials reais reflete o código, não uma falha silenciosa da ferramenta ou do
script.

Essa análise não foi formalizada como uma RQ4 com H0/H1. Os 6 katas do
experimento são métodos estáticos puros sobre `String`/array/`Map`/pilha,
sem I/O, SQL, criptografia ou desserialização, ou seja, sem nenhuma
superfície de ataque que um scanner estático de Java tipicamente cobre.
Com **0 em todas as 18 observações** (`com_ia` e `sem_ia` idênticos e
constantes), não havia variância para nenhum teste estatístico (Wilcoxon
incluso) detectar: uma hipótese formal aqui nasceria como uma H0 impossível
de rejeitar pelo próprio desenho dos katas, não por uma conclusão real sobre
o assistente de IA.

O achado deve ser registrado no Relatório Final como qualitativo/negativo:
ferramenta rodada e validada, zero vulnerabilidades estáticas detectadas em
qualquer trial, consistente com o escopo dos katas. Como trabalho futuro,
fica a sugestão de aumentar a complexidade dos katas (incluindo I/O, SQL ou
criptografia) num próximo experimento, para gerar superfície de ataque real
e permitir detectar uma eventual diferença entre `com_ia` e `sem_ia` nessa
dimensão.

## Quantidade de medições

3 integrantes × 6 trials cada = **18 trials no total**, 9 `com_ia` e 9
`sem_ia` (3 de cada tratamento por integrante). Amostra pequena, consistente
com a recomendação do enunciado de usar mediana/IQR nas estatísticas
descritivas e teste de Wilcoxon (pareado, não paramétrico) na análise
inferencial, dado o desenho within-subject.

## Identificação e tratamento de outliers

Revisão do dataset consolidado dos 18 trials
([scripts/outliers.sh](scripts/outliers.sh)), em duas frentes:

**1. Checagem categórica** (não é por cerca estatística, é sim/não): nenhum
dos 18 trials tem `status` diferente de `sucesso` ou algum teste falhando ao
final do time-box. Ou seja, o exemplo citado no enunciado desta análise
("censura por bug no ambiente, não pelo tempo") **não tem nenhuma linha
correspondente no dataset consolidado como ele está hoje** — não há trial
censurado, abortado ou com defeito registrado entre os 18.

Isso não significa que nenhum incidente aconteceu durante a coleta: o trial
`trial-felipe-01-elevador-do-predio-sem_ia` teve um travamento real de
ambiente (processo Java do JUnit preso a 100% de CPU por ~13 min dentro do
container Docker, sem progresso). O trial foi abortado e reiniciado do zero
antes de qualquer linha ser gravada, então a linha commitada (1414,8s,
`sucesso`) já é da segunda tentativa, sem contaminação de tempo — e mesmo
assim não cruza nenhuma cerca estatística abaixo. Registrado aqui por
transparência, não como um outlier a decidir.

**2. Cercas de Tukey** (1,5×IQR moderado, 3×IQR extremo), calculadas sobre
os 18 valores de cada métrica (`tempo_seg`, `loc_total`, `cc_media`,
`duplicacao_pct`, `violacoes_por_100loc`) — pool do conjunto inteiro, não
separado por tratamento ou por kata, já que n=9 (por tratamento) ou n=2-3
(por kata) é pequeno demais para um quartil confiável; a leitura de contexto
de cada ponto sinalizado vem a seguir, em prosa.

**Resultado real** (`results/outliers.csv`, 90 linhas = 18 trials × 5
métricas): só `loc_total` tem pontos fora da cerca, e são dois, os dois do
mesmo kata:

| Trial | Kata | Tratamento | LOC | Cerca 1,5x | Cerca 3x | Classificação |
| --- | --- | --- | --- | --- | --- | --- |
| `trial-arthur-01-cofre-de-senhas-sem_ia` | Cofre de Senhas | `sem_ia` | 118 | [4,75, 66,75] | [-18,5, 90,0] | **outlier extremo** |
| `trial-gabriel-05-cofre-de-senhas-com_ia` | Cofre de Senhas | `com_ia` | 79 | [4,75, 66,75] | [-18,5, 90,0] | outlier moderado |

`tempo_seg`, `cc_media`, `duplicacao_pct` e `violacoes_por_100loc` não têm
nenhum ponto fora da cerca 1,5x em nenhum dos 18 trials — em particular,
`tempo_seg` varia ~60x entre o trial mais rápido (25,3s) e o mais lento
(1506,6s) sem cruzar a cerca superior (~1728s): essa variação é o próprio
efeito grande de RQ1 já documentado acima, não uma anomalia.

**Decisão: manter os dois, sem exclusão.** Dos 3 trials do kata Cofre de
Senhas, 2 de 3 são outliers de LOC relativos aos outros 15 trials (o
terceiro, `trial-felipe-06-cofre-de-senhas-com_ia`, tem LOC=65, dentro da
cerca) — isso aponta para o próprio kata como causa, não para os dois
trials individualmente: Cofre de Senhas é o único kata com 2 métodos
(`classify` e `rank`, ver [katas/README.md](katas/README.md)) e portanto
inerentemente maior que os outros 5. Não há indício de dado corrompido ou
falha de ambiente nesses dois trials — são o sinal esperado de "kata maior
gera mais código", não um artefato de coleta.

**Política adotada**: um outlier estatístico não é excluído por padrão.
Só seria candidato a exclusão havendo evidência concreta de dado corrompido
por falha de ambiente/infraestrutura, o que não é o caso de nenhum dos 18
trials hoje (o único incidente de ambiente real, descrito acima, não deixou
esse tipo de rastro no dado final). Isso não muda a política já adotada
para censura no time-box (nunca descartada, ver RQ1 e a tabela abaixo) —
é uma categoria adicional e complementar, não uma substituição dela.

## Ameaças à validade

| Ameaça | Risco | Mitigação adotada |
| --- | --- | --- |
| Efeito de aprendizado entre katas | Um kata resolvido mais tarde na sessão se beneficiaria do "aquecimento", misturando esse efeito com o do tratamento. | Ordem dos katas contrabalanceada por integrante (rotação cíclica), ver [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md). |
| Kata confundido com tratamento | Se um kata fosse sempre feito com IA por todos, um resultado melhor nele não distinguiria "efeito da IA" de "kata mais fácil". | Cada kata é feito com os dois tratamentos, por integrantes diferentes (nunca 3x0 num único tratamento), ver tabela de conferência em [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md). |
| Fadiga/aprendizado confundido com tratamento | Fazer os 2 trials com IA em bloco (e só depois os 2 sem IA) misturaria cansaço/aprendizado acumulado da sessão com o efeito do tratamento. | Tratamento alternado a cada trial (nunca dois trials seguidos com o mesmo tratamento). |
| Familiaridade prévia com a ferramenta de IA | Integrantes com mais experiência prévia com o Claude tendem a extrair mais proveito dele, inflando o efeito do tratamento por habilidade individual com a ferramenta, não pelo tratamento em si. | Não há controle experimental para isso (N=3 não permite estratificar); registrado como limitação a ser discutida no Relatório Final, junto do nível de experiência prévia de cada integrante com o Claude. |
| Vazamento de solução já vista/memorização | Se os katas fossem exercícios clássicos (LeetCode/HackerRank), o Claude poderia reproduzir uma solução vista em treinamento em vez de efetivamente ajudar, inflando artificialmente o ganho `com_ia`. | Katas autorais do grupo, de baixa indexação, ver [katas/README.md](katas/README.md). |
| Dificuldade desigual entre katas | Mesmo calibrados para ficar perto do teto do time-box manualmente, diferenças residuais de dificuldade entre os katas podem se misturar ao efeito do tratamento em comparações que não sejam corretamente pareadas por integrante/posição. Os katas 5-6 são deliberadamente mais difíceis que os 1-4 (ver [katas/README.md](katas/README.md)), o que aumenta esse risco se comparado ponto a ponto entre katas em vez de pareado por integrante/posição. | Mitigado pelo desenho crossover (cada integrante passa pelos dois tratamentos) e pela conferência de que cada kata aparece nos dois tratamentos; discutido como limitação residual no Relatório Final. |
| Censura no time-box | Um trial que não termina em 35 min é um dado incompleto, não um "tempo real" de conclusão; tratá-lo como dado comum distorceria a mediana. | Registrado como censurado em exatamente 35 min (não descartado), sinalizado no `results/time_results.csv` pelo status (`sucesso`/`censurado`/`abortado`) gerado por `scripts/time_trial.sh`. |
| Ambiente/hardware entre integrantes | Máquinas, IDEs ou latência de rede diferentes entre integrantes podem afetar o tempo de forma alheia ao tratamento. | Não controlado experimentalmente (fora do escopo do grupo padronizar hardware); registrado como limitação. |
| Outliers/anomalias no dataset | Um trial discrepante (por bug de coleta, falha de ambiente, ou apenas variação real grande) poderia distorcer mediana/IQR se não fosse revisado. | Revisão sistemática via `scripts/outliers.sh` (cercas de Tukey 1,5x/3x IQR + checagem categórica de status/defeitos) sobre os 18 trials; ver seção "Identificação e tratamento de outliers" acima para o resultado e a decisão de manter todos. |
