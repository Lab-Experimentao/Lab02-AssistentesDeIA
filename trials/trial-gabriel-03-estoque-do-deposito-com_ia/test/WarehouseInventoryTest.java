import static org.junit.jupiter.api.Assertions.assertArrayEquals;

import org.junit.jupiter.api.Test;

class WarehouseInventoryTest {

    @Test
    void entradaSempreAcumulaNoTotal() {
        assertArrayEquals(
            new String[] {"OK:parafuso:50"},
            WarehouseInventory.process(new String[] {"ENTRADA:parafuso:50"}));
    }

    @Test
    void saidaComEstoqueSuficienteSubtraiDoTotal() {
        assertArrayEquals(
            new String[] {"OK:parafuso:50", "OK:parafuso:30"},
            WarehouseInventory.process(new String[] {"ENTRADA:parafuso:50", "SAIDA:parafuso:20"}));
    }

    @Test
    void saidaSemEstoqueSuficienteERejeitadaESemAlterarTotal() {
        assertArrayEquals(
            new String[] {"OK:parafuso:30", "REJEITADA:parafuso:30"},
            WarehouseInventory.process(new String[] {"ENTRADA:parafuso:30", "SAIDA:parafuso:40"}));
    }

    @Test
    void ajusteEmItemConhecidoSobrescreveOTotal() {
        assertArrayEquals(
            new String[] {"OK:parafuso:50", "OK:parafuso:10"},
            WarehouseInventory.process(new String[] {"ENTRADA:parafuso:50", "AJUSTE:parafuso:10"}));
    }

    @Test
    void ajusteEmItemDesconhecidoTambemFuncionaESobrescreveOTotal() {
        assertArrayEquals(
            new String[] {"OK:prego:5"},
            WarehouseInventory.process(new String[] {"AJUSTE:prego:5"}));
    }

    @Test
    void itensDiferentesTemTotaisIndependentes() {
        assertArrayEquals(
            new String[] {"OK:prego:5", "OK:parafuso:20", "OK:prego:2"},
            WarehouseInventory.process(new String[] {"ENTRADA:prego:5", "ENTRADA:parafuso:20", "SAIDA:prego:3"}));
    }

    @Test
    void fluxoCompletoComVariosItensEOperacoesIntercaladas() {
        String[] operacoes = {
            "ENTRADA:parafuso:50",
            "SAIDA:parafuso:20",
            "SAIDA:parafuso:40",
            "AJUSTE:parafuso:5",
            "ENTRADA:prego:5",
            "SAIDA:prego:2"
        };
        String[] esperado = {
            "OK:parafuso:50",
            "OK:parafuso:30",
            "REJEITADA:parafuso:30",
            "OK:parafuso:5",
            "OK:prego:5",
            "OK:prego:3"
        };
        assertArrayEquals(esperado, WarehouseInventory.process(operacoes));
    }

    @Test
    void operacoesNulasRetornamArrayVazio() {
        assertArrayEquals(new String[0], WarehouseInventory.process(null));
    }
}
