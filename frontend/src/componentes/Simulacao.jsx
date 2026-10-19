import Grafico from "./Grafico";

export default function Simulacao() {
  return (
    <>
      <div className="flex justify-between align-center">
        <h3 className="text-xl font-bold text-text">Simulação do movimento</h3>
        <p className="text-sm text-text-muted">Sem resistência do ar</p>
      </div>
      <div className="flex justify-center py-4">
        <Grafico />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-text-muted">Alcance horizontal</p>
          <h3 className="text-2xl font-bold text-text">40,77 m</h3>
        </div>
        <div>
          <p className="text-sm text-text-muted">Altura máxima</p>
          <h3 className="text-2xl font-bold text-text">10,19 m</h3>
        </div>
        <div>
          <p className="text-sm text-text-muted">Tempo de voo</p>
          <h3 className="text-2xl font-bold text-text">2,88 s</h3>
        </div>
      </div>
    </>
  )
}
