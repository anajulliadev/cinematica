import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState, Fragment } from "react";
import { CAMPOS, MOVIMENTOS, UNIDADES } from "../config/movimentos";

const SIMBOLOS = { "m/s2": "m/s²", grau: "°" };

function Seletor({ value, onChange, options, placeholder, label, disabled = false }) {
  return (
    <Select value={value || null} onValueChange={onChange} disabled={disabled}
      items={options}>
      <SelectTrigger aria-label={label} className="w-full min-w-0 bg-bg border border-border px-4 py-5">
        <SelectValue placeholder={placeholder} className="min-w-0 flex-1 whitespace-nowrap text-left text-text" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>{label}</SelectLabel>
          {options.map((item) => ( <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem> ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}

export default function Configure({ dimension, formData, setFormData, handleSubmit }) {
  const movimentos = MOVIMENTOS.filter((item) => item.dimensao === dimension);
  const movimento = movimentos.find((item) => item.value === formData.tipoMovimento);
  const nomeCampo = (id) => movimento?.value === "mru" && id === "v" ? "Velocidade" : CAMPOS[id].label;
  const objetivos = (movimento?.objetivos ?? []).map((id) => ({ value: id, label: nomeCampo(id) }));

  function handleChange(value) {
      if (value === formData.tipoMovimento) return;

    const selecionado = movimentos.find((item) => item.value === value);
    if (!selecionado) return;

    setFormData({ tipoMovimento: selecionado.value, objetivo: selecionado.objetivos[0], conhecidas: {} });
  }

  function changeCampo(id, propriedade, value) {
    setFormData((prev) => ({
      ...prev,
      conhecidas: {
        ...prev.conhecidas,
        [id]: {
          valor: "",
          unidade: UNIDADES[CAMPOS[id].grandeza][0],
          ...prev.conhecidas[id],
          [propriedade]: value,
        },
      },
    }));
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col p-6 gap-4 bg-surface border border-border rounded-xl pb-11">
      <h3 className="text-xl font-bold text-text">Configure o lançamento</h3>
      <div className="flex flex-col gap-2">
        <p className="text-sm text-text-muted">Tipo de movimento</p>
        <Seletor 
          value={formData.tipoMovimento} 
          onChange={handleChange}
          options={movimentos} label="Tipo de movimento" placeholder="Selecione um tipo" />
      </div>
      <div className="flex flex-col gap-2">
        <p className="text-sm text-text-muted">Objetivo do cálculo</p>
        <Seletor value={formData.objetivo}
          onChange={(value) => setFormData((prev) => ({ ...prev, objetivo: value ?? "" }))}
          options={objetivos} label="Objetivo do cálculo" disabled={!movimento}
          placeholder={movimento ? "Selecione um objetivo" : "Selecione primeiro o movimento"} />
      </div>
      {movimento && (
        <>
          {movimento.value === "obliquo" && (
            <p className="text-text-muted text-sm">Informe velocidade inicial e ângulo, ou as componentes horizontal e vertical.</p>
          )}
          {movimento.value === "horizontal" && (
            <p className="text-text-muted text-sm">O lançamento horizontal considera ângulo de 0° e velocidade vertical inicial nula.</p>
          )}
          <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)] gap-x-1.5 gap-y-4 items-center">
            {movimento.campos.map((id) => {
              const campo = CAMPOS[id];
              const entrada = formData.conhecidas[id];
              return (
                <Fragment key={id}>
                  <label htmlFor={`campo-${id}`} className="text-text text-sm">{nomeCampo(id)}</label>
                  <Input id={`campo-${id}`} className="min-w-0 bg-bg border border-border text-text p-3"
                    type="number" step="any" value={entrada?.valor ?? ""}
                    onChange={(event) => changeCampo(id, "valor", event.target.value)}
                    placeholder={id === "g" ? "9,81" : "Valor"} />
                  <Seletor value={entrada?.unidade ?? UNIDADES[campo.grandeza][0]}
                    onChange={(value) => changeCampo(id, "unidade", value)}
                    options={UNIDADES[campo.grandeza].map((value) => ({ value, label: SIMBOLOS[value] ?? value }))}
                    label={`Unidade de ${nomeCampo(id).toLowerCase()}`} placeholder="Unidade" />
                </Fragment>
              );
            })}
          </div>
          <p className="text-text-muted text-sm">Preencha apenas os dados que você conhece.</p>
        </>
      )}
      <Button type="submit" disabled={!movimento || !formData.objetivo} className="py-5 px-6 rounded-lg">
        <span className="text-base font-bold">Calcular trajetória</span>
      </Button>
    </form>
  );
}
