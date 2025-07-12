from backend.llm_router import call_llm

def execute_tool_node(state: dict) -> dict:
    """
    Executa o LLM com a query e contexto como entrada.
    """
    question = state.get("question", "")
    context = state.get("context", "") or ""

    full_prompt = (
        "Usa exclusivamente a informação do contexto seguinte para responder.\n\n"
        f"{context}\n"
        f"Pergunta: {question}"
    )

    resposta = call_llm(full_prompt)
    resposta_final = str(resposta)

    return {**state, "output": resposta_final}
