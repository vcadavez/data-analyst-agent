from langchain_core.messages import HumanMessage
from backend.utils import get_dataset_context
from backend.llm import llm_with_tools, llm_pure

def build_context_node(state: dict) -> dict:
    context = get_dataset_context()
    return {**state, "context": context}

def execute_tool_node(state: dict) -> dict:
    context = state.get("context", "")
    question = state.get("question", "")

    prompt = (
        f"Contexto do dataset:\n{context}\n\n"
        f"Com base neste contexto, responde à pergunta: {question}\n"
    )

    llm = llm_with_tools or llm_pure
    if llm is None:
        resposta_final = "❌ Nenhum LLM disponível no backend."
    else:
        response = llm.invoke([HumanMessage(content=prompt)])
        resposta_final = getattr(response, "content", str(response))

    return {**state, "output": resposta_final}
