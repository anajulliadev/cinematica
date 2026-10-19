# Calculadora de Cinemática 1D e 2D

Calculadora de cinemática com **solver automático**: você informa só o que tem (em qualquer unidade) e o programa encontra sozinho as fórmulas necessárias até chegar no valor pedido, mostrando o passo a passo. Inclui animações da trajetória e gráficos interativos.

> Trabalho da disciplina **Física Geral e Experimental**.

## Funcionalidades

- **Movimentos:** MRU, MRUV, queda livre e lançamento de projétil (horizontal e oblíquo).
- **Unidade por campo:** cada entrada tem seu seletor (m, cm, km · s, ms, min, h · m/s, km/h · m/s² · graus, rad).
- **Conversão automática:** tudo é convertido para o SI antes do cálculo e o resultado volta na unidade escolhida.
- **Solver:** encadeia as fórmulas até achar a incógnita; se faltar dado, diz exatamente o que falta.
- **Passo a passo** com fórmulas renderizadas em KaTeX.
- **Três temas visuais:**
  1. **Laboratório de Lançamentos**: plano cartesiano (estilo GeoGebra) com trajetória, vetores vₓ e v_y e controle de tempo.
  2. **Pista de Frenagem**: carro animado com gráficos s × t e v × t.
  3. **Torre de Queda Livre**: prédio com régua e marcações a cada 0,5 s.

## Tecnologias

| Camada   | Tecnologia                                        |
| -------- | ------------------------------------------------- |
| Backend  | Python 3.12+ · FastAPI · Pydantic                 |
| Frontend | React · Vite · Tailwind CSS                       |
| Gráficos | Mafs (plano cartesiano) · Recharts (s × t, v × t) |
| Fórmulas | KaTeX                                             |
| Testes   | pytest                                            |

## Estrutura

```
cinematica/
├── package.json            # scripts que sobem back + front juntos
├── backend/
│   ├── requirements.txt
│   ├── fisica/             # núcleo puro (sem FastAPI): tudo em SI
│   │   ├── unidades.py     # unidades e conversão para o SI
│   │   ├── formulas.py     # fórmulas 1D e 2D
│   │   ├── movimentos.py   # MRU, MRUV, queda livre e projétil
│   │   └── solver.py       # escolhe e encadeia as fórmulas até o alvo
│   ├── app/
│   │   ├── main.py         # POST /api/calcular, erros 400 e serve o frontend compilado
│   │   └── schemas.py      # modelos Pydantic (contrato com o React)
│   ├── docs/API.md         # guia da API para o frontend
│   └── tests/              # pytest: unidades, fórmulas, solver, projétil, trajetória, API
└── frontend/
    ├── vite.config.js      # proxy /api -> localhost:8000
    └── src/
        ├── api.js
        ├── componentes/    # CampoUnidade, CartaoResultado, ControleTempo, PassoAPasso
        ├── temas/          # Lancamentos, Frenagem, QuedaLivre
        └── App.jsx
```

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/) (só para desenvolvimento)
- Git

## Como rodar (desenvolvimento)

```bash
# 1. Clonar
git clone https://github.com/SEU_USUARIO/cinematica.git
cd cinematica

# 2. Backend
cd backend
python -m venv .venv
# Windows:      .\.venv\Scripts\Activate.ps1
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
cd ..

# 3. Frontend
npm install
npm --prefix frontend install

# 4. Subir tudo (com a .venv ativada)
npm run dev
```

- Frontend: http://localhost:5173
- API e documentação interativa: http://localhost:8000/docs

Em desenvolvimento, o Vite repassa tudo que começa com `/api` para a porta 8000, sem problemas de CORS.

## Como rodar (entrega / só com Python)

```bash
npm run build   # gera frontend/dist
npm start       # FastAPI serve a API e o site em http://localhost:8000 (com a .venv ativada)
```

Se o `frontend/dist` já estiver pronto, basta o Python:

```bash
cd backend
python -m uvicorn app.main:app --port 8000
```

## Testes

```bash
npm test
# ou: cd backend && pytest
```

Os testes conferem os três exemplos de demonstração e o caso de erro (`tests/test_exemplos.py`):

