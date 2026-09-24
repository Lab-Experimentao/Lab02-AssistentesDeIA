#!/usr/bin/env bash
#
# Correlacao entre tempo do trial e violacoes de estilo, por tratamento
# (Spearman, p exato por permutacao). Le results/time_results.csv e
# results/lint_results.csv (rode scripts/lint_trials.sh antes) e grava
# results/correlacao_tempo_violacoes.csv.
#
# Uso: scripts/correlacao_tempo_violacoes.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for arquivo in time_results.csv lint_results.csv; do
    if [ ! -f "${REPO_ROOT}/results/${arquivo}" ]; then
        echo "Erro: results/${arquivo} nao existe. Rode os scripts de coleta antes." >&2
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
    "${IMAGE}" /opt/correlacao_tempo_violacoes.py \
    --time-csv /results/time_results.csv \
    --lint-csv /results/lint_results.csv \
    --output /results/correlacao_tempo_violacoes.csv

echo "Pronto. results/correlacao_tempo_violacoes.csv atualizado."
