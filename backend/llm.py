# backend/llm.py

from backend.config import settings

LLM_MODE = settings.agent_llm_mode  # "tools" ou "simple"

if LLM_MODE == "tools":
    from langchain_ollama import ChatOllama
    from backend.tools.tool_list import TOOLS
    llm = ChatOllama(model=settings.llm_model, temperature=0.1, base_url="http://host.docker.internal:11434").bind_tools(TOOLS)
else:
    from llama_index.llms.ollama import Ollama
    llm = Ollama(model=settings.llm_model)