#!/usr/bin/env bash
#
# Wilcoxon pareado por kata para RQ1 (tempo) e RQ2 (taxa de sucesso, testes
# falhando). Le results/time_results.csv e grava results/analise_rq1_rq2.csv.
#
# Uso, scripts/analise_rq1_rq2.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "${REPO_ROOT}/results/time_results.csv" ]; then
    echo "Erro, results/time_results.csv nao existe. Rode scripts/time_trial.sh antes." >&2
    exit 1
fi

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

docker run --rm \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/analise_rq1_rq2.py \
    --time-csv /results/time_results.csv \
    --output /results/analise_rq1_rq2.csv

echo "Pronto. results/analise_rq1_rq2.csv atualizado."
