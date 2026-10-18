import pytest

from fisica.formulas import (
    DadosInconsistentes,
    EquacaoHoraria,
    Formula,
    FormulaBase,
    MovimentoUniforme,
    Torricelli,
    VelocidadeMedia,
    VelocidadeTempo,
)

# Um estado de MRUV coerente (conferido à mão):
# v0 = 20, a = -4, t = 3  ->  v = 20 - 4·3 = 8  ;  Δs = 20·3 - 2·9 = 42
MRUV_COERENTE = {"v0": 20.0, "a": -4.0, "t": 3.0, "v": 8.0, "ds": 42.0}
MRU_COERENTE = {"v": 14.0, "t": 3.0, "ds": 42.0}

CASOS = [
    (MovimentoUniforme, MRU_COERENTE, var) for var in ("ds", "v", "t")
] + [
    (classe, MRUV_COERENTE, var)
    for classe in (VelocidadeTempo, EquacaoHoraria, Torricelli, VelocidadeMedia)
    for var in classe.papeis
]


@pytest.mark.parametrize("classe, estado, alvo", CASOS)
def test_cada_isolamento_recupera_o_valor(classe, estado, alvo):
    formula = classe()
    conhecidas = {k: v for k, v in estado.items() if k in formula.variaveis and k != alvo}
    assert formula.calcular(alvo, conhecidas) == pytest.approx(estado[alvo])


# ---------- interface e classe abstrata ----------

def test_interface_e_abstrata_nao_podem_ser_instanciadas():
    with pytest.raises(TypeError):
        Formula()
    with pytest.raises(TypeError):
        FormulaBase()


def test_incognita_isolavel_so_com_exatamente_uma_incognita():
    f = VelocidadeTempo()
    assert f.incognita_isolavel({"v0": 20, "a": -4}) is None          # faltam v e t
    assert f.incognita_isolavel({"v0": 20, "a": -4, "v": 0}) == "t"
    assert f.incognita_isolavel({"v0": 20, "a": -4, "v": 0, "t": 5}) is None  # nada falta


# ---------- casos especiais ----------

def test_frenagem_tempo_ate_parar():
    assert EquacaoHoraria().calcular("t", {"ds": 50, "v0": 20, "a": -4}) == pytest.approx(5)


def test_queda_livre_tempo_de_queda():
    assert EquacaoHoraria().calcular("t", {"ds": 45, "v0": 0, "a": 9.81}) == pytest.approx(3.03, abs=0.01)


def test_equacao_horaria_sem_aceleracao_vira_mru():
    assert EquacaoHoraria().calcular("t", {"ds": 42, "v0": 14, "a": 0}) == pytest.approx(3)


def test_equacao_horaria_deslocamento_inalcancavel():
    # freando a -4 a partir de 20 m/s o carro para em 50 m; 100 m é impossível
    with pytest.raises(DadosInconsistentes, match="nunca atinge"):
        EquacaoHoraria().calcular("t", {"ds": 100, "v0": 20, "a": -4})


def test_torricelli_radicando_negativo():
    with pytest.raises(DadosInconsistentes, match="para antes"):
        Torricelli().calcular("v", {"v0": 20, "a": -4, "ds": 100})


def test_divisao_por_zero_vira_dados_inconsistentes():
    with pytest.raises(DadosInconsistentes, match="divisão por zero"):
        VelocidadeTempo().calcular("t", {"v": 10, "v0": 10, "a": 0})


# ---------- papéis renomeados (reuso na queda livre) ----------

def test_papeis_renomeados():
    f = VelocidadeTempo(nomes={"a": "g"})
    assert f.variaveis == {"v", "v0", "g", "t"}
    assert f.calcular("v", {"v0": 0, "g": 9.81, "t": 2}) == pytest.approx(19.62)


# ---------- passo a passo ----------

def test_passo_gera_latex_com_os_simbolos_do_movimento():
    simbolos = {"v": "v", "v0": "v_0", "a": "a", "t": "t"}
    conhecidas = {"v": 0, "v0": 20, "a": -4}
    passo = VelocidadeTempo().passo("t", conhecidas, 5.0, simbolos)
    assert passo.latex_isolada == "t = \\frac{v - v_0}{a}"
    assert passo.usadas == conhecidas
    assert passo.valor_si == 5.0


def test_passo_de_torricelli_tem_observacao_da_raiz():
    simbolos = {"v": "v", "v0": "v_0", "a": "a", "ds": "\\Delta s"}
    passo = Torricelli().passo("v", {"v0": 20, "a": -4, "ds": 42}, 8.0, simbolos)
    assert "positivo" in passo.observacao
