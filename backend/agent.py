# backend/agent.py

import logging
import uuid
from backend.graph import create_graph

logger = logging.getLogger("AgenteAnalista")
graph = create_graph()

def run_agent(question: str, thread_id: str = None) -> str:
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    logger.info(f"🧠 Pergunta recebida: {question} | thread_id={thread_id}")

    try:
        state = {
            "question": question,
            "thread_id": thread_id
        }

        # Invoca o grafo LangGraph
        result = graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
        logger.info(f"[DEBUG] Resultado do grafo: {result!r}")

        if not result or not isinstance(result, dict):
            logger.error("O grafo não devolveu um dicionário de estado! Resultado: %r", result)
            return "⚠️ Erro interno: o agente não devolveu resposta.", thread_id

        # Tenta sempre devolver o output do último node (agent ou execute_tool)
        resposta = (
            result.get("agent", {}).get("output")
            or result.get("execute_tool", {}).get("output")
            or "⚠️ Nenhuma resposta foi gerada."
        )
        logger.info(f"✅ Resposta devolvida: {resposta}")
        return resposta, thread_id

    except Exception as e:
        logger.error(f"❌ Erro na execução do agente: {e}")
        return f"⚠️ Erro interno no agente: {str(e)}", thread_id
