import requests
import json

def call_ollama_stream(prompt: str, model: str = "llama3:instruct") -> str:
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
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

if __name__ == "__main__":
    prompt = "Hello, how are you?"
    response = call_ollama_stream(prompt)
    print("Resposta completa:", response)
