from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.schemas import CalculoEntrada, CalculoSaida, ErroSaida, GrandezaSaida, PassoSaida

app = FastAPI(title="Calculadora de Cinemática 1D e 2D")

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.post("/api/calcular", responses={400: {"model": ErroSaida}})
def calcular(req: CalculoEntrada) -> CalculoSaida:
    
    return CalculoSaida(
        movimento=req.movimento,
        alvo=req.alvo,
        resultado=GrandezaSaida(
            valor=50.0, unidade="m", valor_si=50.0, unidade_si="m",
            conversoes={"m": 50.0, "cm": 5000.0, "km": 0.05},
        ),
        passos=[
            PassoSaida(
                formula="Equação de Torricelli",
                latex="v^2 = v_0^2 + 2 a \\Delta s",
                latex_isolada="\\Delta s = \\frac{v^2 - v_0^2}{2a}",
                variavel="ds", valor_si=50.0, unidade_si="m",
                usadas={"v0": 20.0, "v": 0.0, "a": -4.0},
            )
        ],
        estado={"v0": 20.0, "v": 0.0, "a": -4.0, "ds": 50.0, "t": 5.0},
        trajetoria=[{"t": t, "s": 20 * t - 2 * t**2, "v": 20 - 4 * t} for t in range(6)],
    )



# Na entrega, serve o React compilado (frontend/dist).
# Fica por último para não sobrepor as rotas /api.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")