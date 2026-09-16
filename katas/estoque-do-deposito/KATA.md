# Estoque do Depósito

Implemente uma classe `WarehouseInventory` com o método:

```java
public static String[] process(String[] operacoes)
```

Cada elemento de `operacoes` é uma string no formato `"TIPO:item:quantidade"`,
em que `TIPO` é `ENTRADA`, `SAIDA` ou `AJUSTE`, `item` é o nome do produto e
`quantidade` é um inteiro não negativo. Mantenha um total acumulado por item
(nomes distintos têm totais independentes, todo item começa com total `0` até
aparecer pela primeira vez numa operação).

Processe as operações **na ordem dada**, e para cada uma produza uma string de
resultado, seguindo estas regras:

1. **`ENTRADA:item:qtd`**: soma `qtd` ao total do item. Sempre bem-sucedida.
   Resultado: `"OK:item:novoTotal"`.
2. **`SAIDA:item:qtd`**: se o total atual do item for **maior ou igual** a
   `qtd`, subtrai `qtd` do total (bem-sucedida). Caso contrário, a operação é
   **rejeitada** e o total do item **não muda**. Resultado:
   `"OK:item:novoTotal"` ou `"REJEITADA:item:totalAtual"`.
3. **`AJUSTE:item:qtd`**: define o total do item diretamente como `qtd`
   (sobrescreve, sempre bem-sucedida, independente do total anterior).
   Resultado: `"OK:item:qtd"`.

Retorne um array de strings de resultado, uma por operação, na mesma ordem de
`operacoes`. Se `operacoes` for `null`, retorne um array vazio.

Exemplo, para
`["ENTRADA:parafuso:50", "SAIDA:parafuso:20", "SAIDA:parafuso:40", "AJUSTE:parafuso:5", "ENTRADA:prego:5", "SAIDA:prego:2"]`:

| Operação | Total antes | Resultado | Total depois |
| --- | --- | --- | --- |
| `ENTRADA:parafuso:50` | 0 | `OK:parafuso:50` | 50 |
| `SAIDA:parafuso:20` | 50 | `OK:parafuso:30` | 30 |
| `SAIDA:parafuso:40` | 30 | `REJEITADA:parafuso:30` (30 < 40) | 30 |
| `AJUSTE:parafuso:5` | 30 | `OK:parafuso:5` | 5 |
| `ENTRADA:prego:5` | 0 | `OK:prego:5` | 5 |
| `SAIDA:prego:2` | 5 | `OK:prego:3` | 3 |

Resultado final:
`["OK:parafuso:50", "OK:parafuso:30", "REJEITADA:parafuso:30", "OK:parafuso:5", "OK:prego:5", "OK:prego:3"]`.

Os testes de aceitação estão em `tests/WarehouseInventoryTest.java`. Sua
solução deve fazer todos passarem.
