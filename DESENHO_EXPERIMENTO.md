# Desenho do Experimento

Documento único do Passo 1 (Desenho do Experimento), reunindo o que foi
produzido nas issues #1 (cronometragem), #2 (ambiente e métricas estáticas),
#3 (katas) e #4 (hipóteses, variáveis e ameaças à validade). Cada seção
resume a decisão e aponta para o artefato correspondente no repositório.

## Objetivo (GQM)

**Analisar** o uso de assistentes de IA generativa na resolução de tarefas de
programação, **com o propósito de** comparar seu efeito frente à codificação
manual, **com respeito a** tempo de resolução, qualidade funcional (defeitos)
e qualidade estrutural do código produzido, **do ponto de vista** do grupo
pesquisador, **no contexto de** katas de dificuldade equivalente resolvidos
por estudantes de graduação sob condições controladas (crossover
within-subject, time-boxed).

## Questões de pesquisa

- **RQ1**: o uso de assistente de IA reduz o tempo necessário para resolver
  uma tarefa de programação?
- **RQ2**: o uso de assistente de IA reduz a quantidade de defeitos (testes
  que falham) no código produzido?
- **RQ3**: o uso de assistente de IA altera a complexidade ciclomática ou a
  duplicação do código produzido?

## Linguagem e ferramentas de métrica estática

**Linguagem: Java.** Escolhida porque a ferramenta de métricas estáticas
usada para RQ3 (CK) só funciona sobre bytecode/fonte Java; fixar a linguagem
em Java evita ter que trocar de ferramenta (ex. Radon, para Python) entre
integrantes ou katas, e mantém as métricas comparáveis dentro do experimento.

**Ferramentas de métrica estática: CK + PMD CPD**, não Radon (alternativa
descartada porque Radon é para Python, e a linguagem escolhida é Java):

- **CK** (`com.github.mauricioaniche:ck`, versão fixada em `0.7.0` no
  [docker/Dockerfile](docker/Dockerfile)) extrai complexidade ciclomática
  média (WMC) por método/classe do código Java produzido em cada trial (RQ3).
- **PMD CPD** (versão `7.7.0`) mede duplicação de código (% de linhas
  duplicadas) sobre o mesmo código (RQ3).
- **LOC** (linhas de código), extraído junto pelo CK, entra como métrica de
  controle obrigatória ao lado de complexidade e duplicação.
- **JUnit Platform Console Standalone** (`1.10.2`) roda os testes de
  aceitação de cada kata, usado tanto na cronometragem do time-to-green
  (RQ1) quanto na contagem de testes passando/falhando (RQ2).

Toda a cadeia de ferramentas (JDK 17, CK, PMD, JUnit console) está empacotada
numa imagem Docker única ([docker/Dockerfile](docker/Dockerfile)), para que a
coleta seja reprodutível entre as máquinas dos três integrantes; guia
completo de uso, com alternativa sem Docker, em [SETUP.md](SETUP.md).

## Hipóteses (H0/H1) e variáveis dependentes/independentes

Detalhadas por RQ, com a justificativa de cada métrica escolhida frente às
alternativas do enunciado, em [HIPOTESES.md](HIPOTESES.md). Resumo:

| RQ | Variável dependente | H0 |
| --- | --- | --- |
| RQ1 (tempo) | Time-to-green (min), mediana por tratamento; trial sem sucesso é censurado em 35 min, não descartado | Mediana do time-to-green não difere entre `com_ia` e `sem_ia` |
| RQ2 (defeitos) | Taxa de sucesso dos testes de aceitação (%); nº absoluto de testes falhando como métrica complementar | Mediana da taxa de sucesso não difere entre `com_ia` e `sem_ia` |
| RQ3 (estrutura) | Complexidade ciclomática média (CK) e % de duplicação (PMD CPD), com LOC como controle | Mediana da complexidade/duplicação não difere entre `com_ia` e `sem_ia` |

**Variável independente**: uso de assistente de IA generativa na resolução
do kata, binária (`com_ia` / `sem_ia`). O assistente usado em todos os
trials `com_ia` do grupo é o **Claude (versão gratuita, claude.ai)**, fixado
para os três integrantes.

## Tratamentos

