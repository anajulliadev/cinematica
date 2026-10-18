from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import (
    CalculoEntrada,
    CalculoSaida,
    ErroSaida,
    GrandezaEntrada,
    GrandezaSaida,
    PassoSaida,
    VariavelFaltante,
)
from fisica.formulas import DadosInconsistentes, Passo
from fisica.movimentos import MOVIMENTOS, Movimento, Variavel
from fisica.solver import DadosInsuficientes, Solver
from fisica.unidades import Conversor, EntradaInvalida, Grandeza, Unidade

app = FastAPI(title="Calculadora de Cinemática 1D e 2D")


@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/calcular", responses={400: {"model": ErroSaida}})
def calcular(req: CalculoEntrada) -> CalculoSaida:
    mov = MOVIMENTOS[req.movimento]

    # 1. Borda de entrada: valor + unidade -> SI (checando a dimensão de cada campo)
    entradas = {id_var: _para_si(mov, id_var, g) for id_var, g in req.conhecidas.items()}
    unidade_saida = _unidade_de_saida(mov, req.alvo, req.unidade_alvo)

    # 2. Núcleo: só números em SI
    resultado = Solver(mov).resolver(entradas, req.alvo)

    # 3. Borda de saída: SI -> unidade escolhida
    return CalculoSaida(
        movimento=req.movimento,
        alvo=req.alvo,
        resultado=_grandeza_saida(resultado.valor_si, unidade_saida),
        passos=[_passo_saida(mov, p) for p in resultado.passos],
        estado=resultado.estado,
        trajetoria=[],   # etapa 8
    )


# ---------- conversões entre o JSON e o núcleo ----------

def _variavel(mov: Movimento, id_var: str) -> Variavel:
    if id_var not in mov.variaveis:
        aceitas = ", ".join(mov.variaveis)
        raise EntradaInvalida(f"'{id_var}' não é variável de {mov.nome} (aceitas: {aceitas})")
    return mov.variaveis[id_var]


def _para_si(mov: Movimento, id_var: str, entrada: GrandezaEntrada) -> float:
    unidade = Conversor.buscar(entrada.unidade)
    Conversor.exigir_dimensao(unidade, _variavel(mov, id_var).dimensao)
    return Conversor.para_si(Grandeza(entrada.valor, unidade))


def _unidade_de_saida(mov: Movimento, alvo: str, id_unidade: str | None) -> Unidade:
    dimensao = _variavel(mov, alvo).dimensao
    if id_unidade is None:
        return Conversor.si_de(dimensao)
    unidade = Conversor.buscar(id_unidade)
    Conversor.exigir_dimensao(unidade, dimensao)
    return unidade


def _grandeza_saida(valor_si: float, unidade: Unidade) -> GrandezaSaida:
    unidades = Conversor.unidades_de(unidade.dimensao)
    return GrandezaSaida(
        valor=Conversor.do_si(valor_si, unidade).valor,
        unidade=unidade.id,
        valor_si=valor_si,
        unidade_si=Conversor.si_de(unidade.dimensao).id,
        conversoes={u.id: Conversor.do_si(valor_si, u).valor for u in unidades},
    )


def _passo_saida(mov: Movimento, passo: Passo) -> PassoSaida:
    dimensao = mov.variaveis[passo.variavel].dimensao
    return PassoSaida(**asdict(passo), unidade_si=Conversor.si_de(dimensao).id)


# ---------- erros do núcleo -> HTTP 400 com corpo ErroSaida ----------

TIPOS_DE_ERRO = {
    DadosInsuficientes: "dados_insuficientes",
    DadosInconsistentes: "dados_inconsistentes",
    EntradaInvalida: "entrada_invalida",
}


@app.exception_handler(DadosInsuficientes)
@app.exception_handler(DadosInconsistentes)
@app.exception_handler(EntradaInvalida)
async def erro_de_fisica(request: Request, erro: Exception) -> JSONResponse:
    faltando = [
        VariavelFaltante(id=id_var, nome=erro.nomes.get(id_var, id_var))
        for id_var in getattr(erro, "faltando", [])
    ]
    corpo = ErroSaida(tipo=TIPOS_DE_ERRO[type(erro)], mensagem=str(erro), faltando=faltando)
    return JSONResponse(status_code=400, content=corpo.model_dump())


# Na entrega, serve o React compilado (frontend/dist).
# Fica por último para não sobrepor as rotas /api.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
