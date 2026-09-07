# Etiquetas de Preço

Implemente uma classe `PriceTagNormalizer` com o método:

```java
public static int[] normalize(String[] brutos)
```

`brutos` é uma lista de preços digitados de forma inconsistente por
diferentes funcionários. Cada entrada pode vir com espaços sobrando, prefixo
`"R$"`, e vírgula ou ponto como separador decimal. Processe as entradas **na
ordem dada**, uma a uma:

1. Remova espaços nas pontas e o prefixo `"R$"` (se houver).
2. Troque `,` por `.` como separador decimal.
3. Tente interpretar o resultado como número.
4. Se não for um número válido, ou for negativo: conte como **inválido** e
   siga para a próxima entrada.
5. Se o valor (em centavos, `arredondar(valor * 100)`) já apareceu antes em
   uma entrada válida anterior (mesmo valor exato em centavos): conte esta
   repetição como **inválida** também (preço duplicado) e não some de novo.
6. Caso contrário, é a primeira vez que esse valor aparece: aplique desconto
   de 10% (arredondando o resultado) se o valor for **maior ou igual a**
   10000 centavos (R$ 100,00). Some o valor (com ou sem desconto) ao total e
   conte como **válido**.

Retorne `{somaCentavosValidos, quantidadeValidos, quantidadeInvalidos}`.

Exemplo, para
`["R$ 12,50", "12.5", "150,00", "150,00", "abc", "-5", "", "99,99"]`:

| Entrada | Centavos | Situação |
| --- | --- | --- |
| `"R$ 12,50"` | 1250 | válida, primeira vez, sem desconto |
| `"12.5"` | 1250 | inválida, duplicada (mesmo valor de `"R$ 12,50"`) |
| `"150,00"` | 15000 | válida, primeira vez, **com desconto**: soma 13500 |
| `"150,00"` | 15000 | inválida, duplicada |
| `"abc"` | — | inválida, não é número |
| `"-5"` | — | inválida, negativo |
| `""` | — | inválida, vazia |
| `"99,99"` | 9999 | válida, primeira vez, sem desconto (abaixo de 10000) |

Soma: `1250 + 13500 + 9999 = 24749`. Válidos: `3`. Inválidos: `5`.

Resultado: `{24749, 3, 5}`.

Os testes de aceitação estão em `tests/PriceTagNormalizerTest.java`. Sua
solução deve fazer todos passarem.
