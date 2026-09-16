import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class NestedBlockValidatorTest {

    @Test
    void textoSemBlocosTemProfundidadeZero() {
        assertEquals(0, NestedBlockValidator.validate("abc"));
    }

    @Test
    void blocosAninhadosDeTiposDiferentesCalculamProfundidadeMaxima() {
        assertEquals(2, NestedBlockValidator.validate("a(b[c]{d})e"));
    }

    @Test
    void blocosTotalmenteAninhadosDoMesmoTipo() {
        assertEquals(3, NestedBlockValidator.validate("((()))"));
    }

    @Test
    void gruposSequenciaisNaoAninhadosUsamAProfundidadeDeCadaGrupo() {
        assertEquals(1, NestedBlockValidator.validate("()[]{}"));
    }

    @Test
    void fechamentoDeTipoErradoEInvalido() {
        assertEquals(-1, NestedBlockValidator.validate("(]"));
    }

    @Test
    void aberturaSemFechamentoEInvalida() {
        assertEquals(-1, NestedBlockValidator.validate("(()"));
    }

    @Test
    void fechamentoSemAberturaPendenteEInvalido() {
        assertEquals(-1, NestedBlockValidator.validate(")("));
    }

    @Test
    void stringVaziaTemProfundidadeZero() {
        assertEquals(0, NestedBlockValidator.validate(""));
    }
}
