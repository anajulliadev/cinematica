"""Os casos do vídeo (PDF, seção "Três exemplos de tema")."""
import pytest

from fisica.movimentos import MOVIMENTOS
from fisica.solver import Solver
from fisica.unidades import Conversor, Grandeza


def si(valor, unidade):
    return Conversor.para_si(Grandeza(valor, Conversor.buscar(unidade)))


def test_tema2_frenagem():
    """Carro a 72 km/h freia com -4 m/s² até parar: para em 5 s, depois de 50 m."""
    entradas = {"v0": si(72, "km/h"), "v": 0.0, "a": si(-4, "m/s2")}
    resultado = Solver(MOVIMENTOS["mruv"]).resolver(entradas, "ds")
    assert resultado.valor_si == pytest.approx(50, abs=0.01)
    assert resultado.estado["t"] == pytest.approx(5, abs=0.01)


def test_tema3_queda_livre():
    """Pedra solta de 4500 cm: chega ao chão em 3,03 s a 29,7 m/s (107 km/h)."""
    resultado = Solver(MOVIMENTOS["queda_livre"]).resolver({"h": si(4500, "cm")}, "v")
    assert resultado.valor_si == pytest.approx(29.71, abs=0.01)
    assert resultado.estado["t"] == pytest.approx(3.03, abs=0.01)
    em_kmh = Conversor.do_si(resultado.valor_si, Conversor.buscar("km/h"))
    assert em_kmh.valor == pytest.approx(107, abs=0.1)
