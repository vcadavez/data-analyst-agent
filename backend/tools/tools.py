# backend/tools.py


from langchain.tools import tool
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO
from backend.config import settings



from langchain.tools import tool
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from backend.config import settings


from langchain.tools import tool
import sys
from io import StringIO
import pandas as pd
import os
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.meta_analysis import effectsize_smd, combine_effects

from .export_subset_tool import export_subset_tool
from .filter_data_tool import filter_data_tool
from .meta_analysis_by_column_tool import meta_analysis_by_column_tool
from backend.config import settings
# from backend.llm_router import call_llm

from backend.indexer import load_index, query_index

@tool
def search_index(question: str) -> str:
    """Consulta os documentos carregados com base numa pergunta."""
    try:
        index = load_index()
        response = query_index(index, question)
        return str(response)
    except Exception as e:
        return f"Erro ao consultar o índice: {str(e)}"

@tool
def count_unique_values(column_name: str, csv_path: str = settings.csv_path) -> str:
    """Conta quantos valores únicos existem numa coluna do ficheiro CSV."""
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    try:
        df = pd.read_csv(csv_path)
        if column_name not in df.columns:
            return f"⚠️ Coluna '{column_name}' não existe. Disponíveis: {', '.join(df.columns)}"
        return f"A coluna '{column_name}' contém {df[column_name].nunique(dropna=True)} valor(es) único(s)."
    except Exception as e:
        return f"⚠️ Erro ao ler o ficheiro: {str(e)}"

@tool
def list_unique_values(column_name: str, csv_path: str = settings.csv_path) -> str:
    """Lista os valores únicos de uma coluna específica do CSV carregado."""
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    try:
        df = pd.read_csv(csv_path)
        if column_name not in df.columns:
            return f"⚠️ Coluna '{column_name}' não existe. Disponíveis: {', '.join(df.columns)}"
        values = df[column_name].dropna().unique()
        values_str = ", ".join(str(v) for v in values[:30])
        return f"{len(values)} valor(es) único(s): {values_str}" + ("..." if len(values) > 30 else "")
    except Exception as e:
        return f"⚠️ Erro ao ler o ficheiro: {str(e)}"

@tool
def describe_column(column_name: str, csv_path: str = settings.csv_path) -> str:
    """Mostra estatísticas descritivas para uma coluna específica."""
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    df = pd.read_csv(csv_path)
    if column_name not in df.columns:
        return f"⚠️ A coluna '{column_name}' não existe. Disponíveis: {', '.join(df.columns)}"
    return f"📊 Estatísticas da coluna '{column_name}':\n{df[column_name].describe(include='all').to_string()}"

@tool
def count_rows(csv_path: str = settings.csv_path) -> str:
    """Conta o número total de linhas do ficheiro CSV."""
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    df = pd.read_csv(csv_path)
    return f"O ficheiro contém {len(df)} linhas."

@tool
def get_column_names(csv_path: str = settings.csv_path) -> List[str]:
    """Lista os nomes das colunas disponíveis no ficheiro CSV."""
    if not os.path.exists(csv_path):
        return ["⚠️ O ficheiro 'uploaded.csv' não foi encontrado."]
    df = pd.read_csv(csv_path)
    return df.columns.tolist()

@tool
def summarize_by_category(column_name: str, csv_path: str = settings.csv_path) -> str:
    """Resume as colunas numéricas agrupadas pela categoria indicada."""
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."
    try:
        df = pd.read_csv(csv_path)
        if column_name not in df.columns:
            return f"⚠️ A coluna '{column_name}' não existe."
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) == 0:
            return "⚠️ Não há colunas numéricas para agrupar."
        summary = df.groupby(column_name)[numeric_cols].describe().round(2)
        return f"📊 Resumo por '{column_name}':\n{summary.to_string()[:3000]}"
    except Exception as e:
        return f"❌ Erro ao gerar resumo: {str(e)}"

@tool
def count_rows_matching_value(column_name: str, value: str, csv_path: str = settings.csv_path) -> str:
    """
    Conta quantas linhas do CSV têm o valor exacto especificado numa determinada coluna.
    Útil para perguntas como: "Quantas linhas têm Salmonella na coluna Bacterium?"
    """
    if not os.path.exists(csv_path):
        return "⚠️ O ficheiro 'uploaded.csv' não foi encontrado."

    try:
        df = pd.read_csv(csv_path)

        if column_name not in df.columns:
            return f"⚠️ A coluna '{column_name}' não existe. Colunas disponíveis: {', '.join(df.columns)}"

        count = df[df[column_name] == value].shape[0]
        return f"A coluna '{column_name}' contém {count} linha(s) com o valor '{value}'."

    except Exception as e:
        return f"⚠️ Ocorreu um erro ao contar as linhas: {str(e)}"


