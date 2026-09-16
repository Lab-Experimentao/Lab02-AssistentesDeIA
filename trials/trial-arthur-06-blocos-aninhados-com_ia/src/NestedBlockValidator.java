import java.util.ArrayDeque;
import java.util.Deque;

public class NestedBlockValidator {

    public static int validate(String expressao) {
        Deque<Character> pilha = new ArrayDeque<>();
        int profundidadeAtual = 0;
        int profundidadeMaxima = 0;

        for (int i = 0; i < expressao.length(); i++) {
            char c = expressao.charAt(i);

            if (c == '(' || c == '[' || c == '{') {
                pilha.push(c);
                profundidadeAtual++;
                if (profundidadeAtual > profundidadeMaxima) {
                    profundidadeMaxima = profundidadeAtual;
                }
            } else if (c == ')' || c == ']' || c == '}') {
                if (pilha.isEmpty() || !correspondem(pilha.pop(), c)) {
                    return -1;
                }
                profundidadeAtual--;
            }
            // outros caracteres são ignorados
        }

        if (!pilha.isEmpty()) {
            return -1;
        }

        return profundidadeMaxima;
    }

    private static boolean correspondem(char abertura, char fechamento) {
        return (abertura == '(' && fechamento == ')')
            || (abertura == '[' && fechamento == ']')
            || (abertura == '{' && fechamento == '}');
    }
}