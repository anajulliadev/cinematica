import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";

const tipo_movimento = [
  { label: "Lançamento Oblíquo", value: "obliquo" },
  { label: "Lançamento Horizontal", value: "horizontal" },
]

const objetivo = [
  { label: "Alcance horizontal", value: "alc_horizontal" },
  { label: "Altura Máxima", value: "alt_max" },
  { label: "Tempo de Voo", value: "tempo_voo" },
]

const velocidade = [
  { label: "km/h", value: "km/h" },
  { label: "m/s", value: "m/s" },
]

const altura = [
  { label: "km", value: "km" },
  { label: "m", value: "m" },
  { label: "cm", value: "cm" },
]

const angulos = [
  { label: "º", value: "graus" },
  { label: "rad", value: "radianos" },
]

const aceleracao = [
  { label: "m/s²", value: "ms2" },
  { label: "km/h²", value: "kmh2" },
]

export default function Configure() {
  return (
    <>
      <h3 className="text-xl font-bold text-text">Configure o lançamento</h3>
      <div className="flex flex-col gap-2">
        <p className="text-sm text-text-muted">Tipo de movimento</p>
        <Select items={tipo_movimento}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione um tipo" className="text-text " />
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
        <Select items={objetivo}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione um objetivo" className="text-text " />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Tipos</SelectLabel>
              {objetivo.map((item) => (
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
        <Input className="bg-bg border border-border text-text p-5" placeholder="Ex: 72" />
        <Select items={velocidade}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione" className="text-text text-sm" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Tipos</SelectLabel>
              {velocidade.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p className="text-text text-sm " >Ângulo de lançamento</p>
        <Input className="bg-bg border border-border text-text p-5" placeholder="Ex: 45" />
        <Select items={angulos}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione" className="text-text text-sm" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Tipos</SelectLabel>
              {angulos.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p className="text-text text-sm " >Altura inicial</p>
        <Input className="bg-bg border border-border text-text p-5" placeholder="Ex: 0" />
        <Select items={altura}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione" className="text-text text-sm" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Tipos</SelectLabel>
              {altura.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <p className="text-text text-sm " >Gravidade</p>
        <Input className="bg-bg border border-border text-text p-5" placeholder="Ex: 9.81" />
        <Select items={aceleracao}>
          <SelectTrigger className="w-full bg-bg border border-border p-5">
            <SelectValue placeholder="Selecione" className="text-text text-sm" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Tipos</SelectLabel>
              {aceleracao.map((item) => (
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
    </>
  )
}
