#!/bin/bash

# Ativa o ambiente virtual
source .venv/bin/activate
ROOT_DIR=$(pwd)

echo "🔁 A iniciar backend com Uvicorn..."

# Liberta a porta 8000 se estiver ocupada
if lsof -i:8000 -t >/dev/null; then
  echo "⚠️ Porta 8000 já está em uso. A libertar..."
  kill -9 $(lsof -i:8000 -t)
  sleep 2
fi

# Inicia o backend e regista log
cd "$ROOT_DIR/backend"
uvicorn api:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Aguarda o arranque do backend
sleep 3

echo "🚀 A iniciar frontend com Streamlit..."
cd "$ROOT_DIR/frontend"
streamlit run app.py --server.port 8501
