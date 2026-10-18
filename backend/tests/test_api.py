from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)

FRENAGEM = {
    "movimento": "mruv",
    "conhecidas": {
        "v0": {"valor": 72, "unidade": "km/h"},
        "v": {"valor": 0, "unidade": "m/s"},
        "a": {"valor": -4, "unidade": "m/s2"},
    },
    "alvo": "ds",
    "unidade_alvo": "m",
}


def test_calcular_segue_o_contrato():
    resposta = cliente.post("/api/calcular", json=FRENAGEM)
    assert resposta.status_code == 200
    assert set(resposta.json()) == {
        "movimento", "alvo", "resultado", "passos", "estado", "trajetoria",
    }


def test_movimento_inexistente_da_422():
    resposta = cliente.post("/api/calcular", json={**FRENAGEM, "movimento": "teletransporte"})
    assert resposta.status_code == 422


def test_valor_nao_numerico_da_422():
    corpo = {**FRENAGEM, "conhecidas": {"a": {"valor": "abc", "unidade": "m/s2"}}}
    assert cliente.post("/api/calcular", json=corpo).status_code == 422
