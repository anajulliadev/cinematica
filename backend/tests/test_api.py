import pytest
from fastapi.testclient import TestClient

from app.exemplos import EXEMPLOS
from app.main import app

cliente = TestClient(app)


# ---------- exemplos do /docs ----------

@pytest.mark.parametrize("nome", list(EXEMPLOS))
def test_exemplo_do_docs_responde_o_status_esperado(nome):
    # "erro_..." tem que dar 400; os outros, 200 (se um exemplo quebrar, o /docs mentiria)
    esperado = 400 if nome.startswith("erro_") else 200
    assert calcular(EXEMPLOS[nome]["value"]).status_code == esperado


def test_docs_mostra_retorno_de_cada_exemplo():
    respostas = cliente.get("/openapi.json").json()["paths"]["/api/calcular"]["post"]["responses"]
    sucesso = respostas["200"]["content"]["application/json"]["examples"]
    erros = respostas["400"]["content"]["application/json"]["examples"]
    assert set(sucesso) | set(erros) == set(EXEMPLOS)
    assert sucesso["q01_deslocamento"]["value"]["resultado"]["valor"] == pytest.approx(60)
    assert erros["erro_dados_insuficientes"]["value"]["tipo"] == "dados_insuficientes"

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


def calcular(corpo):
    return cliente.post("/api/calcular", json=corpo)


# ---------- 200: o contrato com valores reais ----------

def test_calcular_segue_o_contrato():
    resposta = calcular(FRENAGEM)
    assert resposta.status_code == 200
    assert set(resposta.json()) == {
        "movimento", "alvo", "resultado", "passos", "estado", "trajetoria",
    }


def test_frenagem_pela_api():
    corpo = calcular(FRENAGEM).json()
    assert corpo["resultado"]["valor"] == pytest.approx(50, abs=0.01)
    assert corpo["resultado"]["conversoes"]["cm"] == pytest.approx(5000, abs=1)
    assert corpo["estado"]["t"] == pytest.approx(5, abs=0.01)
    assert [p["variavel"] for p in corpo["passos"]] == ["t", "ds"]
    assert corpo["passos"][0]["unidade_si"] == "s"


def test_queda_livre_com_resultado_em_kmh():
    corpo = calcular({
        "movimento": "queda_livre",
        "conhecidas": {"h": {"valor": 4500, "unidade": "cm"}},
        "alvo": "v",
        "unidade_alvo": "km/h",
    }).json()
    assert corpo["resultado"]["unidade"] == "km/h"
    assert corpo["resultado"]["valor"] == pytest.approx(107, abs=0.1)
    assert corpo["resultado"]["valor_si"] == pytest.approx(29.71, abs=0.01)


def test_sem_unidade_alvo_devolve_em_si():
    corpo = calcular({**FRENAGEM, "unidade_alvo": None}).json()
    assert corpo["resultado"]["unidade"] == "m"


def test_lancamento_obliquo_em_graus():
    corpo = calcular({
        "movimento": "projetil",
        "conhecidas": {
            "v0": {"valor": 20, "unidade": "m/s"},
            "theta": {"valor": 35, "unidade": "grau"},
        },
        "alvo": "A",
    }).json()
    assert corpo["resultado"]["valor"] == pytest.approx(38.3, abs=0.05)
    assert corpo["estado"]["H"] == pytest.approx(6.71, abs=0.01)


# ---------- 400: erros de física ----------

def test_caso_de_erro_do_video():
    resposta = calcular({
        "movimento": "projetil",
        "conhecidas": {
            "h0": {"valor": 45, "unidade": "m"},
            "theta": {"valor": 0, "unidade": "grau"},
        },
        "alvo": "v0",
    })
    assert resposta.status_code == 400
    corpo = resposta.json()
    assert corpo["tipo"] == "dados_insuficientes"
    assert "alcance horizontal" in corpo["mensagem"]
    assert corpo["faltando"] == [
        {"id": "A", "nome": "alcance horizontal"},
        {"id": "vx", "nome": "velocidade horizontal"},
    ]


def test_dados_inconsistentes():
    corpo = {**FRENAGEM, "conhecidas": {
        "v0": {"valor": 20, "unidade": "m/s"},
        "a": {"valor": -4, "unidade": "m/s2"},
        "ds": {"valor": 100, "unidade": "m"},
    }, "alvo": "t", "unidade_alvo": None}
    resposta = calcular(corpo)
    assert resposta.status_code == 400
    assert resposta.json()["tipo"] == "dados_inconsistentes"


@pytest.mark.parametrize(
    "mudanca",
    [
        {"conhecidas": {"t": {"valor": 5, "unidade": "km/h"}}},      # dimensão errada
        {"conhecidas": {"v0": {"valor": 5, "unidade": "polegada"}}},  # unidade inexistente
        {"conhecidas": {"x": {"valor": 5, "unidade": "m"}}},          # variável inexistente
        {"alvo": "x"},                                                # alvo inexistente
        {"unidade_alvo": "s"},                                        # ds em segundos
    ],
)
def test_entrada_invalida(mudanca):
    resposta = calcular({**FRENAGEM, **mudanca})
    assert resposta.status_code == 400
    assert resposta.json()["tipo"] == "entrada_invalida"


# ---------- 422: JSON fora do formato (Pydantic) ----------

def test_movimento_inexistente_da_422():
    resposta = calcular({**FRENAGEM, "movimento": "teletransporte"})
    assert resposta.status_code == 422


def test_valor_nao_numerico_da_422():
    corpo = {**FRENAGEM, "conhecidas": {"a": {"valor": "abc", "unidade": "m/s2"}}}
    assert calcular(corpo).status_code == 422
