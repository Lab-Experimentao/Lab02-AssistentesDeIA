#!/usr/bin/env python3
"""Cronometragem de time-to-green do LAB02 (RQ1/RQ2).

Roda desde a execucao do script ate os testes de aceitacao (JUnit) passarem
("sucesso"), o time-box se esgotar ("censurado", gravado como o time-box
cheio) ou Ctrl+C ("abortado"). trials/<id>/src e o codigo do trial, trials/<id>/test
sao os testes de aceitacao fixos do kata.
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

CSV_FIELDS = [
    "timestamp",
    "trial_id",
    "kata",
    "treatment",
    "integrante",
    "timebox_min",
    "tempo_seg",
    "status",
    "testes_total",
    "testes_passando",
    "testes_falhando",
    "taxa_sucesso_pct",
]

TIMEBOX_MAX_MIN = 35


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Mede o time-to-green (RQ1) de um trial do LAB02.",
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
        help="Pasta com o codigo de producao do trial (atualizada ao vivo durante o trial).",
    )
    parser.add_argument(
        "--test",
        required=True,
        type=Path,
        help="Pasta com os testes de aceitacao (JUnit) do kata.",
    )
    parser.add_argument(
        "--timebox-min",
        type=float,
        default=float(os.environ.get("TIMEBOX_MIN", TIMEBOX_MAX_MIN)),
        help=f"Time-box em minutos, no maximo {TIMEBOX_MAX_MIN} (padrao {TIMEBOX_MAX_MIN}). "
        "So pode ser reduzido, nunca aumentado, conforme o enunciado.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=float(os.environ.get("POLL_SECONDS", "3")),
        help="Intervalo entre tentativas de compilar e rodar os testes (padrao 3s).",
    )
    parser.add_argument(
        "--junit-jar",
        default=os.environ.get("JUNIT_CONSOLE"),
        help="Caminho do junit-platform-console-standalone.jar. Se omitido, usa JUNIT_CONSOLE.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("TIME_OUTPUT", "results/time_results.csv")),
        help="Arquivo CSV de resultados (o script acrescenta uma linha por trial).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostra a saida completa do javac/JUnit em cada tentativa.",
    )
    return parser.parse_args(argv)


def validate_inputs(args):
    if not args.junit_jar:
        sys.exit("Erro: informe --junit-jar ou defina a variavel de ambiente JUNIT_CONSOLE.")
    if not Path(args.junit_jar).is_file():
        sys.exit(f"Erro: junit-console.jar nao encontrado em {args.junit_jar}.")
    if not args.src.is_dir():
        sys.exit(f"Erro: pasta de codigo de producao nao encontrada em {args.src}.")
    if not args.test.is_dir():
        sys.exit(
            f"Erro: pasta de testes de aceitacao nao encontrada em {args.test}. "
            "Copie os testes do kata para la antes de iniciar a cronometragem."
        )
    if not list(args.test.rglob("*.java")):
        sys.exit(f"Erro: nenhum arquivo .java em {args.test}.")
    if args.timebox_min <= 0:
        sys.exit("Erro: --timebox-min deve ser maior que zero.")
    if args.timebox_min > TIMEBOX_MAX_MIN:
        sys.exit(
            f"Erro: --timebox-min ({args.timebox_min}) nao pode ser maior que "
            f"{TIMEBOX_MAX_MIN}, o time-box do enunciado do LAB02 so pode ser reduzido."
        )


def fmt_mmss(seconds):
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def compile_and_test(src, test, junit_jar, bin_dir, verbose):
    """Compila src+test e roda os testes; devolve (total, passando, falhando, msg)."""
    if bin_dir.exists():
        shutil.rmtree(bin_dir)
    bin_dir.mkdir(parents=True)

    java_files = list(src.rglob("*.java")) + list(test.rglob("*.java"))
    if not java_files:
        return 0, 0, 0, "nenhum arquivo .java em src/ ainda"

    compile_cmd = [
        "javac",
        "-cp", str(junit_jar),
        "-d", str(bin_dir),
    ] + [str(f) for f in java_files]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if verbose:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        last_line = next(
            (line for line in reversed(result.stderr.strip().splitlines()) if line.strip()),
            "erro de compilacao",
        )
        return 0, 0, 0, f"nao compila: {last_line.strip()}"

    run_cmd = [
        "java",
        "-cp", f"{junit_jar}{os.pathsep}{bin_dir}",
        "org.junit.platform.console.ConsoleLauncher",
        "execute",
        "--scan-classpath",
        "--details=summary",
        "--disable-banner",
        "--disable-ansi-colors",
    ]
    result = subprocess.run(run_cmd, capture_output=True, text=True)
    if verbose:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    output = result.stdout + result.stderr

    def extract(pattern):
        match = re.search(pattern, output)
        return int(match.group(1)) if match else 0

    total = extract(r"(\d+)\s+tests found")
    passing = extract(r"(\d+)\s+tests successful")
    failing = extract(r"(\d+)\s+tests failed")
    if total == 0:
        return 0, 0, 0, "nenhum teste encontrado"
    return total, passing, failing, None


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

    timebox_seconds = args.timebox_min * 60
    print(
        f"Cronometragem iniciada: trial={args.trial_id} kata={args.kata} "
        f"treatment={args.treatment} integrante={args.integrante} "
        f"time-box={fmt_mmss(timebox_seconds)}. Ctrl+C interrompe manualmente."
    )

    status = None
    total = passing = failing = 0
    start = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="lab02-time-") as tmp:
        bin_dir = Path(tmp) / "bin"
        try:
            while True:
                elapsed = time.monotonic() - start
                timed_out = elapsed >= timebox_seconds

                total, passing, failing, msg = compile_and_test(
                    args.src, args.test, args.junit_jar, bin_dir, args.verbose
                )
                elapsed = time.monotonic() - start
                detalhe = msg if msg else f"{passing}/{total} passando"
                print(
                    f"[{fmt_mmss(elapsed)} / {fmt_mmss(timebox_seconds)}] {detalhe}",
                    flush=True,
                )

                if total > 0 and failing == 0 and passing == total:
                    status = "sucesso"
                    elapsed = time.monotonic() - start
                    break

                if timed_out:
                    status = "censurado"
                    elapsed = timebox_seconds
                    break

                remaining = timebox_seconds - (time.monotonic() - start)
                time.sleep(max(0.0, min(args.poll_seconds, remaining)))
        except KeyboardInterrupt:
            status = "abortado"
            elapsed = time.monotonic() - start
            print("\nInterrompido manualmente (Ctrl+C).")

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "trial_id": args.trial_id,
        "kata": args.kata,
        "treatment": args.treatment,
        "integrante": args.integrante,
        "timebox_min": args.timebox_min,
        "tempo_seg": round(elapsed, 1),
        "status": status,
        "testes_total": total,
        "testes_passando": passing,
        "testes_falhando": failing,
        "taxa_sucesso_pct": round(100 * passing / total, 2) if total else 0.0,
    }

    append_row(args.output, row)

    print(f"\nResultado ({status}):")
    for field in CSV_FIELDS:
        print(f"  {field}: {row[field]}")
    print(f"\nLinha adicionada em {args.output}")


if __name__ == "__main__":
    if shutil.which("java") is None:
        sys.exit("Erro: java nao encontrado no PATH.")
    if shutil.which("javac") is None:
        sys.exit("Erro: javac nao encontrado no PATH.")
    main(sys.argv[1:])
