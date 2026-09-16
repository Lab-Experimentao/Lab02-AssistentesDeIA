import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class PasswordStrengthTest {

    @Test
    void senhaNulaEFraca() {
        assertEquals("FRACA", PasswordStrength.classify(null));
    }

    @Test
    void senhaVaziaEFraca() {
        assertEquals("FRACA", PasswordStrength.classify(""));
    }

    @Test
    void senhaCurtaEFraca() {
        assertEquals("FRACA", PasswordStrength.classify("abc"));
    }

    @Test
    void duasCategoriasEMedia() {
        assertEquals("MEDIA", PasswordStrength.classify("abcdefg1"));
    }

    @Test
    void tresCategoriasComMenosDe10CaracteresEMedia() {
        assertEquals("MEDIA", PasswordStrength.classify("Abcdefg1"));
    }

    @Test
    void tresCategoriasComDezOuMaisCaracteresEForte() {
        assertEquals("FORTE", PasswordStrength.classify("Abcdefghi1"));
    }

    @Test
    void repeticaoConsecutivaRebaixaDeForteParaMedia() {
        assertEquals("MEDIA", PasswordStrength.classify("Aaaaaaaaa1"));
    }

    @Test
    void quatroCategoriasSemRepeticaoEForte() {
        assertEquals("FORTE", PasswordStrength.classify("Ab1!Ab1!Ab"));
    }

    @Test
    void rankOrdenaPorNivelComDesempateEmCascata() {
        String[] senhas = {"Abcdefghi1", "abc", "abcdefg1", "Ab1!Ab1!Ab", "Aaaaaaaaa1"};
        String[] esperado = {"abc", "abcdefg1", "Aaaaaaaaa1", "Ab1!Ab1!Ab", "Abcdefghi1"};
        assertArrayEquals(esperado, PasswordStrength.rank(senhas));
    }

    @Test
    void rankDesempataPorComprimentoDentroDoMesmoNivel() {
        String[] senhas = {"abcdefgh12", "abcdefg1"};
        String[] esperado = {"abcdefg1", "abcdefgh12"};
        assertArrayEquals(esperado, PasswordStrength.rank(senhas));
    }

    @Test
    void rankNaoModificaOArrayOriginal() {
        String[] senhas = {"abcdefgh12", "abcdefg1"};
        String[] original = senhas.clone();
        PasswordStrength.rank(senhas);
        assertArrayEquals(original, senhas);
    }

    @Test
    void rankDeArrayVazioRetornaVazio() {
        assertArrayEquals(new String[] {}, PasswordStrength.rank(new String[] {}));
    }
}
