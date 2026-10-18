"""Movimentos: cada um junta as suas variáveis e as suas fórmulas.

Movimento (abstrata) -> MRU, MRUV, QuedaLivre, LancamentoProjetil.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fisica.formulas import (
    Alcance,
    AlturaMaxima,
    AnguloPeloAlcance,
    ComponenteX,
    ComponenteY,
    EquacaoHoraria,
    Formula,
    MovimentoUniforme,
    Passo,
    TempoVoo,
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

# Variáveis do projétil (a ordem define a ordem das sugestões "informe também: ...")
V0_LANCAMENTO = Variavel("v0", "velocidade inicial", "v_0", Dimensao.VELOCIDADE, nao_negativa=True)
THETA = Variavel("theta", "ângulo de lançamento", "\\theta", Dimensao.ANGULO)
H0 = Variavel("h0", "altura inicial", "h_0", Dimensao.COMPRIMENTO, nao_negativa=True)
ALCANCE = Variavel("A", "alcance horizontal", "A", Dimensao.COMPRIMENTO, nao_negativa=True)
ALTURA_MAX = Variavel("H", "altura máxima", "H", Dimensao.COMPRIMENTO, nao_negativa=True)
T_VOO = Variavel("t_voo", "tempo de voo", "t_{voo}", Dimensao.TEMPO, nao_negativa=True)
VX = Variavel("vx", "velocidade horizontal", "v_x", Dimensao.VELOCIDADE)
VY = Variavel("vy", "velocidade vertical inicial", "v_y", Dimensao.VELOCIDADE)


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

    def preparar(self, conhecidas: dict[str, float]) -> list[Passo]:
        """Gancho chamado pelo Solver antes do laço. Pode completar dados
        implícitos em `conhecidas` e devolve os passos que explicam isso.
        Padrão: não faz nada."""
        return []

    def simbolos(self) -> dict[str, str]:
        return {v.id: v.simbolo for v in self._variaveis.values()}

    @abstractmethod
    def trajetoria(self, estado: dict[str, float], n: int = 60) -> list[dict[str, float]]:
        """Pontos (SI) para a animação e os gráficos, de t = 0 até o fim do movimento.
        Lista vazia se o estado não tiver os dados necessários."""

    @staticmethod
    def _instantes(t_final: float, n: int) -> list[float]:
        """n + 1 instantes igualmente espaçados, incluindo 0 e t_final."""
        return [t_final * i / n for i in range(n + 1)]

    @abstractmethod
    def _criar_variaveis(self) -> list[Variavel]: ...

    @abstractmethod
    def _criar_formulas(self) -> list[Formula]: ...


def _tem(estado: dict[str, float], *ids: str) -> bool:
    return all(i in estado for i in ids)


class MRU(Movimento):
    nome = "Movimento Retilíneo Uniforme"

    def _criar_variaveis(self):
        return [DS, V, T]

    def _criar_formulas(self):
        return [MovimentoUniforme()]

    def trajetoria(self, estado, n=60):
        if not _tem(estado, "t", "v"):
            return []
        v = estado["v"]
        return [{"t": t, "s": v * t, "v": v} for t in self._instantes(estado["t"], n)]


class MRUV(Movimento):
    nome = "Movimento Retilíneo Uniformemente Variado"

    def _criar_variaveis(self):
        return [DS, V0, V, A, T]

    def _criar_formulas(self):
        return [VelocidadeTempo(), EquacaoHoraria(), Torricelli(), VelocidadeMedia()]

    def trajetoria(self, estado, n=60):
        if not _tem(estado, "t", "v0", "a"):
            return []
        v0, a = estado["v0"], estado["a"]
        return [
            {"t": t, "s": v0 * t + 0.5 * a * t**2, "v": v0 + a * t}
            for t in self._instantes(estado["t"], n)
        ]


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

    def trajetoria(self, estado, n=60):
        # y = altura até o chão (começa em h e termina em 0), para a régua da torre
        if not _tem(estado, "t", "h", "v0", "g"):
            return []
        h, v0, g = estado["h"], estado["v0"], estado["g"]
        return [
            {"t": t, "y": max(h - (v0 * t + 0.5 * g * t**2), 0.0), "v": v0 + g * t}
            for t in self._instantes(estado["t"], n)
        ]


class LancamentoProjetil(Movimento):
    """Oblíquo e horizontal (horizontal = θ = 0). Eixo y para cima, g > 0."""

    nome = "Lançamento de Projétil"

    def _criar_variaveis(self):
        return [V0_LANCAMENTO, THETA, H0, G, ALCANCE, ALTURA_MAX, T_VOO, VX, VY]

    def _criar_formulas(self):
        return [
            ComponenteX(),
            ComponenteY(),
            TempoVoo(),
            Alcance(),
            AlturaMaxima(),
            AnguloPeloAlcance(),   # o caso inverso fica por último
        ]

    @property
    def padroes(self):
        return {"h0": 0.0, "g": 9.81}

    def trajetoria(self, estado, n=60):
        if not _tem(estado, "t_voo", "vx", "vy", "h0", "g"):
            return []
        vx, vy, h0, g = estado["vx"], estado["vy"], estado["h0"], estado["g"]
        return [
            {
                "t": t,
                "x": vx * t,
                "y": max(h0 + vy * t - 0.5 * g * t**2, 0.0),
                "vx": vx,
                "vy": vy - g * t,
            }
            for t in self._instantes(estado["t_voo"], n)
        ]

    def preparar(self, conhecidas):
        # Lançamento horizontal: θ = 0 implica vy = 0 mesmo sem saber v0.
        # Sem isto o tempo de voo teria duas incógnitas (t_voo e vy).
        theta = conhecidas.get("theta")
        if theta is None or "vy" in conhecidas or abs(theta) > 1e-12:
            return []
        conhecidas["vy"] = 0.0
        return [
            Passo(
                formula="Lançamento horizontal",
                latex="\\theta = 0 \\Rightarrow v_y = v_0 \\cdot \\sin 0 = 0",
                latex_isolada="v_y = 0",
                variavel="vy",
                valor_si=0.0,
                usadas={"theta": theta},
            )
        ]


MOVIMENTOS: dict[str, Movimento] = {
    "mru": MRU(),
    "mruv": MRUV(),
    "queda_livre": QuedaLivre(),
    "projetil": LancamentoProjetil(),
}
