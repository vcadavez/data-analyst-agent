# backend/tools/export_subset_tool.py

import pandas as pd
from backend.config import settings
from langchain.tools import tool

@tool
def export_subset_tool(filter_dict: dict = None, filename: str = 'filtered_data.csv', csv_path: str = settings.csv_path) -> str:
    """
    Exporta um subconjunto de um DataFrame para CSV.
    Parâmetros:
        csv_path (str): Caminho para o CSV de origem.
        filter_dict (dict, opcional): Filtros no formato {coluna: valor}.
        filename (str): Nome do ficheiro de output.
    Retorna:
        str: Mensagem de confirmação (ou erro).
    """
    import os
    import uuid
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro de origem não foi encontrado."
    df = pd.read_csv(csv_path)
    if filter_dict:
        for col, val in filter_dict.items():
            if col not in df.columns:
                return f"⚠️ Coluna '{col}' não existe no dataset. Disponíveis: {', '.join(df.columns)}"
            df = df[df[col] == val]
    if df.empty:
        return "⚠️ O subset filtrado não contém registos e não foi exportado."
    # Garante nome único
    if filename == 'filtered_data.csv':
        filename = f'filtered_data_{uuid.uuid4().hex[:8]}.csv'
    df.to_csv(filename, index=False)
    return f"Subset exportado para {filename}"

