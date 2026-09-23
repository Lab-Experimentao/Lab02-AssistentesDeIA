# Lab02 Assistentes de IA vs. Codificacao Manual

Experimento controlado comparando o uso de assistente de IA com a codificacao
manual na resolucao de katas de programacao. As medidas sao tempo (RQ1),
defeitos (RQ2) e complexidade e duplicacao de codigo (RQ3).

Os katas sao resolvidos em Java. As metricas estaticas sao coletadas com o CK e
o PMD CPD. O tempo de resolucao (time-to-green) e os testes de aceitacao
(JUnit) sao coletados com `scripts/time_trial.sh`.

Desenho completo do experimento (GQM, hipoteses, variaveis, tratamentos, tipo
de projeto e ameacas a validade) em [DESENHO_EXPERIMENTO.md](DESENHO_EXPERIMENTO.md),
com o detalhamento de hipoteses e ameacas em [HIPOTESES.md](HIPOTESES.md).

## Assistente de IA do experimento

O assistente de IA unico para todos os trials do tratamento `com_ia` e o Claude,
usado pela interface Claude Code (CLI no terminal). A escolha vale para todos os
integrantes e todos os katas, para manter o tratamento `com_ia` uniforme entre
os trials.

* Interface: Claude Code, a mesma ferramenta de linha de comando para todos. Nao
  vale usar o claude.ai no navegador nem a extensao de IDE, para nao misturar
  formas de interacao.
* Modelo: o modelo padrao vigente do Claude Code na data do trial, sem fixar
  versao. Cada integrante anota no registro do trial qual modelo estava ativo (o
  Claude Code mostra o id do modelo em uso).
* Conta: cada integrante usa a propria assinatura do Claude.

Nos trials do tratamento `sem_ia`, nenhum assistente de IA e permitido, nem o
Claude, nem autocompletar baseado em modelo de linguagem (Copilot e similares).
Vale apenas consulta a documentacao oficial da linguagem e das bibliotecas.

## Cronometragem do time-to-green (RQ1) e defeitos (RQ2)

A forma padrao de cronometrar um trial e pelo Docker. O guia completo esta em
[SETUP.md](SETUP.md).

```
scripts/time_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [timebox-min]
```

Rodar o comando ja marca o inicio do trial: o script compila e roda os testes
de aceitacao do kata em loop, ao vivo, ate o codigo passar em todos eles
(status `sucesso`) ou o time-box (35 min, so pode ser reduzido) se esgotar sem
sucesso (status `censurado`, registrado como exatamente o time-box). Ctrl+C
encerra manualmente (status `abortado`).

Antes de iniciar, o trial precisa ter `trials/<trial-id>/test/` com os testes
de aceitacao (JUnit) do kata, alem do `trials/<trial-id>/src/` (pode comecar
vazio ou com o esqueleto do kata, editado ao vivo durante o trial).

O resultado e acrescentado em `results/time_results.csv`, com o tempo
decorrido e a contagem de testes passando/falhando ao final do tempo.

### Testar o mecanismo de cronometragem

```
scripts/time_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur 1
cat results/time_results.csv
```

Como o FizzBuzz de teste ja esta correto, o trial termina em poucos segundos
com `status: sucesso`.

## Katas do experimento

Os 6 katas usados no experimento (autorais, de baixa indexacao, para reduzir o
risco de memorizacao pela IA) estao em [katas/](katas/) -- os 4 primeiros de
dificuldade base e mais 2 (`estoque-do-deposito`, `blocos-aninhados`) de
dificuldade um pouco maior. Sao 3 katas com IA e 3 sem IA por integrante (6
trials de 35 min por integrante, ~3h30 no total). Antes de iniciar
qualquer trial, rode o script de verificacao para confirmar que os testes de
aceitacao de cada kata estao corretos:

```
scripts/verify_katas.sh
```

