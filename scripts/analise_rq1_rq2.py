#!/usr/bin/env python3
"""Mediana, IQR e Wilcoxon pareado por kata, com_ia vs sem_ia, para RQ1
(tempo) e RQ2 (taxa de sucesso, testes falhando). RQ2 sem variancia nos 18
trials coletados, Wilcoxon fica indefinido, ver HIPOTESES.md.
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

from stats_utils import (
    classificar_delta,
    iqr,
    medias_por_kata,
    rank_biserial_from_w,
    wilcoxon_exato,
)

COM, SEM = "com_ia", "sem_ia"

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
]

METRICAS = [
    ("tempo_seg", "RQ1: tempo, time-to-green, seg"),
    ("taxa_sucesso_pct", "RQ2: taxa de sucesso dos testes de aceitacao, %"),
    ("testes_falhando", "RQ2: numero de testes falhando ao final do time-box"),
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Mediana, IQR e Wilcoxon pareado por kata, within-subject, "
        "para RQ1, tempo, e RQ2, taxa de sucesso e testes falhando.",
    )
    parser.add_argument("--time-csv", type=Path, default=Path("results/time_results.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/analise_rq1_rq2.csv"))
    return parser.parse_args(argv)


def read_csv(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_trials(rows, campo):
    trials = []
    for row in rows:
        trials.append(
            {
                "trial_id": row["trial_id"],
                "kata": row["kata"],
                "treatment": row["treatment"],
                campo: float(row[campo]),
            }
        )
    return trials


def main(argv):
    args = parse_args(argv)
    rows = read_csv(args.time_csv)

    nao_sucesso = [row["trial_id"] for row in rows if row["status"] != "sucesso"]
    if nao_sucesso:
        print(
            f"Aviso, trials sem status 'sucesso', tempo pode ser censurado, "
            f"registrado mesmo assim: {nao_sucesso}"
        )

    print(f"n, {COM}=9, {SEM}=9, 18 trials no total, ver CONTRABALANCEAMENTO.md\n")

    comparacao = []
    print("Comparacao, mediana e IQR com_ia | sem_ia, Wilcoxon pareado por kata:")
    for campo, nome in METRICAS:
        trials = build_trials(rows, campo)
        v_com = [t[campo] for t in trials if t["treatment"] == COM]
        v_sem = [t[campo] for t in trials if t["treatment"] == SEM]
        med_com, med_sem = statistics.median(v_com), statistics.median(v_sem)

        pares = medias_por_kata(trials, campo)
        wil = wilcoxon_exato([c - s for c, s in pares.values()])
        w, n_w, p_w = wil if wil else (None, 0, None)
        r_w = rank_biserial_from_w(w, n_w) if wil else None
        interpretacao_r = classificar_delta(r_w)

        p_w_str = f"{p_w:.3f}" if p_w is not None else "n/a, sem variancia entre os pares"
        print(
            f"  {nome}, {med_com:g} (IQR {iqr(v_com):g}) | {med_sem:g} (IQR {iqr(v_sem):g}), "
            f"Wilcoxon W+={w} (n={n_w}) p={p_w_str} r={r_w} ({interpretacao_r})"
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
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARACAO_FIELDS)
        writer.writeheader()
        writer.writerows(comparacao)

    print(
        f"\nLinhas escritas em {args.output}. RQ2 sem variancia entre tratamentos "
        "nos 18 trials coletados ate agora, Wilcoxon fica degenerado nesse caso, "
        "ver HIPOTESES.md."
    )


if __name__ == "__main__":
    main(sys.argv[1:])
