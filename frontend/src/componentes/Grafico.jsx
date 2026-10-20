import Plot from "react-plotly.js";

const EIXOS = {
  mru: {
    x: "t",
    y: "s",
    tituloX: "Tempo (s)",
    tituloY: "Deslocamento (m)",
  },
  mruv: {
    x: "t",
    y: "s",
    tituloX: "Tempo (s)",
    tituloY: "Deslocamento (m)",
  },
  queda_livre: {
    x: "t",
    y: "y",
    tituloX: "Tempo (s)",
    tituloY: "Altura (m)",
  },
  projetil: {
    x: "x",
    y: "y",
    tituloX: "Posição horizontal (m)",
    tituloY: "Altura (m)",
  },
  lancamento_vertical: {
    x: "t",
    y: "y",
    tituloX: "Tempo (s)",
    tituloY: "Deslocamento vertical (m)",
  },  
};


export default function Grafico({movimento, trajetoria = []}) {
  const eixos = EIXOS[movimento];

  if (!eixos || trajetoria.length === 0) {
    return (
      <p className="text-text-muted">
        Não há dados suficientes para representar graficamente o cálculo.
      </p>
    );
  }

  console.log("Primeiros pontos:", trajetoria.slice(0, 3));

  const x = trajetoria.map((ponto) => ponto[eixos.x]);
  const y = trajetoria.map((ponto) => ponto[eixos.y]);

  return (
    <div className="w-full min-w-0 py-4">
      <Plot
        data={[
          {
            x,
            y,
            type: "scatter",
            mode: "lines",
            line: {
              color: "#38bdf8",
              width: 3,
            },
            hovertemplate:
              "%{x:.2f}, %{y:.2f}<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height: 350,
          paper_bgcolor: "#13181E",
          plot_bgcolor: "#13181E",
          font: {
            color: "#EBEFF4",
          },
          xaxis: {
            title: {
              text: eixos.tituloX,
            },
            autorange: true,
            gridcolor: "#272C32",
            zerolinecolor: "#989FA8",
          },
          yaxis: {
            title: {
              text: eixos.tituloY,
            },
            autorange: true,
            gridcolor: "#272C32",
            zerolinecolor: "#989FA8",
          },
          showlegend: false,
          margin: {
            l: 65,
            r: 20,
            t: 20,
            b: 60,
          },
        }}
        config={{
          responsive: true,
          displaylogo: false,
        }}
        useResizeHandler
        style={{
          width: "100%",
          height: "350px",
        }}
      />
    </div>
  );
}