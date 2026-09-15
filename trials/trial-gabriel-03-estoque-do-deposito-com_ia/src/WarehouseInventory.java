import java.util.HashMap;
import java.util.Map;

public class WarehouseInventory {

    public static String[] process(String[] operacoes) {
        if (operacoes == null) {
            return new String[0];
        }

        Map<String, Integer> totais = new HashMap<>();
        String[] resultados = new String[operacoes.length];

        for (int i = 0; i < operacoes.length; i++) {
            String[] partes = operacoes[i].split(":", 3);
            String tipo = partes[0];
            String item = partes[1];
            int qtd = Integer.parseInt(partes[2]);

            int totalAtual = totais.getOrDefault(item, 0);

            switch (tipo) {
                case "ENTRADA": {
                    int novoTotal = totalAtual + qtd;
                    totais.put(item, novoTotal);
                    resultados[i] = "OK:" + item + ":" + novoTotal;
                    break;
                }
                case "SAIDA": {
                    if (totalAtual >= qtd) {
                        int novoTotal = totalAtual - qtd;
                        totais.put(item, novoTotal);
                        resultados[i] = "OK:" + item + ":" + novoTotal;
                    } else {
                        resultados[i] = "REJEITADA:" + item + ":" + totalAtual;
                    }
                    break;
                }
                case "AJUSTE": {
                    totais.put(item, qtd);
                    resultados[i] = "OK:" + item + ":" + qtd;
                    break;
                }
            }
        }

        return resultados;
    }
}