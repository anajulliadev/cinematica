export async function calcular(payload) {
  const resposta = await fetch("/api/calcular", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return resposta.json();
}
