#!/usr/bin/env bash
#
# Gera o dashboard HTML autocontido (results/dashboard.html) a partir dos
# CSVs ja coletados. Diferente dos outros scripts de analise, NAO precisa
# de Docker/JDK - so le CSV e escreve HTML com a biblioteca padrao do
# Python, entao roda direto no host.
#
# Uso: scripts/build_dashboard.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for arquivo in time_results.csv metrics_results.csv lint_normalizado.csv \
               lint_normalizado_comparacao.csv tamanho_efeito_rq1_rq3.csv \
               security_results.csv outliers.csv; do
    if [ ! -f "${REPO_ROOT}/results/${arquivo}" ]; then
        echo "Erro: results/${arquivo} nao existe. Rode os scripts de coleta/analise antes." >&2
        exit 1
    fi
done

PYTHON_BIN=""
for candidato in python python3 py; do
    if "${candidato}" --version >/dev/null 2>&1; then
        PYTHON_BIN="${candidato}"
        break
    fi
done
if [ -z "${PYTHON_BIN}" ]; then
    echo "Erro: nenhum interpretador Python encontrado (tentei python, python3, py)." >&2
    exit 1
fi

(cd "${REPO_ROOT}" && "${PYTHON_BIN}" scripts/build_dashboard.py)

echo "Abra results/dashboard.html num navegador."
