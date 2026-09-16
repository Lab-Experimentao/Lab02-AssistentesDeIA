public class CheckoutQueueBalancer {

    public static int[] simulate(int[] filasIniciais, int[] chegadas, int capacidadeMaxima) {
        int numFilas = filasIniciais.length;
        int[] totais = filasIniciais.clone();
        int desistencias = 0;

        for (int tempoCliente : chegadas) {
            if (numFilas == 0) {
                desistencias++;
                continue;
            }

            int indiceMenor = 0;
            for (int i = 1; i < numFilas; i++) {
                if (totais[i] < totais[indiceMenor]) {
                    indiceMenor = i;
                }
            }

            if (totais[indiceMenor] + tempoCliente > capacidadeMaxima) {
                desistencias++;
            } else {
                totais[indiceMenor] += tempoCliente;
            }
        }

        int[] resultado = new int[numFilas + 1];
        System.arraycopy(totais, 0, resultado, 0, numFilas);
        resultado[numFilas] = desistencias;
        return resultado;
    }
}