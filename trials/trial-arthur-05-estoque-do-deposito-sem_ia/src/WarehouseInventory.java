import java.util.HashMap;
import java.util.Map;

public class WarehouseInventory {

    public static String[] process(String[] operacoes) {
        if (operacoes == null) {
            return new String[0];
        }

        Map<String, Integer> totais = new HashMap<>();
        String[] resultados = new String[operacoes.length];

        for (int indice = 0; indice < operacoes.length; indice++) {
            String operacao = operacoes[indice];
            String[] partes = operacao.split(":");

            String tipo = partes[0];
            String item = partes[1];
            int quantidade = Integer.parseInt(partes[2]);

            int totalAtual = 0;
            if (totais.containsKey(item)) {
                totalAtual = totais.get(item);
            }

            if (tipo.equals("ENTRADA")) {
                int novoTotal = totalAtual + quantidade;
                totais.put(item, novoTotal);
                String resultado = "OK:" + item + ":" + novoTotal;
                resultados[indice] = resultado;
            } else if (tipo.equals("SAIDA")) {
                if (totalAtual >= quantidade) {
                    int novoTotal = totalAtual - quantidade;
                    totais.put(item, novoTotal);
                    String resultado = "OK:" + item + ":" + novoTotal;
                    resultados[indice] = resultado;
                } else {
                    String resultado = "REJEITADA:" + item + ":" + totalAtual;
                    resultados[indice] = resultado;
                }
            } else if (tipo.equals("AJUSTE")) {
                totais.put(item, quantidade);
                String resultado = "OK:" + item + ":" + quantidade;
                resultados[indice] = resultado;
            }
        }

        return resultados;
    }
}
