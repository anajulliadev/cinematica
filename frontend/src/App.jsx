import { Button } from "@/components/ui/button";
import Configure from "./componentes/Configure";
import Simulacao from "./componentes/Simulacao";
import { useState } from "react";
import { criarFormulario } from "./config/movimentos";
import { calcular } from "./api";
import Passos from "./componentes/Passos";

export default function App() {
  const [dimension, setDimension] = useState(1);
  const [formData, setFormData] = useState(() => criarFormulario(1));

  const [respostaCalculo, setRespostaCalculo] = useState(null);
  const [erro, setErro] = useState("");
  const [calculando, setCalculando] = useState(false);

  function changeDimension(event) {
    if (dimension == event) return;
    setDimension(event);
    setFormData(criarFormulario(event));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if(calculando) return;

    setErro("");
    setRespostaCalculo(null);

    //Testando apenas Movimento Retilíneo Uniforme e Movimento Retilíneo Uniformemente Variado
    if(!["mru", "mruv"].includes(formData.tipoMovimento)) return;

    setCalculando(true);

    try {
      //Variváveis do formulário preenchida pelo usuário
      const conhecidas = {};

      for(const [id, entrada] of Object.entries(formData.conhecidas)) {
        if(id == formData.objetivo) continue;

        const text = String(entrada.valor ?? "").trim();

        if(text == "") continue;

        const valor = Number(text);

        if(!Number.isFinite(valor)) {
          throw new Error(`Informe um número válido para ${id}.`)
        }

        conhecidas[id] = {
          valor,
          unidade: entrada.unidade
        };
      }

      const payload = {
        movimento: formData.tipoMovimento,
        alvo: formData.objetivo,
        conhecidas
      };

      const dados = await calcular(payload);

      setRespostaCalculo(dados);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível calcular");
    } finally {
      setCalculando(false);
    }
  }

  return (
    <main className="flex flex-col bg-bg w-full h-screen items-center justify-start">
      <header className="w-full bg-surface h-16" />

      <main className="flex flex-col w-full max-w-400 px-14 py-8 gap-6">
        <header className="flex flex-col justify-center items-center gap-2">
          <h1 className="text-3xl font-bold text-text">Do Cálculo ao Movimento</h1>
          <p className="text-base text-text-muted">
            Informe seus dados e descubra o movimento
          </p>
          <div className="flex gap-1 bg-surface rounded-full p-1">
            <Button
              onClick={() => changeDimension(1)}
              aria-pressed={dimension === 1}
              className={`py-5 px-6 rounded-full ${
                dimension == 2 ? 'bg-surface' : 'bg-primary'
              }`}>
              <p className="text-base font-bold">1D</p>
            </Button>
            <Button
              onClick={() => changeDimension(2)}
              aria-pressed={dimension === 2}
              className={`py-5 px-6 rounded-full ${
                dimension == 1 ? 'bg-surface' : 'bg-primary'
              }`}>
              <p className="text-base font-bold">2D</p>
            </Button>
          </div>
        </header>
        <section className="grid grid-cols-3 gap-6">
          <Configure dimension={dimension} formData={formData} setFormData={setFormData} handleSubmit={handleSubmit} />
          <div className="flex flex-col col-span-2 p-6 gap-4 bg-surface border border-border rounded-xl">
            <Simulacao resposta={respostaCalculo} />
          </div>
        </section>
        <div aria-live="polite"> 
          { calculando && ( <p className="text-text-muted">/</p> )}
          { erro && ( <p role="alert" className="text-red-400"> {erro} </p> )}
      </div>
        <Passos resposta={respostaCalculo} />
      </main>

    </main>
  );
}

