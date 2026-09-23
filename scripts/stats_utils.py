"""Primitivos de estatistica exata (sem scipy) usados pelos scripts de
analise pos-hoc. Reunido aqui porque scripts/correlacao_tempo_violacoes.py,
scripts/normalizacao_estilo_loc.py e scripts/tamanho_efeito_rq1_rq3.py
precisam dos mesmos primitivos; antes esses primitivos estavam duplicados/
espalhados entre os dois primeiros.
"""

import itertools
import statistics
import sys

EPS = 1e-9
MAX_N_MANNWHITNEY = 20

# Thresholds de magnitude para Cliff's delta / r rank-biserial (mesma escala
# [-1, 1] para as duas medidas). Fonte: Romano, J. et al. (2006), "Appropriate
# statistics for ordinal level data", tambem usados por Vargha & Delaney
# (2000) para Cliff's delta.
LIMIAR_NEGLIGIVEL = 0.147
LIMIAR_PEQUENO = 0.33
LIMIAR_MEDIO = 0.474


def ranks(values):
    """Postos (1-based), com media dos postos em caso de empate."""
    ordem = sorted(range(len(values)), key=lambda i: values[i])
    resultado = [0.0] * len(values)
    i = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and values[ordem[j + 1]] == values[ordem[i]]:
            j += 1
        media = (i + j) / 2 + 1
        for k in range(i, j + 1):
            resultado[ordem[k]] = media
        i = j + 1
    return resultado


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
    """Media do campo por kata/tratamento. Erro se algum kata nao tiver os
    dois tratamentos (nao da para parear)."""
    from collections import defaultdict

    por_kata = defaultdict(lambda: defaultdict(list))
    for t in trials:
        por_kata[t["kata"]][t["treatment"]].append(t[campo])
    resultado = {}
    for kata, grupos in sorted(por_kata.items()):
        if "com_ia" not in grupos or "sem_ia" not in grupos:
            sys.exit(f"Erro: kata {kata} sem os dois tratamentos, nao da para parear.")
        resultado[kata] = (statistics.mean(grupos["com_ia"]), statistics.mean(grupos["sem_ia"]))
    return resultado


def iqr(valores):
    if len(valores) < 2:
        return 0.0
    q1, _, q3 = statistics.quantiles(valores, n=4, method="inclusive")
    return q3 - q1


def cliffs_delta_from_u(u, n1, n2):
    """Cliff's delta a partir do U (Mann-Whitney) do primeiro grupo.
    delta = 2U/(n1*n2) - 1, em [-1, 1]. Positivo: grupo 1 tende a ter
    valores maiores que o grupo 2."""
    if n1 == 0 or n2 == 0:
        return None
    return round(2 * u / (n1 * n2) - 1, 4)


def rank_biserial_from_w(w_mais, n):
    """r rank-biserial pareado a partir do W+ (Wilcoxon signed-rank).
    r = 2*W+/(n*(n+1)/2) - 1, em [-1, 1]. Positivo: diferencas positivas
    (grupo 1 - grupo 2) dominam em posto."""
    if not n:
        return None
    total = n * (n + 1) / 2
    if total == 0:
        return None
    return round(2 * w_mais / total - 1, 4)


def classificar_delta(valor):
    """Classifica a magnitude de um Cliff's delta / r rank-biserial (escala
    [-1, 1] comum as duas medidas), pelos limiares de Romano et al. (2006)."""
    if valor is None:
        return "n/a"
    absoluto = abs(valor)
    if absoluto < LIMIAR_NEGLIGIVEL:
        return "negligivel"
    if absoluto < LIMIAR_PEQUENO:
        return "pequeno"
    if absoluto < LIMIAR_MEDIO:
        return "medio"
    return "grande"
