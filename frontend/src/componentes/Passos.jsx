import katex from "katex";
import "katex/dist/katex.min.css";
import { CAMPOS } from "../config/movimentos";

export default function Passos({ resposta }) {
  if (!resposta) return null;

  return (
    <section className="flex flex-col p-6 gap-4 bg-surface border border-border rounded-xl">
      <h3 className="text-xl font-bold text-text">
        Como chegamos ao resultado
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {resposta.passos.map((passo, indice) => (
            <div key={`${indice}-${passo.variavel}`} className="flex flex-col min-w-0 gap-3">
              <p className="text-text font-medium"> {indice + 1}. {passo.formula} </p>
              <div className="overflow-x-auto bg-bg text-text p-3 rounded-lg"
                dangerouslySetInnerHTML={{
                  __html: katex.renderToString(passo.latex_isolada,
                    {
                      throwOnError: false,
                      trust: false,
                      displayMode: true,
                    }
                  ),
                }} 
              />
              {passo.observacao && ( <p className="text-sm text-text-muted">{passo.observacao}</p> )}
            </div>
          ))}
        </div>
    </section>
  );
}