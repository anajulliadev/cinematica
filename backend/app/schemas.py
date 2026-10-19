from typing import Literal

from pydantic import BaseModel, Field

# Literal: o campo só aceita exatamente estes textos (outro valor -> erro 422).
IdMovimento = Literal["mru", "mruv", "queda_livre", "lancamento_vertical", "projetil"]


# ---------- Entrada ----------

class GrandezaEntrada(BaseModel):
    # allow_inf_nan=False recusa "Infinity"/"NaN", que quebrariam as contas
    valor: float = Field(allow_inf_nan=False)
    unidade: str


class CalculoEntrada(BaseModel):
    movimento: IdMovimento
    # dict[str, GrandezaEntrada]: cada valor do dicionário é validado como GrandezaEntrada
    conhecidas: dict[str, GrandezaEntrada]
    alvo: str
    # "str | None = None" = campo opcional; se não vier, devolvemos em SI
    unidade_alvo: str | None = None


# ---------- Saída ----------

class SolucaoSaida(BaseModel):
    rotulo: str          # ex.: "Subida", "Descida"
    valor: float         # na unidade do resultado
    valor_si: float


class GrandezaSaida(BaseModel):
    valor: float
    unidade: str
    valor_si: float
    unidade_si: str
    conversoes: dict[str, float]
    # Quando o alvo tem mais de uma resposta válida (ex.: os dois instantes do
    # lançamento vertical). Vazio no caso comum; "valor" é sempre a primeira.
    solucoes: list[SolucaoSaida] = []


class PassoSaida(BaseModel):
    formula: str
    latex: str
    latex_isolada: str
    variavel: str
    valor_si: float
    unidade_si: str
    usadas: dict[str, float]
    observacao: str | None = None


class CalculoSaida(BaseModel):
    movimento: IdMovimento
    alvo: str
    resultado: GrandezaSaida
    passos: list[PassoSaida]
    estado: dict[str, float]
    trajetoria: list[dict[str, float]]


# ---------- Erro ----------

class VariavelFaltante(BaseModel):
    id: str
    nome: str


class ErroSaida(BaseModel):
    tipo: Literal["dados_insuficientes", "dados_inconsistentes", "entrada_invalida"]
    mensagem: str
    faltando: list[VariavelFaltante] = []
