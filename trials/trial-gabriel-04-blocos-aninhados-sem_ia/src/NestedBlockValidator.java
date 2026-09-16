import java.util.ArrayDeque;
import java.util.Deque;

public class NestedBlockValidator {
    
    public static int validate(String expressao) {
        if (expressao == null) {
            return -1;
        }

        Deque<Character> pilha = new ArrayDeque<>();
        int profundidadeMaxima = 0;

        for (char c : expressao.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                pilha.push(c);
                if (pilha.size() > profundidadeMaxima) {
                    profundidadeMaxima = pilha.size();
                }
            } else if (c == ')' || c == ']' || c == '}') {
                if (pilha.isEmpty()) {
                    return -1;
                }

                char topo = pilha.pop();

                if (!correspondem(topo, c)) {
                    return -1;
                }
            }
        }

        if (!pilha.isEmpty()) {
            return -1;
        }

        return profundidadeMaxima;
    }

    private static boolean correspondem(char abertura, char fechamento) {
        return (abertura == '(' && fechamento == ')') ||
               (abertura == '[' && fechamento == ']') ||
               (abertura == '{' && fechamento == '}');
    }
}