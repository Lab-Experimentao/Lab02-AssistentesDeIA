public class ElevatorRouter {
    public static int[] route(int andarInicial, int[] paradas) {
        int distanciaTotal = 0;
        int trocasDeDirecao = 0;
        int paradasInvalidas = 0;
        boolean indoParaCima = true;
        boolean houveMovimento = false;
        int andarAtual = andarInicial;

        for (int i = 0; i < paradas.length; i++){
            int proximaParada = paradas[i];
            if (proximaParada < -2 || proximaParada > 20){
                paradasInvalidas++;
                continue;
            }
            if (proximaParada >= andarAtual){
                distanciaTotal += proximaParada - andarAtual;
                if (houveMovimento && !indoParaCima) trocasDeDirecao++;
                indoParaCima = true;
            } else {
                distanciaTotal += andarAtual - proximaParada;
                if (houveMovimento && indoParaCima) trocasDeDirecao++;
                indoParaCima = false;
            }
            andarAtual = proximaParada;
            houveMovimento = true;
        }

        return new int[]{distanciaTotal, trocasDeDirecao, paradasInvalidas};
    }
}
