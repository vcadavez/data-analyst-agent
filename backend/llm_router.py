from backend.llm import llm_with_tools, llm_pure
from langchain_core.messages import HumanMessage
import requests
import json

def call_ollama_stream(prompt: str, model: str = "llama3:instruct") -> str:
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True, timeout=60)

    full_response = ""
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            obj = json.loads(decoded)
            content = obj.get("message", {}).get("content", "")
            full_response += content
            if obj.get("done", False):
                break
    return full_response

def call_llm(question: str, context: str = "", **kwargs):
    """
    Encaminha o pedido para o LLM apropriado:
      - Tool-calling via LangChain, se apropriado
      - Retrieval puro via LlamaIndex (Ollama) caso contrário
    """
    prompt = f"{context}\n\n{question}" if context else question

    if llm_with_tools is not None:
        response = llm_with_tools.invoke([HumanMessage(content=prompt)])
        return getattr(response, "content", str(response))
    elif llm_pure is not None:
        # Usa streaming com a API Ollama
        return call_ollama_stream(prompt)
    else:
        return "❌ Nenhum LLM ativo."