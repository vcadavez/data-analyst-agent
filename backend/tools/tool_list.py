# backend/tools/tool_list.py

"""
Lista de todas as ferramentas (tools) registadas para uso pelo agente de dados.
Para adicionar novas ferramentas, basta importá-las e incluir em TOOLS.
"""

from backend.tools.tools import (
    search_index,
    count_unique_values,
    list_unique_values,
    describe_column,
    count_rows,
    get_column_names,
    summarize_by_category,
    count_rows_matching_value,
)
from backend.tools.filter_data_tool import filter_data_tool
from backend.tools.export_subset_tool import export_subset_tool
from backend.tools.plot_prevalence_by_column import plot_prevalence_by_column
from backend.tools.meta_analysis_by_column_tool import meta_analysis_by_column_tool

TOOLS = [
    search_index,
    count_unique_values,
    list_unique_values,
    describe_column,
    count_rows,
    get_column_names,
    summarize_by_category,
    count_rows_matching_value,
    filter_data_tool,
    export_subset_tool,
    plot_prevalence_by_column,
    meta_analysis_by_column_tool,
]
