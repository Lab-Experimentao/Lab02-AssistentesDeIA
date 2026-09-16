import java.util.Arrays;
import java.util.Comparator;

public class PasswordStrength {

    public static String classify(String senha) {
        if (senha == null || senha.length() < 6) {
            return "FRACA";
        }

        boolean temMinuscula = false;
        boolean temMaiuscula = false;
        boolean temDigito = false;
        boolean temEspecial = false;

        for (int i = 0; i < senha.length(); i++) {
            char c = senha.charAt(i);
            if (Character.isLowerCase(c)) {
                temMinuscula = true;
            } else if (Character.isUpperCase(c)) {
                temMaiuscula = true;
            } else if (Character.isDigit(c)) {
                temDigito = true;
            } else {
                temEspecial = true;
            }
        }

        int categorias = 0;
        if (temMinuscula) categorias++;
        if (temMaiuscula) categorias++;
        if (temDigito) categorias++;
        if (temEspecial) categorias++;

        String nivel;
        if (categorias >= 3 && senha.length() >= 10) {
            nivel = "FORTE";
        } else if (categorias >= 2) {
            nivel = "MEDIA";
        } else {
            nivel = "FRACA";
        }

        boolean temRepeticao = false;
        int consecutivos = 1;
        for (int i = 1; i < senha.length(); i++) {
            if (senha.charAt(i) == senha.charAt(i - 1)) {
                consecutivos++;
                if (consecutivos >= 3) {
                    temRepeticao = true;
                    break;
                }
            } else {
                consecutivos = 1;
            }
        }

        if (temRepeticao) {
            if (nivel.equals("FORTE")) {
                nivel = "MEDIA";
            } else if (nivel.equals("MEDIA")) {
                nivel = "FRACA";
            }
        }

        return nivel;
    }

    public static String[] rank(String[] senhas) {
        String[] copia = Arrays.copyOf(senhas, senhas.length);

        Arrays.sort(copia, Comparator
                .comparingInt((String s) -> nivelOrdinal(classify(s)))
                .thenComparingInt(String::length)
                .thenComparing(Comparator.naturalOrder()));

        return copia;
    }

    private static int nivelOrdinal(String nivel) {
        switch (nivel) {
            case "FRACA":
                return 0;
            case "MEDIA":
                return 1;
            case "FORTE":
                return 2;
            default:
                return -1;
        }
    }
}