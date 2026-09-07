# Cofre de Senhas

Implemente uma classe `PasswordStrength` com dois métodos:

```java
public static String classify(String senha)
public static String[] rank(String[] senhas)
```

## `classify`

Classifica a força de uma senha em `"FRACA"`, `"MEDIA"` ou `"FORTE"`,
seguindo as regras abaixo, nessa ordem:

1. Senha `null` ou com menos de 6 caracteres: sempre `"FRACA"`.
2. Conte quantas das 4 categorias de caractere aparecem na senha: letra
   minúscula, letra maiúscula, dígito, caractere especial (qualquer coisa que
   não seja letra nem dígito).
3. Nível base:
   - 3 ou mais categorias **e** comprimento >= 10: `"FORTE"`.
   - 2 ou mais categorias (com comprimento >= 6, já garantido pela regra 1):
     `"MEDIA"`.
   - Caso contrário: `"FRACA"`.
4. Se a senha tiver 3 ou mais caracteres iguais **consecutivos** (ex.:
   `"aaa"`), rebaixe um nível: `FORTE` vira `MEDIA`, `MEDIA` vira `FRACA`.
   `FRACA` continua `FRACA`.

Exemplos:

| Senha | Resultado |
| --- | --- |
| `""` | `FRACA` |
| `"abc"` | `FRACA` |
| `"abcdefg1"` | `MEDIA` |
| `"Abcdefghi1"` | `FORTE` |
| `"Aaaaaaaaa1"` | `MEDIA` (seria FORTE, mas rebaixa por repetição) |
| `"Ab1!Ab1!Ab"` | `FORTE` |

## `rank`

Recebe um array de senhas (nenhuma delas `null`) e devolve um **novo** array
com as mesmas senhas ordenadas da mais fraca para a mais forte, usando o
resultado de `classify` como critério principal (`FRACA` < `MEDIA` <
`FORTE`). Em caso de empate no nível, use, nesta ordem:

1. Comprimento da senha, da menor para a maior.
2. Se o comprimento também empatar, ordem alfabética padrão do Java
   (`String.compareTo`, sensível a maiúsculas/minúsculas).

Não modifique o array recebido.

Exemplo, para
`["Abcdefghi1", "abc", "abcdefg1", "Ab1!Ab1!Ab", "Aaaaaaaaa1"]`:

- Níveis: `Abcdefghi1` = FORTE, `abc` = FRACA, `abcdefg1` = MEDIA,
  `Ab1!Ab1!Ab` = FORTE, `Aaaaaaaaa1` = MEDIA (rebaixada por repetição).
- FRACA: `abc`.
- MEDIA, por comprimento: `abcdefg1` (8), `Aaaaaaaaa1` (10).
- FORTE, mesmo comprimento (10), por ordem alfabética: `Ab1!Ab1!Ab` vem antes
  de `Abcdefghi1` (o caractere `'1'` vem antes de `'c'` na comparação).

Resultado: `["abc", "abcdefg1", "Aaaaaaaaa1", "Ab1!Ab1!Ab", "Abcdefghi1"]`.

Os testes de aceitação estão em `tests/PasswordStrengthTest.java`. Sua
solução deve fazer todos passarem.
