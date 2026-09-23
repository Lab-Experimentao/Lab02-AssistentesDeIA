#!/usr/bin/env bash
#
# Complexidade ciclomatica por 100 LOC e duplicacao, com_ia vs sem_ia (RQ3).
# Le results/metrics_results.csv e grava results/estrutura_normalizada.csv e
# results/estrutura_normalizada_comparacao.csv.
#
# Uso: scripts/normalizacao_estrutura_loc.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "${REPO_ROOT}/results/metrics_results.csv" ]; then
    echo "Erro: results/metrics_results.csv nao existe. Rode scripts/run_trial.sh antes." >&2
    exit 1
fi

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

docker run --rm \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/normalizacao_estrutura_loc.py \
    --metrics-csv /results/metrics_results.csv \
    --output /results/estrutura_normalizada.csv \
    --comparacao-output /results/estrutura_normalizada_comparacao.csv

echo "Pronto. results/estrutura_normalizada.csv e results/estrutura_normalizada_comparacao.csv atualizados."
