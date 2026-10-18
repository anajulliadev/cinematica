import math

import pytest

from fisica.unidades import UNIDADES, Conversor, Dimensao, EntradaInvalida, Grandeza


def grandeza(valor, id_unidade):
    return Grandeza(valor, Conversor.buscar(id_unidade))


# parametrize: o mesmo teste roda uma vez para cada linha da lista
@pytest.mark.parametrize(
    "valor, unidade, esperado_si",
    [
        (4500, "cm", 45.0),        # tema 3: 4500 cm -> 45 m
        (2, "km", 2000.0),
        (500, "ms", 0.5),
        (2, "min", 120.0),
        (1, "h", 3600.0),
        (72, "km/h", 20.0),        # tema 2: 72 km/h -> 20 m/s
        (35, "grau", math.radians(35)),
        (-4, "m/s2", -4.0),
    ],
)
def test_para_si(valor, unidade, esperado_si):
    assert Conversor.para_si(grandeza(valor, unidade)) == pytest.approx(esperado_si)


def test_do_si_velocidade_da_queda_livre_em_kmh():
    resultado = Conversor.do_si(29.71, Conversor.buscar("km/h"))
    assert resultado.valor == pytest.approx(106.96, abs=0.01)  


@pytest.mark.parametrize("id_unidade", list(UNIDADES))
def test_ida_e_volta_nao_perde_valor(id_unidade):
    unidade = Conversor.buscar(id_unidade)
    si = Conversor.para_si(Grandeza(3.7, unidade))
    assert Conversor.do_si(si, unidade).valor == pytest.approx(3.7)


def test_unidade_desconhecida():
    with pytest.raises(EntradaInvalida, match="polegada"):
        Conversor.buscar("polegada")


def test_unidades_de_tempo_na_ordem_dos_seletores():
    ids = [u.id for u in Conversor.unidades_de(Dimensao.TEMPO)]
    assert ids == ["s", "ms", "min", "h"]


def test_unidade_si_de_cada_dimensao():
    assert Conversor.si_de(Dimensao.VELOCIDADE).id == "m/s"
    assert Conversor.si_de(Dimensao.ANGULO).id == "rad"


def test_dimensao_errada():
    with pytest.raises(EntradaInvalida, match="tempo"):
        Conversor.exigir_dimensao(Conversor.buscar("km/h"), Dimensao.TEMPO)
