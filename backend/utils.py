import os
import logging
import pandas as pd
from backend.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def get_qdrant_client():
    logging.info(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
    return QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        timeout=300.0
    )

def ensure_collection(client, collection_name, vector_size):
    """
    Garante que a coleção existe com a configuração correta.
    """
    collections = client.get_collections().collections
    if not any(col.name == collection_name for col in collections):
        logging.info(f"Criando coleção '{collection_name}' com tamanho do vetor {vector_size}")
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    else:
        logging.info(f"Coleção '{collection_name}' já existe.")

def index_csv_to_qdrant(csv_path, collection_name="dataset"):
    """
    Lê o CSV, garante a coleção e faz a indexação no Qdrant.
    """
    if not os.path.exists(csv_path):
        logging.error(f"Arquivo CSV não encontrado: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    if df.empty:
        logging.warning("CSV está vazio.")
        return False

    # Exemplo: usando as 3 primeiras colunas como vetor (ajuste conforme seu caso)
    vector_columns = df.columns[:3]
    vectors = df[vector_columns].values.tolist()
    payloads = df.to_dict(orient="records")
    ids = list(range(1, len(df) + 1))

    client = get_qdrant_client()
    ensure_collection(client, collection_name, vector_size=len(vector_columns))

    logging.info("Iniciando upsert no Qdrant...")
    try:
        response = client.upsert(
            collection_name=collection_name,
            points=[
                {
                    "id": id_,
                    "vector": vector,
                    "payload": payload
                }
                for id_, vector, payload in zip(ids, vectors, payloads)
            ]
        )
        logging.info("Upsert concluído com sucesso.")
        return response
    except Exception as e:
        logging.error(f"Erro ao indexar pontos no Qdrant: {e}")
        return False

def get_dataset_context() -> str:
    csv_path = settings.csv_path
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        columns = ", ".join(f'"{col}"' for col in df.columns)
        preview = df.head(5).to_string(index=False)
        context = (
            f"O dataset contém as colunas: {columns}.\n"
            f"Aqui estão as 5 primeiras linhas como exemplo:\n{preview}\n\n"
        )
    else:
        context = "(⚠️ O ficheiro uploaded.csv não foi encontrado)\n\n"
    return context
