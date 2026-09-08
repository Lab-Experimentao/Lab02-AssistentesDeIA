# Ambiente e coleta de metricas do LAB02

Este guia descreve como preparar o ambiente, cronometrar o time-to-green de cada
trial e coletar as metricas estaticas do codigo Java final. As metricas alimentam
as questoes de pesquisa:

* RQ1: tempo de resolucao ate passar em todos os testes de aceitacao
  (`scripts/time_trial.sh`, secao 4).
* RQ2: defeitos, taxa de sucesso e numero de testes falhando ao final do tempo
  (tambem coletado por `scripts/time_trial.sh`, junto com o RQ1).
* RQ3: complexidade ciclomatica, duplicacao e LOC (`scripts/run_trial.sh`,
  secao 5).

A linguagem escolhida para os katas e Java. As ferramentas de metrica sao o CK,
o PMD CPD e o JUnit (via JUnit Platform Console Standalone).

A forma padrao de rodar a cronometragem e a coleta e pelo Docker (secoes 4 e 5).
A execucao local (secao 8) fica como alternativa quando nao houver Docker
disponivel.

## 1. Requisitos

Para o fluxo padrao, a unica dependencia da maquina e o Docker.

```
docker --version
docker info
```

A imagem `lab02-metrics` traz JDK 17, Python 3, o CK, o PMD e o JUnit Platform
Console Standalone ja instalados, entao nada mais precisa estar na maquina.

No Windows, use o Git Bash (os scripts sao `.sh`). Os scripts ja definem
`MSYS_NO_PATHCONV=1` para o Git Bash nao reescrever os caminhos `/trials` e
`/results` passados ao container como se fossem caminhos do Windows.

## 2. Estrutura de pastas

```
Lab02-AssistentesDeIA/
  docker/Dockerfile          imagem com JDK, Python, CK, PMD e JUnit console
  scripts/run_trial.sh       compila o trial e roda a coleta de metricas estaticas (RQ3)
  scripts/collect_metrics.py script de coleta de metricas estaticas, chamado no container
  scripts/time_trial.sh      inicia a cronometragem do time-to-green (RQ1/RQ2)
  scripts/time_trial.py      script de cronometragem, chamado dentro do container
  trials/                    um subdiretorio por trial
    <trial-id>/
      src/                   codigo de producao final do trial (usado na RQ3)
      test/                  testes de aceitacao (JUnit) do kata (usados na RQ1/RQ2)
      bin/                   .class compilados de src/ (recriados a cada coleta)
  results/                   recebe o time_results.csv e o metrics_results.csv
  tools/                     CK e PMD para uso local (fora do controle de versao)
  SETUP.md
```

### Estrutura esperada por trial

Cada trial fica em `trials/<trial-id>/` com:

* `src/`: os arquivos `.java` de producao na forma final entregue no trial.
  E sobre essa pasta que rodam o CK e o CPD (RQ3), e a pasta `bin/` (gerada
  pelo proprio fluxo de coleta, nao precisa ser criada a mao) confirma que o
  codigo compila, pre-requisito da RQ2.
* `test/`: os testes de aceitacao (JUnit) do kata, fixados antes do inicio do
  trial. Ficam fora de `src/` de proposito, para nao entrar nas metricas de
  complexidade/duplicacao da RQ3. E sobre `src/` + `test/` que roda a
  cronometragem do time-to-green (RQ1).

## 3. Preparando um kata para o experimento

Antes de rodar um trial de verdade:

1. Escreva os testes de aceitacao do kata em JUnit 5 (anotacao `@Test`) e
   coloque-os em `trials/<trial-id>/test/`.
2. Deixe `trials/<trial-id>/src/` pronto para o integrante comecar (vazio, ou
   com um esqueleto/assinatura de metodo, conforme combinado no desenho do
   experimento).
3. So depois disso rode `scripts/time_trial.sh`, ja que o comando marca o
   inicio do trial.

## 4. Cronometragem do time-to-green (RQ1) e defeitos (RQ2)

### 4.1 Build da imagem (uma vez)

Da raiz do repositorio:

```
docker build -f docker/Dockerfile -t lab02-metrics .
```

O build baixa o CK, o PMD e o JUnit console para dentro da imagem. Refazer o
build so quando o `Dockerfile`, o `scripts/collect_metrics.py` ou o
`scripts/time_trial.py` mudarem. Tanto `time_trial.sh` quanto `run_trial.sh`
fazem esse build sozinhos na primeira vez, se a imagem ainda nao existir.

### 4.2 Iniciar a cronometragem de um trial

```
scripts/time_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [timebox-min]
```

Exemplo:

```
scripts/time_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
```

Rodar o comando **ja inicia o cronometro**. O script, dentro do container:

1. Compila `trials/<trial-id>/src` + `trials/<trial-id>/test` com `javac` e
   roda os testes de aceitacao com o JUnit console, a cada poucos segundos.
