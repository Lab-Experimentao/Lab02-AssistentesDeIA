import java.util.Arrays;
import java.util.Comparator;

public class PasswordStrength {

    public static String classify(String senha) {
        if (senha == null || senha.length() < 6) {
            return "FRACA";
        }

        boolean hasLower = false, hasUpper = false, hasDigit = false, hasSpecial = false;
        for (int i = 0; i < senha.length(); i++) {
            char c = senha.charAt(i);
            if (Character.isLowerCase(c)) hasLower = true;
            else if (Character.isUpperCase(c)) hasUpper = true;
            else if (Character.isDigit(c)) hasDigit = true;
            else hasSpecial = true;
        }

        int categories = 0;
        if (hasLower) categories++;
        if (hasUpper) categories++;
        if (hasDigit) categories++;
        if (hasSpecial) categories++;

        String level;
        if (categories >= 3 && senha.length() >= 10) {
            level = "FORTE";
        } else if (categories >= 2) {
            level = "MEDIA";
        } else {
            level = "FRACA";
        }

        boolean hasRun = false;
        int run = 1;
        for (int i = 1; i < senha.length(); i++) {
            if (senha.charAt(i) == senha.charAt(i - 1)) {
                run++;
                if (run >= 3) {
                    hasRun = true;
                    break;
                }
            } else {
                run = 1;
            }
        }

        if (hasRun) {
            if (level.equals("FORTE")) level = "MEDIA";
            else if (level.equals("MEDIA")) level = "FRACA";
        }

        return level;
    }

    public static String[] rank(String[] senhas) {
        String[] result = Arrays.copyOf(senhas, senhas.length);

        Comparator<String> comparator = Comparator
                .comparingInt((String s) -> levelOrder(classify(s)))
                .thenComparingInt(String::length)
                .thenComparing(Comparator.naturalOrder());

        Arrays.sort(result, comparator);
        return result;
    }

    private static int levelOrder(String level) {
        switch (level) {
            case "FRACA": return 0;
            case "MEDIA": return 1;
            case "FORTE": return 2;
            default: throw new IllegalStateException("Unknown level: " + level);
        }
    }
}