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


# =====================================================================
# Fórmulas 2D (projétil). Eixo y para cima, g > 0, θ acima da horizontal.
# =====================================================================

def _quase_zero(valor: float) -> bool:
    return abs(valor) < 1e-12


class ComponenteX(FormulaBase):
    nome = "Componente horizontal da velocidade"
    papeis = ("vx", "v0", "theta")
    latex = "$vx = $v0 \\cdot \\cos $theta"
    isoladas = {
        "vx": "$vx = $v0 \\cdot \\cos $theta",
        "v0": "$v0 = \\frac{$vx}{\\cos $theta}",
    }

    def incognita_isolavel(self, conhecidas):
        var = super().incognita_isolavel(conhecidas)
        theta = conhecidas.get(self._var["theta"])
        # θ = 90° (lançamento vertical): vx = 0 não diz nada sobre v0
        if var == self._var["v0"] and theta is not None and _quase_zero(math.cos(theta)):
            return None
        return var

    def _isolar(self, papel, x):
        match papel:
            case "vx":
                return x["v0"] * math.cos(x["theta"])
            case "v0":
                return x["vx"] / math.cos(x["theta"])


class ComponenteY(FormulaBase):
    nome = "Componente vertical da velocidade"
    papeis = ("vy", "v0", "theta")
    latex = "$vy = $v0 \\cdot \\sin $theta"
    isoladas = {
        "vy": "$vy = $v0 \\cdot \\sin $theta",
        "v0": "$v0 = \\frac{$vy}{\\sin $theta}",
        "theta": "$theta = \\arcsin \\frac{$vy}{$v0}",
    }

    def incognita_isolavel(self, conhecidas):
        var = super().incognita_isolavel(conhecidas)
        theta = conhecidas.get(self._var["theta"])
        # θ = 0 (lançamento horizontal): vy = 0 não diz nada sobre v0
        if var == self._var["v0"] and theta is not None and _quase_zero(math.sin(theta)):
            return None
        return var

    def _isolar(self, papel, x):
        match papel:
            case "vy":
                return x["v0"] * math.sin(x["theta"])
            case "v0":
                return x["vy"] / math.sin(x["theta"])
            case "theta":
                return math.asin(x["vy"] / x["v0"])


class TempoVoo(FormulaBase):
    nome = "Tempo de voo"
    papeis = ("t_voo", "vy", "h0", "g")
    latex = "$t_voo = \\frac{$vy + \\sqrt{$vy^2 + 2 $g \\cdot $h0}}{$g}"
    isoladas = {
        "t_voo": "$t_voo = \\frac{$vy + \\sqrt{$vy^2 + 2 $g \\cdot $h0}}{$g}",
        "vy": "$vy = \\frac{\\frac{1}{2} $g \\cdot $t_voo^2 - $h0}{$t_voo}",
        "h0": "$h0 = \\frac{1}{2} $g \\cdot $t_voo^2 - $vy \\cdot $t_voo",
    }

    def _isolar(self, papel, x):
        match papel:
            case "t_voo":
                radicando = x["vy"] ** 2 + 2 * x["g"] * x["h0"]
                if radicando < 0:
                    raise DadosInconsistentes("Tempo de voo: o projétil nunca chega ao chão")
                return (x["vy"] + math.sqrt(radicando)) / x["g"]
            case "vy":
                return (0.5 * x["g"] * x["t_voo"] ** 2 - x["h0"]) / x["t_voo"]
            case "h0":
                return 0.5 * x["g"] * x["t_voo"] ** 2 - x["vy"] * x["t_voo"]


