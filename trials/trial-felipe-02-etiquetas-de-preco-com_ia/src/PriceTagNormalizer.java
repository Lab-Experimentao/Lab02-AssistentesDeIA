import java.util.HashSet;
import java.util.Set;

public class PriceTagNormalizer {

    public static int[] normalize(String[] brutos) {
        long somaCentavosValidos = 0;
        int quantidadeValidos = 0;
        int quantidadeInvalidos = 0;
        Set<Long> vistos = new HashSet<>();

        for (String bruto : brutos) {
            String s = bruto == null ? "" : bruto.trim();

            if (s.startsWith("R$")) {
                s = s.substring(2).trim();
            }

            s = s.replace(',', '.');

            double valor;
            try {
                if (s.isEmpty()) {
                    throw new NumberFormatException("vazio");
                }
                valor = Double.parseDouble(s);
            } catch (NumberFormatException e) {
                quantidadeInvalidos++;
                continue;
            }

            if (valor < 0) {
                quantidadeInvalidos++;
                continue;
            }

            long centavos = Math.round(valor * 100.0);

            if (vistos.contains(centavos)) {
                quantidadeInvalidos++;
                continue;
            }

            vistos.add(centavos);

            long valorFinal = centavos;
            if (centavos >= 10000) {
                valorFinal = Math.round(centavos * 0.9);
            }

            somaCentavosValidos += valorFinal;
            quantidadeValidos++;
        }

        return new int[] {
            (int) somaCentavosValidos,
            quantidadeValidos,
            quantidadeInvalidos
        };
    }
}