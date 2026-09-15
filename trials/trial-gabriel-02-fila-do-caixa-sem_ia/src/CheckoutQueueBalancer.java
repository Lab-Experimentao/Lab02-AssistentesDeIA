public class CheckoutQueueBalancer {
    
    public static int[] simulate(int[] filasIniciais, int[] chegadas, int capacidadeMaxima) {
        int tamanho = filasIniciais.length;
        int[] resultado = new int[tamanho + 1];

        if (tamanho == 0) {
            resultado[0] = chegadas.length;
            return resultado;
        }

        for (int i = 0; i < tamanho; i++) {
            resultado[i] = filasIniciais[i];
        }

        int desistencias = 0;

        for (int chegada : chegadas) {
            int menorIndex = 0;

            for (int i = 1; i < tamanho; i++) {
                if (resultado[i] < resultado[menorIndex]) {
                    menorIndex = i;
                }
            }

            if (resultado[menorIndex] + chegada <= capacidadeMaxima) {
                resultado[menorIndex] += chegada;
            } else {
                desistencias++;
            }
        }

        resultado[tamanho] = desistencias;

        return resultado;
    }
}
