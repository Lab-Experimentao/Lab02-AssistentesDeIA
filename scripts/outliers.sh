#!/usr/bin/env bash
#
# Identificacao de outliers no dataset consolidado: cercas de Tukey (1,5x/3x
# IQR) sobre tempo_seg, loc_total, cc_media, duplicacao_pct e
# violacoes_por_100loc, mais uma checagem categorica de status/testes
# falhando. Le results/time_results.csv, results/metrics_results.csv e
# results/lint_normalizado.csv (rode scripts/normalizacao_estilo_loc.sh
# antes) e grava results/outliers.csv.
#
# Uso: scripts/outliers.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for arquivo in time_results.csv metrics_results.csv lint_normalizado.csv; do
    if [ ! -f "${REPO_ROOT}/results/${arquivo}" ]; then
        echo "Erro: results/${arquivo} nao existe. Rode os scripts de coleta/analise antes." >&2
        exit 1
    fi
done

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

docker run --rm \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/outliers.py \
    --time-csv /results/time_results.csv \
    --metrics-csv /results/metrics_results.csv \
    --lint-csv /results/lint_normalizado.csv \
    --output /results/outliers.csv

echo "Pronto. results/outliers.csv atualizado."
