# Imagem para coleta de metricas estaticas e cronometragem do LAB02.
# JDK 17, Python 3, CK, PMD, JUnit console e Semgrep ja instalados em /opt.
# trials/ e results/ do host entram como volumes no docker run.

FROM eclipse-temurin:17-jdk

# Versoes fixas para manter a coleta reproduzivel entre execucoes.
ARG CK_VERSION=0.7.0
ARG PMD_VERSION=7.7.0
ARG JUNIT_VERSION=1.10.2
ARG SEMGREP_VERSION=1.90.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Semgrep (varredura de vulnerabilidades, RQ de seguranca)
RUN pip3 install --no-cache-dir --break-system-packages "semgrep==${SEMGREP_VERSION}" \
    && pip3 install --no-cache-dir --break-system-packages "protobuf>=6.30" "setuptools<81"

# CK, jar com dependencias publicado no Maven Central.
RUN curl -fsSL -o /opt/ck.jar \
    "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/${CK_VERSION}/ck-${CK_VERSION}-jar-with-dependencies.jar"

# PMD, a distribuicao binaria ja inclui o CPD.
RUN curl -fsSL -o /tmp/pmd.zip \
    "https://github.com/pmd/pmd/releases/download/pmd_releases%2F${PMD_VERSION}/pmd-dist-${PMD_VERSION}-bin.zip" \
    && unzip -q /tmp/pmd.zip -d /opt \
    && mv "/opt/pmd-bin-${PMD_VERSION}" /opt/pmd \
    && rm /tmp/pmd.zip

# JUnit console standalone, usado na cronometragem do time-to-green (RQ1/RQ2).
RUN curl -fsSL -o /opt/junit-console.jar \
    "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/${JUNIT_VERSION}/junit-platform-console-standalone-${JUNIT_VERSION}.jar"

COPY scripts/collect_metrics.py /opt/collect_metrics.py
COPY scripts/time_trial.py /opt/time_trial.py
COPY scripts/lint_trials.py /opt/lint_trials.py
COPY scripts/stats_utils.py /opt/stats_utils.py
COPY scripts/correlacao_tempo_violacoes.py /opt/correlacao_tempo_violacoes.py
COPY scripts/security_scan.py /opt/security_scan.py
COPY scripts/normalizacao_estilo_loc.py /opt/normalizacao_estilo_loc.py
COPY scripts/tamanho_efeito_rq1_rq3.py /opt/tamanho_efeito_rq1_rq3.py
COPY scripts/outliers.py /opt/outliers.py
COPY scripts/analise_rq1_rq2.py /opt/analise_rq1_rq2.py
COPY scripts/normalizacao_estrutura_loc.py /opt/normalizacao_estrutura_loc.py

# Padrao lido pelos scripts; docker run so passa os argumentos de negocio.
ENV CK_JAR=/opt/ck.jar
ENV PMD_BIN=/opt/pmd/bin/pmd
ENV JUNIT_CONSOLE=/opt/junit-console.jar
ENV METRICS_OUTPUT=/results/metrics_results.csv
ENV TIME_OUTPUT=/results/time_results.csv

WORKDIR /results

ENTRYPOINT ["python3", "/opt/collect_metrics.py"]
