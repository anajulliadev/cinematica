"""Casos de uso mostrados no /docs: as questões do MVP (MVP_Cinematica_Questoes_do_Professor.pdf).

Cada exemplo aparece em dois lugares:
- no "Try it out" do POST /api/calcular (menu "Examples"), já preenchido;
- em "Responses", com o retorno REAL desse caso (gerado em main.py chamando calcular()).

Os de nome "erro_..." devolvem 400; os demais, 200.
"""


def _g(valor, unidade):
    return {"valor": valor, "unidade": unidade}


def _exemplo(summary, description, movimento, conhecidas, alvo, unidade_alvo=None):
    valor = {"movimento": movimento, "conhecidas": conhecidas, "alvo": alvo}
    if unidade_alvo:
        valor["unidade_alvo"] = unidade_alvo
    return {"summary": summary, "description": description, "value": valor}


EXEMPLOS = {
    # ---------------- 1D ----------------
    "q01_deslocamento": _exemplo(
        "Q01 · MU · motorista a 72 km/h durante 3 s → deslocamento",
        "Velocidade constante. 72 km/h vira 20 m/s antes da conta. Esperado: 60 m.",
        "mru", {"v": _g(72, "km/h"), "t": _g(3, "s")}, "ds", "m",
    ),
    "q02_deslocamento": _exemplo(
        "Q02 · MUV · leopardo de 6,20 a 23,1 m/s em 3,3 s → deslocamento",
        "A aceleração não é informada: o deslocamento sai pela velocidade média. Esperado: 48,345 m.",
        "mruv", {"v0": _g(6.20, "m/s"), "v": _g(23.1, "m/s"), "t": _g(3.3, "s")}, "ds", "m",
    ),
    "q03_aceleracao": _exemplo(
        "Q03 · MUV · carro de 18,5 a 46,1 m/s em 2,47 s → aceleração",
        "Com os mesmos dados, trocar o alvo para `ds` dá o deslocamento (79,781 m). Esperado: 11,174089 m/s².",
        "mruv", {"v0": _g(18.5, "m/s"), "v": _g(46.1, "m/s"), "t": _g(2.47, "s")}, "a",
    ),
    "q04_tempo_de_queda": _exemplo(
        "Q04 · Queda livre · pena caindo de 1,40 m na Lua → tempo de queda",
        "Gravidade lunar informada (1,67 m/s²); v0 = 0 é o padrão. Esperado: 1,294854 s.",
        "queda_livre", {"h": _g(1.40, "m"), "g": _g(1.67, "m/s2")}, "t", "s",
    ),
    "q05_tempo_para_altura": _exemplo(
        "Q05 · Lançamento vertical · lápis a 18,3 m/s até 12,2 m → os dois instantes",
        "`dy` é a altura acima do lançamento. Os dois instantes vêm em `resultado.solucoes` "
        "(Subida 0,869 s e Descida 2,862 s); `resultado.valor` é o primeiro.",
        "lancamento_vertical", {"v0": _g(18.3, "m/s"), "dy": _g(12.2, "m")}, "t", "s",
    ),
    # ---------------- 2D ----------------
    "q06_tempo_de_queda": _exemplo(
        "Q06 · Lançamento horizontal · prédio de 60 m → tempo de queda",
        "Horizontal = `theta: 0`. O alcance não é necessário para o tempo. Esperado: 3,497487 s.",
        "projetil", {"h0": _g(60, "m"), "theta": _g(0, "grau")}, "t_voo", "s",
    ),
    "q06_rapidez_de_impacto": _exemplo(
        "Q06 · Lançamento horizontal · prédio de 60 m, cai a 100 m → rapidez de impacto",
        "Com o alcance, sai a velocidade horizontal e a rapidez. Outros alvos com os mesmos dados: "
        "`vx` (28,59 m/s) e `vy_f` (−34,31 m/s). Esperado: 44,662064 m/s.",
        "projetil", {"h0": _g(60, "m"), "theta": _g(0, "grau"), "A": _g(100, "m")}, "v_f", "m/s",
    ),
    "q07_tempo_de_voo": _exemplo(
        "Q07 · Lançamento oblíquo · componentes 16 e 12 m/s → tempo de voo",
        "Entrada por componentes (`vx`, `vy`), do chão ao chão. Com os mesmos dados: "
        "`H` (7,34 m) e `v_f` (20 m/s). Esperado: 2,446483 s.",
        "projetil", {"vx": _g(16, "m/s"), "vy": _g(12, "m/s")}, "t_voo", "s",
    ),
    "q08_altura_no_instante": _exemplo(
        "Q08 · Lançamento oblíquo · flecha a 30 m/s e 60°, de 1,5 m, chega ao penhasco em 4 s → altura",
        "`t` é o instante de chegada (alturas diferentes entre início e fim). Com os mesmos dados: "
        "`H` (35,90 m) e `v_f` (20,02 m/s, rapidez no instante t). Esperado: 26,943048 m.",
        "projetil",
        {"v0": _g(30, "m/s"), "theta": _g(60, "grau"), "h0": _g(1.5, "m"), "t": _g(4, "s")},
        "y", "m",
    ),
    # ---------------- Erros (400) ----------------
    "erro_dados_insuficientes": _exemplo(
        "Erro 400 · Q03 sem o tempo",
        "Sem o intervalo de tempo não dá para calcular a aceleração. `faltando` lista o que resolveria.",
        "mruv", {"v0": _g(18.5, "m/s"), "v": _g(46.1, "m/s")}, "a",
    ),
    "erro_dados_inconsistentes": _exemplo(
        "Erro 400 · Q05 com Δy = 20 m (acima da altura máxima)",
        "A 18,3 m/s o lápis sobe no máximo cerca de 17,07 m: essa altura não é atingida.",
        "lancamento_vertical", {"v0": _g(18.3, "m/s"), "dy": _g(20, "m")}, "t",
    ),
    "erro_entrada_invalida": _exemplo(
        "Erro 400 · Q04 com gravidade zero",
        "A gravidade precisa ser maior que zero.",
        "queda_livre", {"h": _g(1.40, "m"), "g": _g(0, "m/s2")}, "t",
    ),
}
