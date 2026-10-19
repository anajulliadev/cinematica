from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import Body, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.exemplos import EXEMPLOS
from app.schemas import (
    CalculoEntrada,
    CalculoSaida,
    ErroSaida,
    GrandezaEntrada,
    GrandezaSaida,
    PassoSaida,
    SolucaoSaida,
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


@app.post(
    "/api/calcular",
    summary="Calcula uma grandeza a partir do que se conhece",
    responses={400: {"model": ErroSaida, "description": "Erro de física (faltam dados, conta impossível ou entrada inválida)"}},
)
def calcular(req: Annotated[CalculoEntrada, Body(openapi_examples=EXEMPLOS)]) -> CalculoSaida:
    """Informe as grandezas conhecidas (cada uma com sua unidade) e o `alvo`.
    O solver escolhe e encadeia as fórmulas e devolve o resultado, o passo a passo,
    o estado completo (SI) e 61 pontos da trajetória.

    Use o menu **Examples** abaixo para carregar um caso pronto; os retornos de cada
    caso aparecem em **Responses** (200 e 400). Guia completo: `backend/docs/API.md`.
    """
    mov = MOVIMENTOS[req.movimento]

    # 1. Borda de entrada: valor + unidade -> SI (checando a dimensão de cada campo)
    entradas = {id_var: _para_si(mov, id_var, g) for id_var, g in req.conhecidas.items()}
    unidade_saida = _unidade_de_saida(mov, req.alvo, req.unidade_alvo)

    # 2. Núcleo: só números em SI
    resultado = Solver(mov).resolver(entradas, req.alvo)

    # 3. Borda de saída: SI -> unidade escolhida
    solucoes = mov.solucoes(req.alvo, resultado.estado)
    return CalculoSaida(
        movimento=req.movimento,
        alvo=req.alvo,
        resultado=_grandeza_saida(resultado.valor_si, unidade_saida, solucoes),
        passos=[_passo_saida(mov, p) for p in resultado.passos],
        estado=resultado.estado,
        trajetoria=mov.trajetoria(resultado.estado),
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


def _grandeza_saida(valor_si: float, unidade: Unidade, solucoes=()) -> GrandezaSaida:
    unidades = Conversor.unidades_de(unidade.dimensao)
    return GrandezaSaida(
        valor=Conversor.do_si(valor_si, unidade).valor,
        unidade=unidade.id,
        valor_si=valor_si,
        unidade_si=Conversor.si_de(unidade.dimensao).id,
        conversoes={u.id: Conversor.do_si(valor_si, u).valor for u in unidades},
        solucoes=[
            SolucaoSaida(rotulo=rotulo, valor=Conversor.do_si(v, unidade).valor, valor_si=v)
            for rotulo, v in solucoes
        ],
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


def _erro_saida(erro: Exception) -> ErroSaida:
    faltando = [
        VariavelFaltante(id=id_var, nome=erro.nomes.get(id_var, id_var))
        for id_var in getattr(erro, "faltando", [])
    ]
    return ErroSaida(tipo=TIPOS_DE_ERRO[type(erro)], mensagem=str(erro), faltando=faltando)


@app.exception_handler(DadosInsuficientes)
@app.exception_handler(DadosInconsistentes)
@app.exception_handler(EntradaInvalida)
async def erro_de_fisica(request: Request, erro: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content=_erro_saida(erro).model_dump())


# ---------- /docs: retorno real de cada exemplo ----------
# O FastAPI monta o OpenAPI na primeira vez que alguém abre /docs. Aqui o resultado é
# completado com o retorno de cada caso de app/exemplos.py, calculado chamando a
# própria rota. Assim os exemplos de resposta nunca ficam desatualizados.

_gerar_openapi = app.openapi


def _resumir(saida: dict) -> dict:
    """Mostra só 3 dos 61 pontos da trajetória, para o exemplo caber na tela."""
    pontos = saida["trajetoria"]
    if len(pontos) > 3:
        saida["trajetoria"] = [pontos[0], pontos[len(pontos) // 2], pontos[-1]]
    return saida


def _openapi_com_exemplos() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = _gerar_openapi()

    sucesso, erros = {}, {}
    for nome, exemplo in EXEMPLOS.items():
        try:
            saida = calcular(CalculoEntrada.model_validate(exemplo["value"]))
            sucesso[nome] = {
                "summary": exemplo["summary"],
                "description": "Trajetória resumida: 1º, ponto do meio e último dos 61 pontos.",
                "value": _resumir(saida.model_dump()),
            }
        except tuple(TIPOS_DE_ERRO) as erro:
            erros[nome] = {"summary": exemplo["summary"], "value": _erro_saida(erro).model_dump()}

    respostas = schema["paths"]["/api/calcular"]["post"]["responses"]
    respostas["200"]["content"]["application/json"]["examples"] = sucesso
    respostas["400"]["content"]["application/json"]["examples"] = erros
    return schema


app.openapi = _openapi_com_exemplos


# Na entrega, serve o React compilado (frontend/dist).
# Fica por último para não sobrepor as rotas /api.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
