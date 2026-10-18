import pytest

from fisica.formulas import DadosInconsistentes
from fisica.movimentos import MOVIMENTOS, Movimento
from fisica.solver import DadosInsuficientes, Solver
from fisica.unidades import EntradaInvalida

mruv = Solver(MOVIMENTOS["mruv"])


def test_movimento_e_abstrato():
    with pytest.raises(TypeError):
        Movimento()


def test_mru_em_um_passo():
    resultado = Solver(MOVIMENTOS["mru"]).resolver({"v": 20, "t": 3}, "ds")
    assert resultado.valor_si == pytest.approx(60)
    assert [p.formula for p in resultado.passos] == ["Função horária do MRU"]


def test_encadeia_duas_formulas():
    # sem t não dá para usar a equação horária direto: primeiro acha t, depois ds
    resultado = mruv.resolver({"v0": 20, "v": 0, "a": -4}, "ds")
    assert [p.variavel for p in resultado.passos] == ["t", "ds"]


def test_mensagem_do_pdf_tempo_ou_velocidade_final():
    # PDF: o solver informa o que falta (ex.: "informe o tempo ou a velocidade final")
    with pytest.raises(DadosInsuficientes) as erro:
        mruv.resolver({"v0": 20, "a": -4}, "ds")
    assert erro.value.faltando == ["v", "t"]
    assert "velocidade final (v) ou tempo (t)" in str(erro.value)


def test_faltam_dois_dados():
    with pytest.raises(DadosInsuficientes, match="pelo menos dois") as erro:
        mruv.resolver({"v0": 20}, "ds")
    assert erro.value.faltando == []


def test_dados_impossiveis():
    # freando de 20 m/s a -4 m/s² o carro para em 50 m: nunca chega a 100 m
    with pytest.raises(DadosInconsistentes):
        mruv.resolver({"v0": 20, "a": -4, "ds": 100}, "t")


def test_alvo_ja_informado_nao_gera_passos():
    resultado = mruv.resolver({"v0": 20, "a": -4, "t": 2}, "v0")
    assert resultado.valor_si == 20
    assert resultado.passos == []


def test_variavel_inexistente():
    with pytest.raises(EntradaInvalida, match="'x'"):
        mruv.resolver({"x": 1}, "ds")


def test_tempo_negativo_na_entrada():
    with pytest.raises(EntradaInvalida, match="tempo"):
        mruv.resolver({"t": -1, "v0": 2, "a": 1}, "ds")


def test_queda_livre_usa_padroes():
    resultado = Solver(MOVIMENTOS["queda_livre"]).resolver({"t": 2}, "h")
    assert resultado.valor_si == pytest.approx(0.5 * 9.81 * 4)
    assert resultado.estado["g"] == 9.81
