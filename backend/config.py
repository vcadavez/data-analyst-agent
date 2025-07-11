# backend/config.py

from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    csv_path: str = "backend/data/uploaded.csv"
    persist_dir: str = "storage/qdrant"
    collection_name: str = "dataset"
    llm_model: str = "llama3:instruct"
    embedding_model: str = "nomic-embed-text"
    agent_llm_mode: str = "tools"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    class Config:
        env_file = ".env"

settings = Settings()
