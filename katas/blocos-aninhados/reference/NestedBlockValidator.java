import java.util.ArrayDeque;
import java.util.Deque;

public class NestedBlockValidator {

    public static int validate(String expressao) {
        if (expressao == null) {
            return 0;
        }

        Deque<Character> pilha = new ArrayDeque<>();
        int profundidadeAtual = 0;
        int profundidadeMaxima = 0;

        for (char c : expressao.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                pilha.push(c);
                profundidadeAtual++;
                profundidadeMaxima = Math.max(profundidadeMaxima, profundidadeAtual);
            } else if (c == ')' || c == ']' || c == '}') {
                if (pilha.isEmpty() || !correspondem(pilha.pop(), c)) {
                    return -1;
                }
                profundidadeAtual--;
            }
        }

        return pilha.isEmpty() ? profundidadeMaxima : -1;
    }

    private static boolean correspondem(char abertura, char fechamento) {
        return (abertura == '(' && fechamento == ')')
            || (abertura == '[' && fechamento == ']')
            || (abertura == '{' && fechamento == '}');
    }
}
