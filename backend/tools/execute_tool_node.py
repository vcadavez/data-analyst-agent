# backend/tools/execute_tool_node.py

from langchain_core.messages import HumanMessage

from backend.llm_router import call_llm

def execute_tool_node(state: dict) -> dict:
    """
    Executa o LLM com a query e contexto como entrada.
    """
    question = state.get("question", "")
    context = state.get("context", "") or ""

    if llm is None:
        return {**state, "output": "❌ Erro interno: LLM não está definido. Contacte o administrador."}

    full_prompt = (
        "Usa exclusivamente a informação do contexto seguinte para responder.\n\n"
        f"{context}\n"
        f"Pergunta: {question}"
    )

    result = llm.invoke([HumanMessage(content=full_prompt)])
    resposta = getattr(result, "content", str(result))

    return {**state, "output": resposta}
