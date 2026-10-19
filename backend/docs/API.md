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
3. Com `t` conhecido, ele procura de novo. Em `Δs = v₀·t + ½·a·t²`, agora só falta `Δs`, e daí sai Δs = 50 m.
4. Como `Δs` era o que foi pedido, ele para e devolve o resultado, as fórmulas usadas e os pontos do movimento.

Se em algum momento nenhuma fórmula tiver só uma incógnita, o solver para e responde com um erro dizendo o que falta.

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
| `movimento` | sim | `mru`, `mruv`, `queda_livre` ou `projetil` |
| `conhecidas` | sim | valores informados, no formato `{ id: { valor, unidade } }` |
| `alvo` | sim | id da variável a calcular |
| `unidade_alvo` | não | unidade em que o resultado deve voltar; se omitida, volta em SI |

Algumas regras não aparecem no `/docs`:

- Campo vazio não deve ser enviado. Mandar `"valor": ""` dá erro 422.
- `valor` precisa ser número. O `<input type="number">` devolve texto, então converta com `Number()`.
- Os ids de unidade são os da tabela abaixo, escritos exatamente assim (`grau`, e não `graus`; `m/s2`, e não `ms2`).
- A unidade precisa ser da mesma grandeza da variável. Um tempo em `km/h`, por exemplo, volta como erro 400.
- Valores com padrão (como g = 9,81) não precisam ser enviados.

### Variáveis de cada movimento

| `movimento` | Variáveis | Padrões |
|---|---|---|
| `mru` | `ds` deslocamento, `v` velocidade, `t` tempo | — |
| `mruv` | `ds` deslocamento, `v0` velocidade inicial, `v` velocidade final, `a` aceleração, `t` tempo | — |
| `queda_livre` | `h` altura de queda, `v0` velocidade inicial, `v` velocidade final, `g` gravidade, `t` tempo | `v0 = 0`, `g = 9,81` |
| `projetil` | `v0` velocidade inicial, `theta` ângulo, `h0` altura inicial, `g` gravidade, `A` alcance, `H` altura máxima, `t_voo` tempo de voo, `vx` velocidade horizontal, `vy` velocidade vertical inicial | `h0 = 0`, `g = 9,81` |

Qualquer variável da lista pode ir em `conhecidas` ou ser o `alvo`.

### Unidades

| Grandeza | ids | Variáveis |
|---|---|---|
| Comprimento | `m`, `cm`, `km` | `ds`, `h`, `h0`, `A`, `H` |
| Tempo | `s`, `ms`, `min`, `h` | `t`, `t_voo` |
| Velocidade | `m/s`, `km/h` | `v`, `v0`, `vx`, `vy` |
| Aceleração | `m/s2` | `a`, `g` |
| Ângulo | `grau`, `rad` | `theta` |

`h` aparece duas vezes: como variável (altura de queda) e como unidade (hora). Não há conflito, porque um vai como chave de `conhecidas` e o outro no campo `unidade`.

### Convenções

- No MRUV, aceleração negativa significa frenagem (`a: -4`).
- Na queda livre, o eixo aponta para baixo, então `h`, `v` e `g` são positivos.
- No projétil, `theta` é medido a partir da horizontal. Lançamento horizontal é `theta: 0`.

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
    "conversoes": { "m": 40.77471967380224, "cm": 4077.4719673802238, "km": 0.04077471967380224 }
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

- `resultado`: o valor pedido, na unidade de `unidade_alvo`. Em `conversoes` vem o mesmo valor nas outras unidades da grandeza, então dá para trocar a unidade exibida sem nova chamada.
- `passos`: as fórmulas usadas, na ordem em que o solver as aplicou. `latex_isolada` é a fórmula já isolada para a variável calculada (pronta para o KaTeX), `usadas` são os valores que entraram na conta e `observacao` traz um aviso quando há (por exemplo, quando uma raiz quadrada foi resolvida pelo valor positivo).
- `estado`: todas as variáveis conhecidas no fim do cálculo, sejam informadas, padrão ou calculadas. No projétil, `A`, `H` e `t_voo` vêm sempre, qualquer que seja o alvo.
- `trajetoria`: 61 pontos do movimento, de t = 0 até o fim, para o gráfico e a animação.