2. Imprime o progresso ao vivo, por exemplo `[00:04:12 / 35:00] 3/5 passando`.
3. Encerra sozinho quando:
   * todos os testes passam antes do time-box: status `sucesso`, com o tempo
     real ate esse ponto;
   * o time-box se esgota sem sucesso: status `censurado`, registrado como
     exatamente o time-box (nao o tempo real de overrun), conforme pedido no
     enunciado do laboratorio;
   * o integrante aperta Ctrl+C: status `abortado`, com o tempo real ate a
     interrupcao. Nao faz parte do fluxo padrao, serve so para encerrar uma
     sessao com problema (ex.: ambiente travou).
4. Acrescenta uma linha em `results/time_results.csv`.

O `timebox-min` e opcional, padrao 35 (o maximo permitido pelo enunciado do
LAB02). Pode ser reduzido (o script recusa qualquer valor acima de 35). Como o
`src/` fica montado como volume, o integrante edita os arquivos normalmente na
IDE fora do container enquanto o cronometro roda.

Enquanto o trial esta rodando, o integrante resolve o kata normalmente (com ou
sem o assistente de IA, conforme o tratamento) editando `trials/<trial-id>/src`
na IDE. O script nao interfere na edicao, so observa a pasta.

### 4.3 Saida em results/time_results.csv

Cada trial acrescenta uma linha com as colunas:

```
timestamp, trial_id, kata, treatment, integrante, timebox_min, tempo_seg,
status, testes_total, testes_passando, testes_falhando, taxa_sucesso_pct
```

* `tempo_seg`: tempo decorrido ate o status final (tempo real para `sucesso`
  e `abortado`, exatamente `timebox_min * 60` para `censurado`).
* `status`: `sucesso`, `censurado` ou `abortado`.
* `testes_total` / `testes_passando` / `testes_falhando`: contagem do JUnit ao
  final do tempo (RQ2).
* `taxa_sucesso_pct`: `100 * testes_passando / testes_total`.

## 5. Coleta de metricas estaticas (RQ3), via Docker

### 5.1 Rodar um trial

```
scripts/run_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [min-tokens]
```

Exemplo:

```
scripts/run_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
```

O script faz tudo dentro do container:

1. Se a imagem `lab02-metrics` nao existir, roda o build.
2. Compila `trials/<trial-id>/src` com `javac`, saida em `trials/<trial-id>/bin`.
3. Roda o CK e o PMD CPD sobre `trials/<trial-id>/src`.
4. Acrescenta uma linha em `results/metrics_results.csv`.

As pastas `trials/` e `results/` sao montadas como volumes, entao o CSV persiste
no host e o container nao depende de nada instalado na maquina.

O parametro `min-tokens` e opcional, padrao 100. Ele define o minimo de tokens
para o CPD marcar um bloco como duplicado.

### 5.2 Rodar sem o script auxiliar

O `run_trial.sh` e um atalho. O mesmo pode ser feito com dois `docker run`.

Compilar o trial:

```
docker run --rm \
  -v "$PWD/trials:/trials" \
  --entrypoint bash \
  lab02-metrics -c \
  'mkdir -p /trials/t01/bin && find /trials/t01/bin -name "*.class" -delete && javac -d /trials/t01/bin $(find /trials/t01/src -name "*.java")'
```

Coletar as metricas:

```
docker run --rm \
  -v "$PWD/trials:/trials" \
  -v "$PWD/results:/results" \
  lab02-metrics \
  --trial-id t01 \
  --kata fizzbuzz \
  --treatment sem_ia \
  --integrante arthur \
  --src /trials/t01/src \
  --bin /trials/t01/bin
```

O `ENTRYPOINT` da imagem ja chama `python3 /opt/collect_metrics.py`, e as
variaveis `CK_JAR`, `PMD_BIN` e `METRICS_OUTPUT` ja vem definidas, entao o
`docker run` da coleta so passa os argumentos de negocio do trial.

Para rodar a cronometragem (`time_trial.py`) sem o `time_trial.sh`, troque o
entrypoint:

```
docker run --rm -it \
  -v "$PWD/trials:/trials" \
  -v "$PWD/results:/results" \
  --entrypoint python3 \
  lab02-metrics /opt/time_trial.py \
  --trial-id t01 \
  --kata fizzbuzz \
  --treatment sem_ia \
  --integrante arthur \
  --src /trials/t01/src \
  --test /trials/t01/test \
  --timebox-min 35
```

### 5.3 Saida em results/metrics_results.csv

Cada execucao acrescenta uma linha com as colunas:

```
timestamp, trial_id, kata, treatment, integrante,
loc_total, loc_classes, cc_media, metodos,
linhas_duplicadas, duplicacao_pct, min_tokens
```

