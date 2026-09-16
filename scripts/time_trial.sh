#!/usr/bin/env bash
#
# Inicia a cronometragem de time-to-green (RQ1) de um trial, via Docker.
# A execucao deste comando marca o inicio do trial: compila e roda os testes
# de aceitacao em loop ate "sucesso", o time-box esgotar ("censurado") ou
# Ctrl+C ("abortado"). Resultado em results/time_results.csv.
#
# Uso: scripts/time_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [timebox-min]
# trials/<trial-id>/test precisa ja existir com os testes de aceitacao do kata.

set -euo pipefail

# Evita reescrita de paths tipo "/trials" pelo Git Bash (MSYS) no Windows.
export MSYS_NO_PATHCONV=1

IMAGE="lab02-metrics"
TIMEBOX_MAX_MIN=35

if [ "$#" -lt 4 ]; then
    echo "Uso: scripts/time_trial.sh <trial-id> <kata> <com_ia|sem_ia> <integrante> [timebox-min]" >&2
    exit 1
fi

TRIAL_ID="$1"
KATA="$2"
TREATMENT="$3"
INTEGRANTE="$4"
TIMEBOX="${5:-$TIMEBOX_MAX_MIN}"

if awk -v a="${TIMEBOX}" -v b="${TIMEBOX_MAX_MIN}" 'BEGIN { exit !(a > b) }'; then
    echo "Erro: timebox-min (${TIMEBOX}) nao pode ser maior que ${TIMEBOX_MAX_MIN}, o time-box do enunciado do LAB02 so pode ser reduzido." >&2
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/trials/${TRIAL_ID}/src"
TEST_DIR="${REPO_ROOT}/trials/${TRIAL_ID}/test"

if [ ! -d "${SRC_DIR}" ]; then
    echo "Erro: ${SRC_DIR} nao existe. Crie o trial em trials/${TRIAL_ID}/src antes." >&2
    exit 1
fi
if [ ! -d "${TEST_DIR}" ]; then
    echo "Erro: ${TEST_DIR} nao existe. Copie os testes de aceitacao do kata para trials/${TRIAL_ID}/test antes de iniciar a cronometragem." >&2
    exit 1
fi

mkdir -p "${REPO_ROOT}/results"

# Builda a imagem se ainda nao existir.
if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "Imagem ${IMAGE} nao encontrada, rodando o build."
    docker build -f "${REPO_ROOT}/docker/Dockerfile" -t "${IMAGE}" "${REPO_ROOT}"
fi

echo "Iniciando cronometragem de trials/${TRIAL_ID} (time-box: ${TIMEBOX} min)."
echo "O relogio comeca a contar agora. Ctrl+C interrompe manualmente."

# -it exige terminal interativo; sem TTY (ex.: chamado por outro script), cai para -i.
DOCKER_TTY_FLAGS="-i"
if [ -t 0 ] && [ -t 1 ]; then
    DOCKER_TTY_FLAGS="-it"
fi

docker run --rm ${DOCKER_TTY_FLAGS} \
    -v "${REPO_ROOT}/trials:/trials" \
    -v "${REPO_ROOT}/results:/results" \
    --entrypoint python3 \
    "${IMAGE}" /opt/time_trial.py \
    --trial-id "${TRIAL_ID}" \
    --kata "${KATA}" \
    --treatment "${TREATMENT}" \
    --integrante "${INTEGRANTE}" \
    --src "/trials/${TRIAL_ID}/src" \
    --test "/trials/${TRIAL_ID}/test" \
    --timebox-min "${TIMEBOX}"

echo "Pronto. Linha acrescentada em results/time_results.csv."
