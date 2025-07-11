# backend/llm_router.py

from backend.llm import llm_with_tools, llm_pure
from backend.tools.tool_list import TOOLS

def call_llm(question: str, context: str = "", **kwargs):
    """
    Encaminha o pedido para o LLM apropriado:
      - Tool-calling via LangChain, se apropriado
      - Retrieval puro via LlamaIndex (Ollama) caso contrário
    """
    if llm_with_tools is not None:
        response = llm_with_tools.invoke(question)
        return response
    else:
        return "❌ Modo 'tools' não está ativo."