* `loc_total`: soma de `loc` por metodo (method.csv do CK).
* `loc_classes`: soma de `loc` por classe (class.csv do CK).
* `cc_media`: media de `wmc` entre os metodos.
* `metodos`: quantidade de metodos analisados.
* `linhas_duplicadas`: soma do atributo `lines` dos blocos `duplication` do CPD.
* `duplicacao_pct`: `100 * linhas_duplicadas / loc_total`.

## 6. Trial de validacao

O repositorio traz `trials/trial-teste-fizzbuzz/` com um kata FizzBuzz simples e
seus testes de aceitacao em `test/FizzBuzzTest.java`, usado so para validar o
pipeline ponta a ponta. Ele nao faz parte dos dados do experimento.

Cronometragem (RQ1/RQ2), termina em poucos segundos porque o FizzBuzz de teste
ja esta correto:

```
scripts/time_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur 1
cat results/time_results.csv
```

Esperado, com a data e hora do momento e `status: sucesso`:

```
timestamp,trial_id,kata,treatment,integrante,timebox_min,tempo_seg,status,testes_total,testes_passando,testes_falhando,taxa_sucesso_pct
2026-09-07T18:20:14+00:00,trial-teste-fizzbuzz,fizzbuzz,sem_ia,arthur,1.0,0.8,sucesso,4,4,0,100.0
```

Metricas estaticas (RQ3):

```
scripts/run_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
cat results/metrics_results.csv
```

## 7. Problemas comuns

1. `cat: results/time_results.csv: No such file or directory` ou o mesmo para
   `metrics_results.csv`: o script correspondente nao chegou a rodar ou
   falhou, rode de novo e leia a saida.
2. `Cannot connect to the Docker daemon`: o Docker Desktop nao esta aberto.
3. `permission denied: scripts/time_trial.sh` (ou `run_trial.sh`): rode
   `chmod +x scripts/time_trial.sh scripts/run_trial.sh`.
4. `trials/<id>/src nao existe` ou `trials/<id>/test nao existe`: o
   `<trial-id>` passado nao bate com a pasta em `trials/`, ou os testes de
   aceitacao ainda nao foram copiados para `test/` (ver secao 3).
5. `cannot attach stdin to a TTY-enabled container because stdin is not a
   terminal`: o `time_trial.sh` foi chamado de um jeito nao interativo (ex.:
   outro script, pipe). Rode direto num terminal de verdade.

## 8. Alternativa, execucao local sem Docker

Use apenas se nao houver Docker na maquina.

### 8.1 JDK 17

```
java -version
javac -version
```

macOS com Homebrew:

```
brew install --cask temurin@17
```

### 8.2 Ferramentas de metrica

Baixe o CK, o PMD e o JUnit console para a pasta `tools/` na raiz do
repositorio. Essa pasta fica fora do controle de versao.

CK, jar com dependencias publicado no Maven Central:

```
mkdir -p tools
curl -fsSL -o tools/ck.jar \
  "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/ck-0.7.0-jar-with-dependencies.jar"
```

PMD 7.x, a distribuicao binaria ja inclui o CPD:

```
cd tools
curl -fsSL -o pmd.zip \
  "https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.7.0/pmd-dist-7.7.0-bin.zip"
unzip -q pmd.zip
mv pmd-bin-7.7.0 pmd
rm pmd.zip
cd ..
```

JUnit Platform Console Standalone, jar publicado no Maven Central:

```
curl -fsSL -o tools/junit-console.jar \
  "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.2/junit-platform-console-standalone-1.10.2.jar"
```

### 8.3 Cronometrar um trial (RQ1/RQ2)

```
python3 scripts/time_trial.py \
  --trial-id <trial-id> \
  --kata <kata> \
  --treatment <com_ia|sem_ia> \
  --integrante <integrante> \
  --src trials/<trial-id>/src \
  --test trials/<trial-id>/test \
  --junit-jar tools/junit-console.jar \
  --timebox-min 35 \
  --output results/time_results.csv
```

O script aceita a variavel de ambiente `JUNIT_CONSOLE` no lugar de
`--junit-jar`. Ctrl+C interrompe o trial manualmente (status `abortado`).

### 8.4 Compilar e coletar metricas estaticas (RQ3)

```
cd trials/<trial-id>
mkdir -p bin
javac -d bin $(find src -name "*.java")
cd ../..

python3 scripts/collect_metrics.py \
  --trial-id <trial-id> \
  --kata <kata> \
  --treatment <com_ia|sem_ia> \
  --integrante <integrante> \
  --src trials/<trial-id>/src \
  --bin trials/<trial-id>/bin \
  --ck-jar tools/ck.jar \
  --pmd-bin tools/pmd/bin/pmd \
  --min-tokens 100
```

Os dois scripts usam apenas a biblioteca padrao do Python 3, sem dependencias
externas. Tambem aceitam as variaveis de ambiente `CK_JAR` e `PMD_BIN` no lugar
de `--ck-jar` e `--pmd-bin`.
