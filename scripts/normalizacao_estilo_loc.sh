#!/usr/bin/env bash
#
# Violacoes de estilo por 100 LOC e comparacao com_ia vs sem_ia (Wilcoxon
# pareado por kata e Mann-Whitney exatos). Le results/lint_results.csv (rode
# scripts/lint_trials.sh antes) e grava results/lint_normalizado.csv e
# results/lint_normalizado_comparacao.csv.
#
# Uso: scripts/normalizacao_estilo_loc.sh

set -euo pipefail

# Evita reescrita de paths tipo "/results" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "${REPO_ROOT}/results/lint_results.csv" ]; then
    echo "Erro: results/lint_results.csv nao existe. Rode scripts/lint_trials.sh antes." >&2
    exit 1
fi

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

docker run --rm \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/normalizacao_estilo_loc.py \
    --lint-csv /results/lint_results.csv \
    --output /results/lint_normalizado.csv \
    --comparacao-output /results/lint_normalizado_comparacao.csv

echo "Pronto. results/lint_normalizado.csv e results/lint_normalizado_comparacao.csv atualizados."
