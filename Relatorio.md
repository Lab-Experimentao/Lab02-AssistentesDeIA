# Relatório de Laboratório

*Laboratório de Experimentação de Software — Modelo/Template de Relatório*

Este documento é um MODELO válido para qualquer um dos 5 laboratórios da disciplina (Lab01 a Lab05). Os parágrafos em itálico cinza/verde, iniciados por "ORIENTAÇÃO", explicam o que cada subseção deve conter — apague-os e escreva o conteúdo real do grupo no lugar. Textos entre colchetes [assim] indicam onde inserir informação específica do seu grupo/laboratório.

| | |
|---|---|
| **Curso** | Engenharia de Software |
| **Disciplina** | Laboratório de Experimentação de Software |
| **Turno / Período** | Noite / 6º |
| **Professor(a)** | Danilo Maia |
| **Laboratório** | [Lab02 — Assistentes de IA vs. Codificação Manual] |
| **Grupo (trio)** | Arthur Lara Panzera · Felipe Augusto Pereira · Gabriel Reis Lebron |
| **Link do repositório / GitHub Projects** | https://github.com/Lab-Experimentao/Lab02-AssistentesDeIA |
| **Data de entrega** | 23/09/2026 |

---

## 1. Introdução

Ferramentas de IA generativa (GitHub Copilot, ChatGPT, Claude, Gemini etc.) se tornaram onipresentes no desenvolvimento de software, mas grande parte do que se afirma sobre seu impacto em produtividade e qualidade vem de relato anedótico, sem controle experimental. Este laboratório busca produzir evidência controlada e reproduzível sobre o efeito real de um assistente de IA na resolução de tarefas de programação, comparando-o diretamente com a codificação manual sob as mesmas condições.

O grupo conduziu um experimento controlado do tipo *crossover within-subject*: cada um dos 3 integrantes resolveu 6 katas autorais em Java, 3 deles com apoio de um assistente de IA (tratamento `com_ia`) e 3 sem nenhum apoio (tratamento `sem_ia`), em ordem contrabalanceada e sob o mesmo time-box de 35 minutos por trial, totalizando **18 trials**.

As Questões de Pesquisa do enunciado, mantidas sem alteração, são:

- **RQ1**: o uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação?
- **RQ2**: o uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código produzido?
- **RQ3**: o uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?

Hipóteses informais do grupo, definidas antes da execução (S02) e formalizadas em H0/H1 no desenho do experimento ([HIPOTESES.md](HIPOTESES.md)):

- **RQ1**: esperava-se que o uso de IA reduzisse o tempo até passar em todos os testes de aceitação (*time-to-green*), pela geração e revisão de código mais rápida que a digitação manual.
- **RQ2**: esperava-se que a taxa de sucesso dos testes ao final do time-box fosse igual ou maior com IA, já que o assistente ajudaria a produzir código correto mais depressa, sobrando mais tempo para revisão dentro do próprio trial.
- **RQ3**: esperava-se pouca diferença de complexidade ciclomática ou duplicação entre os tratamentos, mas um possível aumento de verbosidade (LOC) no código gerado por IA, por isso o LOC entrou como métrica de controle obrigatória, e não apenas complementar.

Além do descrito no enunciado, o grupo propôs seis frentes adicionais de análise:

