#!/bin/bash

ROOT_DIR=$(pwd)

# Terminar backend
if [ -f "$ROOT_DIR/backend/backend.pid" ]; then
  PID=$(cat "$ROOT_DIR/backend/backend.pid")
  echo "🛑 A terminar backend (PID $PID)..."
  kill "$PID"
  rm "$ROOT_DIR/backend/backend.pid"
else
  echo "⚠️ backend.pid não encontrado. O backend pode já estar parado."
fi

# Opcional: Terminar Streamlit
echo "🛑 A procurar processos Streamlit..."
pkill -f "streamlit run app.py"

echo "✅ Todos os serviços foram terminados."
