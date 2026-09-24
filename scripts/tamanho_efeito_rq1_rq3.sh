#!/usr/bin/env bash
#
# Teste de significancia e tamanho de efeito para RQ1 (tempo) e RQ3 (cc_media,
# duplicacao_pct): Wilcoxon pareado por kata (com r rank-biserial) e
# Mann-Whitney nao pareado (com Cliff's delta), ambos exatos. Le
# results/time_results.csv e results/metrics_results.csv (rode
# scripts/time_trial.sh e scripts/run_trial.sh nos trials antes) e grava
# results/tamanho_efeito_rq1_rq3.csv.
#
# Uso: scripts/tamanho_efeito_rq1_rq3.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "${REPO_ROOT}/results/time_results.csv" ]; then
    echo "Erro: results/time_results.csv nao existe. Rode scripts/time_trial.sh antes." >&2
    exit 1
fi
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
    "${IMAGE}" /opt/tamanho_efeito_rq1_rq3.py \
    --time-csv /results/time_results.csv \
    --metrics-csv /results/metrics_results.csv \
    --output /results/tamanho_efeito_rq1_rq3.csv

echo "Pronto. results/tamanho_efeito_rq1_rq3.csv atualizado."
