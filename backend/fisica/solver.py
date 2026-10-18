"""Solver: encadeia as fórmulas de um movimento até chegar no alvo."""
import math
from dataclasses import dataclass

from fisica.formulas import DadosInconsistentes, Formula, Passo
from fisica.movimentos import Movimento
from fisica.unidades import EntradaInvalida


class DadosInsuficientes(Exception):
    def __init__(self, alvo: str, faltando: list[str], mensagem: str):
        super().__init__(mensagem)
        self.alvo = alvo
        self.faltando = faltando


@dataclass
class Resultado:
    alvo: str
    valor_si: float
    passos: list[Passo]
    estado: dict[str, float]     # tudo que foi possível calcular (SI)


class Solver:
    def __init__(self, movimento: Movimento):
        self.mov = movimento

    def resolver(self, entradas: dict[str, float], alvo: str) -> Resultado:
        self._validar(entradas, alvo)
        conhecidas = {**self.mov.padroes, **entradas}
        passos: list[Passo] = []
        bloqueadas: dict[tuple[Formula, str], DadosInconsistentes] = {}

        # Laço do PDF: enquanto houver fórmula com exatamente uma incógnita
        while alvo not in conhecidas:
            passo = self._dar_um_passo(conhecidas, bloqueadas)
            if passo is None:
                break
            passos.append(passo)

        if alvo not in conhecidas:
            if bloqueadas:
                # alguma conta foi impossível: o problema são os dados, não a falta deles
                raise next(iter(bloqueadas.values()))
            faltando = self._o_que_falta(conhecidas, alvo)
            raise DadosInsuficientes(alvo, faltando, self._mensagem(alvo, faltando))

        # Continua sem guardar passos, para o card e a animação terem tudo
        estado = dict(conhecidas)
        while self._dar_um_passo(estado, bloqueadas) is not None:
            pass

        return Resultado(alvo, conhecidas[alvo], passos, estado)

    # ------------------------------------------------------------------

    def _dar_um_passo(self, conhecidas, bloqueadas) -> Passo | None:
        """Resolve a primeira fórmula possível. Recomeçar da primeira fórmula
        a cada passo deixa o passo a passo mais curto e previsível."""
        for formula in self.mov.formulas:
            var = formula.incognita_isolavel(conhecidas)
            if var is None or (formula, var) in bloqueadas:
                continue
            try:
                valor = formula.calcular(var, conhecidas)
                self._checar_sinal(var, valor)
            except DadosInconsistentes as erro:
                bloqueadas[(formula, var)] = erro
                continue
            passo = formula.passo(var, conhecidas, valor, self.mov.simbolos())
            conhecidas[var] = valor
            return passo
        return None

    def _alcancaveis(self, conhecidas: dict[str, float]) -> set[str]:
        """Quais variáveis dá para chegar, olhando só os NOMES (sem fazer contas)."""
        k = dict(conhecidas)
        mudou = True
        while mudou:
            mudou = False
            for formula in self.mov.formulas:
                var = formula.incognita_isolavel(k)
                if var is not None:
                    k[var] = math.nan      # "conhecida", valor ainda não importa
                    mudou = True
        return set(k)

    def _o_que_falta(self, conhecidas, alvo) -> list[str]:
        """Variáveis que, se o usuário informasse só ela a mais, destravariam o alvo."""
        return [
            u for u in self.mov.variaveis
            if u not in conhecidas and u != alvo
            and alvo in self._alcancaveis({**conhecidas, u: math.nan})
        ]

    def _mensagem(self, alvo, faltando) -> str:
        variaveis = self.mov.variaveis
        inicio = f"Não foi possível calcular {variaveis[alvo].nome} ({alvo})."
        if not faltando:
            return inicio + " Faltam pelo menos dois dados: informe mais grandezas."
        opcoes = [f"{variaveis[u].nome} ({u})" for u in faltando]
        if len(opcoes) > 1:
            texto = ", ".join(opcoes[:-1]) + " ou " + opcoes[-1]
        else:
            texto = opcoes[0]
        return f"{inicio} Informe também: {texto}."

    def _validar(self, entradas, alvo):
        variaveis = self.mov.variaveis
        for id_var in [*entradas, alvo]:
            if id_var not in variaveis:
                aceitas = ", ".join(variaveis)
                raise EntradaInvalida(
                    f"'{id_var}' não é variável de {self.mov.nome} (aceitas: {aceitas})"
                )
        for id_var, valor in entradas.items():
            if variaveis[id_var].nao_negativa and valor < 0:
                raise EntradaInvalida(f"{variaveis[id_var].nome} não pode ser negativo")

    def _checar_sinal(self, var, valor):
        variavel = self.mov.variaveis[var]
        if variavel.nao_negativa and valor < -1e-9:
            raise DadosInconsistentes(f"{variavel.nome} deu negativo ({valor:.3g})")
