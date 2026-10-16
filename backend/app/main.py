from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Calculadora de Cinemática 2D e 3D")

@app.get("/api/ping")
def ping():
    return {"status": "ok"}


# Na entrega, serve o React compilado (frontend/dist).
# Fica por último para não sobrepor as rotas /api.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")