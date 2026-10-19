# Calculadora de Cinemática 1D e 2D

O usuário informa o que sabe sobre um movimento (cada valor na unidade que quiser) e o que quer descobrir. O programa converte tudo para o SI, escolhe as fórmulas e mostra o resultado, o passo a passo e a animação do movimento. Cobre MRU, MRUV, queda livre e lançamento de projétil (oblíquo e horizontal).

Backend em Python (FastAPI) e frontend em React (Vite).

## Pré-requisitos

- Python 3.12+
- Node.js 20+

## Como rodar

```bash
# backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cd ..

# frontend
npm install
npm --prefix frontend install

# sobe os dois (com a .venv ativada)
npm run dev
```

- Site: http://localhost:5173
- API: http://localhost:8000/docs

## API

`POST /api/calcular`. O `/docs` tem o formato de cada campo e exemplos prontos para testar; ver mais em [`backend/docs/API.md`](backend/docs/API.md).
