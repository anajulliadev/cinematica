import math

import pytest

from fisica.movimentos import MOVIMENTOS
from fisica.solver import Solver


def trajetoria(id_movimento, entradas, alvo):
    movimento = MOVIMENTOS[id_movimento]
    resultado = Solver(movimento).resolver(entradas, alvo)
    return movimento.trajetoria(resultado.estado), resultado.estado


def test_mru_anda_com_velocidade_constante():
    pontos, _ = trajetoria("mru", {"v": 10, "t": 4}, "ds")
    assert pontos[-1] == {"t": 4, "s": 40, "v": 10}


def test_frenagem_vai_de_0_a_50_m_e_para():
    pontos, _ = trajetoria("mruv", {"v0": 20, "v": 0, "a": -4}, "ds")
    assert len(pontos) == 61                       # n = 60 intervalos -> 61 pontos
    assert pontos[0] == {"t": 0, "s": 0, "v": 20}
    assert pontos[-1]["t"] == pytest.approx(5)
    assert pontos[-1]["s"] == pytest.approx(50)
    assert pontos[-1]["v"] == pytest.approx(0, abs=1e-9)


def test_queda_livre_comeca_no_alto_e_termina_no_chao():
    pontos, estado = trajetoria("queda_livre", {"h": 45}, "t")
    assert pontos[0]["y"] == pytest.approx(45)
    assert pontos[-1]["y"] == pytest.approx(0, abs=1e-6)
    assert pontos[-1]["v"] == pytest.approx(estado["v"])


def test_projetil_sobe_ate_H_e_cai_no_alcance():
    entradas = {"v0": 20, "theta": math.radians(35)}
    pontos, estado = trajetoria("projetil", entradas, "A")
    assert pontos[0]["x"] == 0 and pontos[0]["y"] == 0
    assert pontos[-1]["x"] == pytest.approx(estado["A"])
    assert pontos[-1]["y"] == pytest.approx(0, abs=1e-6)
    assert max(p["y"] for p in pontos) == pytest.approx(estado["H"], abs=0.01)
    assert pontos[-1]["vy"] == pytest.approx(-estado["vy"])   # cai com a mesma velocidade vertical


def test_sem_tempo_nao_ha_trajetoria():
    # só v0 e a: o solver pode até achar outra coisa, mas sem t não há curva
    assert MOVIMENTOS["mruv"].trajetoria({"v0": 20, "a": -4}) == []
