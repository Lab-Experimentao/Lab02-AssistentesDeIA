# Fila do Caixa

Implemente uma classe `CheckoutQueueBalancer` com o método:

```java
public static int[] simulate(int[] filasIniciais, int[] chegadas, int capacidadeMaxima)
```

`filasIniciais` representa o tempo total (em minutos) já acumulado em cada
fila de caixa. `chegadas` é a sequência, em ordem, do tempo de atendimento de
cada novo cliente que chega. `capacidadeMaxima` é o tempo máximo (em minutos)
que qualquer fila pode acumular.

Para cada cliente, nessa ordem:

1. Encontre a fila com **menor tempo total acumulado no momento** (em caso de
   empate, a de menor índice).
2. Se o tempo desse cliente, somado ao total dessa fila, **ultrapassar**
   `capacidadeMaxima`, o cliente **desiste** (não entra em nenhuma fila — pela
   forma como a fila de menor total é escolhida, se ela não comporta o
   cliente, nenhuma outra fila comporta também).
3. Caso contrário, o cliente entra nessa fila, e o tempo dele é somado ao
   total dela.

Retorne um array com o tempo final de cada fila (na mesma ordem de
`filasIniciais`), seguido de mais uma posição no final com a **quantidade de
clientes que desistiram**. Ou seja, o array de retorno tem sempre
`filasIniciais.length + 1` posições. Se `filasIniciais` for vazio, todo
cliente que chegar desiste (não há fila para entrar).

Exemplos:

| filasIniciais | chegadas | capacidadeMaxima | resultado |
| --- | --- | --- | --- |
| `[0, 0]` | `[5, 3, 2]` | `100` | `[5, 5, 0]` |
| `[0, 10]` | `[15]` | `10` | `[0, 10, 1]` |
| `[0]` | `[10]` | `10` | `[10, 0]` |
| `[0]` | `[5, 5, 5]` | `10` | `[10, 1]` |
| `[]` | `[1, 2]` | `5` | `[2]` |

No quarto exemplo: o 1º cliente (5) entra, fila fica em 5. O 2º cliente (5)
entra, fila fica em 10 (exatamente no limite, permitido). O 3º cliente (5)
faria a fila passar de 10 para 15, o que ultrapassa `capacidadeMaxima = 10`,
então desiste. Resultado: fila final `10`, `1` desistência.

Os testes de aceitação estão em `tests/CheckoutQueueBalancerTest.java`. Sua
solução deve fazer todos passarem.
