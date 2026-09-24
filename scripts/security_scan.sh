#!/usr/bin/env bash
#
# Varredura de vulnerabilidades (Semgrep) de todos os trials ja coletados em
# results/metrics_results.csv. Roda uma vez sobre o conjunto inteiro (nao e
# por-trial como run_trial.sh/time_trial.sh). Resultado em
# results/security_results.csv, com o resumo por tratamento impresso no
# final. Mesmo padrao de scripts/lint_trials.sh, so trocando a ferramenta.
#
# Uso: scripts/security_scan.sh [ruleset]
#   ruleset (opcional): pack do Semgrep Registry (padrao p/java) ou caminho
#   de um .yml local, para reprodutibilidade entre execucoes.

set -euo pipefail

# Evita reescrita de paths tipo "/trials" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULESET="${1:-p/java}"

if [ ! -f "${REPO_ROOT}/results/metrics_results.csv" ]; then
    echo "Erro: results/metrics_results.csv nao existe. Rode run_trial.sh nos trials antes." >&2
    exit 1
fi

if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

docker run --rm \
    -v "${REPO_ROOT}/trials:/trials" \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/security_scan.py \
    --metrics-csv /results/metrics_results.csv \
    --trials-dir /trials \
    --ruleset "${RULESET}" \
    --output /results/security_results.csv

echo "Pronto. results/security_results.csv atualizado."
