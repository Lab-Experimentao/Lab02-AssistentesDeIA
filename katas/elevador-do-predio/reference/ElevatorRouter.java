public class ElevatorRouter {

    private static final int ANDAR_MINIMO = -2;
    private static final int ANDAR_MAXIMO = 20;

    public static int[] route(int andarInicial, int[] paradas) {
        if (paradas == null || paradas.length == 0) {
            return new int[] {0, 0, 0};
        }

        int distanciaTotal = 0;
        int trocas = 0;
        int invalidas = 0;
        int atual = andarInicial;
        Integer direcaoAnterior = null;

        for (int parada : paradas) {
            if (parada < ANDAR_MINIMO || parada > ANDAR_MAXIMO) {
                invalidas++;
                continue;
            }

            int diff = parada - atual;
            if (diff != 0) {
                int direcao = diff > 0 ? 1 : -1;
                distanciaTotal += Math.abs(diff);
                if (direcaoAnterior != null && direcao != direcaoAnterior) {
                    trocas++;
                }
                direcaoAnterior = direcao;
            }
            atual = parada;
        }

        return new int[] {distanciaTotal, trocas, invalidas};
    }
}
