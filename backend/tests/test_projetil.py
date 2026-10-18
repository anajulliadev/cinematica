import math

import pytest

from fisica.formulas import (
    Alcance,
    AlturaMaxima,
    AnguloPeloAlcance,
    ComponenteX,
    ComponenteY,
    DadosInconsistentes,
    TempoVoo,
)
from fisica.movimentos import MOVIMENTOS
from fisica.solver import DadosInsuficientes, Solver

projetil = Solver(MOVIMENTOS["projetil"])


def estado_coerente(v0, theta_graus, h0, g=9.81):
    """Monta um estado 2D completo pelas fórmulas do livro, para os testes de ida e volta."""
    theta = math.radians(theta_graus)
    vx, vy = v0 * math.cos(theta), v0 * math.sin(theta)
    t_voo = (vy + math.sqrt(vy**2 + 2 * g * h0)) / g
    return {
        "v0": v0, "theta": theta, "h0": h0, "g": g, "vx": vx, "vy": vy,
        "t_voo": t_voo, "A": vx * t_voo, "H": h0 + vy**2 / (2 * g),
    }


DO_ALTO = estado_coerente(15, 40, h0=12)
DO_CHAO = estado_coerente(20, 35, h0=0)

CASOS = [
    (classe, DO_ALTO, papel)
    for classe in (ComponenteX, ComponenteY, TempoVoo, Alcance, AlturaMaxima)
    for papel in classe.isoladas
] + [(AnguloPeloAlcance, DO_CHAO, papel) for papel in AnguloPeloAlcance.isoladas]


@pytest.mark.parametrize("classe, estado, alvo", CASOS)
def test_cada_isolamento_2d_recupera_o_valor(classe, estado, alvo):
    formula = classe()
    conhecidas = {k: v for k, v in estado.items() if k in formula.variaveis and k != alvo}
    assert formula.calcular(alvo, conhecidas) == pytest.approx(estado[alvo])


def test_componente_y_nao_isola_v0_com_theta_zero():
    assert ComponenteY().incognita_isolavel({"vy": 0.0, "theta": 0.0}) is None


def test_angulo_pelo_alcance_nao_vale_fora_do_chao():
    conhecidas = {"A": 30, "v0": 20, "g": 9.81, "h0": 5}
    assert AnguloPeloAlcance().incognita_isolavel(conhecidas) is None


def test_lancamento_horizontal_com_alcance():
    # de 45 m de altura cai em 3,03 s; para andar 30 m precisa de vx = v0 ≈ 9,90 m/s
    resultado = projetil.resolver({"h0": 45, "theta": 0, "A": 30}, "v0")
    assert resultado.valor_si == pytest.approx(9.90, abs=0.01)
    assert resultado.passos[0].formula == "Lançamento horizontal"


def test_caso_inverso_angulo_pelo_alcance():
    resultado = projetil.resolver({"v0": 20, "A": DO_CHAO["A"]}, "theta")
    assert math.degrees(resultado.valor_si) == pytest.approx(35)
    assert "complementar" in resultado.passos[-1].observacao


def test_alcance_impossivel():
    # com 10 m/s o alcance máximo é 10²/9,81 ≈ 10,2 m
    with pytest.raises(DadosInconsistentes, match="impossível"):
        projetil.resolver({"v0": 10, "A": 100}, "theta")


def test_horizontal_sem_dados_pede_alcance_ou_vx():
    with pytest.raises(DadosInsuficientes) as erro:
        projetil.resolver({"h0": 45, "theta": 0}, "v0")
    assert erro.value.faltando == ["A", "vx"]
