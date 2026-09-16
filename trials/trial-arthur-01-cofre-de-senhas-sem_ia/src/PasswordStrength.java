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

        for (char caractere : senha.toCharArray()) {
            if (Character.isLowerCase(caractere)) {
                temMinuscula = true;
            } else if (Character.isUpperCase(caractere)) {
                temMaiuscula = true;
            } else if (Character.isDigit(caractere)) {
                temDigito = true;
            } else {
                temEspecial = true;
            }
        }

        int quantidadeCategorias = 0;
        if (temMinuscula) {
            quantidadeCategorias++;
        }
        if (temMaiuscula) {
            quantidadeCategorias++;
        }
        if (temDigito) {
            quantidadeCategorias++;
        }
        if (temEspecial) {
            quantidadeCategorias++;
        }

        String nivel;
        if (quantidadeCategorias >= 3 && senha.length() >= 10) {
            nivel = "FORTE";
        } else if (quantidadeCategorias >= 2) {
            nivel = "MEDIA";
        } else {
            nivel = "FRACA";
        }

        int repeticaoConsecutiva = 1;
        for (int i = 1; i < senha.length(); i++) {
            if (senha.charAt(i) == senha.charAt(i - 1)) {
                repeticaoConsecutiva++;
                if (repeticaoConsecutiva >= 3) {
                    if (nivel.equals("FORTE")) {
                        nivel = "MEDIA";
                    } else if (nivel.equals("MEDIA")) {
                        nivel = "FRACA";
                    }
                    break;
                }
            } else {
                repeticaoConsecutiva = 1;
            }
        }

        return nivel;
    }

    public static String[] rank(String[] senhas) {
        String[] copia = Arrays.copyOf(senhas, senhas.length);

        Arrays.sort(copia, new Comparator<String>() {
            @Override
            public int compare(String senha1, String senha2) {
                int nivel1 = converterNivel(classify(senha1));
                int nivel2 = converterNivel(classify(senha2));

                if (nivel1 != nivel2) {
                    return Integer.compare(nivel1, nivel2);
                }

                if (senha1.length() != senha2.length()) {
                    return Integer.compare(senha1.length(), senha2.length());
                }

                return senha1.compareTo(senha2);
            }

            private int converterNivel(String nivel) {
                if (nivel.equals("FRACA")) {
                    return 0;
                }
                if (nivel.equals("MEDIA")) {
                    return 1;
                }
                if (nivel.equals("FORTE")) {
                    return 2;
                }
                return -1;
            }
        });

        return copia;
    }
}
