import java.util.*;

public class WarehouseInventory {
    public static String[] process(String[] operacoes) {
        if (operacoes == null) {
            return new String[0];
        }

        Map<String, Long> totals = new HashMap<>();
        String[] resultados = new String[operacoes.length];

        for (int i = 0; i < operacoes.length; i++) {
            String[] partes = operacoes[i].split(":", 3);
            String tipo = partes[0];
            String item = partes[1];
            long qtd = Long.parseLong(partes[2]);

            long atual = totals.getOrDefault(item, 0L);

            switch (tipo) {
                case "ENTRADA": {
                    long novoTotal = atual + qtd;
                    totals.put(item, novoTotal);
                    resultados[i] = "OK:" + item + ":" + novoTotal;
                    break;
                }
                case "SAIDA": {
                    if (atual >= qtd) {
                        long novoTotal = atual - qtd;
                        totals.put(item, novoTotal);
                        resultados[i] = "OK:" + item + ":" + novoTotal;
                    } else {
                        resultados[i] = "REJEITADA:" + item + ":" + atual;
                    }
                    break;
                }
                case "AJUSTE": {
                    totals.put(item, qtd);
                    resultados[i] = "OK:" + item + ":" + qtd;
                    break;
                }
                default:
                    throw new IllegalArgumentException("Tipo de operação desconhecido: " + tipo);
            }
        }

        return resultados;
    }
}