#!/usr/bin/env python3
"""Teste de significancia e tamanho de efeito para RQ1 (tempo) e RQ3
(complexidade ciclomatica media, duplicacao), com_ia vs sem_ia: Wilcoxon
pareado por kata (6 pares, r rank-biserial) e Mann-Whitney nao pareado (9 vs
9, Cliff's delta), exatos por permutacao (scripts/stats_utils.py). RQ2 fica
de fora (taxa_sucesso_pct e 100% em todos os 18 trials, sem variancia).
Detalhes e ressalva sobre N pequeno em HIPOTESES.md.
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
    "mannwhitney_U",
    "mannwhitney_p",
    "cliffs_delta",
    "cliffs_delta_interpretacao",
]

# (nome da coluna no CSV de origem, nome amigavel, arquivo de origem)
METRICAS = [
    ("tempo_seg", "RQ1: tempo (time-to-green, seg)", "time"),
    ("cc_media", "RQ3: complexidade ciclomatica media", "metrics"),
    ("duplicacao_pct", "RQ3: duplicacao (%)", "metrics"),
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Wilcoxon+r (pareado por kata) e Mann-Whitney+Cliff's delta "
        "(nao pareado) para RQ1 (tempo) e RQ3 (cc_media, duplicacao_pct).",
    )
    parser.add_argument("--time-csv", type=Path, default=Path("results/time_results.csv"))
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics_results.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/tamanho_efeito_rq1_rq3.csv")
    )
    return parser.parse_args(argv)


def read_csv(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_trials(time_rows, metrics_rows, campo, origem):
    """Lista de trials no formato esperado por medias_por_kata: trial_id,
    kata, treatment, <campo>. Origem escolhe de qual CSV o campo vem."""
    linhas = time_rows if origem == "time" else metrics_rows
    trials = []
    for row in linhas:
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
    time_rows = read_csv(args.time_csv)
    metrics_rows = read_csv(args.metrics_csv)

    nao_sucesso = [row["trial_id"] for row in time_rows if row["status"] != "sucesso"]
    if nao_sucesso:
        print(
            f"Aviso: trials sem status 'sucesso' (tempo pode ser censurado, "
            f"registrado mesmo assim): {nao_sucesso}"
        )

    print(f"n: {COM}=9, {SEM}=9 (18 trials no total, ver CONTRABALANCEAMENTO.md)\n")

    comparacao = []
    print("Comparacao (mediana e IQR com_ia | sem_ia; Wilcoxon pareado por kata; Mann-Whitney):")
    for campo, nome, origem in METRICAS:
        trials = build_trials(time_rows, metrics_rows, campo, origem)
        v_com = [t[campo] for t in trials if t["treatment"] == COM]
        v_sem = [t[campo] for t in trials if t["treatment"] == SEM]
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

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARACAO_FIELDS)
        writer.writeheader()
        writer.writerows(comparacao)

    print(
        f"\nLinhas escritas em {args.output}. Lembrete: com N=6 pares (ou 9 vs 9), "
        "a magnitude de r/delta e indicativa, nao conclusiva (amostra pequena)."
    )


if __name__ == "__main__":
    main(sys.argv[1:])
