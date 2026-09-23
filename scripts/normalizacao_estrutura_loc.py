#!/usr/bin/env python3
"""Complexidade ciclomatica normalizada por LOC (por 100 linhas) e duplicacao,
com_ia vs sem_ia, para RQ3. duplicacao_pct ja e normalizado por LOC no
collect_metrics.py, entra aqui so para comparacao direta com a complexidade.
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
    "complexidade_total",
    "complexidade_por_100loc",
    "duplicacao_pct",
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
    ("complexidade_por_100loc", "complexidade ciclomatica por 100 LOC"),
    ("duplicacao_pct", "duplicacao (%)"),
]
COM, SEM = "com_ia", "sem_ia"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Complexidade ciclomatica por 100 LOC e duplicacao, com_ia vs sem_ia.",
    )
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics_results.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/estrutura_normalizada.csv"))
    parser.add_argument(
        "--comparacao-output",
        type=Path,
        default=Path("results/estrutura_normalizada_comparacao.csv"),
    )
    return parser.parse_args(argv)


def read_trials(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    trials = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            loc = int(float(row["loc_total"]))
            if loc <= 0:
                sys.exit(f"Erro: loc_total invalido em {row['trial_id']}.")
            complexidade_total = round(float(row["cc_media"]) * int(row["metodos"]), 2)
            trials.append(
                {
                    "trial_id": row["trial_id"],
                    "kata": row["kata"],
                    "treatment": row["treatment"],
                    "integrante": row["integrante"],
                    "loc_total": loc,
                    "complexidade_total": complexidade_total,
                    "complexidade_por_100loc": round(100 * complexidade_total / loc, 2),
                    "duplicacao_pct": float(row["duplicacao_pct"]),
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
    trials = read_trials(args.metrics_csv)
    write_csv(args.output, TRIAL_FIELDS, trials)

    por_trat = {t: [x for x in trials if x["treatment"] == t] for t in (COM, SEM)}
    print(f"n: {COM}={len(por_trat[COM])}, {SEM}={len(por_trat[SEM])}\n")

    comparacao = []
    print("Comparacao (mediana e IQR com_ia | sem_ia; Wilcoxon pareado por kata; Mann-Whitney):")
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

        p_w_str = f"{p_w:.3f}" if p_w is not None else "n/a"
        print(
            f"  {nome}: {med_com:g} (IQR {iqr(v_com):g}) | {med_sem:g} (IQR {iqr(v_sem):g})  "
            f"Wilcoxon W+={w} (n={n_w}) p={p_w_str} r={r_w} ({interpretacao_r})  "
            f"Mann-Whitney U={u:g} p={p_u:.3f} delta={delta} ({interpretacao_delta})"
        )
        comparacao.append(
            {
                "metrica": campo,
                "mediana_com_ia": round(med_com, 3),
                "iqr_com_ia": round(iqr(v_com), 3),
                "mediana_sem_ia": round(med_sem, 3),
                "iqr_sem_ia": round(iqr(v_sem), 3),
                "wilcoxon_kata_W": w,
                "wilcoxon_kata_n": n_w,
                "wilcoxon_kata_p": round(p_w, 4) if p_w is not None else None,
                "wilcoxon_kata_r": r_w,
                "wilcoxon_kata_r_interpretacao": interpretacao_r,
                "mannwhitney_U": u,
                "mannwhitney_p": round(p_u, 4),
                "cliffs_delta": delta,
                "cliffs_delta_interpretacao": interpretacao_delta,
            }
        )

    write_csv(args.comparacao_output, COMPARACAO_FIELDS, comparacao)
    print(f"\nLinhas escritas em {args.output} e {args.comparacao_output}.")


if __name__ == "__main__":
    main(sys.argv[1:])
