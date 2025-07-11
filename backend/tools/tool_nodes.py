# backend/tools/tool_nodes.py

from langchain_core.messages import HumanMessage
from backend.utils import get_dataset_context
from backend.llm import llm

# Nodo para construir o contexto a partir do ficheiro CSV
def build_context_node(state: dict) -> dict:
    context = get_dataset_context()

    # Mantém o resto do estado se for necessário para outros nós
    return {**state, "context": context}

# Nodo para executar o LLM sobre o contexto e a pergunta
def execute_tool_node(state: dict) -> dict:
    context = state.get("context", "")
    question = state.get("question", "")

    prompt = (
        f"Contexto do dataset:\n{context}\n\n"
        f"Com base neste contexto, responde à pergunta: {question}\n"
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    # Resposta segura (content pode não existir)
    resposta_final = getattr(response, "content", str(response))

    # Mantém todo o estado para permitir cadeia de execução
    return {**state, "output": resposta_final}