`passos` e `trajetoria` são coisas diferentes. `passos` mostra como se chegou ao resultado, uma fórmula por item. `trajetoria` mostra o movimento em si, um instante por item, e não depende do alvo: o mesmo lançamento gera a mesma curva, peça-se o alcance ou a altura máxima.

### Pontos da trajetória

| `movimento` | Chaves | Significado |
|---|---|---|
| `mru`, `mruv` | `t`, `s`, `v` | instante (s), distância percorrida desde o início (m), velocidade (m/s) |
| `queda_livre` | `t`, `y`, `v` | instante, altura até o chão (começa em `h` e termina em 0), velocidade |
| `projetil` | `t`, `x`, `y`, `vx`, `vy` | instante, distância horizontal, altura, componentes da velocidade |

Os pontos são igualmente espaçados no tempo (`t` do ponto i = i × tempo total / 60). Se não for possível descobrir a duração do movimento, `trajetoria` vem vazia.

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
- `entrada_invalida`: id de unidade ou de variável que não existe, ou unidade de outra grandeza. Quase sempre indica um problema no que o front está enviando.

Já o 422 é gerado automaticamente pelo FastAPI quando o JSON está fora do formato (texto no lugar de número, campo obrigatório ausente). O corpo é diferente, com um `detail` em que `loc` indica o campo com problema. Também é erro do lado de quem envia.

Exemplos reais:

Lançamento horizontal só com a altura, pedindo `v0` (o caso de erro do vídeo):
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

## 6. Os casos do vídeo

### Tema 1: Laboratório de Lançamentos

Bola chutada do chão a 20 m/s e 35°:
```json
{ "movimento": "projetil", "alvo": "A",
  "conhecidas": { "v0": { "valor": 20, "unidade": "m/s" }, "theta": { "valor": 35, "unidade": "grau" } } }
```
O alcance volta em torno de 38,3 m, e o `estado` traz também `t_voo` ≈ 2,34 s e `H` ≈ 6,71 m. Para o gráfico, use `x` e `y` de cada ponto; as setas saem de `vx` e `vy` do ponto atual. Para mudar o objetivo, basta trocar o `alvo` por `H` ou `t_voo`. No lançamento horizontal, mande `theta` igual a 0 e a altura em `h0`.

### Tema 2: Pista de Frenagem

Carro a 72 km/h que freia a −4 m/s² até parar:
```json
{ "movimento": "mruv", "alvo": "ds", "unidade_alvo": "m",
  "conhecidas": { "v0": { "valor": 72, "unidade": "km/h" }, "v": { "valor": 0, "unidade": "m/s" }, "a": { "valor": -4, "unidade": "m/s2" } } }
```
Volta `ds` = 50 m, com `t` = 5 s no `estado`. "Até parar" é o mesmo que informar `v = 0`. O gráfico s × t usa as chaves `t` e `s` da trajetória, e o v × t usa `t` e `v`.

### Tema 3: Torre de Queda Livre

Pedra solta de 4500 cm:
```json
{ "movimento": "queda_livre", "alvo": "v", "unidade_alvo": "km/h",
  "conhecidas": { "h": { "valor": 4500, "unidade": "cm" } } }
```
Volta `v` ≈ 106,97 km/h (29,71 m/s em `valor_si`), com `t` ≈ 3,03 s no `estado`. Como a pedra é solta, não é preciso mandar `v0`. Na torre, a posição da pedra é o `y` de cada ponto. Para as marcas a cada 0,5 s, dá para interpolar os pontos ou calcular `y = h − ½·g·t²` a partir do `estado`.

### Caso de erro

Lançamento horizontal, só com a altura, pedindo a velocidade inicial:
```json
{ "movimento": "projetil", "alvo": "v0",
  "conhecidas": { "h0": { "valor": 45, "unidade": "m" }, "theta": { "valor": 0, "unidade": "grau" } } }
```
A resposta é o erro 400 `dados_insuficientes` mostrado na seção 5, citando o alcance horizontal. Para esse caso aparecer na tela, o seletor de objetivo precisa ter a opção velocidade inicial (`alvo: "v0"`).

## 7. Dúvidas comuns

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
