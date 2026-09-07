import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class FizzBuzzTest {

    @Test
    void multiploDeTres() {
        assertEquals("Fizz", FizzBuzz.converte(3));
    }

    @Test
    void multiploDeCinco() {
        assertEquals("Buzz", FizzBuzz.converte(5));
    }

    @Test
    void multiploDeTresECinco() {
        assertEquals("FizzBuzz", FizzBuzz.converte(15));
    }

    @Test
    void numeroComum() {
        assertEquals("2", FizzBuzz.converte(2));
    }
}
