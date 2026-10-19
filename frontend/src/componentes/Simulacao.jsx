import Grafico from "./Grafico";
import { CAMPOS } from "../config/movimentos";

export default function Simulacao({ resposta }) {
  return (
    <>
      <div className="flex justify-between align-center">
        <h3 className="text-xl font-bold text-text">Simulação do movimento</h3>
        <p className="text-sm text-text-muted">Sem resistência do ar</p>
      </div>

      {!resposta ? (
        <>
          <div className="flex justify-center py-4">
            <Grafico movimento="mru" trajetoria={Array.from({length:61},(_,i)=>{const t=(3*i)/60;return{t,s:20*t,v:20};})} />
          </div>
          <div>
            <p className="text-sm text-text-muted">
              Deslocamento
            </p>

            <p className="text-2xl font-bold text-text">
              60m
            </p>
          </div>
        </>
      ) : (
        <>
          <div className="flex justify-center py-4">
            <Grafico movimento={resposta.movimento} trajetoria={resposta.trajetoria} />
          </div>
          <div>
            <p className="text-sm text-text-muted">
              {CAMPOS[resposta.alvo]?.label ?? resposta.alvo}
            </p>

            <p className="text-2xl font-bold text-text">
              {resposta.resultado.valor.toLocaleString("pt-BR", { maximumFractionDigits: 4 })} {" "}
              {resposta.resultado.unidade}
            </p>
          </div>
        </>
      )}
    </>
  );
}