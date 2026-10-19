export async function calcular(payload) {
  const resposta = await fetch("/api/calcular", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const dados = await resposta.json();

  if(!resposta.ok) {
    throw new Error(
      dados.mensagem ??
      "Não foi possível calcular. Verifique os dados informados."
    )
  }
  
  return dados;
}
