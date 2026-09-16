import java.util.ArrayDeque;

public class NestedBlockValidator {
    public static int validate(String expressao) {
        int profundidadeMaxima = 0;
        int profundidadeAtual = 0;
        String aberturas = "({[";
        String fechamentos = ")}]";
        ArrayDeque<Character> pilha = new ArrayDeque<>();

        for (int i = 0; i < expressao.length(); i++) {
            char atual = expressao.charAt(i);
            if (pilha.isEmpty() && fechamentos.indexOf(atual) != -1) {
                return -1;
            }
            if (aberturas.indexOf(atual) != -1){
                pilha.push(atual);
                profundidadeAtual++;
                profundidadeMaxima = Math.max(profundidadeMaxima, profundidadeAtual);
            }
            if (fechamentos.indexOf(atual) != -1){
                if (aberturas.indexOf(pilha.peek()) != -1 && aberturas.indexOf(pilha.peek()) == fechamentos.indexOf(atual)) {
                    pilha.pop();
                    profundidadeAtual--;
                }
            }
        }

        return !pilha.isEmpty() ? -1 : profundidadeMaxima;
    }
}