Ele compila a solucao de referencia de cada kata com os testes JUnit 5 e roda
tudo, usando o JDK local ou, se nao houver, um container Docker automatico.
Ver [katas/README.md](katas/README.md) para a lista de katas e a estrutura de
pastas, e [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md) para a ordem e o
tratamento (`com_ia`/`sem_ia`) de cada kata por integrante.

## Coleta de metricas estaticas

A forma padrao de rodar a coleta e pelo Docker. A unica dependencia da maquina e
o Docker. O guia completo esta em [SETUP.md](SETUP.md).

### Passo a passo para testar o ambiente

1. Instalar o Docker Desktop e deixar o app aberto. Conferir:

   ```
   docker --version
   docker info
   ```

2. Clonar o repositorio e entrar na pasta:

   ```
   git clone <url-do-repo> Lab02-AssistentesDeIA
   cd Lab02-AssistentesDeIA
   ```

3. Buildar a imagem, uma vez. Refazer so quando o `docker/Dockerfile` ou o
   `scripts/collect_metrics.py` mudarem:

   ```
   docker build -f docker/Dockerfile -t lab02-metrics .
   ```

4. Rodar o trial de teste FizzBuzz:

   ```
   scripts/run_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
   ```

   A saida termina com `Pronto. Linha acrescentada em results/metrics_results.csv.`

5. Conferir o resultado:

   ```
   cat results/metrics_results.csv
   ```

   Esperado, com a data e hora do momento:

   ```
   timestamp,trial_id,kata,treatment,integrante,loc_total,loc_classes,cc_media,metodos,linhas_duplicadas,duplicacao_pct,min_tokens
   2026-09-07T03:45:42+00:00,trial-teste-fizzbuzz,fizzbuzz,sem_ia,arthur,19,21,4.5,2,0,0.0,100
   ```

   Se apareceu uma linha com esses numeros, o ambiente esta ok.

### Rodar um trial de verdade

```
scripts/run_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [min-tokens]
```

1. Criar `trials/<trial-id>/src/` com os arquivos `.java` finais do trial.
2. Rodar o comando acima com esse `<trial-id>`.
3. O script compila, roda o CK e o PMD, e acrescenta uma linha em
   `results/metrics_results.csv`.

A pasta `bin/` e gerada pelo script. O `min-tokens` e opcional, padrao 100.

## Analises pos-hoc: estilo, seguranca e inferencia

Depois de coletar as metricas estaticas de todos (ou de um grupo) de trials,
analises agregadas rodam sobre o conjunto inteiro de uma vez (leem
`results/metrics_results.csv`/`results/time_results.csv` para saber quais
trials existem):

```
scripts/lint_trials.sh              # PMD codestyle -> results/lint_results.csv
scripts/security_scan.sh [ruleset]  # Semgrep (p/java por padrao) -> results/security_results.csv
scripts/tamanho_efeito_rq1_rq3.sh   # Wilcoxon+r / Mann-Whitney+Cliff's delta (RQ1 tempo, RQ3 cc_media/duplicacao) -> results/tamanho_efeito_rq1_rq3.csv
scripts/outliers.sh                 # cercas de Tukey (1,5x/3x IQR) sobre o dataset consolidado -> results/outliers.csv
scripts/build_dashboard.sh          # dashboard HTML (boxplots + slope charts) -> results/dashboard.html, NAO precisa de Docker
```

