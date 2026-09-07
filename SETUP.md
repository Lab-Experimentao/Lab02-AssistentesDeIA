# Ambiente e coleta de metricas estaticas (LAB02)

Este guia descreve como preparar o ambiente e rodar o script que coleta metricas
estaticas do codigo Java final de cada trial do experimento. As metricas alimentam
as questoes de pesquisa:

* RQ1: tempo de resolucao (coletado a parte, nao entra neste script).
* RQ2: defeitos (a compilacao dos trials e pre requisito, ver abaixo).
* RQ3: complexidade ciclomatica, duplicacao e LOC (o que este script calcula).

A linguagem escolhida para os katas e Java. As ferramentas de metrica sao o CK e
o PMD CPD.

A forma padrao de rodar a coleta e pelo Docker (secao 3). A execucao local
(secao 6) fica como alternativa quando nao houver Docker disponivel.

## 1. Requisitos

Para o fluxo padrao, a unica dependencia da maquina e o Docker.

```
docker --version
```

A imagem `lab02-metrics` traz JDK 17, Python 3, o CK e o PMD ja instalados, entao
nada mais precisa estar na maquina.

## 2. Estrutura de pastas

```
Lab02-AssistentesDeIA/
  docker/Dockerfile          imagem com JDK, Python, CK e PMD
  scripts/run_trial.sh       compila o trial e roda a coleta, tudo no container
  scripts/collect_metrics.py script de coleta chamado dentro do container
  trials/                    um subdiretorio por trial
    <trial-id>/
      src/                   arquivos .java finais do trial
      bin/                   .class compilados (recriados a cada coleta)
  results/                   recebe o metrics_results.csv
  tools/                     CK e PMD para uso local (fora do controle de versao)
  SETUP.md
```

### Estrutura esperada por trial

Cada trial fica em `trials/<trial-id>/` com uma pasta `src/` contendo todos os
arquivos `.java` na forma final entregue no trial. A pasta `bin/` com os `.class`
e gerada pelo proprio fluxo de coleta, nao precisa ser criada a mao.

A analise do CK e do CPD e feita sobre `src/`. A pasta `bin/` serve para confirmar
que o codigo do trial compila, o que e pre requisito da analise de defeitos da RQ2.

## 3. Fluxo padrao, coleta via Docker

### 3.1 Build da imagem (uma vez)

Da raiz do repositorio:

```
docker build -f docker/Dockerfile -t lab02-metrics .
```

O build baixa o CK e o PMD para dentro da imagem. Refazer o build so quando o
`Dockerfile` ou o `scripts/collect_metrics.py` mudarem.

### 3.2 Rodar um trial

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

### 3.3 Rodar sem o script auxiliar

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

## 4. Saida em results/metrics_results.csv

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

## 5. Trial de validacao

O repositorio traz `trials/trial-teste-fizzbuzz/` com um kata FizzBuzz simples,
usado so para validar o pipeline ponta a ponta. Ele nao faz parte dos dados do
experimento.

```
scripts/run_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
cat results/metrics_results.csv
```

## 6. Alternativa, execucao local sem Docker

Use apenas se nao houver Docker na maquina.

### 6.1 JDK 17

```
java -version
javac -version
```

macOS com Homebrew:

```
brew install --cask temurin@17
```

### 6.2 Ferramentas de metrica

Baixe o CK e o PMD para a pasta `tools/` na raiz do repositorio. Essa pasta fica
fora do controle de versao.

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

### 6.3 Compilar e coletar

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

O script usa a biblioteca padrao do Python 3, sem dependencias externas. Ele
tambem aceita as variaveis de ambiente `CK_JAR` e `PMD_BIN` no lugar de
`--ck-jar` e `--pmd-bin`.
