import { Button } from "@/components/ui/button";
import Configure from "./componentes/Configure";
import Simulacao from "./componentes/Simulacao";


export default function App() {

  return (
    <main className="flex flex-col bg-bg w-full h-screen items-center justify-start">
      <header className="w-full bg-surface h-16" />

      <main className="flex flex-col w-full max-w-400 px-14 py-8 gap-7">
        <header className="flex flex-col justify-center items-center gap-2">
          <h1 className="text-3xl font-bold text-text">Do Cálculo ao Movimento</h1>
          <p className="text-base text-text-muted">
            Informe seus dados e descubra o movimento
          </p>
          <div className="flex gap-1 bg-surface rounded-full p-1">
            <Button className="py-5 px-6 rounded-full">
              <p className="text-base font-bold">1D</p>
            </Button>
            <Button disabled className="py-5 px-6 rounded-full">
              <p className="text-base font-bold">2D</p>
            </Button>
          </div>
        </header>
        <section className="grid grid-cols-3 gap-7">
          <div className="flex flex-col p-7 gap-4 bg-surface border border-border rounded-xl pb-11">
            <Configure />
          </div>
          <div className="flex flex-col col-span-2 p-7 gap-4 bg-surface border border-border rounded-xl">
            <Simulacao />
          </div>
        </section>
        <div id="social" />
      </main>

    </main>
  );
}

