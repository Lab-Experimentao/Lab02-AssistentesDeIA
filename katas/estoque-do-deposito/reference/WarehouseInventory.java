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
            String[] partes = operacoes[i].split(":");
            String tipo = partes[0];
            String item = partes[1];
            int quantidade = Integer.parseInt(partes[2]);

            int totalAtual = totais.getOrDefault(item, 0);

            switch (tipo) {
                case "ENTRADA":
                    totalAtual += quantidade;
                    totais.put(item, totalAtual);
                    resultados[i] = "OK:" + item + ":" + totalAtual;
                    break;
                case "SAIDA":
                    if (totalAtual >= quantidade) {
                        totalAtual -= quantidade;
                        totais.put(item, totalAtual);
                        resultados[i] = "OK:" + item + ":" + totalAtual;
                    } else {
                        resultados[i] = "REJEITADA:" + item + ":" + totalAtual;
                    }
                    break;
                case "AJUSTE":
                    totais.put(item, quantidade);
                    resultados[i] = "OK:" + item + ":" + quantidade;
                    break;
                default:
                    resultados[i] = "REJEITADA:" + item + ":" + totalAtual;
            }
        }

        return resultados;
    }
}
