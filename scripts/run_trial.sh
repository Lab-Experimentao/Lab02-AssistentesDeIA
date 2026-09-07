#!/usr/bin/env bash
#
# Compila um trial e roda a coleta de metricas, tudo dentro do container.
# A unica dependencia da maquina e o Docker.
#
# Uso:
#   scripts/run_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [min-tokens]
#
# Exemplo:
#   scripts/run_trial.sh trial-teste-fizzbuzz fizzbuzz sem_ia arthur
#
# O trial precisa existir em trials/<trial-id>/src com os arquivos .java finais.
# A pasta trials/<trial-id>/bin e recriada a cada execucao.
# O resultado e acrescentado em results/metrics_results.csv.

set -euo pipefail

IMAGE="lab02-metrics"

if [ "$#" -lt 4 ]; then
    echo "Uso: scripts/run_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [min-tokens]" >&2
    exit 1
fi

TRIAL_ID="$1"
KATA="$2"
TREATMENT="$3"
INTEGRANTE="$4"
MIN_TOKENS="${5:-100}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/trials/${TRIAL_ID}/src"

if [ ! -d "${SRC_DIR}" ]; then
    echo "Erro: ${SRC_DIR} nao existe. Crie o trial em trials/${TRIAL_ID}/src antes." >&2
    exit 1
fi

mkdir -p "${REPO_ROOT}/results"

# Build da imagem na primeira vez ou quando ela ainda nao existir.
if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

# Passo 1, compila o trial dentro do container. Saida em trials/<trial-id>/bin.
echo "Compilando trials/${TRIAL_ID} ..."
docker run --rm \
    -v "${REPO_ROOT}/trials:/trials" \
    --entrypoint bash \
    "${IMAGE}" -c "\
        mkdir -p /trials/${TRIAL_ID}/bin && \
        find /trials/${TRIAL_ID}/bin -name '*.class' -delete && \
        javac -d /trials/${TRIAL_ID}/bin \$(find /trials/${TRIAL_ID}/src -name '*.java')"

# Passo 2, roda a coleta de metricas.
echo "Coletando metricas de trials/${TRIAL_ID} ..."
docker run --rm \
    -v "${REPO_ROOT}/trials:/trials" \
    -v "${REPO_ROOT}/results:/results" \
    "${IMAGE}" \
    --trial-id "${TRIAL_ID}" \
    --kata "${KATA}" \
    --treatment "${TREATMENT}" \
    --integrante "${INTEGRANTE}" \
    --src "/trials/${TRIAL_ID}/src" \
    --bin "/trials/${TRIAL_ID}/bin" \
    --min-tokens "${MIN_TOKENS}"

echo "Pronto. Linha acrescentada em results/metrics_results.csv."
