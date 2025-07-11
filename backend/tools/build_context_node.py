# backend/tools/context_nodes.py

from backend.utils import get_dataset_context

def build_context_node(state: dict) -> dict:
    """
    Constrói contexto textual com base no ficheiro uploaded.csv.
    Atualiza o estado com uma chave `context`.
    """
    context = get_dataset_context()

    # Atualiza o estado com o contexto
    return {**state, "context": context}