| Caso               | Entrada                                 | Resultado esperado                             |
| ------------------ | --------------------------------------- | ---------------------------------------------- |
| Lançamento oblíquo | 20 m/s a 35°, do chão                   | t_voo = 2,34 s · alcance = 38,3 m · H = 6,71 m |
| Frenagem           | 72 km/h, a = −4 m/s²                    | para em 5 s, após 50 m                         |
| Queda livre        | solta de 4500 cm                        | 3,03 s · 29,7 m/s (107 km/h)                   |
| Erro               | só altura → v₀ de lançamento horizontal | "falta o alcance horizontal"                   |

Além deles: cada isolamento de cada fórmula, conversões de unidade, o comportamento do solver, a trajetória e a API (sucesso, erros 400 e 422).

## API

O frontend usa uma única rota: **`POST /api/calcular`**. O contrato completo (com todos os modelos) fica em `/docs`.

Explicação mais detalhada, com os casos do vídeo e os erros: [`backend/docs/API.md`](backend/docs/API.md).

### Variáveis aceitas

| `movimento`   | variáveis (`id`)                                        | padrões           |
| ------------- | ------------------------------------------------------- | ----------------- |
| `mru`         | `ds`, `v`, `t`                                          | —                 |
| `mruv`        | `ds`, `v0`, `v`, `a`, `t`                               | —                 |
| `queda_livre` | `h`, `v0`, `v`, `g`, `t`                                | v0 = 0 · g = 9,81 |
| `projetil`    | `v0`, `theta`, `h0`, `g`, `A`, `H`, `t_voo`, `vx`, `vy` | h0 = 0 · g = 9,81 |

Unidades (`id`): `m` `cm` `km` · `s` `ms` `min` `h` · `m/s` `km/h` · `m/s2` · `grau` `rad`.
Lançamento horizontal = `projetil` com `theta` = 0.

### Exemplo (Pista de Frenagem)

```json
POST /api/calcular
{
  "movimento": "mruv",
  "conhecidas": {
    "v0": {"valor": 72, "unidade": "km/h"},
    "v":  {"valor": 0,  "unidade": "m/s"},
    "a":  {"valor": -4, "unidade": "m/s2"}
  },
  "alvo": "ds",
  "unidade_alvo": "m"
}
```

Resposta `200` (resumida):

```json
{
  "resultado": {
    "valor": 50.0,
    "unidade": "m",
    "valor_si": 50.0,
    "unidade_si": "m",
    "conversoes": { "m": 50.0, "cm": 5000.0, "km": 0.05 }
  },
  "passos": [
    {
      "formula": "Função horária da velocidade",
      "latex_isolada": "t = \\frac{v - v_0}{a}",
      "variavel": "t",
      "valor_si": 5.0,
      "...": "..."
    },
    {
      "formula": "Função horária da posição",
      "variavel": "ds",
      "valor_si": 50.0,
      "...": "..."
    }
  ],
  "estado": { "v0": 20.0, "v": 0.0, "a": -4.0, "t": 5.0, "ds": 50.0 },
  "trajetoria": [
    { "t": 0.0, "s": 0.0, "v": 20.0 },
    "...",
    { "t": 5.0, "s": 50.0, "v": 0.0 }
  ]
}
```

- `conversoes`: o resultado em todas as unidades da mesma dimensão (para trocar a unidade sem nova chamada).
- `estado`: tudo o que foi possível calcular, em SI.
- `trajetoria`: 61 pontos de t = 0 até o fim do movimento. Chaves: `t, s, v` (MRU/MRUV) · `t, y, v` (queda livre, y = altura até o chão) · `t, x, y, vx, vy` (projétil).

### Erros

| Status | `tipo`                 | Quando                                                      |
| ------ | ---------------------- | ----------------------------------------------------------- |
| 400    | `dados_insuficientes`  | faltam dados; `faltando` lista o que destravaria o cálculo  |
| 400    | `dados_inconsistentes` | a conta é impossível (ex.: o carro para antes da distância) |
| 400    | `entrada_invalida`     | unidade inexistente, dimensão errada, variável inexistente  |
| 422    | —                      | JSON fora do formato (validação automática do Pydantic)     |

```json
{
  "tipo": "dados_insuficientes",
  "mensagem": "Não foi possível calcular velocidade inicial (v0). Informe também: alcance horizontal (A) ou velocidade horizontal (vx).",
  "faltando": [
    { "id": "A", "nome": "alcance horizontal" },
    { "id": "vx", "nome": "velocidade horizontal" }
  ]
}
```

## Licença

Projeto acadêmico, uso educacional.