As quatro primeiras comparam ou revisam `com_ia` vs `sem_ia` (mediana/IQR, e algumas
tambem p-valor e tamanho de efeito) no resumo impresso ao final. Detalhes, colunas
de cada CSV e o aviso sobre reprodutibilidade do ruleset do Semgrep em
[SETUP.md](SETUP.md#7-analises-pos-hoc-estilo-e-seguranca); a justificativa
estatistica do tamanho de efeito (Cliff's delta / r rank-biserial, de onde
vem cada medida e a ressalva sobre N pequeno) em
[HIPOTESES.md](HIPOTESES.md#tamanho-de-efeito-complementa-o-p-valor-de-rq1-e-rq3).

`scripts/build_dashboard.sh` é diferente dos outros quatro: não roda testes
estatísticos novos, só reorganiza o que os outros já calcularam (boxplots +
gráfico de linha por kata, KPIs, tabela de outliers) num `results/dashboard.html`
autocontido (Apache ECharts via CDN), pronto para abrir no navegador e
exportar os gráficos (ícone de câmera no canto de cada um) para o Relatório
Final. Não precisa de Docker, só de um `python`/`python3`/`py` qualquer no
PATH.

### Problemas comuns

1. `cat: results/metrics_results.csv: No such file or directory`, o `run_trial.sh`
   nao chegou a rodar ou falhou, rode de novo e leia a saida.
2. `Cannot connect to the Docker daemon`, o Docker Desktop nao esta aberto.
3. `permission denied: scripts/run_trial.sh`, rode `chmod +x scripts/run_trial.sh`.
4. `trials/<id>/src nao existe`, o `<trial-id>` passado nao bate com a pasta em
   `trials/`.

## Estrutura

```
docker/Dockerfile          imagem com JDK 17, Python 3, CK, PMD, JUnit console e Semgrep
scripts/run_trial.sh       compila o trial e roda a coleta de metricas estaticas
scripts/collect_metrics.py script de coleta (RQ3) chamado dentro do container
scripts/time_trial.sh      inicia a cronometragem do time-to-green (RQ1/RQ2)
scripts/time_trial.py      script de cronometragem chamado dentro do container
scripts/verify_katas.sh    roda os testes de aceitacao de cada kata isoladamente
scripts/correlacao_tempo_violacoes.sh  correlacao tempo x violacoes por tratamento
scripts/normalizacao_estilo_loc.sh  violacoes de estilo por 100 LOC, com_ia vs sem_ia
scripts/lint_trials.sh     analise pos-hoc de estilo (PMD codestyle) de todos os trials coletados
scripts/security_scan.sh   analise pos-hoc de seguranca (Semgrep) de todos os trials coletados
scripts/stats_utils.py     postos/Wilcoxon/Mann-Whitney exatos e tamanho de efeito, usado pelos scripts acima
scripts/tamanho_efeito_rq1_rq3.sh  Wilcoxon+r e Mann-Whitney+Cliff's delta para RQ1 (tempo) e RQ3 (cc_media/duplicacao)
scripts/outliers.sh        identifica outliers no dataset consolidado (cercas de Tukey)
scripts/build_dashboard.sh  gera o dashboard HTML (boxplots + slope charts), sem Docker
katas/<kata>/              enunciado, solucao de referencia e testes de cada kata
trials/<trial-id>/src      arquivos .java finais de cada trial (RQ3)
trials/<trial-id>/test     testes de aceitacao (JUnit) do kata (RQ1/RQ2)
results/metrics_results.csv saida acumulada da coleta de metricas estaticas
results/time_results.csv    saida acumulada da cronometragem
results/correlacao_tempo_violacoes.csv  Spearman tempo x violacoes por tratamento
results/lint_normalizado.csv  violacoes por 100 LOC por trial
results/lint_normalizado_comparacao.csv  testes com_ia vs sem_ia (LOC, brutas, por 100 LOC)
results/lint_results.csv    saida acumulada da analise de estilo
results/security_results.csv saida acumulada da varredura de seguranca
results/tamanho_efeito_rq1_rq3.csv  Wilcoxon/Mann-Whitney + tamanho de efeito para RQ1/RQ3
results/outliers.csv        cercas de Tukey por trial/metrica, dataset consolidado
results/dashboard.html      dashboard visual (boxplots + slope charts), para o Relatorio Final
SETUP.md                   guia detalhado, inclui a alternativa sem Docker
DESENHO_EXPERIMENTO.md     GQM, hipoteses, variaveis, tratamentos e desenho do experimento
HIPOTESES.md               H0/H1, variaveis e ameacas a validade, detalhado
CONTRABALANCEAMENTO.md     ordem e tratamento de cada kata por integrante
```
