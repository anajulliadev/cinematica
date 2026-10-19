# API da calculadora

Este documento explica como o frontend deve conversar com o backend: o que mandar, o que volta e o que cada campo da resposta significa. Os exemplos de JSON foram tirados de chamadas reais à API.

O `/docs` (http://localhost:8000/docs) continua sendo a referência do formato de cada campo e tem os mesmos casos de uso prontos para testar.

## 1. Rodando localmente

Na raiz do projeto, com a `.venv` do backend ativada:

```powershell
npm run dev
```

Isso sobe o Vite em http://localhost:5173 e a API em http://localhost:8000.

No React, chame a API pelo caminho relativo `/api/calcular`, sem `http://localhost:8000`. Em desenvolvimento, o proxy do `vite.config.js` repassa para a porta 8000; na entrega, o FastAPI serve o site e a API no mesmo endereço. O mesmo código funciona nos dois casos.

## 2. Como o backend resolve um problema

Existe uma rota só, `POST /api/calcular`. O front manda o que o usuário sabe e o que ele quer descobrir; o backend escolhe as fórmulas sozinho.

Pegando a frenagem do vídeo como exemplo (carro a 72 km/h, freando a −4 m/s² até parar, quanto ele anda):

1. As entradas são convertidas para o SI: 72 km/h vira 20 m/s.
2. O solver procura uma fórmula em que falte só uma variável. Em `v = v₀ + a·t`, só falta `t`, e daí sai t = 5 s.
3. Com `t` conhecido, ele procura de novo. Em `Δs = (v₀ + v)/2 · t`, agora só falta `Δs`, e daí sai Δs = 50 m.
4. Como `Δs` era o que foi pedido, ele para e devolve o resultado, as fórmulas usadas e os pontos do movimento.

Se em algum momento nenhuma fórmula tiver só uma incógnita, o solver para e responde com um erro dizendo o que falta. No passo a passo devolvido ficam só as fórmulas de que o resultado depende; contas feitas no caminho que não entram no resultado são descartadas.

Por isso, o front não precisa saber qual fórmula usar, nem ter um formulário diferente para cada pergunta: basta mandar o que foi preenchido e o `alvo`.

## 3. Requisição

```json
{
  "movimento": "projetil",
  "conhecidas": {
    "v0":    { "valor": 20, "unidade": "m/s" },
    "theta": { "valor": 45, "unidade": "grau" }
  },
  "alvo": "A",
  "unidade_alvo": "m"
}
```

| Campo | Obrigatório | Descrição |
|---|---|---|
| `movimento` | sim | `mru`, `mruv`, `queda_livre`, `lancamento_vertical` ou `projetil` |
| `conhecidas` | sim | valores informados, no formato `{ id: { valor, unidade } }` |
| `alvo` | sim | id da variável a calcular |
| `unidade_alvo` | não | unidade em que o resultado deve voltar; se omitida, volta em SI |

Algumas regras não aparecem no `/docs`:

- Campo vazio não deve ser enviado. Mandar `"valor": ""` dá erro 422.
- `valor` precisa ser número. O `<input type="number">` devolve texto, então converta com `Number()`.
- Os ids de unidade são os da tabela abaixo, escritos exatamente assim (`grau`, e não `graus`; `m/s2`, e não `ms2`).
- A unidade precisa ser da mesma grandeza da variável. Um tempo em `km/h`, por exemplo, volta como erro 400.
- Valores com padrão (como g = 9,81) não precisam ser enviados. Quando enviada, a gravidade precisa ser maior que zero.

### Variáveis de cada movimento

| `movimento` | Variáveis | Padrões |
|---|---|---|
| `mru` | `ds` deslocamento, `v` velocidade, `t` tempo | — |
| `mruv` | `ds` deslocamento, `v0` velocidade inicial, `v` velocidade final, `a` aceleração, `t` tempo | — |
| `queda_livre` | `h` altura de queda, `v0` velocidade inicial, `v` velocidade final, `g` gravidade, `t` tempo | `v0 = 0`, `g = 9,81` |
| `lancamento_vertical` | `v0` velocidade inicial, `dy` altura acima do lançamento, `g` gravidade, `t` tempo, `v` velocidade no instante `t` | `g = 9,81` |
| `projetil` | `v0` velocidade inicial, `theta` ângulo, `h0` altura inicial, `g` gravidade, `A` alcance, `H` altura máxima, `t_voo` tempo de voo, `vx` velocidade horizontal, `vy` velocidade vertical inicial, `t` instante de chegada, `y` altura no instante `t`, `vy_f` velocidade vertical na chegada, `v_f` rapidez na chegada | `h0 = 0`, `g = 9,81` |

Qualquer variável da lista pode ir em `conhecidas` ou ser o `alvo`.

No projétil, "chegada" depende do que foi informado: com `t`, é o instante `t` (por exemplo, a flecha que chega ao topo de um penhasco); sem `t`, é o retorno ao chão, no instante `t_voo`. `vy_f` e `v_f` seguem a mesma regra.

### Unidades

| Grandeza | ids | Variáveis |
|---|---|---|
| Comprimento | `m`, `cm`, `km` | `ds`, `h`, `dy`, `h0`, `A`, `H`, `y` |
| Tempo | `s`, `ms`, `min`, `h` | `t`, `t_voo` |
| Velocidade | `m/s`, `km/h` | `v`, `v0`, `vx`, `vy`, `vy_f`, `v_f` |
| Aceleração | `m/s2` | `a`, `g` |
| Ângulo | `grau`, `rad` | `theta` |

`h` aparece duas vezes: como variável (altura de queda) e como unidade (hora). Não há conflito, porque um vai como chave de `conhecidas` e o outro no campo `unidade`.

### Convenções

- No MRUV, aceleração negativa significa frenagem (`a: -4`).
- Na queda livre, o eixo aponta para baixo, então `h`, `v` e `g` são positivos.
- No lançamento vertical e no projétil, o eixo aponta para cima e a aceleração é −g. A gravidade é sempre enviada como valor positivo.
- No lançamento vertical, `dy` é a altura em relação ao ponto de lançamento, não ao chão.
- No projétil, `theta` é medido a partir da horizontal. Lançamento horizontal é `theta: 0`. A velocidade pode ser informada como módulo + ângulo (`v0` e `theta`) ou por componentes (`vx` e `vy`).

## 4. Resposta (200)

Projétil a 20 m/s e 45°, pedindo o alcance (a trajetória foi encurtada):

```json
{
  "movimento": "projetil",
  "alvo": "A",
  "resultado": {
    "valor": 40.77471967380224,
    "unidade": "m",
    "valor_si": 40.77471967380224,
    "unidade_si": "m",
    "conversoes": { "m": 40.77471967380224, "cm": 4077.4719673802238, "km": 0.04077471967380224 },
    "solucoes": []
  },
  "passos": [
    { "formula": "Componente horizontal da velocidade", "latex": "v_x = v_0 \\cdot \\cos \\theta",
      "latex_isolada": "v_x = v_0 \\cdot \\cos \\theta", "variavel": "vx", "valor_si": 14.142135623730951,
      "unidade_si": "m/s", "usadas": { "v0": 20.0, "theta": 0.7853981633974483 }, "observacao": null },
    { "formula": "Componente vertical da velocidade", "variavel": "vy", "valor_si": 14.142135623730951, "...": "..." },
    { "formula": "Tempo de voo", "variavel": "t_voo", "valor_si": 2.8832080782326095, "...": "..." },
    { "formula": "Alcance horizontal", "latex_isolada": "A = v_x \\cdot t_{voo}",
      "variavel": "A", "valor_si": 40.77471967380224, "unidade_si": "m", "...": "..." }
  ],
  "estado": {
    "h0": 0.0, "g": 9.81, "v0": 20.0, "theta": 0.7853981633974483,
    "vx": 14.142135623730951, "vy": 14.142135623730951,
    "t_voo": 2.8832080782326095, "A": 40.77471967380224, "H": 10.193679918450561
  },
  "trajetoria": [
    { "t": 0.0,   "x": 0.0,   "y": 0.0,   "vx": 14.14, "vy": 14.14 },
    "...",
    { "t": 1.442, "x": 20.39, "y": 10.19, "vx": 14.14, "vy": 0.0 },
    { "t": 2.883, "x": 40.77, "y": 0.0,   "vx": 14.14, "vy": -14.14 }
  ]
}
```

O que cada campo traz:

- `resultado`: o valor pedido, na unidade de `unidade_alvo`. Em `conversoes` vem o mesmo valor nas outras unidades da grandeza, então dá para trocar a unidade exibida sem nova chamada. Quando há mais de uma resposta válida, todas vêm em `solucoes`, cada uma com um `rotulo` (veja a questão 05 na seção 7); no caso comum, `solucoes` vem vazia.
- `passos`: as fórmulas usadas, na ordem em que o solver as aplicou. `latex_isolada` é a fórmula já isolada para a variável calculada (pronta para o KaTeX), `usadas` são os valores que entraram na conta e `observacao` traz um aviso quando há (por exemplo, quando uma raiz quadrada foi resolvida pelo valor positivo).
- `estado`: todas as variáveis conhecidas no fim do cálculo, sejam informadas, padrão ou calculadas. No projétil, `A`, `H` e `t_voo` vêm junto sempre que os dados permitem, qualquer que seja o alvo.
- `trajetoria`: 61 pontos do movimento, de t = 0 até o fim, para o gráfico e a animação.

`passos` e `trajetoria` são coisas diferentes. `passos` mostra como se chegou ao resultado, uma fórmula por item. `trajetoria` mostra o movimento em si, um instante por item, e não depende do alvo: o mesmo lançamento gera a mesma curva, peça-se o alcance ou a altura máxima.

### Pontos da trajetória

| `movimento` | Chaves | Significado |
|---|---|---|
| `mru`, `mruv` | `t`, `s`, `v` | instante (s), distância percorrida desde o início (m), velocidade (m/s) |
| `queda_livre` | `t`, `y`, `v` | instante, altura até o chão (começa em `h` e termina em 0), velocidade |
| `lancamento_vertical` | `t`, `y`, `v` | instante, altura acima do lançamento, velocidade (positiva subindo) |
| `projetil` | `t`, `x`, `y`, `vx`, `vy` | instante, distância horizontal, altura, componentes da velocidade |

Os pontos são igualmente espaçados no tempo (`t` do ponto i = i × tempo total / 60). Se não for possível descobrir a duração do movimento, `trajetoria` vem vazia.

O fim da trajetória: no lançamento vertical, é a volta à altura do lançamento; no projétil, é o instante `t` quando ele é informado e, sem ele, o chão.

### Detalhes que costumam pegar

- Fora de `resultado`, tudo está em SI: `estado`, `trajetoria`, `passos[].valor_si` e `passos[].usadas`.
- Ângulos voltam em radianos. Quem digitou 45° recebe `theta: 0.785...` no `estado`; para exibir, converta com `rad * 180 / Math.PI`.
- Os números não vêm arredondados. O arredondamento para exibição fica com a tela.
- Valores que deveriam ser zero às vezes chegam como `3.55e-15`, por causa da aritmética de ponto flutuante. Arredondando para duas casas, isso some.
- Acesse o `estado` pelo nome da chave (`estado.A`); a ordem das chaves não é garantida.

## 5. Erros

Erros de física voltam com status 400 e um corpo neste formato:

```json
{ "tipo": "...", "mensagem": "...", "faltando": [] }
```

A `mensagem` já está pronta para ser mostrada ao usuário. O `tipo` pode ser:

- `dados_insuficientes`: faltam dados para chegar ao alvo. Neste caso, `faltando` lista as variáveis que, informadas a mais (basta uma delas), resolveriam o cálculo, e dá para usar esses ids para destacar os campos. Se `faltando` vier vazio, faltam dois dados ou mais.
- `dados_inconsistentes`: a conta não tem solução com os valores informados.
- `entrada_invalida`: id de unidade ou de variável que não existe, unidade de outra grandeza ou gravidade menor ou igual a zero. Quase sempre indica um problema no que o front está enviando.

Já o 422 é gerado automaticamente pelo FastAPI quando o JSON está fora do formato (texto no lugar de número, campo obrigatório ausente). O corpo é diferente, com um `detail` em que `loc` indica o campo com problema. Também é erro do lado de quem envia.

Exemplos reais:

Lançamento horizontal só com a altura, pedindo `v0`:
```json
{
  "tipo": "dados_insuficientes",
  "mensagem": "Não foi possível calcular velocidade inicial (v0). Informe também: alcance horizontal (A) ou velocidade horizontal (vx).",
  "faltando": [
    { "id": "A",  "nome": "alcance horizontal" },
    { "id": "vx", "nome": "velocidade horizontal" }
  ]
}
```

Carro que para em 50 m e precisaria andar 100 m:
```json
{ "tipo": "dados_inconsistentes", "mensagem": "Função horária da posição: o móvel nunca atinge esse deslocamento", "faltando": [] }
```

Unidade `graus` no lugar de `grau`:
```json
{ "tipo": "entrada_invalida", "mensagem": "unidade desconhecida: 'graus' (aceitas: m, cm, km, s, ms, min, h, m/s, km/h, m/s2, grau, rad)", "faltando": [] }
```

`"valor": ""` (422):
```json
{ "detail": [ { "type": "float_parsing", "loc": ["body", "conhecidas", "v0", "valor"],
                "msg": "Input should be a valid number, unable to parse string as a number", "input": "" } ] }
```

## 6. Lançamentos 2D (horizontal e oblíquo)

Os dois usam `movimento: "projetil"`. O eixo y aponta para cima, a origem fica no chão abaixo do ponto de lançamento e a gravidade age só na vertical (aₓ = 0, aᵧ = −g).

### Como informar a velocidade inicial

| Forma | O que mandar | Quando usar |
|---|---|---|
| Módulo + ângulo | `v0` e `theta` | o enunciado dá a velocidade e o ângulo (flecha a 30 m/s e 60°) |
| Componentes | `vx` e `vy` | o enunciado dá as componentes (bola com 16 m/s na horizontal e 12 m/s na vertical) |
| Horizontal | `theta` = 0 | lançamento horizontal; o backend deduz `vy` = 0 e mostra isso como primeiro passo |

Não é preciso converter uma forma na outra antes de chamar a API. Com módulo + ângulo, o backend calcula `vx` e `vy`; com componentes, usa os valores direto.

### Os dois cenários de chegada

O que acontece no fim do movimento depende de o instante `t` ter sido informado:

- **Sem `t`: retorno ao chão.** A chegada é no instante `t_voo`, quando o projétil volta a y = 0. É o caso da bola chutada do chão (questão 07) e da bola lançada do prédio (questão 06). A `trajetoria` termina no chão.
- **Com `t`: chegada no instante dado.** A chegada é no instante `t`, numa altura que pode ser diferente da inicial. É o caso da flecha que chega ao topo do penhasco após 4 s (questão 08). A `trajetoria` termina nesse instante, e `y` é a altura nesse ponto.

`vy_f` (componente vertical na chegada) e `v_f` (rapidez na chegada) seguem o mesmo cenário: no chão, sem `t`; no instante `t`, com ele. Já `t_voo` e `A` no `estado` sempre se referem ao retorno ao chão, mesmo quando `t` é informado. Na questão 08 eles valem 5,35 s e 80,31 m, que é onde a flecha cairia se não houvesse o penhasco. Para a tela da flecha, use `y`, `vy_f` e `v_f`.

### O que cada objetivo precisa

Lançamento horizontal (sempre com `theta` = 0):

| Objetivo | `alvo` | Precisa de | Fórmula |
|---|---|---|---|
| Tempo de queda | `t_voo` | `h0` | t = √(2h₀/g) |
| Velocidade horizontal inicial | `vx` | `h0`, `A` | vₓ = A / t |
| Velocidade vertical no impacto | `vy_f` | `h0` | vᵧ = −g·t |
| Rapidez de impacto | `v_f` | `h0`, `A` | \|v\| = √(vₓ² + vᵧ²) |

Lançamento oblíquo:

| Objetivo | `alvo` | Precisa de | Fórmula |
|---|---|---|---|
| Tempo de voo | `t_voo` | `vy` ou (`v0`, `theta`); `h0` opcional | t_voo = (vᵧ + √(vᵧ² + 2g·h₀)) / g, que do chão ao chão vira 2vᵧ/g |
| Altura máxima | `H` | `vy` ou (`v0`, `theta`); `h0` opcional | H = h₀ + vᵧ²/(2g) |
| Rapidez de impacto | `v_f` | (`vx`, `vy`) ou (`v0`, `theta`); `t` opcional | \|v\| = √(vₓ² + (vᵧ − g·t)²) |
| Altura em determinado instante | `y` | `t` e (`vy` ou `v0`, `theta`); `h0` | y = h₀ + vᵧ·t − ½·g·t² |

`g` é opcional em todos (padrão 9,81). O tempo de voo e a altura máxima só dependem da componente vertical, então `vx` não é obrigatório para eles. A altura máxima é medida a partir do chão; na questão 08, o ganho acima do lançamento é `H − h0` = 34,40 m.

### Exemplo completo: a flecha (questão 08)

```json
POST /api/calcular
{
  "movimento": "projetil",
  "conhecidas": {
    "v0":    { "valor": 30,  "unidade": "m/s" },
    "theta": { "valor": 60,  "unidade": "grau" },
    "h0":    { "valor": 1.5, "unidade": "m" },
    "t":     { "valor": 4,   "unidade": "s" }
  },
  "alvo": "y"
}
```

Resposta (resumida):

```json
{
  "resultado": { "valor": 26.943048454132622, "unidade": "m", "...": "..." },
  "passos": [
    { "formula": "Componente vertical da velocidade", "latex_isolada": "v_y = v_0 \cdot \sin \theta",
      "variavel": "vy", "valor_si": 25.980762113533157, "usadas": { "v0": 30.0, "theta": 1.0471975511965976 } },
    { "formula": "Altura no instante", "latex_isolada": "y = h_0 + v_y \cdot t - \frac{1}{2} g \cdot t^2",
      "variavel": "y", "valor_si": 26.943048454132622, "usadas": { "g": 9.81, "h0": 1.5, "t": 4.0, "vy": 25.980762113533157 } }
  ],
  "estado": {
    "h0": 1.5, "g": 9.81, "v0": 30.0, "theta": 1.0471975511965976, "t": 4.0,
    "vx": 15.000000000000004, "vy": 25.980762113533157,
    "t_voo": 5.353910531784178, "A": 80.30865797676269, "H": 35.90366972477064,
    "y": 26.943048454132622, "vy_f": -13.259237886466845, "v_f": 20.020174557928257
  },
  "trajetoria": [
    { "t": 0.0, "x": 0.0, "y": 1.5, "...": "..." },
    "...",
    { "t": 4.0, "x": 60.000000000000014, "y": 26.943048454132622, "vx": 15.000000000000004, "vy": -13.259237886466845 }
  ]
}
```

Os três itens da questão saem dessa mesma resposta: a altura do penhasco é o `resultado` (26,94 m), e a altura máxima e a rapidez de impacto estão no `estado` (`H` = 35,90 m e `v_f` = 20,02 m/s). Pedindo `alvo: "H"` ou `alvo: "v_f"` com os mesmos dados, o valor muda de lugar e o passo a passo passa a mostrar as fórmulas daquele objetivo.

Sem o `t`, a altura no instante não tem como ser calculada:

```json
{ "tipo": "dados_insuficientes",
  "mensagem": "Não foi possível calcular altura no instante (y). Informe também: instante de chegada (t).",
  "faltando": [ { "id": "t", "nome": "instante de chegada" } ] }
```

Com os mesmos dados e sem `t`, `alvo: "v_f"` não dá erro: devolve a rapidez no retorno ao chão (30,49 m/s), que é o outro cenário de chegada.

### Sinais

- `vy` positivo é para cima. Na questão 07, `vy` = 12 m/s.
- `vy_f` negativo significa que o projétil está descendo na chegada (−12 m/s na questão 07, −34,31 m/s no prédio da questão 06).
- `v_f` é a rapidez, sempre positiva.
- Na `trajetoria`, `vy` de cada ponto troca de sinal no ponto mais alto.

## 7. Questões do MVP

Cada questão do material do professor vira uma requisição. Os dois selects da tela correspondem a `movimento` e `alvo`:

| Aba | Tipo de movimento | `movimento` |
|---|---|---|
| 1D | Movimento uniforme | `mru` |
| 1D | Uniformemente variado | `mruv` |
| 1D | Queda livre | `queda_livre` |
| 1D | Lançamento vertical | `lancamento_vertical` |
| 2D | Lançamento horizontal | `projetil`, com `theta` = 0 |
| 2D | Lançamento oblíquo | `projetil` |

| Objetivo do cálculo | `alvo` |
|---|---|
| Deslocamento | `ds` |
| Aceleração | `a` |
| Tempo de queda (1D) | `t` |
| Tempo para atingir uma altura | `t` |
| Tempo de queda (2D) / Tempo de voo | `t_voo` |
| Velocidade horizontal inicial | `vx` |
| Velocidade vertical no impacto | `vy_f` |
| Rapidez de impacto | `v_f` |
| Altura máxima | `H` |
| Altura em determinado instante | `y` |

As oito questões, com o que vai em `conhecidas` e o que volta (todas verificadas pelos testes em `backend/tests/test_mvp.py`):

| Questão | `movimento` | `conhecidas` | `alvo` → resultado |
|---|---|---|---|
| 01 Motorista | `mru` | `v` 72 km/h, `t` 3 s | `ds` → 60 m |
| 02 Leopardo | `mruv` | `v0` 6,20 m/s, `v` 23,1 m/s, `t` 3,3 s | `ds` → 48,345 m |
| 03 Carro de corrida | `mruv` | `v0` 18,5 m/s, `v` 46,1 m/s, `t` 2,47 s | `a` → 11,174089 m/s²; `ds` → 79,781 m |
| 04 Pena na Lua | `queda_livre` | `h` 1,40 m, `g` 1,67 m/s² | `t` → 1,294854 s |
| 05 Lápis | `lancamento_vertical` | `v0` 18,3 m/s, `dy` 12,2 m | `t` → 0,869140 s (subida) e 2,861747 s (descida) |
| 06 Prédio de 60 m | `projetil` | `h0` 60 m, `theta` 0°, `A` 100 m | `t_voo` → 3,497487 s; `vx` → 28,591957 m/s; `vy_f` → −34,310348 m/s; `v_f` → 44,662064 m/s |
| 07 Componentes 16 e 12 | `projetil` | `vx` 16 m/s, `vy` 12 m/s | `t_voo` → 2,446483 s; `H` → 7,339450 m; `v_f` → 20 m/s |
| 08 Flecha no penhasco | `projetil` | `v0` 30 m/s, `theta` 60°, `h0` 1,5 m, `t` 4 s | `y` → 26,943048 m; `H` → 35,903670 m; `v_f` → 20,020175 m/s |

Os mesmos dados servem para todos os objetivos de uma questão: basta trocar o `alvo`. Campos que o objetivo não usa podem ir preenchidos sem problema (o alcance da questão 06 não atrapalha o tempo de queda), e campos vazios não devem ser enviados. Os valores FIXO das telas (aceleração zero no MU, `v0` = 0 na queda livre, `vy` = 0 no lançamento horizontal) não precisam ir na requisição.

### A resposta com duas soluções (questão 05)

```json
POST /api/calcular
{ "movimento": "lancamento_vertical", "alvo": "t",
  "conhecidas": { "v0": { "valor": 18.3, "unidade": "m/s" }, "dy": { "valor": 12.2, "unidade": "m" } } }
```

O `resultado` volta assim:

```json
{
  "valor": 0.8691396199753026,
  "unidade": "s",
  "valor_si": 0.8691396199753026,
  "unidade_si": "s",
  "conversoes": { "s": 0.8691396199753026, "ms": 869.1396199753026, "min": 0.01448566033292171, "h": 0.00024142767221536186 },
  "solucoes": [
    { "rotulo": "Subida",  "valor": 0.8691396199753026, "valor_si": 0.8691396199753026 },
    { "rotulo": "Descida", "valor": 2.8617472301776026, "valor_si": 2.8617472301776026 }
  ]
}
```

`valor` é sempre a primeira solução; para mostrar as duas, use `solucoes`. Se a altura pedida for maior que o máximo do lançamento (por exemplo, `dy` = 20 m nessa questão), volta o erro `dados_inconsistentes` com a mensagem "essa altura não é atingida (o máximo é 17,07 m acima do lançamento)".

### O que cada questão testa

- 01: a conversão de 72 km/h para 20 m/s.
- 02: o deslocamento sai sem a aceleração.
- 03: os mesmos dados respondem dois objetivos; sem o tempo, o erro é `dados_insuficientes`.
- 04: a gravidade é editável; g = 0 ou negativa volta `entrada_invalida`.
- 05: as duas raízes, com os rótulos subida e descida.
- 06: o tempo de queda funciona sem o alcance; a velocidade horizontal e a rapidez precisam dele.
- 07: entrada por componentes; sem `vx`, ainda saem o tempo de voo e a altura máxima, mas não a rapidez.
- 08: a chegada numa altura diferente da inicial; sem `t`, a altura máxima continua calculável e a altura no instante não.

## 8. Dúvidas comuns

**Preciso de um formulário diferente para cada objetivo?**
Não. O formulário é o mesmo; só muda o `alvo`.

**E se o usuário preencher mais dados do que o necessário?**
O backend usa os que precisar. Ele não confere se os dados extras são coerentes entre si.

**O usuário pode informar o próprio alvo como dado?**
Pode. O resultado é o próprio valor informado e `passos` vem vazio.

**Por que a resposta tem `valor` e `valor_si`?**
`valor` está na unidade pedida, para exibição. `valor_si` está em SI, como o `estado` e a `trajetoria`.

**Como mostrar a conversão de unidades no passo a passo?**
Esse passo não vem da API, mas dá para montar comparando o que o usuário digitou (72 km/h) com o valor correspondente no `estado` (`v0` = 20 m/s).

**Posso chamar a API a cada tecla digitada?**
A resposta é rápida o bastante, mas o mais comum é chamar no botão "Calcular", para não mostrar erro enquanto o usuário ainda digita.

**Onde está o formato exato de cada campo?**
No `/docs` (seção Schemas, no fim da página) ou em `backend/app/schemas.py`.
