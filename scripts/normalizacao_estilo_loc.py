#!/usr/bin/env python3
"""Normalizacao das violacoes de estilo por LOC (violacoes por 100 linhas) e
comparacao com_ia vs sem_ia.

Para separar "codigo mais verboso" de "menos conforme", compara tres metricas:
LOC, violacoes brutas e violacoes por 100 LOC. Cada uma recebe dois testes
exatos (sem scipy):
  - Wilcoxon signed-rank pareado por kata (6 pares; controla a dificuldade e o
    tamanho do kata, ja que cada kata aparece 2x num tratamento e 1x no outro)
  - Mann-Whitney U nao pareado (9 vs 9)
Tambem decompoe a diferenca bruta de violacoes em efeito de tamanho (LOC) e
efeito de taxa (violacoes por LOC).
"""

import argparse
import csv
import itertools
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from correlacao_tempo_violacoes import ranks

TRIAL_FIELDS = [
    "trial_id",
    "kata",
    "treatment",
    "integrante",
    "loc_total",
    "violacoes_total",
    "violacoes_por_100loc",
]
COMPARACAO_FIELDS = [
    "metrica",
    "mediana_com_ia",
    "iqr_com_ia",
    "mediana_sem_ia",
    "iqr_sem_ia",
    "wilcoxon_kata_W",
    "wilcoxon_kata_n",
    "wilcoxon_kata_p",
    "mannwhitney_U",
    "mannwhitney_p",
]
METRICAS = [
    ("loc_total", "LOC (verbosidade)"),
    ("violacoes_total", "violacoes brutas"),
    ("violacoes_por_100loc", "violacoes por 100 LOC"),
]
COM, SEM = "com_ia", "sem_ia"
EPS = 1e-9
MAX_N_MANNWHITNEY = 20


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Violacoes de estilo por 100 LOC, com_ia vs sem_ia.",
    )
    parser.add_argument("--lint-csv", type=Path, default=Path("results/lint_results.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/lint_normalizado.csv"))
    parser.add_argument(
        "--comparacao-output",
        type=Path,
        default=Path("results/lint_normalizado_comparacao.csv"),
    )
    return parser.parse_args(argv)


