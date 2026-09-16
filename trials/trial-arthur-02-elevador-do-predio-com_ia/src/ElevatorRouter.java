public class ElevatorRouter {

    private static final int ANDAR_MIN = -2;
    private static final int ANDAR_MAX = 20;

    public static int[] route(int andarInicial, int[] paradas) {
        int andarAtual = andarInicial;
        int direcaoAtual = 0; // 0 = nenhuma, 1 = subindo, -1 = descendo
        int distanciaTotal = 0;
        int trocasDeDirecao = 0;
        int paradasInvalidas = 0;

        for (int parada : paradas) {
            if (parada < ANDAR_MIN || parada > ANDAR_MAX) {
                paradasInvalidas++;
                continue;
            }

            int deslocamento = parada - andarAtual;
            if (deslocamento != 0) {
                int novaDirecao = deslocamento > 0 ? 1 : -1;
                if (direcaoAtual != 0 && novaDirecao != direcaoAtual) {
                    trocasDeDirecao++;
                }
                direcaoAtual = novaDirecao;
                distanciaTotal += Math.abs(deslocamento);
                andarAtual = parada;
            }
        }

        return new int[] { distanciaTotal, trocasDeDirecao, paradasInvalidas };
    }
}