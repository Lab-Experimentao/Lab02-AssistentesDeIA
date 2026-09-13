# Katas do experimento

Seis katas em Java, usados nos trials do experimento (RQ1-RQ3). São
problemas originais do grupo, não exercícios clássicos de LeetCode, para
reduzir o risco de o assistente de IA reproduzir uma solução já vista em
treinamento em vez de efetivamente ajudar.

Os katas se dividem em duas faixas de dificuldade:

* **Katas 1-4** (dificuldade base, resolvíveis por um estudante de graduação
  em até 35 minutos): `cofre-de-senhas`, `elevador-do-predio`,
  `etiquetas-de-preco`, `fila-do-caixa`.
* **Katas 5-6** (dificuldade um pouco maior, introduzem `Map`/pilha em vez de
  só array/String/Set): `estoque-do-deposito`, `blocos-aninhados`.

Número par para permitir a divisão exata pela metade entre trials com e sem
assistente de IA: 3 katas com IA e 3 sem IA por integrante, em ordem
contrabalanceada, ver [README.md principal](../README.md).

## Lista

| Kata | Pasta | Tema | Domínio técnico |
| --- | --- | --- | --- |
| Cofre de Senhas | `cofre-de-senhas` | Classificar força de senha por regras | strings, contadores |
| Elevador do Prédio | `elevador-do-predio` | Distância percorrida e trocas de direção | array, sinal/direção |
| Etiquetas de Preço | `etiquetas-de-preco` | Normalizar preços em formatos inconsistentes | parsing de string, validação |
| Fila do Caixa | `fila-do-caixa` | Balancear chegadas entre filas | array, simulação simples |
| Estoque do Depósito | `estoque-do-deposito` | Processar operações de entrada/saída/ajuste num inventário | `Map`, múltiplos tipos de operação, estado condicional |
| Blocos Aninhados | `blocos-aninhados` | Validar aninhamento de `()`/`[]`/`{}` e calcular profundidade máxima | pilha (`Deque`), validação com estado |

Os katas 1-4 têm complexidade comparável entre si: 1-2 métodos estáticos por
kata (o Cofre de Senhas tem dois: `classify` e `rank`), sem I/O, sem
bibliotecas externas, resolvíveis com laços, condicionais, comparadores e
arrays/strings da biblioteca padrão do Java. Nenhum depende de estrutura de
dados além de array/String/Set. Os quatro cobrem domínios técnicos distintos
entre si (regras condicionais + ordenação, array/direção com validação de
intervalo, parsing/validação com desconto e deduplicação, simulação com laço
aninhado e condição de capacidade), para não repetir o mesmo tipo de
raciocínio em mais de um kata. Cada um foi calibrado para ficar perto do teto
do time-box de 35 minutos quando resolvido manualmente, deixando espaço real
para o assistente de IA mostrar ganho de tempo (RQ1) sem estourar o limite
com frequência.

Os katas 5-6 sobem um degrau de dificuldade em relação aos 1-4: introduzem
uma estrutura de dados adicional (`HashMap` no Estoque do Depósito, pilha via
`ArrayDeque` nos Blocos Aninhados), continuando com 1 método estático, sem
I/O e sem bibliotecas externas além da coleção usada. Cobrem domínios
técnicos que os katas 1-4 não cobrem (acumulação com múltiplos tipos de
operação sobre um mapa; validação de aninhamento e profundidade via pilha),
então servem também para diversificar o tipo de raciocínio exigido no
experimento. Como o time-box é fixo em 35 min para todos os katas (só pode
ser reduzido, nunca aumentado, ver [README.md principal](../README.md)), o
Estoque do Depósito foi deliberadamente simplificado (regras uniformes para
`ENTRADA`/`SAIDA`/`AJUSTE`, sem pré-condição extra em `AJUSTE`) para caber no
mesmo teto sem aumentar o risco de censura.

## Estrutura de cada kata

```
katas/<kata>/
  KATA.md              enunciado entregue ao participante (inclui a assinatura exigida)
  reference/*.java     solução de referência correta, usada só para validar os testes
  tests/*.java         testes de aceitação JUnit 5, entregues ao participante
```

**Importante:** durante o trial, o participante recebe apenas `KATA.md` e
`tests/`. A pasta `reference/` não é distribuída, ela existe unicamente para
o script `scripts/verify_katas.sh` confirmar que os testes de aceitação estão
corretos e passam contra uma solução válida, antes do experimento começar.

## Verificação antes do experimento

Rode, a partir da raiz do repositório:

```
scripts/verify_katas.sh
```

O script compila `reference/` + `tests/` de cada kata, roda os testes com o
JUnit Platform Console Standalone e confirma que todos passam contra a
solução de referência. Se algum kata falhar (erro de compilação ou teste
quebrando mesmo com a solução correta), o script termina com código de saída
diferente de zero e aponta qual kata precisa de correção. Nenhum trial deve
começar antes desse script rodar limpo para os 6 katas.