def read_trials(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    trials = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            loc = int(float(row["loc_total"]))
            total = int(float(row["violacoes_total"]))
            if loc <= 0:
                sys.exit(f"Erro: loc_total invalido em {row['trial_id']}.")
            trials.append(
                {
                    "trial_id": row["trial_id"],
                    "kata": row["kata"],
                    "treatment": row["treatment"],
                    "integrante": row["integrante"],
                    "loc_total": loc,
                    "violacoes_total": total,
                    "violacoes_por_100loc": round(100 * total / loc, 2),
                }
            )
    return trials


def iqr(valores):
    if len(valores) < 2:
        return 0.0
    q1, _, q3 = statistics.quantiles(valores, n=4, method="inclusive")
    return q3 - q1


def wilcoxon_exato(diferencas):
    """Signed-rank exato bilateral. Devolve (W+, n sem zeros, p) ou None."""
    d = [x for x in diferencas if abs(x) > EPS]
    n = len(d)
    if n == 0:
        return None
    r = ranks([abs(x) for x in d])
    w_mais = sum(rk for rk, x in zip(r, d) if x > 0)
    centro = sum(r) / 2
    obs = abs(w_mais - centro)
    extremos = 0
    for sinais in itertools.product((0, 1), repeat=n):
        w = sum(rk for rk, s in zip(r, sinais) if s)
        if abs(w - centro) >= obs - EPS:
            extremos += 1
    return w_mais, n, extremos / 2**n


def mann_whitney_exato(a, b):
    """U exato bilateral por permutacao dos rotulos. Devolve (U de a, p)."""
    n1, n2 = len(a), len(b)
    if n1 + n2 > MAX_N_MANNWHITNEY:
        sys.exit(f"Erro: n={n1 + n2} inviabiliza o teste exato (maximo {MAX_N_MANNWHITNEY}).")
    r = ranks(a + b)
    base = n1 * (n1 + 1) / 2
    u_obs = sum(r[:n1]) - base
    centro = n1 * n2 / 2
    extremos = total = 0
    for comb in itertools.combinations(range(n1 + n2), n1):
        u = sum(r[i] for i in comb) - base
        total += 1
        if abs(u - centro) >= abs(u_obs - centro) - EPS:
            extremos += 1
    return u_obs, extremos / total


def medias_por_kata(trials, campo):
    por_kata = defaultdict(lambda: defaultdict(list))
    for t in trials:
        por_kata[t["kata"]][t["treatment"]].append(t[campo])
    resultado = {}
    for kata, grupos in sorted(por_kata.items()):
        if COM not in grupos or SEM not in grupos:
            sys.exit(f"Erro: kata {kata} sem os dois tratamentos, nao da para parear.")
        resultado[kata] = (statistics.mean(grupos[COM]), statistics.mean(grupos[SEM]))
    return resultado


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv):
    args = parse_args(argv)
    trials = read_trials(args.lint_csv)
    write_csv(args.output, TRIAL_FIELDS, trials)

    por_trat = {t: [x for x in trials if x["treatment"] == t] for t in (COM, SEM)}
    print(f"n: {COM}={len(por_trat[COM])}, {SEM}={len(por_trat[SEM])}\n")

    print("Densidade agregada (soma de violacoes / soma de LOC * 100):")
    for trat, grupo in por_trat.items():
        soma_v = sum(x["violacoes_total"] for x in grupo)
        soma_loc = sum(x["loc_total"] for x in grupo)
        print(f"  {trat}: {soma_v} violacoes / {soma_loc} LOC = {100 * soma_v / soma_loc:.2f} por 100 LOC")

    v = {trat: sum(x["violacoes_total"] for x in g) for trat, g in por_trat.items()}
    loc = {trat: sum(x["loc_total"] for x in g) for trat, g in por_trat.items()}
    taxa = {trat: v[trat] / loc[trat] for trat in (COM, SEM)}
    efeito_tamanho = (loc[COM] - loc[SEM]) * taxa[SEM]
    efeito_taxa = loc[COM] * (taxa[COM] - taxa[SEM])
    print(
        f"\nDiferenca bruta ({COM} - {SEM}) = {v[COM] - v[SEM]:+d} violacoes = "
        f"{efeito_tamanho:+.1f} por tamanho (LOC {loc[COM]} vs {loc[SEM]}) "
        f"e {efeito_taxa:+.1f} por taxa (violacoes por LOC)"
    )

    comparacao = []
    print("\nComparacao (mediana e IQR com_ia | sem_ia; Wilcoxon pareado por kata; Mann-Whitney):")
    for campo, nome in METRICAS:
        v_com = [x[campo] for x in por_trat[COM]]
        v_sem = [x[campo] for x in por_trat[SEM]]
        med_com, med_sem = statistics.median(v_com), statistics.median(v_sem)

        pares = medias_por_kata(trials, campo)
        wil = wilcoxon_exato([c - s for c, s in pares.values()])
        w, n_w, p_w = wil if wil else (None, 0, None)
        u, p_u = mann_whitney_exato(v_com, v_sem)

        print(
            f"  {nome}: {med_com:g} (IQR {iqr(v_com):g}) | {med_sem:g} (IQR {iqr(v_sem):g})  "
            f"Wilcoxon W+={w} (n={n_w}) p={p_w:.3f}  Mann-Whitney U={u:g} p={p_u:.3f}"
        )
        comparacao.append(
            {
                "metrica": campo,
                "mediana_com_ia": round(med_com, 2),
                "iqr_com_ia": round(iqr(v_com), 2),
                "mediana_sem_ia": round(med_sem, 2),
                "iqr_sem_ia": round(iqr(v_sem), 2),
                "wilcoxon_kata_W": w,
                "wilcoxon_kata_n": n_w,
                "wilcoxon_kata_p": round(p_w, 4),
                "mannwhitney_U": u,
                "mannwhitney_p": round(p_u, 4),
            }
        )

    print("\nPor kata (media da taxa por 100 LOC, com_ia | sem_ia):")
    for kata, (c, s) in medias_por_kata(trials, "violacoes_por_100loc").items():
        print(f"  {kata}: {c:.2f} | {s:.2f}  (dif {c - s:+.2f})")

    print("\nPor integrante (mediana da taxa por 100 LOC, com_ia | sem_ia):")
    for integrante in sorted({x["integrante"] for x in trials}):
        med = {
            trat: statistics.median(
                x["violacoes_por_100loc"] for x in por_trat[trat] if x["integrante"] == integrante
            )
            for trat in (COM, SEM)
        }
        print(f"  {integrante}: {med[COM]:.2f} | {med[SEM]:.2f}")

    write_csv(args.comparacao_output, COMPARACAO_FIELDS, comparacao)
    print(f"\nLinhas escritas em {args.output} e {args.comparacao_output}.")


if __name__ == "__main__":
    main(sys.argv[1:])
