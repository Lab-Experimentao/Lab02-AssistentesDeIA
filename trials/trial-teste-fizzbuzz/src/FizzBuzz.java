public class FizzBuzz {

    public static String converte(int numero) {
        boolean multiploDeTres = numero % 3 == 0;
        boolean multiploDeCinco = numero % 5 == 0;

        if (multiploDeTres && multiploDeCinco) {
            return "FizzBuzz";
        }
        if (multiploDeTres) {
            return "Fizz";
        }
        if (multiploDeCinco) {
            return "Buzz";
        }
        return Integer.toString(numero);
    }

    public static void main(String[] args) {
        for (int i = 1; i <= 100; i++) {
            System.out.println(converte(i));
        }
    }
}
