import { Button } from "@/components/ui/button";
import Configure from "./componentes/Configure";
import Simulacao from "./componentes/Simulacao";
import { useState } from "react";


export default function App() {
  const [dimension, setDimension] = useState(1);
  const [formData, setFormData] = useState({
    tipoMovimento: "",
    objetivo: "",
    velocidadeInicial: "",
    unidadeVelocidade: "",
    angulo: "",
    unidadeAngulo: "",
    alturaInicial: "",
    unidadeAltura: "",
    gravidade: "9.81",
    unidadeGravidade: "",
  });

  function changeDimension1(event) {
    if (dimension == 1) {
      setDimension(2);
    }
  }

  function changeDimension2(event) {
    if (dimension == 2) {
      setDimension(1);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();

    console.log(formData);
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
              onClick={() => setDimension(1)}
              className={`py-5 px-6 rounded-full ${
                dimension == 2 ? 'bg-surface' : 'bg-primary'
              }`}>
              <p className="text-base font-bold">1D</p>
            </Button>
            <Button
              onClick={() => setDimension(2)}
              className={`py-5 px-6 rounded-full ${
                dimension == 1 ? 'bg-surface' : 'bg-primary'
              }`}>
              <p className="text-base font-bold">2D</p>
            </Button>
          </div>
        </header>
        <section className="grid grid-cols-3 gap-6">
          <Configure formData={formData} setFormData={setFormData} handleSubmit={handleSubmit} />
          <div className="flex flex-col col-span-2 p-6 gap-4 bg-surface border border-border rounded-xl">
            <Simulacao />
          </div>
        </section>
        <div className="flex flex-col p-6 gap-4 bg-surface border border-border rounded-xl">
          <h3 className="text-xl font-bold text-text">Como chegamos ao resultado</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex flex-col gap-3">
              <p className="text-text text-base">1. Conversão de unidades</p>
              <p className="text-text-muted text-sm">A velocidade foi convertida para o SI.</p>
              <p className="bg-bg text-text p-3 rounded-lg" >72 km/h ÷ 3,6 = 20 m/s</p>
            </div>
            <div className="flex flex-col gap-3">
              <p className="text-text text-base">2   Fórmula aplicada</p>
              <p className="text-text-muted text-sm">Alturas inicial e final iguais, sem resistência do ar.</p>
              <p className="bg-bg text-text p-3 rounded-lg" >R = v₀² · sen(2θ) / g</p>
            </div>
            <div className="flex flex-col gap-3">
              <p className="text-text text-base">3   Substituição dos valores</p>
              <p className="text-text-muted text-sm">Com v₀ = 20 m/s, θ = 45° e g = 9,81 m/s².</p>
              <p className="bg-bg text-text p-3 rounded-lg" >R = 20² · sen(90°) / 9,81 = 40,77 m</p>
            </div>
          </div>
        </div>
      </main>

    </main>
  );
}

