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

Os 18 trials planejados (3 integrantes x 6 katas, 9 `com_ia` e 9 `sem_ia`) foram todos concluídos, 100% do volume-alvo, entre 14 e 16 de setembro de 2026. Nenhum trial foi descartado, censurado (não terminou dentro do time-box de 35 minutos) ou abortado por falha de ambiente, os 18 têm status `sucesso` em `results/time_results.csv`, com 100% dos testes de aceitação passando ao final de cada um.

A revisão sistemática de outliers ([scripts/outliers.sh](scripts/outliers.sh), cercas de Tukey 1,5x/3x IQR sobre tempo, LOC, complexidade, duplicação e violações de estilo) identificou dois trials fora da cerca de LOC, nenhum nas demais métricas. `trial-arthur-01-cofre-de-senhas-sem_ia`, 118 LOC, outlier extremo, acima da cerca superior de 66,75 (mediana do grupo na faixa de 30-40 LOC), e `trial-gabriel-05-cofre-de-senhas-com_ia`, 79 LOC, outlier moderado, mesma cerca. Os dois foram revisados e mantidos no dataset, ambos do kata Cofre de Senhas, o mais longo dos seis, não indício de erro de coleta, e a decisão está detalhada em [HIPOTESES.md](HIPOTESES.md#identificação-e-tratamento-de-outliers).

Duplicação de código (PMD CPD) deu 0% nos 18 trials, sem nenhuma ocorrência em nenhum tratamento, resultado plausível para katas desse tamanho e já validado com um teste sintético de duplicação antes da coleta real.

### 4.2 Visualização Gráfica

Cada RQ recebe um boxplot pareado (`com_ia` vs `sem_ia`) e, quando aplicável, um gráfico de pontos conectados por kata, o tipo de visualização recomendado para comparar dois tratamentos no mesmo grupo. Os dois tipos se repetem ao longo da seção, a leitura abaixo vale para todos. No boxplot, a caixa cobre do primeiro ao terceiro quartil, os 50% centrais dos 9 trials daquele tratamento, com a mediana marcada dentro dela, os traços finos (whiskers) marcam o menor e o maior valor observado. Quanto menos as duas caixas se sobrepõem, mais consistente é a diferença entre tratamentos. No gráfico por kata, cada linha liga a média de `com_ia` (esquerda) à média de `sem_ia` (direita) para um mesmo kata, controlando a dificuldade específica dele, uma linha subindo da esquerda para a direita indica que aquele kata teve valor menor com IA, descendo indica valor maior com IA, e linhas todas para o mesmo lado indicam um efeito consistente entre katas, linhas em direções diferentes indicam um efeito que muda conforme o kata.

**RQ1, o uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação?**

![Boxplot do tempo, time-to-green, com_ia vs sem_ia](results/graficos/rq1_tempo_boxplot.png)
![Tempo por kata, com_ia vs sem_ia](results/graficos/rq1_tempo_slope.png)

**Resultado**: mediana do tempo até passar em todos os testes de aceitação, 206,5s em `com_ia` (IQR 205,3s) contra 1007,0s em `sem_ia` (IQR 348,6s), cerca de 4,9 vezes mais rápido com IA, diferença estatisticamente significativa (Mann-Whitney p<0,001).

A caixa de `com_ia` fica inteira abaixo da caixa de `sem_ia`, sem nenhuma sobreposição, o padrão mais limpo de toda a seção. No gráfico por kata, as 6 linhas sobem da esquerda para a direita, sem exceção, `com_ia` mais rápido em cada um dos 6 katas.

**RQ2, o uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código produzido?**

**Resultado**: 100% de sucesso e 0 testes falhando em todos os 18 trials, `com_ia` e `sem_ia`, sem nenhuma diferença entre tratamentos.

Sem gráfico aqui, de propósito, um boxplot ou uma linha de valor constante não teria caixa nem inclinação para interpretar.

**RQ3, o uso de assistente de IA altera a complexidade ciclomática ou a duplicação do código produzido?**

![Boxplot da complexidade ciclomática média, com_ia vs sem_ia](results/graficos/rq3_cc_media_boxplot.png)
![Complexidade ciclomática média por kata, com_ia vs sem_ia](results/graficos/rq3_cc_media_slope.png)

**Resultado**: mediana da complexidade ciclomática média por método, 8,33 em `com_ia` (IQR 2,0) contra 9,0 em `sem_ia` (IQR 1,0), diferença pequena e não significativa (Mann-Whitney p=0,377).

Quanto menor a complexidade, mais simples o código. As caixas de `com_ia` e `sem_ia` se sobrepõem bastante aqui, ao contrário do gráfico de tempo, coerente com uma diferença pequena.

![Boxplot da complexidade ciclomática por 100 LOC, com_ia vs sem_ia](results/graficos/rq3_complexidade_boxplot.png)
![Complexidade ciclomática por 100 LOC por kata, com_ia vs sem_ia](results/graficos/rq3_complexidade_slope.png)

**Resultado**: mediana 22,22 por 100 LOC em `com_ia` (IQR 11,38) contra 29,03 em `sem_ia` (IQR 11,74), também pequena e não significativa (Mann-Whitney p=0,588). Duplicação, mediana 0% nos dois tratamentos, sem gráfico pelo mesmo motivo de RQ2.

Mesma complexidade do gráfico anterior, agora dividida pelo tamanho do código, por 100 linhas, em vez de pelo número de métodos. Repare no gráfico por kata, diferente do de tempo, as linhas não vão todas para o mesmo lado, 3 dos 6 katas descem (`com_ia` mais complexo por LOC, Blocos Aninhados, Cofre de Senhas, Etiquetas de Preço), 2 sobem (`com_ia` menos complexo, Estoque do Depósito, Fila do Caixa) e 1 fica praticamente empatado (Elevador do Prédio, diferença de 0,05), essa mistura de direção é a inconsistência discutida em 4.3.

**Inovações do grupo (verbosidade e estilo)**

![Boxplot de LOC, com_ia vs sem_ia](results/graficos/inovacao_loc_boxplot.png)
![LOC por kata, com_ia vs sem_ia](results/graficos/inovacao_loc_slope.png)

**Resultado**: mediana 41 linhas em `com_ia` (IQR 16,0) contra 31 em `sem_ia` (IQR 14,0), maior verbosidade com IA, mas sem significância no teste não pareado (Mann-Whitney p=0,624).

LOC é o controle de verbosidade da RQ3, não uma métrica de qualidade por si só. As duas caixas quase se sobrepõem por inteiro (o primeiro quartil é o mesmo nos dois tratamentos), a diferença aparece na mediana, deslocada para cima em `com_ia`.

![Boxplot de violações de estilo por 100 LOC, com_ia vs sem_ia](results/graficos/inovacao_estilo_boxplot.png)
![Violações de estilo por 100 LOC por kata, com_ia vs sem_ia](results/graficos/inovacao_estilo_slope.png)

**Resultado**: mediana 27,27 violações por 100 LOC em `com_ia` (IQR 7,68) contra 22,58 em `sem_ia` (IQR 16,77), sem diferença estatística clara (Mann-Whitney p=0,950).

Violações de estilo (PMD `codestyle`) já divididas por 100 LOC, para não confundir "mais violações" com "mais código". Caixas bem próximas e sobrepostas, as linhas por kata também vão em direções diferentes entre si.

### 4.3 Discussão

**RQ1, tempo**: hipótese confirmada. A mediana de tempo caiu de 1007,0s (`sem_ia`) para 206,5s (`com_ia`), efeito máximo e significativo nas duas medidas, r rank-biserial de -1,0 no Wilcoxon pareado por kata (W+=0, n=6, p=0,031, o menor p alcançável com apenas 6 pares) e Cliff's delta de -1,0 no Mann-Whitney não pareado (9 vs 9, p<0,001, separação perfeita entre os dois grupos). Os 6 katas, sem exceção, tiveram `com_ia` mais rápido que `sem_ia`, a convergência das duas análises, pareada e não pareada, dá confiança de que o efeito é real e não um artefato de um único teste.

**RQ2, defeitos**: hipótese nem confirmada nem refutada, sem o que testar. Os 18 trials tiveram 100% de sucesso e 0 testes falhando, `com_ia` e `sem_ia`, sem nenhuma variância entre tratamentos. Isso não significa "sem efeito", significa que os katas foram calibrados dentro da capacidade dos dois tratamentos no time-box de 35 minutos, um resultado esperado do próprio desenho do experimento, não uma falha de coleta.

**RQ3, estrutura do código**: hipótese parcialmente confirmada, com uma inconsistência que vale registrar. A parte de duplicação bateu com o esperado, 0% nos dois tratamentos, sem diferença. A complexidade ciclomática bruta por método ficou menor em `com_ia` (mediana 8,33 vs 9,0, Wilcoxon pareado p=0,625 com r=-0,40 médio, Mann-Whitney p=0,377 com Cliff's delta -0,25 pequeno), mas com apenas n=4 pares não zerados (2 dos 6 katas tiveram diferença zero de `cc_media` entre tratamentos), é a estimativa menos confiável do conjunto. A versão normalizada por 100 LOC não confirma essa direção, os 18 trials agrupados só por tratamento dão `com_ia` menor (mediana 22,22 vs 29,03), mas pareando por kata a direção não é uniforme, `com_ia` fica mais complexo por LOC em 3 dos 6 katas, menos complexo em 2, e praticamente empatado em 1 (Wilcoxon p=0,688, r=0,24 pequeno, sinal oposto ao da métrica bruta). Nenhuma das estatísticas cruza 0,05, então nada disso é conclusivo, mas a inversão de sinal entre a comparação simples por tratamento e a comparação pareada por kata mostra que a mediana não pareada pode estar sendo puxada por qual kata caiu em qual tratamento (o contrabalanceamento troca o integrante, não o kata, entre tratamentos), não por um efeito real do assistente de IA. Com N=18 e 6 pares, RQ3 fica sem resposta clara, nem confirmando nem refutando a expectativa de pouca diferença de complexidade levantada na Introdução.

**Inovação, verbosidade e estilo (LOC e PMD `codestyle`)**: LOC ficou maior em `com_ia` (mediana 41 vs 31 linhas), confirmando a expectativa de maior verbosidade levantada na Introdução, com efeito grande no teste pareado (r=-0,87, p=0,125) mas não significativo no não pareado (p=0,624), o mesmo padrão de RQ1, um efeito visível que ainda não cruza 0,05 com N=18. Violações de estilo por 100 LOC ficaram um pouco maiores em `com_ia` (mediana 27,27 contra 22,58 de `sem_ia`), mas sem diferença estatística clara, o teste pareado deu efeito médio não significativo (p=0,563) e o não pareado deu efeito negligível (p=0,950). Ou seja, o código com IA saiu mais verboso, mas não claramente menos conforme ao style guide por linha.

**Inovação, correlação tempo x violações**: a hipótese de que "pressa gera mais violações" não se sustentou de forma consistente, a correlação de Spearman deu sinais opostos entre os tratamentos e nenhuma passou no limiar de 0,05 bilateral (a mais próxima, `com_ia`, tempo x violações por KLOC, rho=-0,57, p=0,121), então não há evidência forte de que o tempo do trial, por si só, explique a diferença de conformidade de estilo.

**Inovação, segurança (Semgrep)**: 0 vulnerabilidades encontradas nos 18 trials, `com_ia` e `sem_ia`, resultado esperado dado o escopo pequeno e a natureza dos katas, que não envolvem entrada de rede, banco de dados ou serialização, superfícies mais comuns de vulnerabilidade estática.

**Síntese das inovações**: as seis frentes adicionais (seção 1) não contradisseram os 70% do enunciado, aprofundaram, dando tamanho de efeito onde só havia p-valor, mostrando que a maior verbosidade de `com_ia` é real mas não necessariamente pior em conformidade de estilo, e descartando a hipótese simples de que pressa explica a diferença de estilo observada.

## 5. Conclusão

*ORIENTAÇÃO: Sintetize, em poucos parágrafos, as respostas a todas as RQs (enunciado + inovação do grupo), sem repetir números já discutidos em detalhe — o objetivo aqui é a mensagem final, não os dados brutos. Aponte as principais limitações do estudo (tamanho de amostra, ameaças à validade não mitigadas, período de coleta). Quando o enunciado pedir explicitamente uma postura de consultoria (caso do Lab05, que pede recomendações de melhoria de processo "como se o grupo fosse consultoria para um time real"), inclua recomendações objetivas e acionáveis, não genéricas. Encerre indicando o que o grupo faria diferente com mais tempo ou recursos, e quais das inovações propostas (30%) valeriam a pena expandir em um trabalho futuro.*

*[conteúdo do grupo — substituir este texto]*

## 6. Referências

- ZUSE, Horst. A framework of software measurement. Walter de Gruyter, 2013.
- BASILI, V. R.; CALDIERA, G.; ROMBACH, H. D. The Goal Question Metric Approach. In: Encyclopedia of Software Engineering. Wiley, 1994.
- MCCABE, T. J. A Complexity Measure. IEEE Transactions on Software Engineering, v. SE-2, n. 4, p. 308-320, 1976.
- 