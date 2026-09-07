import static org.junit.jupiter.api.Assertions.assertArrayEquals;

import org.junit.jupiter.api.Test;

class ElevatorRouterTest {

    @Test
    void calculaDistanciaETrocasDeDirecao() {
        assertArrayEquals(new int[] {9, 2, 0}, ElevatorRouter.route(0, new int[] {3, 1, 5}));
    }

    @Test
    void semParadasNaoAndaNemTroca() {
        assertArrayEquals(new int[] {0, 0, 0}, ElevatorRouter.route(5, new int[] {}));
    }

    @Test
    void pararNoMesmoAndarNaoConta() {
        assertArrayEquals(new int[] {0, 0, 0}, ElevatorRouter.route(5, new int[] {5, 5}));
    }

    @Test
    void mesmaDirecaoNaoGeraTroca() {
        assertArrayEquals(new int[] {6, 0, 0}, ElevatorRouter.route(0, new int[] {2, 4, 6}));
    }

    @Test
    void paradaZeroNoMeioNaoQuebraADirecaoCorrente() {
        assertArrayEquals(new int[] {6, 0, 0}, ElevatorRouter.route(0, new int[] {3, 3, 6}));
    }

    @Test
    void limitesDoPredioSaoValidosInclusive() {
        assertArrayEquals(new int[] {24, 1, 0}, ElevatorRouter.route(0, new int[] {-2, 20}));
    }

    @Test
    void paradasForaDoIntervaloSaoDescartadasEContadas() {
        assertArrayEquals(new int[] {5, 1, 2}, ElevatorRouter.route(0, new int[] {25, 3, -5, 1}));
    }

    @Test
    void todasAsParadasInvalidasNaoMovemOElevador() {
        assertArrayEquals(new int[] {0, 0, 2}, ElevatorRouter.route(0, new int[] {21, -3}));
    }
}
