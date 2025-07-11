import pandas as pd
from backend.config import settings
from langchain.tools import tool

@tool
def filter_data_tool(filters: dict = None, csv_path: str = settings.csv_path) -> str:
    """
    Filtra o DataFrame do CSV com base em múltiplos valores de coluna.

    Parameters:
        csv_path (str): Caminho para o ficheiro CSV.
        filters (dict, opcional): {coluna: valor ou lista de valores}.

    Returns:
        str: Registos filtrados em formato JSON (orient="records").
    """
    import os
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    df = pd.read_csv(csv_path)
    if filters:
        for col, val in filters.items():
            if col not in df.columns:
                return f"⚠️ Coluna '{col}' não existe no dataset. Disponíveis: {', '.join(df.columns)}"
            if isinstance(val, list):
                df = df[df[col].isin(val)]
            else:
                df = df[df[col] == val]
    else:
        df = df.head(100)  # limita output se sem filtros
    if df.empty:
        return "⚠️ Nenhum registo encontrado com os filtros fornecidos."
    return df.to_json(orient="records")
