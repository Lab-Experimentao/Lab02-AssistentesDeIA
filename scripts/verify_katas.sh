#!/usr/bin/env bash
#
# Valida cada kata em katas/<kata>/ isoladamente, antes do experimento comecar.
# Para cada kata, compila reference/ (solucao correta) junto com tests/ (testes
# de aceitacao JUnit 5) e roda os testes. Se a solucao de referencia nao passar
# em todos os testes do proprio kata, algo esta errado no enunciado/nos testes
# e o kata precisa ser corrigido antes de ser usado em um trial.
#
# Uso:
#   scripts/verify_katas.sh
#
# Precisa de JDK 17 (java/javac) para compilar e rodar os testes. Se nao
# houver JDK na maquina mas houver Docker, o script roda a si mesmo dentro de
# um container com JDK 17 automaticamente (mesma ideia do run_trial.sh). O
# JUnit Console Standalone e baixado uma vez para tools/ (fora do controle de
# versao, igual ao ck.jar e ao PMD).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KATAS_DIR="${REPO_ROOT}/katas"
TOOLS_DIR="${REPO_ROOT}/tools"
JUNIT_VERSION="1.10.2"
JUNIT_JAR="${TOOLS_DIR}/junit-platform-console-standalone-${JUNIT_VERSION}.jar"
JUNIT_URL="https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/${JUNIT_VERSION}/junit-platform-console-standalone-${JUNIT_VERSION}.jar"
JDK_IMAGE="eclipse-temurin:17-jdk"

mkdir -p "${TOOLS_DIR}"
if [ ! -f "${JUNIT_JAR}" ]; then
    if ! command -v curl >/dev/null 2>&1; then
        echo "Erro: curl nao encontrado para baixar o JUnit Console Standalone." >&2
        exit 1
    fi
    echo "Baixando JUnit Console Standalone ${JUNIT_VERSION} em tools/ ..."
    curl -fsSL -o "${JUNIT_JAR}" "${JUNIT_URL}"
fi

# Sem javac local (ou um javac quebrado, ex.: stub do Windows sem JDK
# instalado por tras): se houver Docker, reexecuta este mesmo script dentro
# de um container com JDK 17 (o repositorio inteiro fica montado em /repo).
if ! javac -version >/dev/null 2>&1 || ! java -version >/dev/null 2>&1; then
    if command -v docker >/dev/null 2>&1; then
        echo "javac/java nao encontrados na maquina, rodando via Docker (${JDK_IMAGE}) ..."
        # MSYS_NO_PATHCONV evita que o Git Bash do Windows reescreva os
        # caminhos /repo do container como se fossem caminhos do host.
        exec env MSYS_NO_PATHCONV=1 docker run --rm \
            -v "${REPO_ROOT}:/repo" \
            -w /repo \
            "${JDK_IMAGE}" \
            bash scripts/verify_katas.sh
    else
        echo "Erro: java/javac nao encontrados no PATH, e Docker tambem nao esta disponivel." >&2
        echo "Instale o JDK 17 ou o Docker Desktop." >&2
        exit 1
    fi
fi

if [ ! -d "${KATAS_DIR}" ]; then
    echo "Erro: pasta ${KATAS_DIR} nao existe." >&2
    exit 1
fi

FALHAS=0
declare -a RESUMO=()

for kata_dir in "${KATAS_DIR}"/*/; do
    [ -d "${kata_dir}reference" ] && [ -d "${kata_dir}tests" ] || continue
    kata_nome="$(basename "${kata_dir}")"

    echo ""
    echo "== Kata: ${kata_nome} =="

    work_dir="$(mktemp -d)"

    fontes=()
    while IFS= read -r arquivo; do
        fontes+=("${arquivo}")
    done < <(find "${kata_dir}reference" "${kata_dir}tests" -name "*.java")

    if [ "${#fontes[@]}" -eq 0 ]; then
        echo "  Erro: nenhum .java em reference/ ou tests/."
        RESUMO+=("${kata_nome}: SEM FONTES")
        FALHAS=$((FALHAS + 1))
        rm -rf "${work_dir}"
        continue
    fi

    if ! javac -cp "${JUNIT_JAR}" -d "${work_dir}" "${fontes[@]}" 2>"${work_dir}/javac.log"; then
        echo "  Erro de compilacao:"
        cat "${work_dir}/javac.log"
        RESUMO+=("${kata_nome}: FALHA DE COMPILACAO")
        FALHAS=$((FALHAS + 1))
        rm -rf "${work_dir}"
        continue
    fi

    saida="${work_dir}/junit.log"
    if java -jar "${JUNIT_JAR}" execute \
        --class-path "${work_dir}" \
        --scan-classpath \
        --details=summary >"${saida}" 2>&1; then
        cat "${saida}"
        RESUMO+=("${kata_nome}: OK")
    else
        cat "${saida}"
        echo "  Erro: os testes de aceitacao falharam contra a solucao de referencia."
        RESUMO+=("${kata_nome}: TESTES FALHARAM")
        FALHAS=$((FALHAS + 1))
    fi

    rm -rf "${work_dir}"
done

echo ""
echo "===== Resumo ====="
for linha in "${RESUMO[@]}"; do
    echo "  ${linha}"
done

if [ "${FALHAS}" -gt 0 ]; then
    echo ""
    echo "${FALHAS} kata(s) com problema. Corrija antes de iniciar o experimento."
    exit 1
fi

echo ""
echo "Todos os katas passaram na verificacao. Prontos para o experimento."