@tool
def plot_histogram(column: str, csv_path: str = settings.csv_path) -> str:
    """
    Gera um histograma para uma coluna numérica. Retorna a imagem base64.
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        return f"⚠️ Coluna '{column}' não existe. Disponíveis: {', '.join(df.columns)}"
    if not pd.api.types.is_numeric_dtype(df[column]):
        return f"⚠️ Coluna '{column}' não é numérica."
    plt.figure(figsize=(8, 5))
    plt.hist(df[column].dropna(), bins=30)
    plt.title(f'Histograma de {column}')
    plt.xlabel(column)
    plt.ylabel('Frequência')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.read()).decode('utf-8')

@tool
def plot_boxplot_by_category(numeric_col: str, category_col: str, csv_path: str = settings.csv_path) -> str:
    """
    Gera um boxplot do valor numérico por categoria. Retorna imagem base64.
    """
    df = pd.read_csv(csv_path)
    if numeric_col not in df.columns or category_col not in df.columns:
        return f"⚠️ Coluna não encontrada. Disponíveis: {', '.join(df.columns)}"
    if not pd.api.types.is_numeric_dtype(df[numeric_col]):
        return f"⚠️ Coluna '{numeric_col}' não é numérica."
    import seaborn as sns
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=category_col, y=numeric_col, data=df)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.read()).decode('utf-8')


@tool
def crosstab_columns(col1: str, col2: str, csv_path: str = settings.csv_path) -> str:
    """
    Cria uma tabela cruzada (contingência) entre duas colunas categóricas.
    """
    df = pd.read_csv(csv_path)
    if col1 not in df.columns or col2 not in df.columns:
        return f"⚠️ Colunas não encontradas. Disponíveis: {', '.join(df.columns)}"
    table = pd.crosstab(df[col1], df[col2])
    return f"Tabela cruzada entre '{col1}' e '{col2}':\n{table.to_string()[:3000]}"


@tool
def missing_values_report(csv_path: str = settings.csv_path) -> str:
    """
    Devolve o número e percentagem de valores em falta por coluna.
    """
    df = pd.read_csv(csv_path)
    total = len(df)
    missing = df.isnull().sum()
    percent = (missing / total * 100).round(2)
    report = pd.DataFrame({'Missing': missing, 'Percent': percent})
    return f"Valores em falta por coluna:\n{report.to_string()}"


@tool
def export_subset_excel(filter_dict: dict = None, filename: str = 'filtered_data.xlsx', csv_path: str = settings.csv_path) -> str:
    """
    Exporta um subconjunto filtrado para Excel.
    """
    df = pd.read_csv(csv_path)
    if filter_dict:
        for col, val in filter_dict.items():
            if col not in df.columns:
                return f"⚠️ Coluna '{col}' não existe no dataset."
            df = df[df[col] == val]
    if df.empty:
        return "⚠️ O subset filtrado não contém registos e não foi exportado."
    df.to_excel(filename, index=False)
    return f"Subset exportado para {filename}"


@tool
def wordcloud_column(column: str, csv_path: str = settings.csv_path) -> str:
    """
    Gera um wordcloud para uma coluna textual. Retorna imagem base64.
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        return f"⚠️ Coluna '{column}' não existe."
    from wordcloud import WordCloud
    text = " ".join(str(val) for val in df[column].dropna())
    if not text.strip():
        return "⚠️ Não há texto suficiente para gerar wordcloud."
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    buf = BytesIO()
    wordcloud.to_image().save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@tool
def plot_time_series(date_col: str, value_col: str, freq: str = 'M', csv_path: str = settings.csv_path) -> str:
    """
    Gera um gráfico de evolução temporal de uma métrica agregada (soma ou média) por data.
    Args:
        date_col (str): Nome da coluna com datas.
        value_col (str): Coluna numérica a agregar.
        freq (str): Frequência de agregação ('D'=dia, 'M'=mês, 'Y'=ano).
    Returns:
        str: Imagem base64.
    """
    df = pd.read_csv(csv_path)
    if date_col not in df.columns or value_col not in df.columns:
        return f"⚠️ Coluna '{date_col}' ou '{value_col}' não existe. Colunas: {', '.join(df.columns)}"
    if not pd.api.types.is_numeric_dtype(df[value_col]):
        return f"⚠️ Coluna '{value_col}' não é numérica."
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    ts = df.groupby(pd.Grouper(key=date_col, freq=freq))[value_col].mean()
    plt.figure(figsize=(10, 5))
    ts.plot(marker='o')
    plt.title(f'{value_col} ao longo do tempo ({freq})')
    plt.xlabel(date_col)
    plt.ylabel(value_col)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.read()).decode('utf-8')


@tool
def kmeans_clustering(n_clusters: int = 3, columns: list = None, csv_path: str = settings.csv_path) -> str:
    """
    Executa KMeans sobre colunas numéricas do CSV.
    Args:
        n_clusters (int): Número de clusters.
        columns (list): Lista de colunas numéricas a usar. Usa todas se None.
    Returns:
        str: Resumo dos clusters.
    """
    from sklearn.cluster import KMeans
    import numpy as np
    df = pd.read_csv(csv_path)
    if columns:
        for col in columns:
            if col not in df.columns:
                return f"⚠️ Coluna '{col}' não existe."
        data = df[columns].select_dtypes(include='number').dropna()
    else:
        data = df.select_dtypes(include='number').dropna()
    if data.empty:
        return "⚠️ Não há dados numéricos suficientes para clustering."
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    clusters = kmeans.fit_predict(data)
    data['Cluster'] = clusters
    counts = data['Cluster'].value_counts().sort_index()
    centers = kmeans.cluster_centers_
    res = f"Distribuição dos clusters:\n{counts.to_string()}\n\nCentros dos clusters:\n{centers}"
    return res

@tool
def automatic_scoring(columns: dict, top_n: int = 5, csv_path: str = settings.csv_path) -> str:
    """
    Calcula score automático para cada linha (soma ponderada das colunas) e devolve top N.
    Args:
        columns (dict): {coluna: peso}. Ex: {'ColA': 0.7, 'ColB': 0.3}
        top_n (int): Número de resultados a devolver.
    Returns:
        str: Top N linhas e respetivos scores.
    """
    df = pd.read_csv(csv_path)
    for col in columns:
        if col not in df.columns:
            return f"⚠️ Coluna '{col}' não existe."
    score = sum(df[col] * weight for col, weight in columns.items())
    df['score'] = score
    top = df.sort_values('score', ascending=False).head(top_n)
    return f"Top {top_n} linhas com maior score:\n{top[['score'] + list(columns.keys())].to_string(index=False)}"
