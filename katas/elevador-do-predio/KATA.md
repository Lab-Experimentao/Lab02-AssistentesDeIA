# Elevador do Prédio

Implemente uma classe `ElevatorRouter` com o método:

```java
public static int[] route(int andarInicial, int[] paradas)
```

O prédio só tem andares entre **-2** (segundo subsolo) e **20** (último
andar), inclusive. Considere `andarInicial` sempre válido.

O elevador visita cada andar de `paradas`, **na ordem dada** (sem
reordenar). Antes de mover o elevador, descarte qualquer parada fora do
intervalo `[-2, 20]`: ela não conta no trajeto, não altera o andar atual do
elevador, mas é contada à parte. Calcule:

- `distanciaTotal`: soma da distância (em andares) percorrida entre cada
  parada válida consecutiva (incluindo a saída de `andarInicial`), ignorando
  paradas descartadas.
- `trocasDeDirecao`: quantas vezes o elevador muda de sentido (de subir para
  descer, ou vice-versa) entre um trecho válido e o seguinte. Trechos de
  distância zero (parar no mesmo andar em que já está) não contam como
  movimento e não alteram a direção corrente.
- `paradasInvalidas`: quantidade de andares em `paradas` fora do intervalo
  `[-2, 20]`.

Retorne `{distanciaTotal, trocasDeDirecao, paradasInvalidas}`.

Exemplos:

| andarInicial | paradas | resultado |
| --- | --- | --- |
| `0` | `[3, 1, 5]` | `{9, 2, 0}` |
| `5` | `[]` | `{0, 0, 0}` |
| `5` | `[5, 5]` | `{0, 0, 0}` |
| `0` | `[2, 4, 6]` | `{6, 0, 0}` |
| `0` | `[-2, 20]` | `{24, 1, 0}` |
| `0` | `[25, 3, -5, 1]` | `{5, 1, 2}` |

No último exemplo: `25` é descartada (fora do intervalo, `paradasInvalidas`
vira 1), o elevador vai de `0` a `3` (distância 3, subindo), `-5` é
descartada (`paradasInvalidas` vira 2), e por fim vai de `3` a `1`
(distância 2, descendo — 1 troca de direção). Total: distância `5`, `1`
troca, `2` paradas inválidas.

Os testes de aceitação estão em `tests/ElevatorRouterTest.java`. Sua solução
deve fazer todos passarem.
