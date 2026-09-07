import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

public class PasswordStrength {

    private static final Map<String, Integer> NIVEL_ORDEM = new HashMap<>();
    static {
        NIVEL_ORDEM.put("FRACA", 0);
        NIVEL_ORDEM.put("MEDIA", 1);
        NIVEL_ORDEM.put("FORTE", 2);
    }

    public static String classify(String senha) {
        if (senha == null || senha.length() < 6) {
            return "FRACA";
        }

        boolean lower = false;
        boolean upper = false;
        boolean digit = false;
        boolean special = false;
        for (char c : senha.toCharArray()) {
            if (Character.isLowerCase(c)) {
                lower = true;
            } else if (Character.isUpperCase(c)) {
                upper = true;
            } else if (Character.isDigit(c)) {
                digit = true;
            } else {
                special = true;
            }
        }

        int categorias = 0;
        if (lower) categorias++;
        if (upper) categorias++;
        if (digit) categorias++;
        if (special) categorias++;

        String nivel;
        if (categorias >= 3 && senha.length() >= 10) {
            nivel = "FORTE";
        } else if (categorias >= 2) {
            nivel = "MEDIA";
        } else {
            nivel = "FRACA";
        }

        if (temRepeticaoConsecutiva(senha, 3)) {
            nivel = rebaixar(nivel);
        }
        return nivel;
    }

    public static String[] rank(String[] senhas) {
        if (senhas == null) {
            return new String[0];
        }

        String[] copia = senhas.clone();
        Arrays.sort(copia, Comparator
            .comparingInt((String s) -> NIVEL_ORDEM.get(classify(s)))
            .thenComparingInt(String::length)
            .thenComparing(Comparator.naturalOrder()));
        return copia;
    }

    private static boolean temRepeticaoConsecutiva(String senha, int minRepeticoes) {
        int contagem = 1;
        for (int i = 1; i < senha.length(); i++) {
            if (senha.charAt(i) == senha.charAt(i - 1)) {
                contagem++;
                if (contagem >= minRepeticoes) {
                    return true;
                }
            } else {
                contagem = 1;
            }
        }
        return false;
    }

    private static String rebaixar(String nivel) {
        if (nivel.equals("FORTE")) {
            return "MEDIA";
        }
        return "FRACA";
    }
}
