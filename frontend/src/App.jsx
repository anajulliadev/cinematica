import { useState } from "react";
import heroImg from "./assets/hero.png";
import viteLogo from "./assets/vite.svg";

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <main className="flex flex-col bg-bg w-full h-screen items-center justify-start">
      <header className="w-full bg-surface h-16" />

      <main className="flex flex-col w-full max-w-400 px-14 py-8 gap-7">
        <header className="flex flex-col justify-center items-center gap-2">
          <h1 className="text-3xl font-bold text-text">Do Cálculo ao Movimento</h1>
          <p className="text-base text-text-muted">
            Informe seus dados e descubra o movimento
          </p>
        </header>
        <div id="social" />
      </main>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </main>
  );
}

