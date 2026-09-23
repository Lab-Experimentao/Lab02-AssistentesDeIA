#!/usr/bin/env python3
"""Identificacao de outliers no dataset consolidado dos 18 trials: cercas de
Tukey (1,5x/3x IQR) sobre tempo_seg, loc_total, cc_media, duplicacao_pct e
violacoes_por_100loc, calculadas sobre o conjunto inteiro (nao por
tratamento nem por kata - n por subgrupo e pequeno demais para confiar num
quartil). Tambem confere, categoricamente, se algum trial tem status
diferente de sucesso ou testes falhando.

O script so classifica; a interpretacao de cada ponto sinalizado (e do kata?
e do tratamento? e um artefato de ambiente?) fica em HIPOTESES.md, mesma
divisao entre calculo (script) e leitura (documento) de
scripts/tamanho_efeito_rq1_rq3.py e scripts/normalizacao_estilo_loc.py.
"""

import argparse
import csv
import sys
from pathlib import Path

from stats_utils import cercas_tukey, quartis

CSV_FIELDS = [
    "trial_id",
    "kata",
    "treatment",
    "integrante",
    "metrica",
    "valor",
    "q1",
    "q3",
    "cerca_inferior",
    "cerca_superior",
    "classificacao",
]

# (nome da coluna no CSV consolidado, nome da coluna de origem, arquivo)
METRICAS = [
    ("tempo_seg", "tempo_seg", "time"),
    ("loc_total", "loc_total", "metrics"),
    ("cc_media", "cc_media", "metrics"),
    ("duplicacao_pct", "duplicacao_pct", "metrics"),
    ("violacoes_por_100loc", "violacoes_por_100loc", "lint"),
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Cercas de Tukey (1,5x/3x IQR) sobre o dataset consolidado dos trials.",
    )
    parser.add_argument("--time-csv", type=Path, default=Path("results/time_results.csv"))
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics_results.csv"))
    parser.add_argument("--lint-csv", type=Path, default=Path("results/lint_normalizado.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/outliers.csv"))
    return parser.parse_args(argv)


def read_csv(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado.")
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["trial_id"]: row for row in csv.DictReader(handle)}


def classificar(valor, cerca_1_5, cerca_3):
    inf_1_5, sup_1_5 = cerca_1_5
    inf_3, sup_3 = cerca_3
    if valor < inf_3 or valor > sup_3:
        return "outlier_extremo"
    if valor < inf_1_5 or valor > sup_1_5:
        return "outlier_moderado"
    return "normal"


def main(argv):
    args = parse_args(argv)
    time_rows = read_csv(args.time_csv)
    metrics_rows = read_csv(args.metrics_csv)
    lint_rows = read_csv(args.lint_csv)
    fontes = {"time": time_rows, "metrics": metrics_rows, "lint": lint_rows}

    trial_ids = sorted(time_rows)
    if not trial_ids:
        sys.exit(f"Erro: nenhum trial em {args.time_csv}.")

    print(f"Revisando {len(trial_ids)} trials.\n")

    # Checagem categorica: nao e por cerca, e sim/nao.
    problemas = [
        trial_id
        for trial_id in trial_ids
        if time_rows[trial_id]["status"] != "sucesso"
        or int(float(time_rows[trial_id]["testes_falhando"])) > 0
    ]
    if problemas:
        print(f"Aviso: {len(problemas)} trial(s) com status != sucesso ou testes falhando: {problemas}")
    else:
        print("Checagem categorica: 0 trials com status != sucesso ou testes falhando.")

    linhas = []
    print("\nMetricas fora da cerca de Tukey (so linhas nao-normais aparecem aqui):")
    algum_fora = False
    for metrica, campo_origem, origem in METRICAS:
        fonte = fontes[origem]
        valores_por_trial = {tid: float(fonte[tid][campo_origem]) for tid in trial_ids}
        valores = list(valores_por_trial.values())
        q1, q3 = quartis(valores)
        cerca_1_5 = cercas_tukey(valores, k=1.5)
        cerca_3 = cercas_tukey(valores, k=3)

        for trial_id in trial_ids:
            valor = valores_por_trial[trial_id]
            classificacao = classificar(valor, cerca_1_5, cerca_3)
            row = time_rows[trial_id]
            linhas.append(
                {
                    "trial_id": trial_id,
                    "kata": row["kata"],
                    "treatment": row["treatment"],
                    "integrante": row["integrante"],
                    "metrica": metrica,
                    "valor": valor,
                    "q1": round(q1, 3),
                    "q3": round(q3, 3),
                    "cerca_inferior": round(cerca_1_5[0], 3),
                    "cerca_superior": round(cerca_1_5[1], 3),
                    "classificacao": classificacao,
                }
            )
            if classificacao != "normal":
                algum_fora = True
                print(
                    f"  {trial_id}: {metrica}={valor:g} ({classificacao}, "
                    f"cerca 1,5x=[{cerca_1_5[0]:.2f}, {cerca_1_5[1]:.2f}], "
                    f"cerca 3x=[{cerca_3[0]:.2f}, {cerca_3[1]:.2f}])"
                )
    if not algum_fora:
        print("  (nenhuma)")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\n{len(linhas)} linhas escritas em {args.output}.")


if __name__ == "__main__":
    main(sys.argv[1:])
