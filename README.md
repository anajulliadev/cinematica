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

| Camada       | Tecnologia                                        |
| ------------ | ------------------------------------------------- |
| Backend      | Python 3.12+ · FastAPI · Pydantic                 |
| Frontend     | React · Vite · Tailwind CSS                       |
| Gráficos     | Mafs (plano cartesiano) · Recharts (s × t, v × t) |
| Fórmulas     | KaTeX                                             |
| Testes       | pytest                                            |
| Diagrama UML | pyreverse (pylint)                                |

## Estrutura

```
cinematica/
├── package.json          # scripts que sobem back + front juntos
├── backend/
│   ├── requirements.txt
│   ├── fisica/           # núcleo puro: unidades, fórmulas, movimentos, solver
│   ├── app/
│   │   ├── main.py       # API + serve o frontend compilado
│   │   └── schemas.py    # modelos Pydantic
│   └── tests/
└── frontend/
    ├── vite.config.js    # proxy /api -> localhost:8000
    └── src/
        ├── api.js
        ├── componentes/  # CampoComUnidade, CartaoResultado, ControleTempo, PassoAPasso
        ├── temas/        # Lancamentos, Frenagem, QuedaLivre
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
npm start       # FastAPI serve a API e o site em http://localhost:8000
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

Os testes conferem os três exemplos de demonstração e o caso de erro:

| Caso               | Entrada                                 | Resultado esperado                             |
| ------------------ | --------------------------------------- | ---------------------------------------------- |
| Lançamento oblíquo | 20 m/s a 35°, do chão                   | t_voo = 2,34 s · alcance = 38,3 m · H = 6,71 m |
| Frenagem           | 72 km/h, a = −4 m/s²                    | para em 5 s, após 50 m                         |
| Queda livre        | solta de 4500 cm                        | 3,03 s · 29,7 m/s (107 km/h)                   |
| Erro               | só altura → v₀ de lançamento horizontal | "falta o alcance horizontal"                   |

## API

`POST /api/calcular`: recebe o movimento, as grandezas conhecidas (valor + unidade) e a incógnita desejada. Devolve o valor, a unidade, o passo a passo e, se houver, a mensagem de erro com as variáveis que faltam. O contrato completo fica em `/docs` (OpenAPI).

## Diagrama de classes

```bash
cd backend
pyreverse -o png -p cinematica fisica
```

Gera `classes_cinematica.png` e `packages_cinematica.png` (para o PNG é preciso ter o [Graphviz](https://graphviz.org/download/) instalado; sem ele use `-o dot` ou `-o puml`).

## Arquitetura do núcleo

- **Unidade / Grandeza:** cada unidade guarda o fator para o SI; a grandeza é valor + unidade.
- **Conversor:** converte qualquer grandeza para o SI e de volta.
- **Formula** (interface) → **FormulaBase** (abstrata): parte comum; cada equação concreta só isola suas variáveis.
- **Movimento** (abstrata) → `MRU`, `MRUV`, `QuedaLivre`, `LancamentoProjetil`.
- **Solver:** enquanto houver fórmula com exatamente uma incógnita, resolve e continua até achar o alvo; registra cada passo.

## Equipe

| Nome   | GitHub |
| ------ | ------ |
| Nome 1 | @      |
| Nome 2 | @      |

## Licença

Projeto acadêmico, uso educacional.
