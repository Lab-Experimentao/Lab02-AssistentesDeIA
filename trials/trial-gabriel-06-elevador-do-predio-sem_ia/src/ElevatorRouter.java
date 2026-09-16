public class ElevatorRouter {

    public static int[] route(int andarInicial, int[] paradas) {
        int distanciaTotal = 0;
        int trocasDirecao = 0;
        int paradasInvalidas = 0;
        
        int andarAtual = andarInicial;
        int direcaoAtual = 0;

        if (paradas != null) {
            for (int parada : paradas) {
                if (parada < -2 || parada > 20) {
                    paradasInvalidas++;
                    continue;
                }

                if (parada == andarAtual) {
                    continue;
                }

                distanciaTotal += Math.abs(parada - andarAtual);

                int novaDirecao = (parada > andarAtual) ? 1 : -1;

                if (direcaoAtual != 0 && novaDirecao != direcaoAtual) {
                    trocasDirecao++;
                }

                direcaoAtual = novaDirecao;
                andarAtual = parada;
            }
        }

        return new int[]{distanciaTotal, trocasDirecao, paradasInvalidas};
    }
    
}
