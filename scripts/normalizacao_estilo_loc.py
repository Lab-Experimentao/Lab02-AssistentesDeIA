#!/usr/bin/env python3
"""Normalizacao das violacoes de estilo por LOC (violacoes por 100 linhas) e
comparacao com_ia vs sem_ia.

Para separar "codigo mais verboso" de "menos conforme", compara tres metricas:
LOC, violacoes brutas e violacoes por 100 LOC. Cada uma recebe dois testes
exatos (sem scipy):
  - Wilcoxon signed-rank pareado por kata (6 pares; controla a dificuldade e o
    tamanho do kata, ja que cada kata aparece 2x num tratamento e 1x no outro),
    com o tamanho de efeito r rank-biserial derivado do W+.
  - Mann-Whitney U nao pareado (9 vs 9), com o tamanho de efeito Cliff's delta
    derivado do U.
Tambem decompoe a diferenca bruta de violacoes em efeito de tamanho (LOC) e
efeito de taxa (violacoes por LOC).

Aviso sobre N pequeno: com 6 pares (Wilcoxon) ou 9 vs 9 (Mann-Whitney), o
valor de r/delta tem variancia amostral alta - uma classificacao "grande"
aqui e indicativa, nao conclusiva.
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

from stats_utils import (
    classificar_delta,
    cliffs_delta_from_u,
    iqr,
    mann_whitney_exato,
    medias_por_kata,
    rank_biserial_from_w,
    wilcoxon_exato,
)

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
    "wilcoxon_kata_r",
    "wilcoxon_kata_r_interpretacao",
    "mannwhitney_U",
    "mannwhitney_p",
    "cliffs_delta",
    "cliffs_delta_interpretacao",
]
METRICAS = [
    ("loc_total", "LOC (verbosidade)"),
    ("violacoes_total", "violacoes brutas"),
    ("violacoes_por_100loc", "violacoes por 100 LOC"),
]
COM, SEM = "com_ia", "sem_ia"


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
        r_w = rank_biserial_from_w(w, n_w) if wil else None
        interpretacao_r = classificar_delta(r_w)
        u, p_u = mann_whitney_exato(v_com, v_sem)
        delta = cliffs_delta_from_u(u, len(v_com), len(v_sem))
        interpretacao_delta = classificar_delta(delta)

        print(
            f"  {nome}: {med_com:g} (IQR {iqr(v_com):g}) | {med_sem:g} (IQR {iqr(v_sem):g})  "
            f"Wilcoxon W+={w} (n={n_w}) p={p_w:.3f} r={r_w} ({interpretacao_r})  "
            f"Mann-Whitney U={u:g} p={p_u:.3f} delta={delta} ({interpretacao_delta})"
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
                "wilcoxon_kata_r": r_w,
                "wilcoxon_kata_r_interpretacao": interpretacao_r,
                "mannwhitney_U": u,
                "mannwhitney_p": round(p_u, 4),
                "cliffs_delta": delta,
                "cliffs_delta_interpretacao": interpretacao_delta,
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
