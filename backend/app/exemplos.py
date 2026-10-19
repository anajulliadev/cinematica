"""Casos de uso mostrados no /docs.

Cada exemplo aparece em dois lugares:
- no "Try it out" do POST /api/calcular (menu "Examples"), já preenchido;
- em "Responses", com o retorno REAL desse caso (gerado em main.py chamando calcular()).

Os de nome "erro_..." devolvem 400; os demais, 200.
"""

EXEMPLOS = {
    # ---------------- MRU ----------------
    "mru": {
        "summary": "MRU · carro a 72 km/h durante 10 min (distância em km)",
        "description": "Velocidade constante. Informa `v` e `t`; pede `ds` em km. "
                       "Repare na conversão: 72 km/h → 20 m/s e 10 min → 600 s.",
        "value": {
            "movimento": "mru",
            "conhecidas": {
                "v": {"valor": 72, "unidade": "km/h"},
                "t": {"valor": 10, "unidade": "min"},
            },
            "alvo": "ds",
            "unidade_alvo": "km",
        },
    },
    # ---------------- MRUV ----------------
    "mruv_frenagem": {
        "summary": "MRUV · tema 2: carro a 72 km/h freia a −4 m/s² até parar",
        "description": "\"Até parar\" = `v = 0`. O solver encadeia duas fórmulas: "
                       "primeiro acha `t` = 5 s, depois `ds` = 50 m (ver `passos`).",
        "value": {
            "movimento": "mruv",
            "conhecidas": {
                "v0": {"valor": 72, "unidade": "km/h"},
                "v": {"valor": 0, "unidade": "m/s"},
                "a": {"valor": -4, "unidade": "m/s2"},
            },
            "alvo": "ds",
            "unidade_alvo": "m",
        },
    },
    "mruv_aceleracao": {
        "summary": "MRUV · de 0 a 100 km/h em 10 s (qual a aceleração?)",
        "description": "Qualquer variável pode ser o alvo, inclusive a aceleração.",
        "value": {
            "movimento": "mruv",
            "conhecidas": {
                "v0": {"valor": 0, "unidade": "km/h"},
                "v": {"valor": 100, "unidade": "km/h"},
                "t": {"valor": 10, "unidade": "s"},
            },
            "alvo": "a",
        },
    },
    # ---------------- Queda livre ----------------
    "queda_livre": {
        "summary": "Queda livre · tema 3: pedra solta de 4500 cm (velocidade em km/h)",
        "description": "\"Solta\" = não informar `v0` (padrão 0). `g` também tem padrão (9,81). "
                       "Na `trajetoria`, `y` é a altura até o chão.",
        "value": {
            "movimento": "queda_livre",
            "conhecidas": {"h": {"valor": 4500, "unidade": "cm"}},
            "alvo": "v",
            "unidade_alvo": "km/h",
        },
    },
    # ---------------- Projétil ----------------
    "projetil_obliquo": {
        "summary": "Projétil · tema 1: bola chutada do chão a 20 m/s e 35°",
        "description": "Pede o alcance `A`; altura máxima `H` e tempo de voo `t_voo` "
                       "vêm juntos no `estado`. Atenção: `theta` volta em radianos no `estado`.",
        "value": {
            "movimento": "projetil",
            "conhecidas": {
                "v0": {"valor": 20, "unidade": "m/s"},
                "theta": {"valor": 35, "unidade": "grau"},
            },
            "alvo": "A",
        },
    },
    "projetil_horizontal": {
        "summary": "Projétil · lançamento horizontal de 45 m de altura que alcança 30 m",
        "description": "Horizontal = `theta: 0`. O primeiro passo é \"θ = 0 ⇒ v_y = 0\".",
        "value": {
            "movimento": "projetil",
            "conhecidas": {
                "h0": {"valor": 45, "unidade": "m"},
                "theta": {"valor": 0, "unidade": "grau"},
                "A": {"valor": 30, "unidade": "m"},
            },
            "alvo": "v0",
        },
    },
    "projetil_angulo": {
        "summary": "Projétil · caso inverso: que ângulo dá 38,3 m de alcance a 20 m/s?",
        "description": "Usa a fórmula própria do caso inverso (só vale com h0 = 0). "
                       "O passo traz a observação de que 90° − θ dá o mesmo alcance.",
        "value": {
            "movimento": "projetil",
            "conhecidas": {
                "v0": {"valor": 20, "unidade": "m/s"},
                "A": {"valor": 38.3, "unidade": "m"},
            },
            "alvo": "theta",
            "unidade_alvo": "grau",
        },
    },
    # ---------------- Erros (400) ----------------
    "erro_dados_insuficientes": {
        "summary": "Erro 400 · caso do vídeo: horizontal só com a altura, pedindo v0",
        "description": "Falta dado. `faltando` lista o que, informado a mais, resolveria "
                       "(alcance horizontal ou velocidade horizontal).",
        "value": {
            "movimento": "projetil",
            "conhecidas": {
                "h0": {"valor": 45, "unidade": "m"},
                "theta": {"valor": 0, "unidade": "grau"},
            },
            "alvo": "v0",
        },
    },
    "erro_dados_inconsistentes": {
        "summary": "Erro 400 · carro que para em 50 m precisa andar 100 m",
        "description": "A conta é impossível com esses valores.",
        "value": {
            "movimento": "mruv",
            "conhecidas": {
                "v0": {"valor": 20, "unidade": "m/s"},
                "a": {"valor": -4, "unidade": "m/s2"},
                "ds": {"valor": 100, "unidade": "m"},
            },
            "alvo": "t",
        },
    },
    "erro_entrada_invalida": {
        "summary": "Erro 400 · tempo informado em km/h",
        "description": "Unidade de outra dimensão (o mesmo vale para id de unidade inexistente, "
                       "como `graus` em vez de `grau`).",
        "value": {
            "movimento": "mru",
            "conhecidas": {
                "v": {"valor": 10, "unidade": "m/s"},
                "t": {"valor": 5, "unidade": "km/h"},
            },
            "alvo": "ds",
        },
    },
}