| Tratamento | Descrição |
| --- | --- |
| `com_ia` | Participante resolve o kata podendo consultar o Claude livremente (prompts, geração e revisão de código), dentro do time-box. |
| `sem_ia` | Participante resolve o kata sozinho, sem qualquer assistente de IA, dentro do time-box. |

## Objetos experimentais (katas)

4 katas autorais em Java, de dificuldade comparável e baixa indexação (para
reduzir o risco de o assistente reproduzir uma solução já vista em
treinamento em vez de efetivamente ajudar): Cofre de Senhas, Elevador do
Prédio, Etiquetas de Preço e Fila do Caixa. Cada um tem 1-2 métodos
estáticos, sem I/O nem bibliotecas externas, calibrado para ficar perto do
teto do time-box (35 min) quando resolvido manualmente. Estrutura de pastas,
enunciados e critério de dificuldade equivalente em
[katas/README.md](katas/README.md); os testes de aceitação de cada kata são
verificados contra uma solução de referência por `scripts/verify_katas.sh`
antes de qualquer trial começar.

## Tipo de projeto experimental

**Crossover / within-subject contrabalanceado.** Cada um dos 3 integrantes
atua como seu próprio controle, passando pelos dois tratamentos (2 katas
`com_ia`, 2 `sem_ia`). Isso controla a variação individual de habilidade
entre pessoas, que teria peso grande demais num desenho between-subject com
apenas 3 participantes. A ordem dos katas é contrabalanceada por integrante
(rotação cíclica) e o tratamento alterna a cada trial (nunca dois seguidos
com o mesmo tratamento), para não confundir aprendizado/fadiga de sessão com
o efeito do tratamento. Matriz completa, por integrante e por kata, em
[CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md).

## Quantidade de medições

3 integrantes × 4 trials cada = **12 trials no total**, 6 `com_ia` e 6
`sem_ia`. Amostra pequena, por isso a análise usa mediana/IQR nas
estatísticas descritivas e teste de Wilcoxon (pareado, não paramétrico) na
análise inferencial (Passo 4), consistente com o desenho within-subject.

## Procedimento e instrumentação

1. **Antes do experimento**: `scripts/verify_katas.sh` confirma que os
   testes de aceitação dos 4 katas passam contra a solução de referência.
2. **Cronometragem (RQ1/RQ2)**: `scripts/time_trial.sh <trial-id> <kata>
   <com_ia|sem_ia> <integrante> [timebox-min]` inicia o trial, roda os testes
   de aceitação em loop até passarem todos (`sucesso`) ou o time-box de 35
   min se esgotar (`censurado`), e grava tempo decorrido e contagem de testes
   passando/falhando em `results/time_results.csv`.
3. **Métricas estáticas (RQ3)**: `scripts/run_trial.sh <trial-id> <kata>
   <com_ia|sem_ia> <integrante>` compila o código final do trial e roda CK e
   PMD CPD sobre ele, gravando complexidade, duplicação e LOC em
   `results/metrics_results.csv`.
4. **Rastreabilidade**: cada trial (kata × tratamento × integrante) vira uma
   Issue individual no GitHub Projects, atribuída ao integrante responsável,
   seguindo a tabela de `trial-id` em [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md).

Detalhes de instalação e uso (Docker e alternativa sem Docker) em
[SETUP.md](SETUP.md); visão geral do repositório e estrutura de pastas no
[README.md](README.md).

## Ameaças à validade

Oito ameaças identificadas e suas mitigações: efeito de aprendizado entre
katas e kata confundido com tratamento (mitigados pela ordem contrabalanceada
e pela alternância de tratamento a cada trial, [CONTRABALANCEAMENTO.md](CONTRABALANCEAMENTO.md));
vazamento de solução já vista/memorização (mitigado por katas autorais de
baixa indexação, [katas/README.md](katas/README.md)); censura no time-box
(registrada como 35 min, não descartada); familiaridade prévia com o Claude,
dificuldade desigual residual entre katas e ambiente/hardware entre
integrantes, sem controle experimental disponível, tratadas como limitações a
discutir no Relatório Final.

Tabela completa (ameaça, risco, mitigação), fonte única, em
[HIPOTESES.md](HIPOTESES.md#ameaças-à-validade).
