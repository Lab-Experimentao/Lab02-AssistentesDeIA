import java.util.HashSet;
import java.util.Set;

public class PriceTagNormalizer {

    public static int[] normalize(String[] brutos) {
        long somaCentavos = 0;
        int validos = 0;
        int invalidos = 0;
        Set<Long> vistos = new HashSet<>();

        for (String bruto : brutos) {
            String s = (bruto == null) ? "" : bruto.trim();

            if (s.startsWith("R$")) {
                s = s.substring(2).trim();
            }

            s = s.replace(",", ".");

            double valor;
            try {
                if (s.isEmpty()) {
                    throw new NumberFormatException();
                }
                valor = Double.parseDouble(s);
            } catch (NumberFormatException e) {
                invalidos++;
                continue;
            }

            if (valor < 0) {
                invalidos++;
                continue;
            }

            long centavos = Math.round(valor * 100);

            if (vistos.contains(centavos)) {
                invalidos++;
                continue;
            }

            vistos.add(centavos);

            long valorFinal = centavos;
            if (centavos >= 10000) {
                valorFinal = Math.round(centavos * 0.9);
            }

            somaCentavos += valorFinal;
            validos++;
        }

        return new int[]{(int) somaCentavos, validos, invalidos};
    }
}