1. Conformidade com style guide (PMD `codestyle`) do código de cada trial, normalizada por 100 LOC, comparando `com_ia` e `sem_ia`.
2. Correlação entre o tempo do trial e o número de violações de estilo, dentro de cada tratamento, para testar se a pressa e não a IA em si, explica parte da diferença de conformidade observada.
3. Varredura de vulnerabilidades estáticas (Semgrep) sobre o código final de cada trial.
4. Tamanho de efeito (r rank-biserial e Cliff's delta), complementando o p-valor de RQ1 e RQ3 dado o N pequeno (18 trials).
5. Identificação e tratamento sistemático de outliers no dataset consolidado, via cercas de Tukey.
6. Dashboard de visualização consolidando tempo, taxa de sucesso e métricas estáticas entre os tratamentos.

## 2. Contexto

Este é o Lab02 da disciplina, um experimento autocontido: diferente de laboratórios que reaproveitam dados de etapas anteriores, aqui tanto o desenho experimental (S01) quanto a coleta de dados (S02) e a análise (S03) foram produzidos inteiramente dentro deste laboratório, ao longo de três sprints mais o Relatório Final.

O objeto de estudo é o próprio processo de resolução de problemas de programação: 6 katas autorais em Java ([katas/README.md](katas/README.md)), quatro de dificuldade base (Cofre de Senhas, Elevador do Prédio, Etiquetas de Preço, Fila do Caixa) e dois de dificuldade intencionalmente maior (Estoque do Depósito, Blocos Aninhados), resolvidos por cada um dos 3 integrantes do grupo (Arthur, Felipe, Gabriel), metade das vezes com um assistente de IA generativa habilitado e metade sem, sob um time-box fixo de 35 minutos por trial. Os katas são autorais e de baixa indexação de propósito, para reduzir o risco de o assistente reproduzir uma solução já vista em treinamento em vez de efetivamente ajudar (ver ameaças à validade em [HIPOTESES.md](HIPOTESES.md)).

O desenho segue o método GQM (*Goal-Question-Metric*) de Basili, Caldiera e Rombach: o Goal, as três Questions (RQ1-RQ3) e as métricas candidatas do enunciado estão detalhados em [DESENHO_EXPERIMENTO.md](DESENHO_EXPERIMENTO.md). A métrica estrutural da RQ3 (complexidade ciclomática) segue a definição clássica de McCabe (1976), coletada via CK; a duplicação de código, via PMD CPD. Dado o N pequeno (18 trials, 9 por tratamento), a análise estatística segue a recomendação do próprio enunciado de usar estatísticas não paramétricas, mediana e IQR nas tabelas descritivas, teste de Wilcoxon signed-rank (pareado) e Mann-Whitney U (não pareado) na análise inferencial, consistente com a prática usual em estudos de engenharia de software com amostras reduzidas.

## 3. Metodologia

*ORIENTAÇÃO: Esta é a seção mais longa do relatório e a que mais evidencia o trabalho real do grupo. Ela tem seis subseções — as cinco primeiras cobrem principalmente os 70% do enunciado; a última (Inovações) é onde os 30% de contribuição própria do grupo devem ficar explícitos e fáceis de identificar na correção.*

### 3.1 Principais Desafios

*ORIENTAÇÃO: Relate as dificuldades técnicas e metodológicas reais enfrentadas pelo grupo — não uma lista de trivialidades já resolvidas, e sim decisões difíceis de fato. Exemplos típicos, conforme o laboratório: limite de taxa (rate limit) da API do GitHub ao consultar milhares de repositórios ou workflow runs (Lab01/Lab03); paginação de grandes volumes de dados; ausência de histórico de mudança de status consultável via API no GitHub Projects, exigindo snapshots manuais recorrentes (todos os laboratórios); dificuldade de padronizar katas de dificuldade equivalente e evitar memorização de soluções pela IA (Lab02); ambiguidade na definição operacional de uma métrica, como lead time (Lab03); dados incompletos ou repositórios sem GitHub Actions habilitado (Lab03).*

*[conteúdo do grupo — substituir este texto]*

### 3.2 Tomadas de Decisão

*ORIENTAÇÃO: Documente as decisões metodológicas do grupo e o raciocínio (trade-off) por trás de cada uma — não apenas a escolha final. Exemplos que os enunciados pedem explicitamente: o limite de WIP definido para a coluna Doing e sua justificativa (obrigatório em todo laboratório); qual assistente de IA foi usado e por quê, e como se garantiu o mesmo tratamento em todos os trials (Lab02); qual definição operacional de métrica foi adotada quando o enunciado permite variação, mantendo-a consistente para toda a amostra (ex.: lead time no Lab03); critério de inclusão/exclusão de repositórios na amostra; linguagem de programação escolhida em função da ferramenta de métricas estáticas disponível (CK exige Java; Radon para Python).*

*[conteúdo do grupo — substituir este texto]*

### 3.3 Etapas

*ORIENTAÇÃO: Descreva o processo de desenvolvimento em sprints, seguindo a estrutura do enunciado (ex.: Lab0XS01, S02, S03 + Relatório Final), com o que foi efetivamente entregue em cada uma e quem (qual integrante) foi responsável por qual parte — a correção do professor é feita a partir do board (GitHub Projects), então a divisão aqui deve refletir os Assignees reais das Issues, não uma divisão apenas narrativa. Inclua também a subseção "Configuração do processo" exigida em todos os laboratórios: as colunas do board (mínimo Backlog → To Do → Doing → Review → Done), a política de limite de WIP em uso, e uma captura de tela (print) do board ao final do laboratório, mostrando o fluxo real de trabalho do grupo.*

[Tabela ou linha do tempo com Sprint | Entregas | Responsável(is) | Issues (nº)]

> Sugestão: insira aqui o print do quadro Kanban (GitHub Projects) mencionado na orientação acima.

### 3.4 Ferramentas

*ORIENTAÇÃO: Liste as ferramentas usadas na coleta, processamento e análise de dados — sejam específicas (nome e versão quando relevante), não genéricas. Exemplos conforme o laboratório: GraphQL e/ou REST API do GitHub para mineração (Lab01/Lab03 — bibliotecas de terceiros para consulta à API não são permitidas, o script deve ser próprio do grupo); Python/Pandas para manipulação de dados; Matplotlib/Seaborn ou Plotly/Dash/Streamlit para visualização; CK, PMD ou Radon para métricas estáticas de código (Lab02); testes estatísticos como o de Wilcoxon para amostras pareadas (Lab02); ferramenta de BI (Power BI, Tableau, Looker Studio) caso o grupo não opte pelo dashboard em código (Lab04). Inclua também a ferramenta de processo, obrigatória em todos os laboratórios: GitHub Projects (v2), com o link do repositório/board do grupo.*

*[conteúdo do grupo — substituir este texto]*

### 3.5 Tabela de Métricas

*ORIENTAÇÃO: Construa uma tabela relacionando cada Questão de Pesquisa à métrica correspondente, sua definição operacional exata (a fórmula ou regra de cálculo — não basta o nome) e a ferramenta/fonte usada para coletá-la. Isso é o que garante que o laboratório seja reprodutível por outro grupo. A primeira linha abaixo é um exemplo ilustrativo (baseado no Lab01); substitua pelas RQs e métricas do seu laboratório.*

| RQ | Métrica | Definição Operacional | Unidade | Ferramenta / Fonte |
|---|---|---|---|---|
| *RQ01 (exemplo)* | *Idade do repositório* | *Data atual − data de criação do repositório* | *Dias* | *Script GraphQL (API do GitHub)* |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

### 3.6 Inovações Propostas pelo Grupo (30% da nota)

*ORIENTAÇÃO: O enunciado do laboratório corresponde a 70% da exigência da disciplina. Os outros 30% dependem de uma contribuição original do grupo, que deve estar claramente identificada aqui — não diluída no restante do texto — para facilitar a correção. Escolha uma ou mais frentes de inovação, entre: (a) uma nova Questão de Pesquisa, além das do enunciado; (b) uma métrica ou variável adicional, não pedida no enunciado; (c) uma mudança de arquitetura/ferramenta de coleta (ex.: paralelizar a coleta, usar cache, trocar de biblioteca de visualização); (d) uma metodologia alternativa ou complementar (ex.: um teste estatístico adicional, uma segmentação diferente da amostra, uma técnica de controle de ameaça à validade não exigida pelo enunciado). Para cada inovação escolhida, explique o que foi feito, por que o grupo considerou relevante, e onde o resultado dela aparece nas seções de Resultados/Discussão e na Conclusão — inovação sem resultado discutido não conta como contribuição efetiva.*

*[conteúdo do grupo — substituir este texto]*

## 4. Resultados

### 4.1 Coleta de Dados

*ORIENTAÇÃO: Relate o volume final de dados efetivamente coletado e analisado — não apenas o volume-alvo do enunciado. Informe: quantos itens restaram após os filtros de qualidade (ex.: dos 1.000 repositórios buscados, quantos tinham dados completos; dos repositórios candidatos, quantos de fato usavam GitHub Actions — Lab03); o período coberto pela coleta; quantos trials/execuções foram concluídos dentro do tempo (Lab02); quantos snapshots do Kanban estão disponíveis e desde quando (Lab04/Lab05); outliers ou dados ausentes identificados, e como foram tratados (removidos, mantidos e discutidos à parte, etc.).*

*[conteúdo do grupo — substituir este texto]*

### 4.2 Visualização Gráfica

*ORIENTAÇÃO: Para cada Questão de Pesquisa (do enunciado e das RQs de inovação do grupo), inclua ao menos uma visualização que a responda diretamente, com a pergunta enunciada em texto imediatamente antes do gráfico correspondente, eixos nomeados com clareza e a medida de tendência central adequada indicada (mediana costuma ser preferível a média quando há outliers ou distribuição assimétrica — comum em dados de repositórios de software). Use o tipo de gráfico adequado ao tipo de pergunta, conforme a tabela abaixo, e explicite no texto os valores-chave que aparecem no gráfico (não deixe o leitor "adivinhar" o número a partir da figura).*

| Tipo de pergunta / dado | Gráfico recomendado |
|---|---|
| Comparar uma métrica entre categorias (ex.: linguagem, benchmark DORA) | Barras (ranking) — ordenadas por valor, não alfabeticamente |
| Comparar dois tratamentos no mesmo grupo (ex.: com IA vs. sem IA) | Boxplot pareado ou gráfico de pontos conectados (before/after) |
| Distribuição de uma métrica numérica (ex.: idade dos repositórios) | Histograma ou boxplot |
| Relação entre duas métricas numéricas (ex.: RQ07 do Lab01, RQ05 do Lab03) | Gráfico de dispersão (scatter plot) |
| Evolução ao longo do tempo (ex.: cycle time por sprint) | Linha, com um ponto por sprint/snapshot |
| Composição/fluxo do Kanban ao longo do tempo (Cumulative Flow Diagram) | Área empilhada (uma camada por coluna do board) |
| Proporção de categorias (ex.: % de issues fechadas) | Barra única 100% ou barras simples — evite pizza com muitas fatias |

*[Insira aqui os gráficos do grupo, um por RQ, cada um precedido da pergunta que ele responde]*

### 4.3 Discussão

*ORIENTAÇÃO: Para cada RQ (do enunciado e das RQs de inovação do grupo), compare explicitamente a hipótese informal levantada na Introdução com o resultado efetivamente obtido — hipótese confirmada, refutada, ou parcialmente confirmada, e por quê. Quando houver teste estatístico (ex.: Wilcoxon no Lab02), reporte o valor obtido e interprete o que ele significa em linguagem acessível, não apenas o número bruto. Discuta as ameaças à validade específicas do laboratório (ex.: efeito de aprendizado entre katas e risco de memorização pela IA — Lab02; diferença de dificuldade entre laboratórios distintos confundindo a tendência de cycle time — Lab05; lacunas nos snapshots do Kanban — Lab05). Finalize relacionando o que as inovações do grupo (seção 3.6) acrescentaram: elas confirmaram, contradisseram ou aprofundaram o que os 70% do enunciado já mostravam?*

*[conteúdo do grupo — substituir este texto]*

## 5. Conclusão

*ORIENTAÇÃO: Sintetize, em poucos parágrafos, as respostas a todas as RQs (enunciado + inovação do grupo), sem repetir números já discutidos em detalhe — o objetivo aqui é a mensagem final, não os dados brutos. Aponte as principais limitações do estudo (tamanho de amostra, ameaças à validade não mitigadas, período de coleta). Quando o enunciado pedir explicitamente uma postura de consultoria (caso do Lab05, que pede recomendações de melhoria de processo "como se o grupo fosse consultoria para um time real"), inclua recomendações objetivas e acionáveis, não genéricas. Encerre indicando o que o grupo faria diferente com mais tempo ou recursos, e quais das inovações propostas (30%) valeriam a pena expandir em um trabalho futuro.*

*[conteúdo do grupo — substituir este texto]*

## 6. Referências

- ZUSE, Horst. A framework of software measurement. Walter de Gruyter, 2013.
- BASILI, V. R.; CALDIERA, G.; ROMBACH, H. D. The Goal Question Metric Approach. In: Encyclopedia of Software Engineering. Wiley, 1994.
- MCCABE, T. J. A Complexity Measure. IEEE Transactions on Software Engineering, v. SE-2, n. 4, p. 308-320, 1976.
- 