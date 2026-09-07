# Lab02 Assistentes de IA vs. Codificacao Manual

Experimento controlado comparando o uso de assistente de IA com a codificacao
manual na resolucao de katas de programacao. As medidas sao tempo (RQ1),
defeitos (RQ2) e complexidade e duplicacao de codigo (RQ3).

Os katas sao resolvidos em Java. As metricas estaticas sao coletadas com o CK e
o PMD CPD. O tempo de resolucao (time-to-green) e os testes de aceitacao
(JUnit) sao coletados com `scripts/time_trial.sh`.

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

Os 4 katas usados no experimento (autorais, de baixa indexacao, para reduzir o
risco de memorizacao pela IA) estao em [katas/](katas/). Sao 2 katas com IA e
2 sem IA por integrante, escolhidos para manter o tempo total de execucao
(ate 4 trials de 35 min, ~2h20) viavel numa sessao so. Antes de iniciar
qualquer trial, rode o script de verificacao para confirmar que os testes de
aceitacao de cada kata estao corretos:

```
scripts/verify_katas.sh
```

Ele compila a solucao de referencia de cada kata com os testes JUnit 5 e roda
tudo, usando o JDK local ou, se nao houver, um container Docker automatico.
Ver [katas/README.md](katas/README.md) para a lista de katas e a estrutura de
pastas.

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

### Problemas comuns

1. `cat: results/metrics_results.csv: No such file or directory`, o `run_trial.sh`
   nao chegou a rodar ou falhou, rode de novo e leia a saida.
2. `Cannot connect to the Docker daemon`, o Docker Desktop nao esta aberto.
3. `permission denied: scripts/run_trial.sh`, rode `chmod +x scripts/run_trial.sh`.
4. `trials/<id>/src nao existe`, o `<trial-id>` passado nao bate com a pasta em
   `trials/`.

## Estrutura

```
docker/Dockerfile          imagem com JDK 17, Python 3, CK, PMD e JUnit console
scripts/run_trial.sh       compila o trial e roda a coleta de metricas estaticas
scripts/collect_metrics.py script de coleta (RQ3) chamado dentro do container
scripts/time_trial.sh      inicia a cronometragem do time-to-green (RQ1/RQ2)
scripts/time_trial.py      script de cronometragem chamado dentro do container
scripts/verify_katas.sh    roda os testes de aceitacao de cada kata isoladamente
katas/<kata>/              enunciado, solucao de referencia e testes de cada kata
trials/<trial-id>/src      arquivos .java finais de cada trial (RQ3)
trials/<trial-id>/test     testes de aceitacao (JUnit) do kata (RQ1/RQ2)
results/metrics_results.csv saida acumulada da coleta de metricas estaticas
results/time_results.csv    saida acumulada da cronometragem
SETUP.md                   guia detalhado, inclui a alternativa sem Docker
```
