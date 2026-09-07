#!/usr/bin/env python3
"""Coleta de metricas estaticas do LAB02 (Assistentes de IA vs. Codificacao Manual).

O script recebe os dados de um trial pela linha de comando, roda o CK sobre o
codigo fonte Java, roda o PMD CPD sobre o mesmo codigo fonte, calcula LOC total,
complexidade ciclomatica media e percentual de duplicacao, e acrescenta uma linha
no arquivo results/metrics_results.csv.

Observacao sobre o CK: o CK analisa arquivos .java (codigo fonte) usando o parser
do Eclipse JDT. Por isso a analise do CK e feita sobre a pasta src/. A pasta bin/
e usada apenas para confirmar que o codigo do trial foi compilado, o que faz parte
do criterio da RQ2 (defeitos).
"""

import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CSV_FIELDS = [
    "timestamp",
    "trial_id",
    "kata",
    "treatment",
    "integrante",
    "loc_total",
    "loc_classes",
    "cc_media",
    "metodos",
    "linhas_duplicadas",
    "duplicacao_pct",
    "min_tokens",
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Coleta metricas estaticas (CK + PMD CPD) de um trial do LAB02.",
    )
    parser.add_argument("--trial-id", required=True, help="Identificador do trial.")
    parser.add_argument("--kata", required=True, help="Nome do kata resolvido no trial.")
    parser.add_argument(
        "--treatment",
        required=True,
        choices=["com_ia", "sem_ia"],
        help="Tratamento aplicado no trial.",
    )
    parser.add_argument(
        "--integrante",
        required=True,
        help="Integrante da equipe responsavel pelo trial.",
    )
    parser.add_argument(
        "--src",
        required=True,
        type=Path,
        help="Pasta com os arquivos .java finais do trial.",
    )
    parser.add_argument(
        "--bin",
        required=True,
        type=Path,
        help="Pasta com os .class compilados do trial (usada para conferir a compilacao).",
    )
    parser.add_argument(
        "--ck-jar",
        default=os.environ.get("CK_JAR"),
        help="Caminho do ck.jar. Se omitido, usa a variavel de ambiente CK_JAR.",
    )
    parser.add_argument(
        "--pmd-bin",
        default=os.environ.get("PMD_BIN"),
        help="Caminho do executavel pmd. Se omitido, usa a variavel de ambiente PMD_BIN.",
    )
    parser.add_argument(
        "--min-tokens",
        type=int,
        default=int(os.environ.get("CPD_MIN_TOKENS", "100")),
        help="Minimo de tokens para o CPD considerar um bloco duplicado (padrao 100).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("METRICS_OUTPUT", "results/metrics_results.csv")),
        help="Arquivo CSV de resultados (o script acrescenta uma linha por execucao).",
    )
    return parser.parse_args(argv)


def validate_inputs(args):
    if not args.ck_jar:
        sys.exit("Erro: informe --ck-jar ou defina a variavel de ambiente CK_JAR.")
    if not args.pmd_bin:
        sys.exit("Erro: informe --pmd-bin ou defina a variavel de ambiente PMD_BIN.")
    if not Path(args.ck_jar).is_file():
        sys.exit(f"Erro: ck.jar nao encontrado em {args.ck_jar}.")
    if not Path(args.pmd_bin).is_file():
        sys.exit(f"Erro: executavel do PMD nao encontrado em {args.pmd_bin}.")
    if not args.src.is_dir():
        sys.exit(f"Erro: pasta de fontes nao encontrada em {args.src}.")
    if not args.bin.is_dir():
        sys.exit(f"Erro: pasta de binarios nao encontrada em {args.bin}.")

    java_files = list(args.src.rglob("*.java"))
    if not java_files:
        sys.exit(f"Erro: nenhum arquivo .java em {args.src}.")
    class_files = list(args.bin.rglob("*.class"))
    if not class_files:
        sys.exit(
            f"Erro: nenhum .class em {args.bin}. Compile o trial com javac antes de coletar."
        )
    print(
        f"Entrada: {len(java_files)} arquivo(s) .java em src/, "
        f"{len(class_files)} arquivo(s) .class em bin/."
    )


