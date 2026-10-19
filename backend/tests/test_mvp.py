"""As 8 questões do MVP (MVP_Cinematica_Questoes_do_Professor.pdf).

Resultados esperados: página 20 do PDF. Os testes "conferência" vêm das
observações no rodapé de cada página preenchida.
"""
import math

import pytest

from fisica.formulas import DadosInconsistentes
from fisica.movimentos import MOVIMENTOS
from fisica.solver import DadosInsuficientes, Solver
from fisica.unidades import Conversor, EntradaInvalida, Grandeza


def si(valor, unidade):
    return Conversor.para_si(Grandeza(valor, Conversor.buscar(unidade)))


def resolver(movimento, entradas, alvo):
    return Solver(MOVIMENTOS[movimento]).resolver(entradas, alvo)


def aprox(valor):
    return pytest.approx(valor, abs=1e-6)


# ---------- 01: motorista a 72 km/h durante 3 s (MU) ----------

def test_q01_deslocamento():
    r = resolver("mru", {"v": si(72, "km/h"), "t": si(3, "s")}, "ds")
    assert r.valor_si == aprox(60)


def test_q01_mesmo_resultado_em_outras_unidades():
    r = resolver("mru", {"v": si(20, "m/s"), "t": si(3000, "ms")}, "ds")
    assert r.valor_si == aprox(60)


# ---------- 02: leopardo (MUV, deslocamento sem aceleração) ----------

def test_q02_deslocamento_sem_aceleracao():
    r = resolver("mruv", {"v0": 6.20, "v": 23.1, "t": 3.3}, "ds")
    assert r.valor_si == aprox(48.345)
    assert [p.formula for p in r.passos] == ["Deslocamento pela velocidade média"]


def test_q02_velocidades_em_kmh():
    r = resolver("mruv", {"v0": si(22.32, "km/h"), "v": si(83.16, "km/h"), "t": 3.3}, "ds")
    assert r.valor_si == aprox(48.345)


# ---------- 03: carro de corrida (MUV, dois objetivos com os mesmos dados) ----------

CARRO = {"v0": 18.5, "v": 46.1, "t": 2.47}


def test_q03_aceleracao():
    assert resolver("mruv", CARRO, "a").valor_si == aprox(11.174089)


def test_q03_deslocamento_com_os_mesmos_dados():
    assert resolver("mruv", CARRO, "ds").valor_si == aprox(79.781)


def test_q03_sem_tempo_nao_inventa_duracao():
    with pytest.raises(DadosInsuficientes):
        resolver("mruv", {"v0": 18.5, "v": 46.1}, "a")


# ---------- 04: pena na Lua (queda livre com g editável) ----------

def test_q04_tempo_de_queda_na_lua():
    assert resolver("queda_livre", {"h": 1.40, "g": 1.67}, "t").valor_si == aprox(1.294854)


def test_q04_altura_em_cm():
    assert resolver("queda_livre", {"h": si(140, "cm"), "g": 1.67}, "t").valor_si == aprox(1.294854)


@pytest.mark.parametrize("g", [0, -1.67])
def test_q04_rejeita_gravidade_zero_ou_negativa(g):
    with pytest.raises(EntradaInvalida, match="maior que zero"):
        resolver("queda_livre", {"h": 1.40, "g": g}, "t")


def test_q04_com_g_terrestre_o_resultado_muda():
    assert resolver("queda_livre", {"h": 1.40}, "t").valor_si != aprox(1.294854)


# ---------- 05: lápis lançado para cima (duas raízes) ----------

def test_q05_os_dois_instantes():
    entradas = {"v0": 18.3, "dy": 12.2}
    r = resolver("lancamento_vertical", entradas, "t")
    solucoes = MOVIMENTOS["lancamento_vertical"].solucoes("t", r.estado)
    assert [rotulo for rotulo, _ in solucoes] == ["Subida", "Descida"]
    assert solucoes[0][1] == aprox(0.869140) and solucoes[1][1] == aprox(2.861747)
    assert r.valor_si == aprox(0.869140)   # o valor principal é o primeiro instante


