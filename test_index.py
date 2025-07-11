#!/usr/bin/env python3
import os

# Certifica-te que os env vars estão definidos
os.environ.setdefault("QDRANT_HOST", "localhost")
os.environ.setdefault("QDRANT_PORT", "6333")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")

from backend.indexer import build_index, query_index

# Indexa
print("🔁 A construir o índice…")
idx = build_index()

# Faz uma pergunta de teste
pergunta = "Quantas linhas tem o dataset?"
resposta = query_index(idx, pergunta)
print(f"📊 Resposta: {resposta}")
