import Plot from "react-plotly.js";

export default function Grafico() {
  const x = Array.from({ length: 101 }, (_, i) => -5 + i * 0.1);
  const y = x.map((value) => value ** 2);

  return (
    <Plot
      data={[
        {
          x,
          y,
          type: "scatter",
          mode: "lines",
          line: {
            color: "#38bdf8",
            width: 3
          },
          name: "y = x²",
        }
      ]}
      layout={{
        width: 900,
        height: 350,
        paper_bgcolor: "#13181E",
        plot_bgcolor: "#13181E",
        font: { color: "#EBEFF4" },

        xaxis: {
          title: {
            text: "x (m)",
            font: {
              color: "#989FA8",
              size: 14,
              standoff: 10,
            },
          },
          zeroline: true,
          range: [-10, 10],
          zerolinecolor: "#989FA8",
          zerolinewidth: 2,
          gridcolor: "#272C32",
          linecolor: "#272C32",
        },

        yaxis: {
          title: {
            text: "y (m)",
            font: {
              color: "#989FA8",
              size: 14,
              standoff: 10,
            },
          },
          zeroline: true,
          range: [-10, 10],
          zerolinecolor: "#989FA8",
          zerolinewidth: 2,
          gridcolor: "#272C32",
          linecolor: "#272C32",
        },

        showlegend: false,
        margin: { l: 45, r: 20, t: 20, b: 40 },
      }}
      config={{ responsive: true }}
    />
  )
}
