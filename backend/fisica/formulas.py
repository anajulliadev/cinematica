"""Fórmulas da cinemática.

Formula      -> interface: o que o Solver precisa saber de uma equação.
FormulaBase  -> classe abstrata: o que é igual em todas as equações.
Subclasses   -> cada equação concreta só diz como isolar cada variável.
"""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from string import Template


class DadosInconsistentes(Exception):
    """A conta é impossível com esses valores (raiz negativa, divisão por zero...)."""


@dataclass
class Passo:
    """Uma linha do passo a passo mostrado na tela."""
    formula: str
    latex: str
    latex_isolada: str
    variavel: str
    valor_si: float
    usadas: dict[str, float]
    observacao: str | None = None


class Formula(ABC):
    """Interface usada pelo Solver."""

    @property
    @abstractmethod
    def variaveis(self) -> frozenset[str]:
        """Quais variáveis a fórmula usa."""

    @abstractmethod
    def incognita_isolavel(self, conhecidas: dict[str, float]) -> str | None:
        """Se der para isolar uma incógnita a partir das conhecidas, devolve qual."""

    @abstractmethod
    def calcular(self, alvo: str, conhecidas: dict[str, float]) -> float:
        """Calcula o valor (SI) do alvo."""


class FormulaBase(Formula):
    """Parte comum a todas as equações.

    A subclasse define só: nome, papeis, latex, isoladas e _isolar().
    "Papéis" são os nomes usados dentro da equação (v, v0, a, t, ds).
    O parâmetro `nomes` liga cada papel a uma variável do movimento,
    o que permite reaproveitar a equação (QuedaLivre: a -> g, ds -> h).
    """

    nome: str
    papeis: tuple[str, ...]
    latex: str
    isoladas: dict[str, str]

    def __init__(self, nomes: dict[str, str] | None = None):
        nomes = nomes or {}
        self._var = {p: nomes.get(p, p) for p in self.papeis}   # papel -> variável
        self._papel = {v: p for p, v in self._var.items()}      # variável -> papel

    def __repr__(self) -> str:
        return f"{type(self).__name__}({sorted(self.variaveis)})"

    @property
    def variaveis(self) -> frozenset[str]:
        return frozenset(self._var.values())

    # ---- comum 1: checar quantas incógnitas faltam ----

    def incognitas(self, conhecidas: dict[str, float]) -> frozenset[str]:
        return self.variaveis - conhecidas.keys()

    def incognita_isolavel(self, conhecidas):
        faltam = self.incognitas(conhecidas)
        if len(faltam) == 1:
            (var,) = faltam
            if self._papel[var] in self.isoladas:
                return var
        return None

    def calcular(self, alvo, conhecidas):
        x = {p: conhecidas[v] for p, v in self._var.items() if v in conhecidas}
        try:
            valor = self._isolar(self._papel[alvo], x)
        except ZeroDivisionError:
            raise DadosInconsistentes(f"{self.nome}: divisão por zero") from None
        except ValueError as erro:
            raise DadosInconsistentes(f"{self.nome}: {erro}") from None
        if not math.isfinite(valor):
            raise DadosInconsistentes(f"{self.nome}: resultado inválido")
        return valor

    # ---- comum 2: gerar o texto do passo a passo ----

    def passo(self, alvo, conhecidas, valor, simbolos: dict[str, str]) -> Passo:
        subs = {p: simbolos.get(v, v) for p, v in self._var.items()}
        papel = self._papel[alvo]
        return Passo(
            formula=self.nome,
            latex=Template(self.latex).substitute(subs),
            latex_isolada=Template(self.isoladas[papel]).substitute(subs),
            variavel=alvo,
            valor_si=valor,
            usadas={v: conhecidas[v] for v in self.variaveis if v != alvo},
            observacao=self._observacao(papel),
        )

    def _observacao(self, papel: str) -> str | None:
        """Gancho opcional: a subclasse pode sobrescrever."""
        return None

    # ---- a única coisa que cada equação concreta implementa ----

    @abstractmethod
    def _isolar(self, papel: str, x: dict[str, float]) -> float:
        """Recebe os valores por papel e devolve o valor do papel pedido."""


# =====================================================================
# Fórmulas 1D
# =====================================================================

