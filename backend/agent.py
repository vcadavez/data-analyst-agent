# backend/agent.py

import logging
import uuid
from backend.graph import create_graph

from backend.llm import llm

logger = logging.getLogger("AgenteAnalista")
graph = create_graph()

def run_agent(question: str) -> str:
    logger.info(f"🧠 Pergunta recebida: {question}")

    try:
        state = {
            "question": question,
            "thread_id": str(uuid.uuid4())
        }

        result = graph.invoke(state, config={"configurable": {"thread_id": state["thread_id"]}})
        logger.info(f"[DEBUG] Resultado do grafo: {result!r}")

        if not result or not isinstance(result, dict):
            logger.error("O grafo não devolveu um dicionário de estado! Resultado: %r", result)
            return "⚠️ Erro interno: o agente não devolveu resposta."

        resposta = result.get("agent", {}).get("output", "⚠️ Nenhuma resposta foi gerada.")
        logger.info(f"✅ Resposta devolvida: {resposta}")
        return resposta

    except Exception as e:
        logger.error(f"❌ Erro na execução do agente: {e}")
        return f"⚠️ Erro interno no agente: {str(e)}"
