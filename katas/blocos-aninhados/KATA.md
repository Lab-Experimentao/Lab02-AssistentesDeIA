# Blocos Aninhados

Implemente uma classe `NestedBlockValidator` com o método:

```java
public static int validate(String expressao)
```

`expressao` pode conter qualquer caractere, mas só os caracteres `(`, `)`,
`[`, `]`, `{` e `}` são considerados "blocos"; todos os outros caracteres são
ignorados (não afetam a validade nem a profundidade).

Um bloco de abertura (`(`, `[`, `{`) precisa ser fechado pelo bloco de
fechamento do **mesmo tipo** (`)`, `]`, `}`, respectivamente), respeitando o
aninhamento: o fechamento sempre corresponde à abertura mais recente ainda não
fechada (como uma pilha).

Regras:

1. Se um caractere de fechamento aparecer sem nenhuma abertura pendente, ou
   fechando um tipo diferente do que está pendente no topo, a expressão é
   **inválida**.
2. Se, ao final da expressão, sobrar alguma abertura sem o fechamento
   correspondente, a expressão também é **inválida**.
3. Se a expressão for inválida (regra 1 ou 2), retorne `-1`.
4. Se a expressão for válida (incluindo o caso de não ter blocos nenhum),
   retorne a **profundidade máxima de aninhamento** atingida em qualquer
   ponto: a profundidade aumenta em 1 a cada abertura e diminui em 1 a cada
   fechamento correspondente; o retorno é o maior valor que a profundidade
   assume durante todo o processamento (`0` se não houver blocos).

Exemplos:

| `expressao` | Resultado | Motivo |
| --- | --- | --- |
| `"abc"` | `0` | sem blocos |
| `"a(b[c]{d})e"` | `2` | profundidade máxima em `[c]` ou `{d}`, dentro de um `(...)` |
| `"((()))"` | `3` | três aberturas aninhadas do mesmo tipo |
| `"()[]{}"` | `1` | grupos sequenciais, nunca aninhados entre si |
| `"(]"` | `-1` | fecha `)` esperado, veio `]` |
| `"(()"` | `-1` | sobra uma abertura `(` sem fechamento |
| `")("` | `-1` | fechamento sem abertura pendente |

Os testes de aceitação estão em `tests/NestedBlockValidatorTest.java`. Sua
solução deve fazer todos passarem.