class MovimentoUniforme(FormulaBase):
    nome = "Função horária do MRU"
    papeis = ("ds", "v", "t")
    latex = "$ds = $v \\cdot $t"
    isoladas = {
        "ds": "$ds = $v \\cdot $t",
        "v": "$v = \\frac{$ds}{$t}",
        "t": "$t = \\frac{$ds}{$v}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "ds":
                return x["v"] * x["t"]
            case "v":
                return x["ds"] / x["t"]
            case "t":
                return x["ds"] / x["v"]


class VelocidadeTempo(FormulaBase):
    nome = "Função horária da velocidade"
    papeis = ("v", "v0", "a", "t")
    latex = "$v = $v0 + $a \\cdot $t"
    isoladas = {
        "v": "$v = $v0 + $a \\cdot $t",
        "v0": "$v0 = $v - $a \\cdot $t",
        "a": "$a = \\frac{$v - $v0}{$t}",
        "t": "$t = \\frac{$v - $v0}{$a}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "v":
                return x["v0"] + x["a"] * x["t"]
            case "v0":
                return x["v"] - x["a"] * x["t"]
            case "a":
                return (x["v"] - x["v0"]) / x["t"]
            case "t":
                return (x["v"] - x["v0"]) / x["a"]


class EquacaoHoraria(FormulaBase):
    nome = "Função horária da posição"
    papeis = ("ds", "v0", "a", "t")
    latex = "$ds = $v0 \\cdot $t + \\frac{1}{2} $a \\cdot $t^2"
    isoladas = {
        "ds": "$ds = $v0 \\cdot $t + \\frac{1}{2} $a \\cdot $t^2",
        "v0": "$v0 = \\frac{$ds - \\frac{1}{2} $a \\cdot $t^2}{$t}",
        "a": "$a = \\frac{2($ds - $v0 \\cdot $t)}{$t^2}",
        "t": "$t = \\frac{-$v0 + \\sqrt{$v0^2 + 2 $a \\cdot $ds}}{$a}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "ds":
                return x["v0"] * x["t"] + 0.5 * x["a"] * x["t"] ** 2
            case "v0":
                return (x["ds"] - 0.5 * x["a"] * x["t"] ** 2) / x["t"]
            case "a":
                return 2 * (x["ds"] - x["v0"] * x["t"]) / x["t"] ** 2
            case "t":
                return self._tempo(x["ds"], x["v0"], x["a"])

    @staticmethod
    def _tempo(ds, v0, a):
        """Resolve ½·a·t² + v0·t − Δs = 0 e devolve o menor tempo positivo."""
        if abs(a) < 1e-12:                  # sem aceleração: vira MRU
            return ds / v0
        delta = v0**2 + 2 * a * ds
        if delta < 0:
            raise DadosInconsistentes(
                "Função horária da posição: o móvel nunca atinge esse deslocamento"
            )
        raiz = math.sqrt(delta)
        raizes = ((-v0 + raiz) / a, (-v0 - raiz) / a)
        positivas = [t for t in raizes if t > 1e-12]
        if positivas:
            return min(positivas)
        if any(abs(t) <= 1e-12 for t in raizes):
            return 0.0
        raise DadosInconsistentes("Função horária da posição: nenhum tempo positivo")


class Torricelli(FormulaBase):
    nome = "Equação de Torricelli"
    papeis = ("v", "v0", "a", "ds")
    latex = "$v^2 = $v0^2 + 2 $a \\cdot $ds"
    isoladas = {
        "v": "$v = \\sqrt{$v0^2 + 2 $a \\cdot $ds}",
        "v0": "$v0 = \\sqrt{$v^2 - 2 $a \\cdot $ds}",
        "a": "$a = \\frac{$v^2 - $v0^2}{2 $ds}",
        "ds": "$ds = \\frac{$v^2 - $v0^2}{2 $a}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "v":
                return self._raiz(x["v0"] ** 2 + 2 * x["a"] * x["ds"])
            case "v0":
                return self._raiz(x["v"] ** 2 - 2 * x["a"] * x["ds"])
            case "a":
                return (x["v"] ** 2 - x["v0"] ** 2) / (2 * x["ds"])
            case "ds":
                return (x["v"] ** 2 - x["v0"] ** 2) / (2 * x["a"])

    @staticmethod
    def _raiz(radicando):
        if radicando < -1e-12:
            raise DadosInconsistentes(
                "Equação de Torricelli: o móvel para antes de percorrer esse deslocamento"
            )
        return math.sqrt(max(radicando, 0.0))

    def _observacao(self, papel):
        if papel in ("v", "v0"):
            return "Raiz quadrada: foi considerado o valor positivo."
        return None


class VelocidadeMedia(FormulaBase):
    nome = "Deslocamento pela velocidade média"
    papeis = ("ds", "v0", "v", "t")
    latex = "$ds = \\frac{$v0 + $v}{2} \\cdot $t"
    isoladas = {
        "ds": "$ds = \\frac{$v0 + $v}{2} \\cdot $t",
        "v0": "$v0 = \\frac{2 $ds}{$t} - $v",
        "v": "$v = \\frac{2 $ds}{$t} - $v0",
        "t": "$t = \\frac{2 $ds}{$v0 + $v}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "ds":
                return (x["v0"] + x["v"]) / 2 * x["t"]
            case "v0":
                return 2 * x["ds"] / x["t"] - x["v"]
            case "v":
                return 2 * x["ds"] / x["t"] - x["v0"]
            case "t":
                return 2 * x["ds"] / (x["v0"] + x["v"])
