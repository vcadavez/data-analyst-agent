from backend.config import settings

LLM_MODE = settings.agent_llm_mode  # "tools" ou "simple"
llm_with_tools = None
llm_pure = None

# Permite definir a URL base do Ollama na .env (ou usa valor default)
OLLAMA_URL = getattr(settings, "ollama_url", None) \
    or getattr(settings, "ollama_base_url", None) \
    or "http://host.docker.internal:11434"

if LLM_MODE == "tools":
    from langchain_ollama import ChatOllama
    from backend.tools.tool_list import TOOLS
    llm_with_tools = ChatOllama(
        model=settings.llm_model,
        temperature=0.1,
        base_url=OLLAMA_URL
    ).bind_tools(TOOLS)
else:
    from llama_index.llms.ollama import Ollama
    llm_pure = Ollama(
        model=settings.llm_model,
        base_url=OLLAMA_URL,
    )
