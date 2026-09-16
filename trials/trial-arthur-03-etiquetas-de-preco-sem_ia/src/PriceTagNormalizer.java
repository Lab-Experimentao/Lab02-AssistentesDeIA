import java.util.HashSet;
import java.util.Set;

public class PriceTagNormalizer {

    public static int[] normalize(String[] brutos) {
        int soma = 0;
        int validos = 0;
        int invalidos = 0;
        Set<Integer> vistos = new HashSet<>();

        for (String entrada : brutos) {
            if (entrada == null) {
                invalidos++;
                continue;
            }

            String limpa = entrada.trim();
            if (limpa.startsWith("R$")) {
                limpa = limpa.substring(2).trim();
            }
            limpa = limpa.replace(',', '.');

            if (limpa.isEmpty()) {
                invalidos++;
                continue;
            }

            double valor;
            try {
                valor = Double.parseDouble(limpa);
            } catch (NumberFormatException e) {
                invalidos++;
                continue;
            }

            if (valor < 0) {
                invalidos++;
                continue;
            }

            int centavos = (int) Math.round(valor * 100);

            if (vistos.contains(centavos)) {
                invalidos++;
                continue;
            }

            vistos.add(centavos);

            int valorFinal = centavos;
            if (centavos >= 10000) {
                valorFinal = (int) Math.round(centavos * 0.9);
            }

            soma += valorFinal;
            validos++;
        }

        return new int[]{soma, validos, invalidos};
    }
}
