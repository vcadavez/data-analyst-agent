from langchain.tools import tool
import pandas as pd
from statsmodels.stats.meta_analysis import combine_effects
from backend.config import settings

@tool
def meta_analysis_by_column_tool(
    group_col: str = 'CountrySampling',
    csv_path: str = settings.csv_path
) -> dict:
    """
    Realiza meta-análise agrupada a partir de CSV. Retorna resumo por grupo.
    """
    df = pd.read_csv(csv_path)
    if not set(['Positive', 'TotalUnitsTested']).issubset(df.columns):
        return {"error": "Colunas necessárias ('Positive', 'TotalUnitsTested') não encontradas."}
    results = []
    for group, subdf in df.groupby(group_col):
        xi = subdf['Positive']
        ni = subdf['TotalUnitsTested']
        mask = (ni > 0) & (~xi.isna()) & (~ni.isna())
        xi = xi[mask]
        ni = ni[mask]
        if len(xi) < 3: continue
        try:
            es = xi / ni
            var = es * (1 - es) / ni
            pooled, var_pooled = combine_effects(es, var, method_re='dl')
            ci_low = pooled - 1.96 * var_pooled**0.5
            ci_high = pooled + 1.96 * var_pooled**0.5
            results.append({
                group_col: group,
                'PooledPrevalence': round(float(pooled), 4),
                '95% CI lower': round(float(ci_low), 4),
                '95% CI upper': round(float(ci_high), 4),
                'n_records': int(len(subdf))
            })
        except Exception:
            continue
    if not results:
        return {"warning": "Não foi possível calcular meta-análise para nenhum grupo (dados insuficientes)."}
    return {"results": results}
