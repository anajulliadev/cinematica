import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";

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

export default function Configure({formData, setFormData, handleSubmit}) {

  function handleChange(name, value){
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col p-6 gap-4 bg-surface border border-border rounded-xl pb-11">
      <h3 className="text-xl font-bold text-text">Configure o lançamento</h3>
      <div className="flex flex-col gap-2">
        <p className="text-sm text-text-muted">Tipo de movimento</p>
        <Select
          value={formData.tipoMovimento}
          onValueChange={(value) =>
            handleChange("tipoMovimento", value)
          }>
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
        <Select
          value={formData.objetivo}
          onValueChange={(value) =>
            handleChange("objetivo", value)
          }>
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
        <Input
          className="bg-bg border border-border text-text p-5"
          type="number"
          value={formData.velocidadeInicial}
          onChange={(e) =>
            handleChange("velocidadeInicial", e.target.value)
          }
          placeholder="Ex: 72" />
        <Select
          value={formData.unidadeVelocidade}
          onValueChange={(value) =>
            handleChange("unidadeVelocidade", value)
          }>
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
        <Input
          className="bg-bg border border-border text-text p-5"
          type="number"
          value={formData.angulo}
          onChange={(e) =>
            handleChange("angulo", e.target.value)
          }
          placeholder="Ex: 45" />
        <Select
          value={formData.unidadeAngulo}
          onValueChange={(value) =>
            handleChange("unidadeAngulo", value)
          }>
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
        <Input
          className="bg-bg border border-border text-text p-5"
          type="number"
          value={formData.altura}
          onChange={(e) =>
            handleChange("altura", e.target.value)
          }
          placeholder="Ex: 45" />
        <Select
          value={formData.unidadeAltura}
          onValueChange={(value) =>
            handleChange("unidadeAltura", value)
          }>
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
        <Input
          className="bg-bg border border-border text-text p-5"
          type="number"
          value={formData.gravidade}
          onChange={(e) =>
            handleChange("gravidade", e.target.value)
          }
          placeholder="Ex: 45" />
        <Select
          value={formData.unidadeGravidade}
          onValueChange={(value) =>
            handleChange("unidadeGravidade", value)
          }>
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
      <Button type="submit" className="py-5 px-6 rounded-lg">
        <span className="text-base font-bold">Calcular trajetória</span>
      </Button>
    </form>
  )
}
