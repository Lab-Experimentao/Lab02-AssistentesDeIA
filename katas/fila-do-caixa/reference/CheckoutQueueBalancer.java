public class CheckoutQueueBalancer {

    public static int[] simulate(int[] filasIniciais, int[] chegadas, int capacidadeMaxima) {
        int[] filas = filasIniciais == null ? new int[0] : filasIniciais.clone();
        int desistencias = 0;

        if (chegadas != null) {
            for (int tempo : chegadas) {
                int indiceMenor = indiceDaFilaMenor(filas);
                if (indiceMenor == -1 || filas[indiceMenor] + tempo > capacidadeMaxima) {
                    desistencias++;
                } else {
                    filas[indiceMenor] += tempo;
                }
            }
        }

        int[] resultado = new int[filas.length + 1];
        System.arraycopy(filas, 0, resultado, 0, filas.length);
        resultado[filas.length] = desistencias;
        return resultado;
    }

    private static int indiceDaFilaMenor(int[] filas) {
        int indice = -1;
        for (int i = 0; i < filas.length; i++) {
            if (indice == -1 || filas[i] < filas[indice]) {
                indice = i;
            }
        }
        return indice;
    }
}
