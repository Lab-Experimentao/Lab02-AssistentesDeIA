# Imagem para coleta de metricas estaticas do LAB02.
# Traz JDK 17, Python 3, o CK e o PMD (com o CPD junto) ja instalados em /opt.
# As pastas trials/ e results/ do host sao montadas como volumes no docker run,
# assim o container nao depende de nada instalado na maquina local e o CSV de
# resultados persiste fora do container.

FROM eclipse-temurin:17-jdk

# Versoes fixas para manter a coleta reproduzivel entre execucoes.
ARG CK_VERSION=0.7.0
ARG PMD_VERSION=7.7.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 curl unzip \
    && rm -rf /var/lib/apt/lists/*

# CK, jar com dependencias publicado no Maven Central.
RUN curl -fsSL -o /opt/ck.jar \
    "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/${CK_VERSION}/ck-${CK_VERSION}-jar-with-dependencies.jar"

# PMD, a distribuicao binaria ja inclui o CPD.
RUN curl -fsSL -o /tmp/pmd.zip \
    "https://github.com/pmd/pmd/releases/download/pmd_releases%2F${PMD_VERSION}/pmd-dist-${PMD_VERSION}-bin.zip" \
    && unzip -q /tmp/pmd.zip -d /opt \
    && mv "/opt/pmd-bin-${PMD_VERSION}" /opt/pmd \
    && rm /tmp/pmd.zip

COPY scripts/collect_metrics.py /opt/collect_metrics.py

# O script le esses caminhos por padrao, entao o docker run so precisa dos
# argumentos de negocio (--trial-id, --kata, --treatment, --integrante, --src, --bin).
ENV CK_JAR=/opt/ck.jar
ENV PMD_BIN=/opt/pmd/bin/pmd
ENV METRICS_OUTPUT=/results/metrics_results.csv

WORKDIR /results

ENTRYPOINT ["python3", "/opt/collect_metrics.py"]