def run_ck(ck_jar, src_dir, work_dir):
    """Roda o CK sobre a pasta de fontes e devolve o caminho do method.csv e do class.csv."""
    out_prefix = str(work_dir) + os.sep
    cmd = [
        "java",
        "-jar",
        str(ck_jar),
        str(src_dir),
        "false",  # use jars
        "0",  # max files per particao, 0 = automatico
        "false",  # metricas de variaveis e campos
        out_prefix,
    ]
    print("Rodando CK:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"Erro: CK terminou com codigo {result.returncode}.")

    method_csv = work_dir / "method.csv"
    class_csv = work_dir / "class.csv"
    if not method_csv.is_file():
        print(result.stdout)
        sys.exit("Erro: CK nao gerou method.csv.")
    return method_csv, class_csv


def read_ck_metrics(method_csv, class_csv):
    """Le o method.csv e o class.csv do CK e calcula LOC e complexidade ciclomatica media."""
    wmc_values = []
    method_loc_total = 0
    with method_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            wmc_values.append(int(float(row["wmc"])))
            method_loc_total += int(float(row["loc"]))

    class_loc_total = 0
    if class_csv.is_file():
        with class_csv.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                class_loc_total += int(float(row["loc"]))

    metodos = len(wmc_values)
    cc_media = round(sum(wmc_values) / metodos, 2) if metodos else 0.0
    return {
        "loc_total": method_loc_total,
        "loc_classes": class_loc_total,
        "cc_media": cc_media,
        "metodos": metodos,
    }


def run_cpd(pmd_bin, src_dir, min_tokens, work_dir):
    """Roda o PMD CPD sobre a pasta de fontes e devolve o caminho do XML gerado."""
    xml_path = work_dir / "cpd.xml"
    cmd = [
        str(pmd_bin),
        "cpd",
        "--minimum-tokens",
        str(min_tokens),
        "--language",
        "java",
        "--format",
        "xml",
        "--no-fail-on-violation",
        "--dir",
        str(src_dir),
    ]
    print("Rodando PMD CPD:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Com --no-fail-on-violation o CPD retorna 0 mesmo achando duplicacao.
    # Sem a flag, retornaria 4, que tambem e tratado como sucesso aqui.
    if result.returncode not in (0, 4):
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"Erro: PMD CPD terminou com codigo {result.returncode}.")

    xml_path.write_text(result.stdout, encoding="utf-8")
    return xml_path


def read_cpd_metrics(xml_path, loc_total):
    """Le o XML do CPD e calcula linhas duplicadas e percentual de duplicacao.

    Cada bloco <duplication> e contado uma vez pelo seu atributo lines. O percentual
    e linhas_duplicadas dividido pelo LOC total, conforme definido na RQ3.
    """
    linhas_duplicadas = 0
    text = xml_path.read_text(encoding="utf-8").strip()
    if text:
        root = ET.fromstring(text)
        # O XML do CPD usa namespace padrao, entao a comparacao e pelo nome local.
        for elem in root.iter():
            if elem.tag.rsplit("}", 1)[-1] == "duplication":
                linhas_duplicadas += int(elem.get("lines", "0"))

    duplicacao_pct = round(100 * linhas_duplicadas / loc_total, 2) if loc_total else 0.0
    return {
        "linhas_duplicadas": linhas_duplicadas,
        "duplicacao_pct": duplicacao_pct,
    }


def append_row(output_path, row):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output_path.is_file() or output_path.stat().st_size == 0
    with output_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main(argv):
    args = parse_args(argv)
    validate_inputs(args)

    with tempfile.TemporaryDirectory(prefix="lab02-metrics-") as tmp:
        work_dir = Path(tmp)
        method_csv, class_csv = run_ck(args.ck_jar, args.src, work_dir)
        ck_metrics = read_ck_metrics(method_csv, class_csv)
        xml_path = run_cpd(args.pmd_bin, args.src, args.min_tokens, work_dir)
        cpd_metrics = read_cpd_metrics(xml_path, ck_metrics["loc_total"])

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "trial_id": args.trial_id,
        "kata": args.kata,
        "treatment": args.treatment,
        "integrante": args.integrante,
        "min_tokens": args.min_tokens,
    }
    row.update(ck_metrics)
    row.update(cpd_metrics)

    append_row(args.output, row)

    print("Linha adicionada em", args.output)
    for field in CSV_FIELDS:
        print(f"  {field}: {row[field]}")


if __name__ == "__main__":
    if shutil.which("java") is None:
        sys.exit("Erro: java nao encontrado no PATH.")
    main(sys.argv[1:])
