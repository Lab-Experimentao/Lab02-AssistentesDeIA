#!/usr/bin/env python3
"""Varredura de vulnerabilidades no codigo gerado: roda o Semgrep sobre o
codigo final de cada trial ja coletado, conta achados por severidade e por
regra, e compara com_ia vs sem_ia.

A lista de trials vem de results/metrics_results.csv (mesma fonte da RQ3),
para nao precisar reparsear o trial-id. LOC tambem vem de la, para reportar
achados por KLOC alem do total bruto. Mesmo padrao de scripts/lint_trials.py,
so trocando a ferramenta.
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
    "vulns_total",
    "vulns_por_kloc",
    "vulns_error",
    "vulns_warning",
    "vulns_info",
]

DEFAULT_RULESET = "p/java"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Conta achados de seguranca (Semgrep) por trial e por tratamento.",
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
        "--semgrep-bin",
        default=os.environ.get("SEMGREP_BIN", "semgrep"),
        help="Caminho (ou nome no PATH) do executavel semgrep. Padrao: 'semgrep'.",
    )
    parser.add_argument(
        "--ruleset",
        default=DEFAULT_RULESET,
        help=f"Ruleset do Semgrep a aplicar (padrao {DEFAULT_RULESET}). "
        "Pode ser um pack do Registry (ex.: p/java, p/security-audit) ou "
        "o caminho de um .yml local, para reprodutibilidade.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("SECURITY_OUTPUT", "results/security_results.csv")),
        help="CSV de saida, uma linha por trial.",
    )
    return parser.parse_args(argv)


def validate_inputs(args):
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


def run_semgrep(semgrep_bin, src_dir, ruleset):
    """Roda o Semgrep sobre a pasta de fontes e devolve a contagem de achados
    por severidade e o detalhe por regra."""
    cmd = [
        str(semgrep_bin),
        "scan",
        "--config", ruleset,
        "--json",
        "--quiet",
        "--no-git-ignore",
        "--metrics", "off",
        str(src_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        # 0 = sem achados, 1 = achados encontrados (ambos sucesso de execucao).
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"Erro: Semgrep terminou com codigo {result.returncode}.")

    report = json.loads(result.stdout)
    contagem_regras = Counter()
    contagem_severidade = Counter()
    for achado in report.get("results", []):
        regra = achado.get("check_id", "desconhecida")
        severidade = achado.get("extra", {}).get("severity", "DESCONHECIDA")
        contagem_regras[regra] += 1
        contagem_severidade[severidade] += 1
    total = sum(contagem_severidade.values())
    return total, contagem_severidade, contagem_regras


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
        por_tratamento[row["treatment"]].append(row["vulns_total"])
        por_tratamento_kloc[row["treatment"]].append(row["vulns_por_kloc"])

    print("\nResumo por tratamento (achados de seguranca, Semgrep):")
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

        total, contagem_severidade, contagem_regras = run_semgrep(
            args.semgrep_bin, src_dir, args.ruleset
        )
        loc_total = trial["loc_total"]
        por_kloc = round(total / (loc_total / 1000), 2) if loc_total else 0.0

        row = {
            "trial_id": trial["trial_id"],
            "kata": trial["kata"],
            "treatment": trial["treatment"],
            "integrante": trial["integrante"],
            "loc_total": loc_total,
            "vulns_total": total,
            "vulns_por_kloc": por_kloc,
            "vulns_error": contagem_severidade.get("ERROR", 0),
            "vulns_warning": contagem_severidade.get("WARNING", 0),
            "vulns_info": contagem_severidade.get("INFO", 0),
        }
        rows.append(row)

        regras_top = ", ".join(f"{regra}={n}" for regra, n in contagem_regras.most_common(3))
        print(f"{trial['trial_id']}: {total} achados ({regras_top})")

    if args.output.is_file():
        args.output.unlink()
    for row in rows:
        append_row(args.output, row)

    print(f"\n{len(rows)} trial(s) processado(s). Linhas escritas em {args.output}.")
    summarize(rows)


if __name__ == "__main__":
    main(sys.argv[1:])
