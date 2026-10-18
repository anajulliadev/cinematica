"""Movimentos: cada um junta as suas variáveis e as suas fórmulas.

"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fisica.formulas import (
    EquacaoHoraria,
    Formula,
    MovimentoUniforme,
    Torricelli,
    VelocidadeMedia,
    VelocidadeTempo,
)
from fisica.unidades import Dimensao


@dataclass(frozen=True)
class Variavel:
    id: str
    nome: str
    simbolo: str              # LaTeX
    dimensao: Dimensao
    nao_negativa: bool = False


# Variáveis reaproveitadas por mais de um movimento
DS = Variavel("ds", "deslocamento", "\\Delta s", Dimensao.COMPRIMENTO)
V0 = Variavel("v0", "velocidade inicial", "v_0", Dimensao.VELOCIDADE)
V = Variavel("v", "velocidade final", "v", Dimensao.VELOCIDADE)
A = Variavel("a", "aceleração", "a", Dimensao.ACELERACAO)
T = Variavel("t", "tempo", "t", Dimensao.TEMPO, nao_negativa=True)
H = Variavel("h", "altura de queda", "h", Dimensao.COMPRIMENTO, nao_negativa=True)
G = Variavel("g", "aceleração da gravidade", "g", Dimensao.ACELERACAO, nao_negativa=True)


class Movimento(ABC):
    """Nome, lista de variáveis e lista de fórmulas (como no PDF)."""

    nome: str

    def __init__(self):
        # Criadas UMA vez por movimento: o Solver identifica cada fórmula pelo objeto.
        self._variaveis = {v.id: v for v in self._criar_variaveis()}
        self._formulas = self._criar_formulas()

    @property
    def variaveis(self) -> dict[str, Variavel]:
        return self._variaveis

    @property
    def formulas(self) -> list[Formula]:
        return self._formulas

    @property
    def padroes(self) -> dict[str, float]:
        """Valores SI usados quando o usuário não informa."""
        return {}

    def simbolos(self) -> dict[str, str]:
        return {v.id: v.simbolo for v in self._variaveis.values()}

    @abstractmethod
    def _criar_variaveis(self) -> list[Variavel]: ...

    @abstractmethod
    def _criar_formulas(self) -> list[Formula]: ...


class MRU(Movimento):
    nome = "Movimento Retilíneo Uniforme"

    def _criar_variaveis(self):
        return [DS, V, T]

    def _criar_formulas(self):
        return [MovimentoUniforme()]


class MRUV(Movimento):
    nome = "Movimento Retilíneo Uniformemente Variado"

    def _criar_variaveis(self):
        return [DS, V0, V, A, T]

    def _criar_formulas(self):
        return [VelocidadeTempo(), EquacaoHoraria(), Torricelli(), VelocidadeMedia()]


class QuedaLivre(Movimento):
    """Eixo para baixo: h é a altura percorrida na queda e g > 0."""

    nome = "Queda Livre"

    def _criar_variaveis(self):
        return [H, V0, V, G, T]

    def _criar_formulas(self):
        nomes = {"a": "g", "ds": "h"}     # as mesmas equações do MRUV, com outros nomes
        return [
            VelocidadeTempo(nomes),
            EquacaoHoraria(nomes),
            Torricelli(nomes),
            VelocidadeMedia(nomes),
        ]

    @property
    def padroes(self):
        return {"v0": 0.0, "g": 9.81}


MOVIMENTOS: dict[str, Movimento] = {
    "mru": MRU(),
    "mruv": MRUV(),
    "queda_livre": QuedaLivre(),
}
