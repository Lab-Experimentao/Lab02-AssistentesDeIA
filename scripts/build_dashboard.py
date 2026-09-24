#!/usr/bin/env python3
"""Gera um dashboard HTML autocontido (Apache ECharts via CDN) a partir dos
CSVs ja coletados em results/ - nao calcula nenhum dado novo, so reorganiza
o que os outros scripts ja produziram (tempo, RQ3, conformidade de estilo,
seguranca, tamanho de efeito, outliers) em boxplots + slope charts por kata
+ KPIs, para uso no Relatorio Final.

Unico script do projeto que nao precisa de Docker/JDK: so le CSV e escreve
HTML com a biblioteca padrao do Python.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from stats_utils import medias_por_kata, quartis

COM, SEM = "com_ia", "sem_ia"

# (chave no JSON, coluna de origem, arquivo de origem, rotulo, unidade)
METRICAS_BOXPLOT = [
    ("tempo_seg", "tempo_seg", "time", "Tempo (time-to-green)", "s"),
    ("cc_media", "cc_media", "metrics", "Complexidade ciclomática média", ""),
    ("complexidade_por_100loc", "complexidade_por_100loc", "estrutura", "Complexidade ciclomática por 100 LOC", ""),
    ("loc_total", "loc_total", "metrics", "LOC (verbosidade)", "linhas"),
    ("violacoes_por_100loc", "violacoes_por_100loc", "lint", "Violações de estilo por 100 LOC", ""),
]


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Gera results/dashboard.html a partir dos CSVs de resultados.",
    )
    parser.add_argument("--time-csv", type=Path, default=Path("results/time_results.csv"))
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics_results.csv"))
    parser.add_argument("--lint-csv", type=Path, default=Path("results/lint_normalizado.csv"))
    parser.add_argument(
        "--efeito-estilo-csv", type=Path, default=Path("results/lint_normalizado_comparacao.csv")
    )
    parser.add_argument(
        "--efeito-rq-csv", type=Path, default=Path("results/tamanho_efeito_rq1_rq3.csv")
    )
    parser.add_argument("--estrutura-csv", type=Path, default=Path("results/estrutura_normalizada.csv"))
    parser.add_argument(
        "--efeito-estrutura-csv", type=Path, default=Path("results/estrutura_normalizada_comparacao.csv")
    )
    parser.add_argument("--security-csv", type=Path, default=Path("results/security_results.csv"))
    parser.add_argument("--outliers-csv", type=Path, default=Path("results/outliers.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/dashboard.html"))
    return parser.parse_args(argv)


def read_csv(path):
    if not path.is_file():
        sys.exit(f"Erro: {path} nao encontrado. Rode os scripts de coleta/analise antes.")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_by_trial(path):
    return {row["trial_id"]: row for row in read_csv(path)}


def read_csv_by_metrica(path):
    return {row["metrica"]: row for row in read_csv(path)}


def boxplot_stats(valores):
    """[min, Q1, mediana, Q3, max], formato esperado pela serie boxplot do
    ECharts (echarts.dataset boxplot: [min, Q1, median, Q3, max])."""
    ordenados = sorted(valores)
    n = len(ordenados)
    mediana = (
        ordenados[n // 2]
        if n % 2
        else (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2
    )
    q1, q3 = quartis(valores)
    return [round(min(ordenados), 3), round(q1, 3), round(mediana, 3), round(q3, 3), round(max(ordenados), 3)]


def montar_boxplot(chave, campo, origem, rotulo, unidade, fontes, trial_ids, kata_por_trial, treatment_por_trial):
    fonte = fontes[origem]
    valores_por_trial = {tid: float(fonte[tid][campo]) for tid in trial_ids}
    grupos = {
        trat: [valores_por_trial[tid] for tid in trial_ids if treatment_por_trial[tid] == trat]
        for trat in (COM, SEM)
    }
    pontos = {
        trat: [
            {"trial_id": tid, "kata": kata_por_trial[tid], "valor": valores_por_trial[tid]}
            for tid in trial_ids
            if treatment_por_trial[tid] == trat
        ]
        for trat in (COM, SEM)
    }
    return {
        "chave": chave,
        "rotulo": rotulo,
        "unidade": unidade,
        "boxes": {trat: boxplot_stats(grupos[trat]) for trat in (COM, SEM)},
        "pontos": pontos,
    }


def montar_slope(campo, fonte_dict, kata_por_trial, treatment_por_trial):
    trials = [
        {"trial_id": tid, "kata": kata_por_trial[tid], "treatment": treatment_por_trial[tid], campo: float(row[campo])}
        for tid, row in fonte_dict.items()
    ]
    pares = medias_por_kata(trials, campo)
    return [
        {"kata": kata, "com_ia": round(c, 3), "sem_ia": round(s, 3)}
        for kata, (c, s) in sorted(pares.items())
    ]


def formatar_estatistica(row):
    if row is None:
        return None
    def numero(campo):
        valor = row.get(campo)
        return float(valor) if valor not in (None, "") else None

    return {
        "mediana_com_ia": numero("mediana_com_ia"),
        "mediana_sem_ia": numero("mediana_sem_ia"),
        "mannwhitney_p": numero("mannwhitney_p"),
        "cliffs_delta": numero("cliffs_delta"),
        "cliffs_delta_interpretacao": row.get("cliffs_delta_interpretacao"),
        "wilcoxon_kata_r": numero("wilcoxon_kata_r"),
        "wilcoxon_kata_r_interpretacao": row.get("wilcoxon_kata_r_interpretacao"),
    }


def main(argv):
    args = parse_args(argv)

    time_rows = read_csv_by_trial(args.time_csv)
    metrics_rows = read_csv_by_trial(args.metrics_csv)
    lint_rows = read_csv_by_trial(args.lint_csv)
    security_rows = read_csv_by_trial(args.security_csv)
    outliers_rows = read_csv(args.outliers_csv)
    efeito_estilo = read_csv_by_metrica(args.efeito_estilo_csv)
    efeito_rq = read_csv_by_metrica(args.efeito_rq_csv)
    estrutura_rows = read_csv_by_trial(args.estrutura_csv)
    efeito_estrutura = read_csv_by_metrica(args.efeito_estrutura_csv)

    trial_ids = sorted(time_rows)
    if not trial_ids:
        sys.exit(f"Erro: nenhum trial em {args.time_csv}.")

    kata_por_trial = {tid: time_rows[tid]["kata"] for tid in trial_ids}
    treatment_por_trial = {tid: time_rows[tid]["treatment"] for tid in trial_ids}
    fontes = {"time": time_rows, "metrics": metrics_rows, "lint": lint_rows, "estrutura": estrutura_rows}

    boxplots = {}
    slopes = {}
    for chave, campo, origem, rotulo, unidade in METRICAS_BOXPLOT:
        boxplots[chave] = montar_boxplot(
            chave, campo, origem, rotulo, unidade, fontes, trial_ids, kata_por_trial, treatment_por_trial
        )
        slopes[chave] = montar_slope(campo, fontes[origem], kata_por_trial, treatment_por_trial)

    estatisticas = {
        "tempo_seg": formatar_estatistica(efeito_rq.get("tempo_seg")),
        "cc_media": formatar_estatistica(efeito_rq.get("cc_media")),
        "complexidade_por_100loc": formatar_estatistica(efeito_estrutura.get("complexidade_por_100loc")),
        "loc_total": formatar_estatistica(efeito_estilo.get("loc_total")),
        "violacoes_por_100loc": formatar_estatistica(efeito_estilo.get("violacoes_por_100loc")),
    }

    n_com = sum(1 for tid in trial_ids if treatment_por_trial[tid] == COM)
    n_sem = sum(1 for tid in trial_ids if treatment_por_trial[tid] == SEM)
    n_falhas = sum(1 for tid in trial_ids if int(float(time_rows[tid]["testes_falhando"])) > 0)
    n_nao_sucesso = sum(1 for tid in trial_ids if time_rows[tid]["status"] != "sucesso")
    vulns_total = sum(int(row["vulns_total"]) for row in security_rows.values())
    dup_valores = [float(metrics_rows[tid]["duplicacao_pct"]) for tid in trial_ids]

    outliers_destaque = sorted(
        {row["trial_id"] for row in outliers_rows if row["metrica"] == "loc_total" and row["classificacao"] != "normal"}
    )
    outliers_tabela = [row for row in outliers_rows if row["classificacao"] != "normal"]

    dados = {
        "n_trials": len(trial_ids),
        "n_com_ia": n_com,
        "n_sem_ia": n_sem,
        "n_nao_sucesso": n_nao_sucesso,
        "n_falhas": n_falhas,
        "vulns_total": vulns_total,
        "duplicacao_max": max(dup_valores),
        "boxplots": boxplots,
        "slopes": slopes,
        "estatisticas": estatisticas,
        "outliers_destaque": sorted(outliers_destaque),
        "outliers_tabela": outliers_tabela,
    }

    html = TEMPLATE.replace("__DADOS_JSON__", json.dumps(dados, ensure_ascii=False))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Pronto. {args.output} gerado a partir de {len(trial_ids)} trials.")


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard - Lab02 Assistentes de IA</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/6.1.0/echarts.min.js"></script>
<style>
  :root {
    --bg: #f7f7fb;
    --card-bg: #ffffff;
    --texto: #1f2430;
    --texto-suave: #5c6270;
    --borda: #e4e4ec;
    --com-ia: #6c5ce7;
    --sem-ia: #00b894;
    --alerta: #e17055;
    --sombra: 0 1px 3px rgba(20, 20, 40, 0.08), 0 1px 2px rgba(20, 20, 40, 0.06);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--texto);
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    padding-block: 32px;
  }
  .wrap { max-width: 1180px; margin: 0 auto; padding-inline: 20px; }
  header.topo { margin-bottom: 28px; }
  header.topo h1 { margin: 0 0 6px; font-size: 1.6rem; }
  header.topo p { margin: 0; color: var(--texto-suave); font-size: 0.95rem; }

  .kpis {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin-bottom: 32px;
  }
  .kpi {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: var(--sombra);
    padding: 16px 18px;
    border-left: 4px solid var(--com-ia);
  }
  .kpi h3 { margin: 0 0 6px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--texto-suave); }
  .kpi .valor { font-size: 1.4rem; font-weight: 600; margin-bottom: 4px; }
  .kpi .detalhe { font-size: 0.82rem; color: var(--texto-suave); }

  section.painel {
    background: var(--card-bg);
    border-radius: 14px;
    box-shadow: var(--sombra);
    padding: 20px 22px 8px;
    margin-bottom: 22px;
  }
  section.painel h2 { margin: 0 0 4px; font-size: 1.15rem; }
  section.painel .subtitulo { color: var(--texto-suave); font-size: 0.88rem; margin-bottom: 10px; }
  .graficos-par {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    gap: 10px;
  }
  .grafico { width: 100%; height: 340px; }
  .nota {
    font-size: 0.82rem;
    color: var(--texto-suave);
    background: #f1f0fb;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 8px 0 16px;
  }
  .nota strong { color: var(--texto); }

  table.outliers { width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-bottom: 18px; }
  table.outliers th, table.outliers td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--borda); }
  table.outliers th { color: var(--texto-suave); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
  .badge.moderado { background: #fff3e0; color: #e17055; }
  .badge.extremo { background: #ffe3e3; color: #d63031; }

  footer.rodape {
    color: var(--texto-suave);
    font-size: 0.82rem;
    text-align: center;
    margin-top: 24px;
    line-height: 1.6;
  }
  footer.rodape a { color: var(--com-ia); }
</style>
</head>
<body>
<div class="wrap">

  <header class="topo">
    <h1>Lab02: Assistente de IA vs. codificação manual</h1>
    <p id="subtitulo-topo"></p>
  </header>

  <div class="kpis" id="kpis"></div>

  <section class="painel">
    <h2>RQ1 · Tempo (time-to-green)</h2>
    <div class="subtitulo" id="rq1-subtitulo"></div>
    <div class="graficos-par">
      <div class="grafico" id="chart-box-tempo_seg"></div>
      <div class="grafico" id="chart-slope-tempo_seg"></div>
    </div>
  </section>

  <section class="painel">
    <h2>RQ2 · Defeitos</h2>
    <div class="subtitulo" id="rq2-texto"></div>
  </section>

  <section class="painel">
    <h2>RQ3 · Estrutura do código</h2>
    <div class="subtitulo" id="rq3-subtitulo"></div>
    <div class="graficos-par">
      <div class="grafico" id="chart-box-cc_media"></div>
      <div class="grafico" id="chart-slope-cc_media"></div>
    </div>
    <div class="graficos-par">
      <div class="grafico" id="chart-box-complexidade_por_100loc"></div>
      <div class="grafico" id="chart-slope-complexidade_por_100loc"></div>
    </div>
    <div class="nota" id="complexidade-nota"></div>
    <div class="nota" id="rq3-duplicacao"></div>
  </section>

  <section class="painel">
    <h2>Conformidade de estilo (exploratória)</h2>
    <div class="subtitulo">LOC e violações de estilo (PMD), não é a RQ3 formal.</div>
    <div class="graficos-par">
      <div class="grafico" id="chart-box-loc_total"></div>
      <div class="grafico" id="chart-slope-loc_total"></div>
    </div>
    <div class="nota" id="loc-nota"></div>
    <div class="graficos-par">
      <div class="grafico" id="chart-box-violacoes_por_100loc"></div>
      <div class="grafico" id="chart-slope-violacoes_por_100loc"></div>
    </div>
  </section>

  <section class="painel">
    <h2>Segurança (exploratória)</h2>
    <div class="subtitulo" id="seguranca-texto"></div>
  </section>

  <section class="painel">
    <h2>Outliers revisados</h2>
    <div class="subtitulo">Cercas de Tukey (1,5x/3x IQR) sobre o dataset consolidado — ver HIPOTESES.md.</div>
    <table class="outliers" id="tabela-outliers"></table>
  </section>

  <footer class="rodape">
    Amostra pequena (N=18) — magnitudes de efeito são indicativas, não conclusivas.
    Fonte completa: <a href="../HIPOTESES.md">HIPOTESES.md</a> e
    <a href="../DESENHO_EXPERIMENTO.md">DESENHO_EXPERIMENTO.md</a>.
  </footer>

</div>

<script>
const DADOS = __DADOS_JSON__;
const CORES = { com_ia: "#6c5ce7", sem_ia: "#00b894" };
const ROTULO_TRAT = { com_ia: "Com IA", sem_ia: "Sem IA" };

function fmt(v, casas = 2) {
  if (v === null || v === undefined) return "n/a";
  return Number(v).toLocaleString("pt-BR", { maximumFractionDigits: casas });
}

document.getElementById("subtitulo-topo").textContent =
  `${DADOS.n_trials} trials (${DADOS.n_com_ia} com IA, ${DADOS.n_sem_ia} sem IA) · 3 integrantes × 6 katas`;

function kpiCard(titulo, valor, detalhe) {
  const div = document.createElement("div");
  div.className = "kpi";
  div.innerHTML = `<h3>${titulo}</h3><div class="valor">${valor}</div><div class="detalhe">${detalhe}</div>`;
  return div;
}

const kpisEl = document.getElementById("kpis");
const et = DADOS.estatisticas.tempo_seg;
kpisEl.appendChild(kpiCard(
  "RQ1 · Tempo",
  `${fmt(et.mediana_com_ia, 0)}s | ${fmt(et.mediana_sem_ia, 0)}s`,
  `p=${fmt(et.mannwhitney_p, 3)} · Cliff's delta=${fmt(et.cliffs_delta, 2)} (${et.cliffs_delta_interpretacao})`
));
kpisEl.appendChild(kpiCard(
  "RQ2 · Sucesso",
  DADOS.n_nao_sucesso === 0 ? "100%" : `${fmt(100 * (DADOS.n_trials - DADOS.n_nao_sucesso) / DADOS.n_trials, 0)}%`,
  DADOS.n_nao_sucesso === 0 ? "sem variância em nenhum dos 18 trials" : `${DADOS.n_nao_sucesso} trial(s) sem sucesso`
));
const ec = DADOS.estatisticas.cc_media;
kpisEl.appendChild(kpiCard(
  "RQ3 · Complexidade",
  `${fmt(ec.mediana_com_ia, 2)} | ${fmt(ec.mediana_sem_ia, 2)}`,
  `p=${fmt(ec.mannwhitney_p, 3)} · Cliff's delta=${fmt(ec.cliffs_delta, 2)} (${ec.cliffs_delta_interpretacao})`
));
kpisEl.appendChild(kpiCard(
  "Segurança",
  DADOS.vulns_total === 0 ? "0 achados" : String(DADOS.vulns_total),
  "Semgrep, ferramenta validada com caso sintético"
));

document.getElementById("rq1-subtitulo").textContent =
  "Boxplot bruto (9 vs 9) e média por kata ligando com_ia a sem_ia (mesma base do teste pareado).";
document.getElementById("rq2-texto").innerHTML =
  DADOS.n_nao_sucesso === 0
    ? `<strong>100% de sucesso</strong> nos ${DADOS.n_trials} trials (nenhum teste falhando ao final do time-box) — sem variância para comparar, por isso sem boxplot aqui (um boxplot de valor constante não informa nada).`
    : `${DADOS.n_nao_sucesso} de ${DADOS.n_trials} trials sem sucesso — ver time_results.csv.`;
document.getElementById("rq3-subtitulo").textContent =
  "Complexidade ciclomática média (CK), boxplot bruto e média por kata, mais a versão normalizada por 100 LOC.";
const ccBruta = DADOS.estatisticas.cc_media;
const ccNormalizada = DADOS.estatisticas.complexidade_por_100loc;
document.getElementById("complexidade-nota").innerHTML =
  `<strong>Atenção ao sinal</strong>: o Wilcoxon pareado por kata da complexidade bruta (r=${fmt(ccBruta.wilcoxon_kata_r, 2)}, ${ccBruta.wilcoxon_kata_r_interpretacao}) tem sinal oposto ao da complexidade por 100 LOC (r=${fmt(ccNormalizada.wilcoxon_kata_r, 2)}, ${ccNormalizada.wilcoxon_kata_r_interpretacao}) — mesmo confundimento por kata do gráfico de LOC abaixo, não inconsistência de coleta. Ver HIPOTESES.md.`;
document.getElementById("rq3-duplicacao").innerHTML =
  `<strong>Duplicação de código</strong>: ${fmt(DADOS.duplicacao_max, 1)}% no máximo entre os ${DADOS.n_trials} trials (0% na maioria) — sem variância suficiente para um teste ou gráfico informativo.`;
document.getElementById("seguranca-texto").innerHTML =
  DADOS.vulns_total === 0
    ? "<strong>0 vulnerabilidades</strong> detectadas pelo Semgrep em nenhum dos trials — validado com um caso sintético (a ferramenta funciona, o código dos katas é que não tem a superfície de ataque que ela cobre)."
    : `${DADOS.vulns_total} achado(s) — ver security_results.csv.`;

const el = DADOS.estatisticas.loc_total;
document.getElementById("loc-nota").innerHTML =
  `<strong>Atenção ao sinal</strong>: o Wilcoxon pareado por kata (r=${fmt(el.wilcoxon_kata_r, 2)}, ${el.wilcoxon_kata_r_interpretacao}) e o Mann-Whitney bruto (delta=${fmt(el.cliffs_delta, 2)}, ${el.cliffs_delta_interpretacao}) discordam de sinal para LOC — é confundimento pelo tamanho do kata (Cofre de Senhas é maior que os outros), não inconsistência. Pontos destacados: ${DADOS.outliers_destaque.join(", ") || "nenhum"}. Ver HIPOTESES.md.`;

function montarBoxplot(elId, spec) {
  const chart = echarts.init(document.getElementById(elId));
  const categorias = ["com_ia", "sem_ia"];
  chart.setOption({
    title: { text: spec.rotulo + (spec.unidade ? ` (${spec.unidade})` : ""), left: "center", textStyle: { fontSize: 13 } },
    toolbox: { feature: { saveAsImage: {} }, right: 8, top: 4 },
    grid: { left: 50, right: 20, top: 46, bottom: 30 },
    xAxis: { type: "category", data: categorias.map(c => ROTULO_TRAT[c]) },
    yAxis: { type: "value", name: spec.unidade || "" },
    series: [{
      type: "boxplot",
      data: categorias.map(c => spec.boxes[c]),
      itemStyle: { color: "#eef0ff", borderColor: "#6c5ce7" },
    }],
  });
  return chart;
}

function montarSlope(elId, pares, rotulo) {
  const chart = echarts.init(document.getElementById(elId));
  const cores = ["#6c5ce7", "#00b894", "#fdcb6e", "#e17055", "#0984e3", "#d63031"];
  chart.setOption({
    title: { text: rotulo + " por kata (média)", left: "center", textStyle: { fontSize: 13 } },
    toolbox: { feature: { saveAsImage: {} }, right: 8, top: 4 },
    grid: { left: 50, right: 110, top: 46, bottom: 30 },
    tooltip: { trigger: "item" },
    legend: { show: false },
    xAxis: { type: "category", data: ["Com IA", "Sem IA"], boundaryGap: false },
    yAxis: { type: "value" },
    series: pares.map((p, i) => ({
      name: p.kata,
      type: "line",
      symbolSize: 7,
      data: [p.com_ia, p.sem_ia],
      lineStyle: { color: cores[i % cores.length] },
      itemStyle: { color: cores[i % cores.length] },
      endLabel: { show: true, formatter: p.kata, fontSize: 10 },
    })),
  });
  return chart;
}

["tempo_seg", "cc_media", "complexidade_por_100loc", "loc_total", "violacoes_por_100loc"].forEach(chave => {
  montarBoxplot(`chart-box-${chave}`, DADOS.boxplots[chave]);
  montarSlope(`chart-slope-${chave}`, DADOS.slopes[chave], DADOS.boxplots[chave].rotulo);
});

const tabela = document.getElementById("tabela-outliers");
if (DADOS.outliers_tabela.length === 0) {
  tabela.outerHTML = "<p>Nenhum outlier fora da cerca moderada (1,5x IQR) em nenhuma métrica.</p>";
} else {
  const linhas = DADOS.outliers_tabela.map(o => `
    <tr>
      <td>${o.trial_id}</td>
      <td>${o.kata}</td>
      <td>${ROTULO_TRAT[o.treatment] || o.treatment}</td>
      <td>${o.metrica}</td>
      <td>${o.valor}</td>
      <td><span class="badge ${o.classificacao.includes('extremo') ? 'extremo' : 'moderado'}">${o.classificacao.replace('outlier_', '')}</span></td>
    </tr>`).join("");
  tabela.innerHTML = `
    <thead><tr><th>Trial</th><th>Kata</th><th>Tratamento</th><th>Métrica</th><th>Valor</th><th>Classificação</th></tr></thead>
    <tbody>${linhas}</tbody>`;
}

window.addEventListener("resize", () => {
  document.querySelectorAll(".grafico").forEach(el => {
    const inst = echarts.getInstanceByDom(el);
    if (inst) inst.resize();
  });
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main(sys.argv[1:])