def test_q05_conferencia_das_raizes():
    for _, t in MOVIMENTOS["lancamento_vertical"].solucoes("t", {"v0": 18.3, "dy": 12.2, "g": 9.81}):
        assert 18.3 * t - 0.5 * 9.81 * t**2 == aprox(12.2)


def test_q05_altura_acima_do_maximo():
    with pytest.raises(DadosInconsistentes, match="17,07"):
        resolver("lancamento_vertical", {"v0": 18.3, "dy": 20}, "t")


# ---------- 06: bola lançada horizontalmente de um prédio de 60 m ----------

PREDIO = {"h0": 60, "theta": 0, "A": 100}


def test_q06_tempo_de_queda_sem_alcance():
    assert resolver("projetil", {"h0": 60, "theta": 0}, "t_voo").valor_si == aprox(3.497487)


def test_q06_velocidade_horizontal():
    assert resolver("projetil", PREDIO, "vx").valor_si == aprox(28.591957)


def test_q06_velocidade_vertical_no_impacto_sem_alcance():
    assert resolver("projetil", {"h0": 60, "theta": 0}, "vy_f").valor_si == aprox(-34.310348)


def test_q06_rapidez_de_impacto():
    assert resolver("projetil", PREDIO, "v_f").valor_si == aprox(44.662064)


@pytest.mark.parametrize("alvo", ["vx", "v_f"])
def test_q06_sem_alcance_faltam_dados(alvo):
    with pytest.raises(DadosInsuficientes) as erro:
        resolver("projetil", {"h0": 60, "theta": 0}, alvo)
    assert "A" in erro.value.faltando


# ---------- 07: bola com componentes 16 e 12 m/s ----------

COMPONENTES = {"vx": 16, "vy": 12}


def test_q07_tempo_de_voo():
    assert resolver("projetil", COMPONENTES, "t_voo").valor_si == aprox(2.446483)


def test_q07_altura_maxima():
    assert resolver("projetil", COMPONENTES, "H").valor_si == aprox(7.339450)


def test_q07_rapidez_de_impacto():
    assert resolver("projetil", COMPONENTES, "v_f").valor_si == aprox(20)


def test_q07_sem_vx_calcula_tempo_e_altura_mas_nao_rapidez():
    assert resolver("projetil", {"vy": 12}, "t_voo").valor_si == aprox(2.446483)
    assert resolver("projetil", {"vy": 12}, "H").valor_si == aprox(7.339450)
    with pytest.raises(DadosInsuficientes):
        resolver("projetil", {"vy": 12}, "v_f")


# ---------- 08: flecha que chega ao penhasco após 4 s ----------

FLECHA = {"v0": 30, "theta": math.radians(60), "h0": 1.5, "t": 4}


def test_q08_altura_no_instante():
    r = resolver("projetil", FLECHA, "y")
    assert r.valor_si == aprox(26.943048)
    assert [p.formula for p in r.passos] == ["Componente vertical da velocidade", "Altura no instante"]


def test_q08_altura_maxima():
    assert resolver("projetil", FLECHA, "H").valor_si == aprox(35.903670)


def test_q08_rapidez_no_instante_de_chegada():
    assert resolver("projetil", FLECHA, "v_f").valor_si == aprox(20.020175)


def test_q08_trajetoria_termina_no_penhasco():
    estado = resolver("projetil", FLECHA, "y").estado
    pontos = MOVIMENTOS["projetil"].trajetoria(estado)
    assert pontos[-1]["t"] == aprox(4)
    assert pontos[-1]["y"] == aprox(26.943048)


def test_q08_sem_tempo_altura_maxima_continua_e_altura_no_instante_nao():
    sem_t = {k: v for k, v in FLECHA.items() if k != "t"}
    assert resolver("projetil", sem_t, "H").valor_si == aprox(35.903670)
    with pytest.raises(DadosInsuficientes) as erro:
        resolver("projetil", sem_t, "y")
    assert erro.value.faltando == ["t"]
