public class CheckoutQueueBalancer {
    public static int[] simulate(int[] filasIniciais, int[] chegadas, int capacidadeMaxima){
        if (filasIniciais.length == 0){
            return new int[]{chegadas.length};
        }
        
        int qtdDesistencias = 0;
        int[] resultado = new int[filasIniciais.length + 1];

        for (int i = 0; i < chegadas.length; i++){
            int atual = chegadas[i];
            int menorFila = -1;
            boolean filaEncontrada = false;
            for (int j = 0; j < filasIniciais.length; j++){
                if ((atual + filasIniciais[j]) <= capacidadeMaxima){
                    filaEncontrada = true;
                    if (menorFila == -1 || filasIniciais[j] < filasIniciais[menorFila]){
                        menorFila = j;
                    }
                }
            }
            if (filaEncontrada) {
                filasIniciais[menorFila] += atual;
            } else {
                qtdDesistencias++;
            }
        }
        for (int i = 0; i < filasIniciais.length; i++){
            resultado[i] = filasIniciais[i];
        }
        resultado[filasIniciais.length] = qtdDesistencias;
        return resultado;
    }
}
