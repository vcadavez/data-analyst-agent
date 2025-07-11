import matplotlib.pyplot as plt
import pandas as pd
from langchain.tools import tool
from backend.config import settings
import base64
from io import BytesIO

@tool
def plot_prevalence_by_column(column: str, csv_path: str = settings.csv_path) -> str:
    """
    Gera um gráfico de barras da prevalência média agrupada por coluna.
    Retorna a imagem PNG codificada em base64.
    """
    try:
        df = pd.read_csv(csv_path)
        if column not in df.columns or 'Prevalence' not in df.columns:
            return f"⚠️ Colunas necessárias ('Prevalence' e '{column}') não encontradas. Disponíveis: {', '.join(df.columns)}"
        plot_df = df.groupby(column)['Prevalence'].mean().reset_index()
        if plot_df.empty:
            return "⚠️ Não há dados para agrupar."
        # Limite opcional de categorias
        if len(plot_df) > 30:
            plot_df = plot_df.sort_values('Prevalence', ascending=False).head(30)
        plt.figure(figsize=(10, 6))
        plt.bar(plot_df[column], plot_df['Prevalence'])
        plt.xticks(rotation=90)
        plt.ylabel('Prevalence')
        plt.title(f'Prevalence by {column}')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        return f"❌ Erro ao gerar gráfico: {str(e)}"