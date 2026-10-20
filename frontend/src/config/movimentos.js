const campo = (id, label, grandeza) => ({
  id,
  label,
  grandeza,
});

export const UNIDADES = {
  comprimento: ["m", "cm", "km"],
  velocidade: ["m/s", "km/h"],
  tempo: ["s", "ms", "min", "h"],
  aceleracao: ["m/s2"],
  angulo: ["grau", "rad"],
};

export const CAMPOS = {
  dy: campo("dy", "Deslocamento vertical", "comprimento"),
  ds: campo("ds", "Deslocamento", "comprimento"),
  s0: campo("s0", "Posição inicial", "comprimento"),
  s: campo("s", "Posição final", "comprimento"),

  v0: campo("v0", "Velocidade inicial", "velocidade"),
  v: campo("v", "Velocidade final", "velocidade"),

  a: campo("a", "Aceleração", "aceleracao"),
  t: campo("t", "Tempo", "tempo"),

  h: campo("h", "Altura de queda", "comprimento"),
  h0: campo("h0", "Altura inicial", "comprimento"),
  g: campo("g", "Gravidade", "aceleracao"),

  theta: campo("theta", "Ângulo de lançamento", "angulo"),
  vx: campo("vx", "Velocidade horizontal inicial", "velocidade"),
  vy: campo("vy", "Velocidade vertical inicial", "velocidade"),

  A: campo("A", "Alcance horizontal", "comprimento"),
  H: campo("H", "Altura máxima", "comprimento"),
  t_voo: campo("t_voo", "Tempo de voo", "tempo"),

  x: campo("x", "Posição horizontal no instante", "comprimento"),
  y: campo("y", "Posição vertical no instante", "comprimento"),

  velocidade: campo(
    "velocidade",
    "Módulo da velocidade no instante",
    "velocidade"
  ),
};

export const MOVIMENTOS = [
  {
    value: "mru",
    label: "Movimento uniforme",
    dimensao: 1,
    campos: ["ds", "v", "t"],
    objetivos: ["ds", "v", "t"],
  },
  {
    value: "mruv",
    label: "Movimento uniformemente variado",
    dimensao: 1,
    campos: ["ds", "v0", "v", "a", "t"],
    objetivos: ["ds", "v0", "v", "a", "t"],
  },
  {
    value: "posicoes",
    label: "Posições e deslocamento",
    dimensao: 1,
    campos: ["s0", "s", "ds"],
    objetivos: ["s0", "s", "ds"],
  },
  {
    value: "queda_livre",
    label: "Queda livre",
    dimensao: 1,
    campos: ["h", "v0", "v", "g", "t"],
    objetivos: ["h", "v0", "v", "g", "t"],
  },
  {
    value: "vertical",
    label: "Lançamento vertical",
    dimensao: 1,
    campos: ["dy", "v0", "v", "g", "t"],
    objetivos: ["dy", "v0", "v", "t"],
  },
  {
    value: "horizontal",
    label: "Lançamento horizontal",
    dimensao: 2,
    campos: ["v0", "h0", "g", "t", "A", "t_voo"],
    objetivos: [
      "A",
      "t_voo",
      "h0",
      "v0",
      "x",
      "y",
      "velocidade",
    ],
  },
  {
    value: "obliquo",
    label: "Lançamento oblíquo",
    dimensao: 2,
    campos: [
      "v0",
      "theta",
      "vx",
      "vy",
      "h0",
      "g",
      "t",
      "A",
      "H",
      "t_voo",
    ],
    objetivos: [
      "A",
      "H",
      "t_voo",
      "v0",
      "theta",
      "vx",
      "vy",
      "x",
      "y",
      "velocidade",
    ],
  },
];

export function criarFormulario(dimensao = 1) {
  const movimento = MOVIMENTOS.find(
    (item) => item.dimensao === dimensao
  );

  return {
    tipoMovimento: movimento.value,
    objetivo: movimento.objetivos[0],
    conhecidas: {},
  };
}