class Alcance(FormulaBase):
    nome = "Alcance horizontal"
    papeis = ("A", "vx", "t_voo")
    latex = "$A = $vx \\cdot $t_voo"
    isoladas = {
        "A": "$A = $vx \\cdot $t_voo",
        "vx": "$vx = \\frac{$A}{$t_voo}",
        "t_voo": "$t_voo = \\frac{$A}{$vx}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "A":
                return x["vx"] * x["t_voo"]
            case "vx":
                return x["A"] / x["t_voo"]
            case "t_voo":
                return x["A"] / x["vx"]


class AlturaMaxima(FormulaBase):
    nome = "Altura máxima"
    papeis = ("H", "h0", "vy", "g")
    latex = "$H = $h0 + \\frac{$vy^2}{2 $g}"
    isoladas = {
        "H": "$H = $h0 + \\frac{$vy^2}{2 $g}",
        "h0": "$h0 = $H - \\frac{$vy^2}{2 $g}",
        "vy": "$vy = \\sqrt{2 $g ($H - $h0)}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "H":
                return x["h0"] + self._subida(x["vy"], x["g"])
            case "h0":
                return x["H"] - self._subida(x["vy"], x["g"])
            case "vy":
                return math.sqrt(2 * x["g"] * (x["H"] - x["h0"]))

    @staticmethod
    def _subida(vy, g):
        """Quanto o projétil sobe acima de h0 (lançado para baixo: nada)."""
        return max(vy, 0.0) ** 2 / (2 * g)

    def _observacao(self, papel):
        if papel == "vy":
            return "Raiz quadrada: foi considerado o valor positivo (lançamento para cima)."
        return None


class AnguloPeloAlcance(FormulaBase):
    """Caso inverso do PDF: achar o ângulo a partir do alcance.
    Não sai por simples isolamento das outras fórmulas, por isso é uma fórmula
    própria. Vale só para lançamento do chão (h0 = 0)."""

    nome = "Alcance no mesmo nível"
    papeis = ("A", "v0", "theta", "g", "h0")
    latex = "$A = \\frac{$v0^2 \\cdot \\sin(2 $theta)}{$g}"
    isoladas = {
        "A": "$A = \\frac{$v0^2 \\cdot \\sin(2 $theta)}{$g}",
        "v0": "$v0 = \\sqrt{\\frac{$A \\cdot $g}{\\sin(2 $theta)}}",
        "theta": "$theta = \\frac{1}{2} \\arcsin \\frac{$A \\cdot $g}{$v0^2}",
    }

    def incognita_isolavel(self, conhecidas):
        h0 = conhecidas.get(self._var["h0"])
        if h0 is not None and not math.isnan(h0) and not _quase_zero(h0):
            return None                    # fora do chão a fórmula não vale
        return super().incognita_isolavel(conhecidas)

    def _isolar(self, papel, x):
        match papel:
            case "A":
                return x["v0"] ** 2 * math.sin(2 * x["theta"]) / x["g"]
            case "v0":
                seno = math.sin(2 * x["theta"])
                if _quase_zero(seno):
                    raise ZeroDivisionError
                return math.sqrt(x["A"] * x["g"] / seno)
            case "theta":
                razao = x["A"] * x["g"] / x["v0"] ** 2
                if razao > 1:
                    raise DadosInconsistentes(
                        "Alcance no mesmo nível: alcance impossível com essa velocidade"
                    )
                return 0.5 * math.asin(razao)

    def _observacao(self, papel):
        if papel == "theta":
            return "O ângulo complementar (90° − θ) atinge o mesmo alcance."
        return None


class AlturaNoInstante(FormulaBase):
    """Altura do projétil num instante dado (ex.: chegada ao topo de um penhasco)."""

    nome = "Altura no instante"
    papeis = ("y", "h0", "vy", "g", "t")
    latex = "$y = $h0 + $vy \\cdot $t - \\frac{1}{2} $g \\cdot $t^2"
    isoladas = {
        "y": "$y = $h0 + $vy \\cdot $t - \\frac{1}{2} $g \\cdot $t^2",
        "h0": "$h0 = $y - $vy \\cdot $t + \\frac{1}{2} $g \\cdot $t^2",
    }

    def _isolar(self, papel, x):
        match papel:
            case "y":
                return x["h0"] + x["vy"] * x["t"] - 0.5 * x["g"] * x["t"] ** 2
            case "h0":
                return x["y"] - x["vy"] * x["t"] + 0.5 * x["g"] * x["t"] ** 2


class RapidezNaChegada(FormulaBase):
    nome = "Rapidez na chegada"
    papeis = ("v_f", "vx", "vy_f")
    latex = "$v_f = \\sqrt{$vx^2 + $vy_f^2}"
    isoladas = {"v_f": "$v_f = \\sqrt{$vx^2 + $vy_f^2}"}

    def _isolar(self, papel, x):
        return math.hypot(x["vx"], x["vy_f"])


# =====================================================================
# Movimento vertical (eixo y para cima, aᵧ = −g, g > 0)
# =====================================================================

class VelocidadeVertical(FormulaBase):
    """v = v0 − g·t. Usada no lançamento vertical e, com outros papéis,
    para a componente vertical do projétil num instante."""

    nome = "Velocidade vertical"
    papeis = ("v", "v0", "g", "t")
    latex = "$v = $v0 - $g \\cdot $t"
    isoladas = {
        "v": "$v = $v0 - $g \\cdot $t",
        "v0": "$v0 = $v + $g \\cdot $t",
        "t": "$t = \\frac{$v0 - $v}{$g}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "v":
                return x["v0"] - x["g"] * x["t"]
            case "v0":
                return x["v"] + x["g"] * x["t"]
            case "t":
                return (x["v0"] - x["v"]) / x["g"]


class VelocidadeVerticalNaChegada(VelocidadeVertical):
    """vᵧ na chegada do projétil. Só calcula a velocidade: se também isolasse o
    tempo, o solver poderia "descobrir" o instante a partir do impacto no chão
    e inventar uma resposta quando o usuário não informou o instante."""

    nome = "Componente vertical na chegada"
    isoladas = {"v": "$v = $v0 - $g \\cdot $t"}


class PosicaoVertical(FormulaBase):
    nome = "Posição no lançamento vertical"
    papeis = ("dy", "v0", "g", "t")
    latex = "$dy = $v0 \\cdot $t - \\frac{1}{2} $g \\cdot $t^2"
    isoladas = {
        "dy": "$dy = $v0 \\cdot $t - \\frac{1}{2} $g \\cdot $t^2",
        "v0": "$v0 = \\frac{$dy + \\frac{1}{2} $g \\cdot $t^2}{$t}",
        "t": "$t = \\frac{$v0 \\pm \\sqrt{$v0^2 - 2 $g \\cdot $dy}}{$g}",
    }

    def _isolar(self, papel, x):
        match papel:
            case "dy":
                return x["v0"] * x["t"] - 0.5 * x["g"] * x["t"] ** 2
            case "v0":
                return (x["dy"] + 0.5 * x["g"] * x["t"] ** 2) / x["t"]
            case "t":
                return self.raizes(x["dy"], x["v0"], x["g"])[0]

    @staticmethod
    def raizes(dy, v0, g) -> list[float]:
        """Instantes positivos em que ½·g·t² − v0·t + Δy = 0, em ordem."""
        delta = v0**2 - 2 * g * dy
        if delta < 0:
            maximo = f"{v0**2 / (2 * g):.2f}".replace(".", ",")
            raise DadosInconsistentes(
                f"Lançamento vertical: essa altura não é atingida "
                f"(o máximo é {maximo} m acima do lançamento)"
            )
        raiz = math.sqrt(delta)
        positivas = sorted(t for t in ((v0 - raiz) / g, (v0 + raiz) / g) if t > 1e-12)
        if not positivas:
            raise DadosInconsistentes("Lançamento vertical: nenhum instante positivo atinge essa altura")
        return positivas

    def _observacao(self, papel):
        if papel == "t":
            return "A equação do 2º grau pode ter duas raízes positivas (subida e descida)."
        return None
