import static org.junit.jupiter.api.Assertions.assertArrayEquals;

import org.junit.jupiter.api.Test;

class CheckoutQueueBalancerTest {

    @Test
    void distribuiClientesPelaFilaMaisVaziaSemEstourarCapacidade() {
        assertArrayEquals(new int[] {5, 5, 0}, CheckoutQueueBalancer.simulate(new int[] {0, 0}, new int[] {5, 3, 2}, 100));
    }

    @Test
    void clienteDesisteQuandoMenorFilaEstouraCapacidade() {
        assertArrayEquals(new int[] {0, 10, 1}, CheckoutQueueBalancer.simulate(new int[] {0, 10}, new int[] {15}, 10));
    }

    @Test
    void clienteEntraQuandoCabeExatamenteNoLimite() {
        assertArrayEquals(new int[] {10, 0}, CheckoutQueueBalancer.simulate(new int[] {0}, new int[] {10}, 10));
    }

    @Test
    void desistenciasAcumulamParaVariosClientes() {
        assertArrayEquals(new int[] {10, 1}, CheckoutQueueBalancer.simulate(new int[] {0}, new int[] {5, 5, 5}, 10));
    }

    @Test
    void semFilasTodosDesistem() {
        assertArrayEquals(new int[] {2}, CheckoutQueueBalancer.simulate(new int[] {}, new int[] {1, 2}, 5));
    }

    @Test
    void escolheAFilaDeMenorTotalMesmoComTotaisIniciaisDiferentes() {
        assertArrayEquals(new int[] {2, 4, 4, 0}, CheckoutQueueBalancer.simulate(new int[] {2, 1, 4}, new int[] {3}, 100));
    }
}
