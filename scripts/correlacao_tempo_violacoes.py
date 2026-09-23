#!/usr/bin/env python3
"""Correlacao entre tempo do trial e violacoes de estilo, por tratamento.

Spearman com p-valor exato por permutacao (N pequeno, sem scipy). H1 unilateral:
rho < 0, ou seja, trials mais rapidos tem mais violacoes.

Analises por tratamento:
  A: tempo_seg x violacoes_total
  B: tempo_seg x violacoes_por_kloc (controla o tamanho do codigo)
  C: tempo e violacoes relativos a media do kata (controla a dificuldade do kata)
"""

import argparse
import csv
import itertools
import math
import sys
from collections import defaultdict
from pathlib import Path

from stats_utils import ranks

CSV_FIELDS = ["treatment", "analise", "n", "spearman_rho", "p_unilateral", "p_bilateral"]
MAX_N_EXATO = 10
EPS = 1e-9

ANALISES = [
    ("A tempo x violacoes_total", "tempo", "violacoes"),
    ("B tempo x violacoes_por_kloc", "tempo", "por_kloc"),
    ("C tempo_rel_kata x violacoes_rel_kata", "tempo_rel", "viol_rel"),
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Correlacao tempo x violacoes de estilo, por tratamento.",
    )
    parser.add_argument("--time-csv", type=Path, default=Path("results/time_results.csv"))
    parser.add_argument("--lint-csv", type=Path, default=Path("results/lint_results.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/correlacao_tempo_violacoes.csv")
    )
    return parser.parse_args(argv)


def read_rows(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["trial_id"]: row for row in csv.DictReader(handle)}


def build_trials(time_rows, lint_rows):
    trials = []
    for trial_id, lint in lint_rows.items():
        tempo = time_rows.get(trial_id)
        if tempo is None:
            sys.exit(f"Erro: {trial_id} sem linha em time_results.csv.")
        trials.append(
            {
                "trial_id": trial_id,
                "kata": lint["kata"],
                "treatment": lint["treatment"],
                "status": tempo["status"],
                "tempo": float(tempo["tempo_seg"]),
                "violacoes": float(lint["violacoes_total"]),
                "por_kloc": float(lint["violacoes_por_kloc"]),
            }
        )
    return trials


def add_relativos(trials):
    por_kata = defaultdict(list)
    for trial in trials:
        por_kata[trial["kata"]].append(trial)
    for grupo in por_kata.values():
        media_tempo = sum(t["tempo"] for t in grupo) / len(grupo)
        media_viol = sum(t["violacoes"] for t in grupo) / len(grupo)
        for trial in grupo:
            trial["tempo_rel"] = trial["tempo"] / media_tempo
            trial["viol_rel"] = trial["violacoes"] / media_viol


def spearman_exato(x, y):
    """Devolve (rho, p_unilateral rho<0, p_bilateral), ou None se uma variavel for constante."""
    n = len(x)
    if n > MAX_N_EXATO:
        sys.exit(f"Erro: n={n} inviabiliza a permutacao exata (maximo {MAX_N_EXATO}).")
    rx, ry = ranks(x), ranks(y)
    media = (n + 1) / 2
    sx = sum((r - media) ** 2 for r in rx)
    sy = sum((r - media) ** 2 for r in ry)
    if sx == 0 or sy == 0:
        return None
    denom = math.sqrt(sx * sy)

    def rho_de(soma):
        return (soma - n * media * media) / denom

    rho = rho_de(sum(a * b for a, b in zip(rx, ry)))
    unilateral = bilateral = total = 0
    for perm in itertools.permutations(ry):
        r = rho_de(sum(a * b for a, b in zip(rx, perm)))
        total += 1
        if r <= rho + EPS:
            unilateral += 1
        if abs(r) >= abs(rho) - EPS:
            bilateral += 1
    return rho, unilateral / total, bilateral / total


def main(argv):
    args = parse_args(argv)
    trials = build_trials(read_rows(args.time_csv), read_rows(args.lint_csv))
    if not trials:
        sys.exit("Erro: nenhum trial encontrado.")

    nao_sucesso = [t["trial_id"] for t in trials if t["status"] != "sucesso"]
    if nao_sucesso:
        print(f"Aviso: trials sem status 'sucesso' (tempo pode ser censurado): {nao_sucesso}")

    add_relativos(trials)

    linhas = []
    for tratamento in sorted({t["treatment"] for t in trials}):
        grupo = [t for t in trials if t["treatment"] == tratamento]
        print(f"\n{tratamento} (n={len(grupo)})")
        for nome, campo_x, campo_y in ANALISES:
            resultado = spearman_exato([t[campo_x] for t in grupo], [t[campo_y] for t in grupo])
            if resultado is None:
                print(f"  {nome}: variavel constante, correlacao indefinida")
                continue
            rho, p_uni, p_bi = resultado
            print(f"  {nome}: rho={rho:+.3f}  p(rho<0)={p_uni:.3f}  p(bilateral)={p_bi:.3f}")
            linhas.append(
                {
                    "treatment": tratamento,
                    "analise": nome,
                    "n": len(grupo),
                    "spearman_rho": round(rho, 4),
                    "p_unilateral": round(p_uni, 4),
                    "p_bilateral": round(p_bi, 4),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(linhas)
    print(f"\nLinhas escritas em {args.output}.")


if __name__ == "__main__":
    main(sys.argv[1:])
