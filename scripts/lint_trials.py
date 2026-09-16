#!/usr/bin/env python3
"""Conformidade com style guide do LAB02: roda o PMD (ruleset codestyle) sobre
o codigo final de cada trial ja coletado, conta violacoes por tratamento, e
compara com_ia vs sem_ia.

A lista de trials vem de results/metrics_results.csv (mesma fonte da RQ3),
para nao precisar reparsear o trial-id. LOC tambem vem de la, para reportar
violacoes por KLOC alem do total bruto.
"""

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

CSV_FIELDS = [
    "trial_id",
    "kata",
    "treatment",
    "integrante",
    "loc_total",
    "violacoes_total",
    "violacoes_por_kloc",
]

DEFAULT_RULESET = "category/java/codestyle.xml"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Conta violacoes de estilo (PMD codestyle) por trial e por tratamento.",
    )
    parser.add_argument(
        "--metrics-csv",
        type=Path,
        default=Path(os.environ.get("METRICS_INPUT", "results/metrics_results.csv")),
        help="CSV com trial_id/kata/treatment/integrante/loc_total (saida do collect_metrics.py).",
    )
    parser.add_argument(
        "--trials-dir",
        type=Path,
        default=Path(os.environ.get("TRIALS_DIR", "trials")),
        help="Pasta com os trials (cada um em <trials-dir>/<trial-id>/src).",
    )
    parser.add_argument(
        "--pmd-bin",
        default=os.environ.get("PMD_BIN"),
        help="Caminho do executavel pmd. Se omitido, usa a variavel de ambiente PMD_BIN.",
    )
    parser.add_argument(
        "--ruleset",
        default=DEFAULT_RULESET,
        help=f"Ruleset do PMD a aplicar (padrao {DEFAULT_RULESET}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("LINT_OUTPUT", "results/lint_results.csv")),
        help="CSV de saida, uma linha por trial.",
    )
    return parser.parse_args(argv)


def validate_inputs(args):
    if not args.pmd_bin:
        sys.exit("Erro: informe --pmd-bin ou defina a variavel de ambiente PMD_BIN.")
    if not Path(args.pmd_bin).is_file():
        sys.exit(f"Erro: executavel do PMD nao encontrado em {args.pmd_bin}.")
    if not args.metrics_csv.is_file():
        sys.exit(f"Erro: {args.metrics_csv} nao encontrado.")
    if not args.trials_dir.is_dir():
        sys.exit(f"Erro: pasta de trials nao encontrada em {args.trials_dir}.")


def read_trials(metrics_csv):
    with metrics_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            {
                "trial_id": row["trial_id"],
                "kata": row["kata"],
                "treatment": row["treatment"],
                "integrante": row["integrante"],
                "loc_total": int(float(row["loc_total"])),
            }
            for row in reader
        ]


def run_pmd(pmd_bin, src_dir, ruleset):
    """Roda o PMD sobre a pasta de fontes e devolve a contagem de violacoes e o detalhe por regra."""
    cmd = [
        str(pmd_bin),
        "check",
        "-d", str(src_dir),
        "-R", ruleset,
        "-f", "json",
        "--no-fail-on-violation",
        "--no-progress",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 4):
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"Erro: PMD terminou com codigo {result.returncode}.")

    report = json.loads(result.stdout)
    contagem_regras = Counter()
    total = 0
    for arquivo in report.get("files", []):
        for violacao in arquivo.get("violations", []):
            contagem_regras[violacao["rule"]] += 1
            total += 1
    return total, contagem_regras


def append_row(output_path, row):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output_path.is_file() or output_path.stat().st_size == 0
    with output_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def summarize(rows):
    por_tratamento = defaultdict(list)
    por_tratamento_kloc = defaultdict(list)
    for row in rows:
        por_tratamento[row["treatment"]].append(row["violacoes_total"])
        por_tratamento_kloc[row["treatment"]].append(row["violacoes_por_kloc"])

    print("\nResumo por tratamento (violacoes de estilo, PMD codestyle):")
    for tratamento in sorted(por_tratamento):
        valores = por_tratamento[tratamento]
        valores_kloc = por_tratamento_kloc[tratamento]
        mediana = statistics.median(valores)
        mediana_kloc = round(statistics.median(valores_kloc), 2)
        if len(valores) >= 2:
            q1, _, q3 = statistics.quantiles(valores, n=4, method="inclusive")
            iqr = round(q3 - q1, 2)
        else:
            iqr = 0.0
        print(
            f"  {tratamento}: n={len(valores)}, total={sum(valores)}, "
            f"mediana={mediana} (IQR={iqr}), mediana_por_kloc={mediana_kloc}"
        )


def main(argv):
    args = parse_args(argv)
    validate_inputs(args)

    trials = read_trials(args.metrics_csv)
    if not trials:
        sys.exit(f"Erro: nenhum trial em {args.metrics_csv}.")

    rows = []
    for trial in trials:
        src_dir = args.trials_dir / trial["trial_id"] / "src"
        if not src_dir.is_dir():
            print(f"Aviso: {src_dir} nao existe, pulando {trial['trial_id']}.", file=sys.stderr)
            continue

        total, contagem_regras = run_pmd(args.pmd_bin, src_dir, args.ruleset)
        loc_total = trial["loc_total"]
        por_kloc = round(total / (loc_total / 1000), 2) if loc_total else 0.0

        row = {
            "trial_id": trial["trial_id"],
            "kata": trial["kata"],
            "treatment": trial["treatment"],
            "integrante": trial["integrante"],
            "loc_total": loc_total,
            "violacoes_total": total,
            "violacoes_por_kloc": por_kloc,
        }
        rows.append(row)

        regras_top = ", ".join(f"{regra}={n}" for regra, n in contagem_regras.most_common(3))
        print(f"{trial['trial_id']}: {total} violacoes ({regras_top})")

    if args.output.is_file():
        args.output.unlink()
    for row in rows:
        append_row(args.output, row)

    print(f"\n{len(rows)} trial(s) processado(s). Linhas escritas em {args.output}.")
    summarize(rows)


if __name__ == "__main__":
    main(sys.argv[1:])
