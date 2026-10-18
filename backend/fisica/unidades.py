"""Unidades de medida e conversão para o SI.

Regra do projeto: dentro de fisica/ tudo é SI. Este módulo é a borda
que traduz "72 km/h" em 20.0 (m/s) e vice-versa.
"""
import math
from dataclasses import dataclass
from enum import Enum


class EntradaInvalida(Exception):
    """Unidade desconhecida ou de dimensão incompatível."""


class Dimensao(Enum):
    COMPRIMENTO = "comprimento"
    TEMPO = "tempo"
    VELOCIDADE = "velocidade"
    ACELERACAO = "aceleracao"
    ANGULO = "angulo"


@dataclass(frozen=True)
class Unidade:
    id: str            # usado no JSON ("km/h", "m/s2")
    simbolo: str       # exibido na tela ("km/h", "m/s²")
    dimensao: Dimensao
    fator: float       # valor_si = valor * fator


@dataclass(frozen=True)
class Grandeza:
    valor: float
    unidade: Unidade

    def __str__(self) -> str:
        return f"{self.valor:g} {self.unidade.simbolo}"


# A ordem desta lista é a ordem em que as unidades aparecem nos seletores.
_TODAS = [
    Unidade("m", "m", Dimensao.COMPRIMENTO, 1.0),
    Unidade("cm", "cm", Dimensao.COMPRIMENTO, 0.01),
    Unidade("km", "km", Dimensao.COMPRIMENTO, 1000.0),
    Unidade("s", "s", Dimensao.TEMPO, 1.0),
    Unidade("ms", "ms", Dimensao.TEMPO, 0.001),
    Unidade("min", "min", Dimensao.TEMPO, 60.0),
    Unidade("h", "h", Dimensao.TEMPO, 3600.0),
    Unidade("m/s", "m/s", Dimensao.VELOCIDADE, 1.0),
    Unidade("km/h", "km/h", Dimensao.VELOCIDADE, 1 / 3.6),
    Unidade("m/s2", "m/s²", Dimensao.ACELERACAO, 1.0),
    Unidade("grau", "°", Dimensao.ANGULO, math.pi / 180),
    Unidade("rad", "rad", Dimensao.ANGULO, 1.0),
]

# dict comprehension: monta {"m": Unidade(...), "cm": Unidade(...), ...}
UNIDADES: dict[str, Unidade] = {u.id: u for u in _TODAS}

UNIDADE_SI: dict[Dimensao, Unidade] = {
    Dimensao.COMPRIMENTO: UNIDADES["m"],
    Dimensao.TEMPO: UNIDADES["s"],
    Dimensao.VELOCIDADE: UNIDADES["m/s"],
    Dimensao.ACELERACAO: UNIDADES["m/s2"],
    Dimensao.ANGULO: UNIDADES["rad"],
}


class Conversor:
    """Converte grandezas para o SI e de volta."""

    @staticmethod
    def buscar(id_unidade: str) -> Unidade:
        try:
            return UNIDADES[id_unidade]
        except KeyError:
            aceitas = ", ".join(UNIDADES)
            raise EntradaInvalida(
                f"unidade desconhecida: '{id_unidade}' (aceitas: {aceitas})"
            ) from None

    @staticmethod
    def para_si(grandeza: Grandeza) -> float:
        return grandeza.valor * grandeza.unidade.fator

    @staticmethod
    def do_si(valor_si: float, unidade: Unidade) -> Grandeza:
        return Grandeza(valor_si / unidade.fator, unidade)

    @staticmethod
    def unidades_de(dimensao: Dimensao) -> list[Unidade]:
        return [u for u in _TODAS if u.dimensao is dimensao]

    @staticmethod
    def si_de(dimensao: Dimensao) -> Unidade:
        return UNIDADE_SI[dimensao]

    @staticmethod
    def exigir_dimensao(unidade: Unidade, dimensao: Dimensao) -> None:
        """Ex.: impede mandar 'km/h' para um tempo."""
        if unidade.dimensao is not dimensao:
            raise EntradaInvalida(
                f"'{unidade.simbolo}' é unidade de {unidade.dimensao.value}, "
                f"mas era esperado {dimensao.value}"
            )
