import static org.junit.jupiter.api.Assertions.assertArrayEquals;

import org.junit.jupiter.api.Test;

class PriceTagNormalizerTest {

    @Test
    void normalizaFormatosMistosComDescontoEDuplicataEInvalidos() {
        String[] brutos = {"R$ 12,50", "12.5", "150,00", "150,00", "abc", "-5", "", "99,99"};
        assertArrayEquals(new int[] {24749, 3, 5}, PriceTagNormalizer.normalize(brutos));
    }

    @Test
    void listaVaziaResultaEmZeros() {
        assertArrayEquals(new int[] {0, 0, 0}, PriceTagNormalizer.normalize(new String[] {}));
    }

    @Test
    void descontoAplicadoAcimaDoLimiar() {
        assertArrayEquals(new int[] {13500, 1, 0}, PriceTagNormalizer.normalize(new String[] {"150,00"}));
    }

    @Test
    void limiarDeDescontoEInclusivo() {
        assertArrayEquals(new int[] {9000, 1, 0}, PriceTagNormalizer.normalize(new String[] {"100,00"}));
    }

    @Test
    void semDescontoAbaixoDoLimiar() {
        assertArrayEquals(new int[] {9999, 1, 0}, PriceTagNormalizer.normalize(new String[] {"99,99"}));
    }

    @Test
    void duplicataMesmoValorContaComoInvalida() {
        String[] brutos = {"12,50", "R$ 12,50"};
        assertArrayEquals(new int[] {1250, 1, 1}, PriceTagNormalizer.normalize(brutos));
    }

    @Test
    void todosInvalidos() {
        String[] brutos = {"", "xyz", "-1,00"};
        assertArrayEquals(new int[] {0, 0, 3}, PriceTagNormalizer.normalize(brutos));
    }
}
