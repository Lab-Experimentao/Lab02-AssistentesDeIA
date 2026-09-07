import java.util.HashSet;
import java.util.Set;

public class PriceTagNormalizer {

    private static final int LIMIAR_DESCONTO_CENTAVOS = 10000;
    private static final double PERCENTUAL_DESCONTO = 0.10;

    public static int[] normalize(String[] brutos) {
        long somaCentavos = 0;
        int validos = 0;
        int invalidos = 0;
        Set<Integer> vistos = new HashSet<>();

        if (brutos != null) {
            for (String bruto : brutos) {
                Integer centavos = parsePreco(bruto);
                if (centavos == null) {
                    invalidos++;
                    continue;
                }
                if (!vistos.add(centavos)) {
                    invalidos++;
                    continue;
                }
                somaCentavos += aplicarDesconto(centavos);
                validos++;
            }
        }

        return new int[] {(int) somaCentavos, validos, invalidos};
    }

    private static int aplicarDesconto(int centavos) {
        if (centavos >= LIMIAR_DESCONTO_CENTAVOS) {
            return (int) Math.round(centavos * (1 - PERCENTUAL_DESCONTO));
        }
        return centavos;
    }

    private static Integer parsePreco(String bruto) {
        if (bruto == null) {
            return null;
        }
        String limpo = bruto.trim();
        if (limpo.isEmpty()) {
            return null;
        }
        limpo = limpo.replace("R$", "").trim();
        limpo = limpo.replace(",", ".");

        try {
            double valor = Double.parseDouble(limpo);
            if (valor < 0) {
                return null;
            }
            return (int) Math.round(valor * 100);
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
