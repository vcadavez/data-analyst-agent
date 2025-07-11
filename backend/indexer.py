# backend/indexer.py

import os
import logging
import pandas as pd

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.schema import Document
from llama_index.core.settings import Settings
from llama_index.llms.ollama import Ollama

from backend.config import settings
from backend.utils import get_qdrant_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QdrantIndexer")

# Endpoint Ollama a partir da env
ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Configuração global de embeddings e LLM
Settings.embed_model = OllamaEmbedding(
    model_name=settings.embedding_model,
    base_url=ollama_url,
)
Settings.llm = Ollama(
    model=settings.llm_model,
    base_url=ollama_url,
)

def build_index(
    csv_path: str = settings.csv_path,
    collection_name: str = settings.collection_name,
    clear_collection: bool = True,
):
    """
    Build and persist a vector index from a CSV using Qdrant.
    One Document per CSV row. Can clear collection if rebuilding.
    """
    logger.info(f"Construindo índice a partir do ficheiro: {csv_path}")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"O ficheiro '{csv_path}' não foi encontrado.")

    size = os.path.getsize(csv_path)
    logger.info(f"Tamanho do ficheiro: {size} bytes")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("O ficheiro está vazio.")

    df = df.fillna("").astype(str)
    logger.info(f"Dataframe carregado com {len(df)} linhas e {len(df.columns)} colunas.")

    documents = [
        Document(text=", ".join(f"{col}: {row[col]}" for col in df.columns))
        for _, row in df.iterrows()
    ]
    logger.info(f"📝 Criados {len(documents)} documentos para indexação.")

    client = get_qdrant_client()
    collections_info = client.get_collections()
    existing = [c.name for c in collections_info.collections]

    if clear_collection and collection_name in existing:
        try:
            client.delete_collection(collection_name=collection_name)
            logger.info(f"🗑️ Coleção '{collection_name}' removida antes da indexação.")
        except Exception as e:
            logger.warning(f"(Ignorado) não foi possível remover coleção: {e}")

    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=client,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    logger.info("✅ Indexação concluída e persistida.")
    return index

def load_index(
    collection_name: str = settings.collection_name,
):
    """
    Load a persisted Qdrant vector index.
    """
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=client,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    logger.info(f"📦 Índice carregado da coleção '{collection_name}'.")
    return index

def query_index(
    index,
    question: str,
    top_k: int = 3,
):
    """
    Query the index with a natural language question.
    Uses `response_mode="simple"` para evitar chamadas ao LLM.
    """
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="simple",
    )
    response = query_engine.query(question)

    if hasattr(response, "response") and response.response:
        return response.response
    if hasattr(response, "source_nodes") and response.source_nodes:
        return "\n---\n".join(node.text for node in response.source_nodes)
    return str(response)

if __name__ == "__main__":
    try:
        idx = build_index()
        answer = query_index(idx, "Quantas linhas tem o dataset?")
        print("Resposta:", answer)
    except Exception as e:
        logger.error(f"Erro no teste rápido: {e}")
