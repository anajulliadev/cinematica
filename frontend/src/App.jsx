import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";

const tipo_movimento = [
  { label: "Lancamento Obliquo", value: "obliquo" },
  { label: "Lancamento Nao Obliquo", value: "nobliquo" },
  { label: "Lancamento reto", value: "reto" },
  { label: "Lancamento nao reto", value: "nreto" },
]

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
            <p className="text-xl font-bold text-text">Configure o lançamento</p>
            <div className="flex flex-col gap-2">
              <p className="text-sm text-text-muted">Tipo de movimento</p>
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-sm text-text-muted">Objetivo do cálculo</p>
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-3 gap-x-1.5 gap-y-4 justify-items-start items-center">
              <p className="text-text text-sm " >Velocidade inicial</p>
              <Input className="bg-bg border border-border text-text p-5" placeholder="Ex:72" />
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              <p className="text-text text-sm " >Ângulo de lançamento</p>
              <Input className="bg-bg border border-border text-text p-5" placeholder="Ex:72" />
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              <p className="text-text text-sm " >Altura inicial</p>
              <Input className="bg-bg border border-border text-text p-5" placeholder="Ex:72" />
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              <p className="text-text text-sm " >Gravidade</p>
              <Input className="bg-bg border border-border text-text p-5" placeholder="Ex:72" />
              <Select items={tipo_movimento}>
                <SelectTrigger className="w-full bg-bg border border-border p-5">
                  <SelectValue placeholder="Selectione um tipo" className="text-text" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tipos</SelectLabel>
                    {tipo_movimento.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <p className="text-text-muted text-sm">Preencha apenas os dados que você conhece.</p>
            <Button className="py-5 px-6 rounded-lg">
              <p className="text-base font-bold">Calcular trajetória</p>
            </Button>
          </div>
          <div className="col-span-2 p-4 bg-surface border border-border rounded-xl">
            TESTE
          </div>
        </section>
        <div id="social" />
      </main>

    </main>
  );
}

